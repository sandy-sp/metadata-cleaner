import os
import unittest
from metadata_cleaner.core.metadata_processor import metadata_processor
from metadata_cleaner.core.file_utils import validate_file, get_safe_output_path
from metadata_cleaner.core.logger import logger

class TestMetadataCleaner(unittest.TestCase):
    def setUp(self):
        """Setup test files and directories."""
        self.test_image = "test_image.jpg"
        self.test_doc = "test_document.pdf"
        self.test_audio = "test_audio.mp3"
        self.test_video = "test_video.mp4"
        
        # Create dummy test files
        for file in [self.test_image, self.test_doc, self.test_audio, self.test_video]:
            with open(file, "w") as f:
                f.write("Dummy file content")
    
    def tearDown(self):
        """Cleanup test files."""
        for file in [self.test_image, self.test_doc, self.test_audio, self.test_video]:
            if os.path.exists(file):
                os.remove(file)
    
    def test_validate_file(self):
        """Test file validation function."""
        self.assertTrue(validate_file(self.test_image))
        self.assertFalse(validate_file("non_existent_file.txt"))
    
    def test_get_safe_output_path(self):
        """Test safe output path generation."""
        output_path = get_safe_output_path(self.test_image, prefix="cleaned_")
        self.assertTrue(output_path.startswith("cleaned_"))
    
    def test_view_metadata(self):
        """Test metadata extraction."""
        metadata = metadata_processor.view_metadata(self.test_image)
        self.assertIsInstance(metadata, dict)
    
    def test_remove_metadata(self):
        """Test metadata removal."""
        output_file = metadata_processor.delete_metadata(self.test_image)
        self.assertTrue(os.path.exists(output_file))
    
    def test_edit_metadata(self):
        """Test metadata editing."""
        metadata_changes = {"Author": "Test User"}
        output_file = metadata_processor.edit_metadata(self.test_doc, metadata_changes)
        self.assertTrue(os.path.exists(output_file))
        
if __name__ == "__main__":
    unittest.main()
