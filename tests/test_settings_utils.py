import os
import unittest
from metadata_cleaner.config.settings import (
    DEFAULT_OUTPUT_FOLDER,
    ENABLE_PARALLEL_PROCESSING,
    LOG_LEVEL,
    SUPPORTED_FORMATS,
)
from metadata_cleaner.core.metadata_utils import ensure_output_folder, copy_file_without_metadata, get_file_extension

class TestSettingsAndUtils(unittest.TestCase):
    def test_default_output_folder(self) -> None:
        """
        Test that the default output folder is set correctly.
        """
        self.assertEqual(DEFAULT_OUTPUT_FOLDER, "cleaned")

    def test_parallel_processing_flag(self) -> None:
        """
        Test that the parallel processing flag is a boolean value.
        """
        self.assertIsInstance(ENABLE_PARALLEL_PROCESSING, bool)

    def test_log_level(self) -> None:
        """
        Test that the log level is one of the valid options.
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self.assertIn(LOG_LEVEL, valid_levels)

    def test_supported_formats(self) -> None:
        """
        Test that supported formats include key file type categories.
        """
        self.assertIn("images", SUPPORTED_FORMATS)
        self.assertIn("documents", SUPPORTED_FORMATS)
        self.assertIn("audio", SUPPORTED_FORMATS)
        self.assertIn("videos", SUPPORTED_FORMATS)

    def test_ensure_output_folder(self) -> None:
        """
        Test that ensure_output_folder creates the specified directory if it does not exist.
        """
        test_folder = "test_output_folder"
        ensure_output_folder(test_folder)
        self.assertTrue(os.path.exists(test_folder))
        os.rmdir(test_folder)  # Cleanup after test

    def test_copy_file_without_metadata(self) -> None:
        """
        Test that copy_file_without_metadata correctly copies a file.
        """
        test_file = "test_original.txt"
        copied_file = "test_copied.txt"

        # Create a test file.
        with open(test_file, "w") as f:
            f.write("Test file content")

        result = copy_file_without_metadata(test_file, copied_file)
        self.assertTrue(result is not None and os.path.exists(result))

        # Cleanup
        os.remove(test_file)
        os.remove(copied_file)

    def test_get_file_extension(self) -> None:
        """
        Test that get_file_extension correctly extracts the file extension in lowercase.
        """
        self.assertEqual(get_file_extension("image.JPG"), ".jpg")
        self.assertEqual(get_file_extension("document.PDF"), ".pdf")
        self.assertEqual(get_file_extension("music.mp3"), ".mp3")

if __name__ == "__main__":
    unittest.main()
