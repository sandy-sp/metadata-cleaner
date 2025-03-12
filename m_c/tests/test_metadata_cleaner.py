import os
import unittest
import hashlib
from m_c.core.metadata_processor import metadata_processor
from m_c.core.file_utils import validate_file, get_safe_output_path
from m_c.core.logger import logger

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
    
    def test_handle_corrupt_file():
        """Test if the tool correctly handles a corrupt file."""
        corrupt_file = "corrupt.jpg"
        
        # Create a dummy corrupt file
        with open(corrupt_file, "wb") as f:
            f.write(b"corrupt data")

        result = metadata_processor.view_metadata(corrupt_file)
        
        # Expected to return None or an error message
        assert result is None or "error" in str(result).lower()
        
        os.remove(corrupt_file)

    def compute_hash(file_path):
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()

    def test_no_data_loss_after_removal():
        """Ensure the cleaned file maintains data integrity (except metadata)."""
        original_file = "sample.jpg"
        cleaned_file = "sample_cleaned.jpg"
        
        # Copy a sample image for testing
        shutil.copyfile("test_files/sample.jpg", original_file)
        
        metadata_processor.delete_metadata(original_file, cleaned_file)
        
        # Ensure the file exists
        assert os.path.exists(cleaned_file)
        
        # Verify file integrity
        assert compute_hash(original_file) == compute_hash(cleaned_file)
        
        os.remove(original_file)
        os.remove(cleaned_file)

    def test_fallback_mechanism():
        """Test if fallback tools work when the primary tool fails."""
        test_file = "test_image.jpg"
        shutil.copyfile("test_files/sample.jpg", test_file)

        # Simulate failure by disabling ExifTool
        tool_manager._cached_tools["ExifTool"] = False

        metadata = metadata_processor.view_metadata(test_file)
        
        # Ensure metadata is still extracted via fallback tools (Piexif)
        assert metadata is not None

        os.remove(test_file)

if __name__ == "__main__":
    unittest.main()
