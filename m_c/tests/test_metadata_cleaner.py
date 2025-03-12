import os
import shutil
import unittest
import hashlib
from m_c.core.metadata_processor import MetadataProcessor
from m_c.core.file_utils import validate_file, get_safe_output_path
from m_c.core.logger import logger
from m_c.utils.tool_utils import ToolManager

class TestMetadataCleaner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment before all tests."""
        cls.test_dir = "m_c/tests/sample"
        cls.cleaned_dir = os.path.join(cls.test_dir, "cleaned")

        # Create necessary directories
        os.makedirs(cls.test_dir, exist_ok=True)
        os.makedirs(cls.cleaned_dir, exist_ok=True)

        # Define test files
        cls.test_files = {
            "image": os.path.join(cls.test_dir, "sample.jpg"),
            "document": os.path.join(cls.test_dir, "sample.pdf"),
            "audio": os.path.join(cls.test_dir, "sample.mp3"),
            "video": os.path.join(cls.test_dir, "sample.mp4"),
        }

        # Create dummy test files
        for file in cls.test_files.values():
            with open(file, "w") as f:
                f.write("Dummy file content")

        # Initialize MetadataProcessor instance
        cls.processor = MetadataProcessor()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if os.path.exists(cls.cleaned_dir):
            shutil.rmtree(cls.cleaned_dir)

    def test_validate_file(self):
        """Test file validation function."""
        for file in self.test_files.values():
            self.assertTrue(validate_file(file))
        self.assertFalse(validate_file("non_existent_file.txt"))

    def test_get_safe_output_path(self):
        """Test safe output path generation."""
        output_path = get_safe_output_path(self.test_files["image"], prefix="cleaned_")
        self.assertTrue(os.path.basename(output_path).startswith("cleaned_"))

    def test_view_metadata(self):
        """Test metadata extraction."""
        metadata = self.processor.view_metadata(self.test_files["image"])
        self.assertIsInstance(metadata, dict)

    def test_remove_metadata(self):
        """Test metadata removal for all file types."""
        for category, file_path in self.test_files.items():
            cleaned_file_path = os.path.join(self.cleaned_dir, f"cleaned_{os.path.basename(file_path)}")

            output_file = self.processor.delete_metadata(file_path, cleaned_file_path)
            self.assertIsNotNone(output_file, f"Failed to clean {category} file")
            self.assertTrue(os.path.exists(cleaned_file_path), f"Cleaned file missing: {cleaned_file_path}")

    def test_edit_metadata(self):
        """Test metadata editing."""
        metadata_changes = {"Author": "Test User"}
        output_file = self.processor.edit_metadata(self.test_files["document"], metadata_changes)
        self.assertTrue(os.path.exists(output_file))

    def test_handle_corrupt_file(self):
        """Test handling of a corrupt file."""
        corrupt_file = os.path.join(self.test_dir, "corrupt.jpg")

        # Create a dummy corrupt file
        with open(corrupt_file, "wb") as f:
            f.write(b"corrupt data")

        result = self.processor.view_metadata(corrupt_file)
        self.assertTrue(result is None or "error" in str(result).lower())

        os.remove(corrupt_file)

    def compute_hash(self, file_path):
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()

    def test_no_data_loss_after_removal(self):
        """Ensure the cleaned file maintains data integrity (except metadata)."""
        original_file = self.test_files["image"]
        cleaned_file = os.path.join(self.cleaned_dir, "sample_cleaned.jpg")

        self.processor.delete_metadata(original_file, cleaned_file)

        self.assertTrue(os.path.exists(cleaned_file))
        self.assertEqual(self.compute_hash(original_file), self.compute_hash(cleaned_file))

    def test_fallback_mechanism(self):
        """Test if fallback tools work when the primary tool fails."""
        test_file = self.test_files["image"]
        fallback_file = os.path.join(self.test_dir, "fallback_test.jpg")
        shutil.copyfile(test_file, fallback_file)

        # Ensure ToolManager is properly initialized
        tool_manager = ToolManager()
        tool_manager.check_tools()  # Ensures `_cached_tools` is set

        # Simulate failure by modifying cached tools
        tool_manager._cached_tools["ExifTool"] = False

        metadata = self.processor.view_metadata(fallback_file)
        self.assertIsNotNone(metadata, "Fallback mechanism failed to extract metadata")

        os.remove(fallback_file)

    def test_clean_all_files_in_sample(self):
        """Test cleaning all files in the 'sample' directory and saving to 'cleaned'."""
        files = [f for f in os.listdir(self.test_dir) if os.path.isfile(os.path.join(self.test_dir, f))]

        for file in files:
            file_path = os.path.join(self.test_dir, file)
            cleaned_file_path = os.path.join(self.cleaned_dir, file)

            self.assertTrue(validate_file(file_path), f"Invalid file: {file_path}")

            output_file = self.processor.delete_metadata(file_path, cleaned_file_path)

            self.assertIsNotNone(output_file, f"Failed to clean: {file_path}")
            self.assertTrue(os.path.exists(cleaned_file_path), f"Cleaned file missing: {cleaned_file_path}")

    def test_validate_cleaned_files(self):
        """Ensure cleaned files exist and have valid content."""
        cleaned_files = [f for f in os.listdir(self.cleaned_dir) if os.path.isfile(os.path.join(self.cleaned_dir, f))]
        original_files = [f for f in os.listdir(self.test_dir) if os.path.isfile(os.path.join(self.test_dir, f))]

        logger.info(f"Original files count: {len(original_files)}")
        logger.info(f"Cleaned files count: {len(cleaned_files)}")

        self.assertEqual(len(cleaned_files), len(original_files), "Mismatch between cleaned and original files")

if __name__ == "__main__":
    unittest.main()
