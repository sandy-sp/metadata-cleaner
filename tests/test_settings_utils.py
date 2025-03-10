import os
import unittest
import tempfile
import shutil
import logging
from unittest.mock import patch
from metadata_cleaner.config.settings import (
    DEFAULT_OUTPUT_FOLDER,
    ENABLE_PARALLEL_PROCESSING,
    LOG_LEVEL,
    SUPPORTED_FORMATS,
)
from metadata_cleaner.core.metadata_utils import (
    ensure_output_folder,
    copy_file_without_metadata,
    get_file_extension,
)

class TestSettingsAndUtils(unittest.TestCase):
    def test_default_output_folder(self):
        """
        Test that the default output folder is set correctly.
        """
        self.assertEqual(DEFAULT_OUTPUT_FOLDER, "cleaned")

    def test_parallel_processing_flag(self):
        """
        Test that the parallel processing flag is a boolean value.
        """
        self.assertIsInstance(ENABLE_PARALLEL_PROCESSING, bool)

    def test_log_level(self):
        """
        Test that the log level is one of the valid options.
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self.assertIn(LOG_LEVEL, valid_levels)

    def test_supported_formats(self):
        """
        Test that supported formats include key file type categories.
        """
        self.assertTrue("images" in SUPPORTED_FORMATS)
        self.assertTrue("documents" in SUPPORTED_FORMATS)
        self.assertTrue("audio" in SUPPORTED_FORMATS)
        self.assertTrue("videos" in SUPPORTED_FORMATS)

    @patch.dict(os.environ, {"METADATA_CLEANER_OUTPUT_DIR": "custom_output"})
    def test_environment_variable_override(self):
        """
        Test that environment variable overrides the default output folder.
        """
        from importlib import reload
        import metadata_cleaner.config.settings as settings
        reload(settings)
        self.assertEqual(settings.DEFAULT_OUTPUT_FOLDER, "custom_output")

    def test_ensure_output_folder(self):
        """
        Test that ensure_output_folder creates the specified directory if it does not exist.
        """
        test_folder = tempfile.mkdtemp()
        test_subfolder = os.path.join(test_folder, "test_output_folder")
        ensure_output_folder(test_subfolder)
        self.assertTrue(os.path.exists(test_subfolder))
        shutil.rmtree(test_folder)

    def test_copy_file_without_metadata(self):
        """
        Test that copy_file_without_metadata correctly copies a file.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_original.txt")
            copied_file = os.path.join(temp_dir, "test_copied.txt")

            with open(test_file, "w") as f:
                f.write("Test file content")

            result = copy_file_without_metadata(test_file, copied_file)
            self.assertTrue(result is not None and os.path.exists(result))

    def test_copy_file_without_metadata_missing_source(self):
        """
        Test copy_file_without_metadata when source file is missing.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_file = os.path.join(temp_dir, "test_copied.txt")
            try:
                result = copy_file_without_metadata("non_existent.txt", copied_file)
            except FileNotFoundError:
                result = None
            self.assertIsNone(result)

    def test_get_file_extension(self):
        """
        Test that get_file_extension correctly extracts the file extension in lowercase.
        """
        self.assertEqual(get_file_extension("image.JPG"), ".jpg")
        self.assertEqual(get_file_extension("document.PDF"), ".pdf")
        self.assertEqual(get_file_extension("music.mp3"), ".mp3")
        self.assertEqual(get_file_extension("hiddenfile"), "")
        self.assertEqual(get_file_extension(".config"), "")

if __name__ == "__main__":
    unittest.main()
