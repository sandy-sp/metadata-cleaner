import os
import json
import tempfile
from typing import Optional
import piexif
from PIL import Image
from metadata_cleaner.file_handlers.image_handler import remove_image_metadata

def create_test_image(path: str) -> None:
    """
    Create a test image with dummy EXIF data.

    The EXIF data includes:
      - Orientation (tag 274) in the '0th' IFD.
      - DateTimeOriginal (tag 36867) in the 'Exif' IFD.
      - GPS data in the 'GPS' IFD.
    
    Parameters:
        path (str): The path where the test image will be saved.
    """
    img = Image.new("RGB", (100, 100), color="red")
    exif_dict = {
        "0th": {274: 1},  # Orientation
        "Exif": {36867: "2025:02:23 10:00:00"},  # DateTimeOriginal
        "GPS": {1: b"N", 2: ((40, 1), (26, 1), (0, 1))},  # GPS data
        "1st": {},
        "thumbnail": None
    }
    exif_bytes = piexif.dump(exif_dict)
    img.save(path, exif=exif_bytes)

def test_image_filtering() -> None:
    """
    Test that the image filtering function removes or modifies EXIF data as per configuration.

    It creates a test image with known EXIF data, then applies metadata removal using a test configuration,
    and finally verifies that:
      - Orientation (tag 274) is removed if set to False.
      - GPS data is removed if configured.
      - Timestamp (DateTimeOriginal, tag 36867) is converted to date-only.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path: str = os.path.join(tmpdir, "test.jpg")
        output_path: str = os.path.join(tmpdir, "test_cleaned.jpg")
        # Create a test image with dummy EXIF data.
        create_test_image(input_path)

        # Create a temporary configuration file with our test rules.
        test_rules = {
            "Orientation": False,         # Remove orientation
            "GPS": "remove",              # Remove GPS data
            "Timestamp": "date_only",     # Convert timestamp to date only
            "CameraSettings": "all_except_make_model",
            "Descriptions": False,
            "Thumbnail": False,
            "ImageMetrics": False
        }
        config_path: str = os.path.join(tmpdir, "test_config.json")
        with open(config_path, "w") as f:
            json.dump(test_rules, f)

        # Run metadata removal on the test image.
        result: Optional[str] = remove_image_metadata(input_path, output_path, config_path)
        assert result is not None, "Metadata removal should succeed."

        # Load the cleaned image's EXIF data.
        img = Image.open(output_path)
        exif_data = piexif.load(img.info.get("exif", b""))
        
        # Verify that Orientation (tag 274) has been removed.
        assert 274 not in exif_data.get("0th", {}), "Orientation should be removed."
        
        # Verify that GPS data has been removed.
        assert exif_data.get("GPS", {}) == {}, "GPS data should be removed."
        
        # Verify that Timestamp (tag 36867) is converted to date-only.
        timestamp = exif_data.get("Exif", {}).get(36867, b"").decode("utf-8")
        assert len(timestamp.split(" ")) == 1, "Timestamp should be date only."

if __name__ == "__main__":
    test_image_filtering()
    print("Test passed!")
