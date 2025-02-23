import os
import piexif
from PIL import Image
import json
import tempfile
from src.file_handlers.image_handler import remove_image_metadata

def create_test_image(path):
    img = Image.new("RGB", (100, 100), color="red")
    # Inject dummy Exif data (Orientation: 1, GPS: some value, Timestamp: "2025:02:23 10:00:00")
    exif_dict = {
        "0th": {
            274: 1,  # Orientation
            36867: "2025:02:23 10:00:00"
        },
        "GPS": {
            1: b"N",
            2: ((40, 1), (26, 1), (0, 1))  # Some GPS data
        },
        "Exif": {},
        "1st": {},
        "thumbnail": None
    }
    exif_bytes = piexif.dump(exif_dict)
    img.save(path, exif=exif_bytes)

def test_image_filtering():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "test.jpg")
        output_path = os.path.join(tmpdir, "test_cleaned.jpg")
        # Create a test image with dummy Exif data.
        create_test_image(input_path)

        # Create a temporary config file with our test rules.
        test_rules = {
            "Orientation": False,
            "GPS": "remove",
            "Timestamp": "date_only",
            "CameraSettings": "all_except_make_model",
            "Descriptions": False,
            "Thumbnail": False,
            "ImageMetrics": False
        }
        config_path = os.path.join(tmpdir, "test_config.json")
        with open(config_path, "w") as f:
            json.dump(test_rules, f)

        # Run metadata removal.
        result = remove_image_metadata(input_path, output_path, config_path)
        assert result is not None
        # Load the cleaned image's Exif data.
        img = Image.open(output_path)
        exif_data = piexif.load(img.info.get("exif", b""))
        # Check that Orientation and GPS data have been removed.
        assert 274 not in exif_data.get("0th", {}), "Orientation should be removed"
        assert exif_data.get("GPS", {}) == {}, "GPS data should be removed"
        # Check that the timestamp is date-only.
        timestamp = exif_data.get("0th", {}).get(36867, b"").decode("utf-8")
        assert len(timestamp.split(" ")) == 1, "Timestamp should be date only"

if __name__ == "__main__":
    test_image_filtering()
    print("Test passed!")
