import os
import json
import tempfile
import unittest
import piexif
from PIL import Image
from typing import Optional, Dict
from metadata_cleaner.file_handlers.image_handler import remove_image_metadata


def create_test_image(path: str) -> None:
    """
    Create a test image with dummy EXIF data.

    The EXIF data includes:
      - Orientation (tag 274) in the '0th' IFD.
      - DateTimeOriginal (tag 36867) in the 'Exif' IFD.
      - GPS data in the 'GPS' IFD.

    Args:
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


class TestMetadataFilter(unittest.TestCase):
    def setUp(self) -> None:
        """
        Creates a temporary test directory and generates a test image with EXIF data.
        """
        self.tmpdir = tempfile.TemporaryDirectory()
        self.input_path = os.path.join(self.tmpdir.name, "test.jpg")
        self.output_path = os.path.join(self.tmpdir.name, "test_cleaned.jpg")
        
        # Create test image with EXIF data
        create_test_image(self.input_path)

        # Create metadata filter configuration
        self.test_rules: Dict[str, bool] = {
            "Orientation": False,         # Remove orientation
            "GPS": "remove",              # Remove GPS data
            "Timestamp": "date_only",     # Convert timestamp to date only
            "CameraSettings": "all_except_make_model",
            "Descriptions": False,
            "Thumbnail": False,
            "ImageMetrics": False
        }
        self.config_path = os.path.join(self.tmpdir.name, "test_config.json")
        with open(self.config_path, "w") as f:
            json.dump(self.test_rules, f)

    def test_image_filtering(self) -> None:
        """
        Test that image metadata removal correctly applies filter rules.

        - Orientation (tag 274) should be removed.
        - GPS data should be removed.
        - Timestamp (tag 36867) should be converted to date-only.
        """
        # Run metadata removal on the test image
        result: Optional[str] = remove_image_metadata(self.input_path, self.output_path, self.config_path)
        self.assertIsNotNone(result, "Metadata removal failed.")

        # Load the cleaned image's EXIF data
        img = Image.open(self.output_path)
        exif_data = piexif.load(img.info.get("exif", b""))

        # Verify that Orientation (tag 274) has been removed
        self.assertNotIn(274, exif_data.get("0th", {}), "Orientation should be removed.")

        # Verify that GPS data has been removed
        self.assertEqual(exif_data.get("GPS", {}), {}, "GPS data should be removed.")

        # Verify that Timestamp (tag 36867) is converted to date-only
        timestamp = exif_data.get("Exif", {}).get(36867, b"").decode("utf-8")
        self.assertEqual(len(timestamp.split(" ")), 1, "Timestamp should be date-only.")

    def tearDown(self) -> None:
        """
        Cleans up temporary test files.
        """
        self.tmpdir.cleanup()


if __name__ == "__main__":
    unittest.main()
