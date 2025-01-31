import unittest
import os
import shutil
from src.core.remover import remove_metadata, remove_metadata_from_folder

class TestMetadataRemover(unittest.TestCase):

    def setUp(self):
        """Create test files and a test folder."""
        self.test_folder = "test_batch"
        self.output_folder = "test_batch_output"

        os.makedirs(self.test_folder, exist_ok=True)

        self.test_files = [
            os.path.join(self.test_folder, "test_image.jpg"),
            os.path.join(self.test_folder, "test_document.pdf"),
            os.path.join(self.test_folder, "test_document.docx"),
            os.path.join(self.test_folder, "test_audio.mp3"),
            os.path.join(self.test_folder, "test_video.mp4"),
        ]

        for file in self.test_files:
            open(file, 'a').close()  # Create empty test files

    def test_batch_processing(self):
        """Test metadata removal for a batch of files."""
        cleaned_files = remove_metadata_from_folder(self.test_folder, self.output_folder)
        self.assertEqual(len(cleaned_files), len(self.test_files))

        for file in cleaned_files:
            self.assertTrue(os.path.exists(file))

    def tearDown(self):
        """Clean up test files and folders."""
        shutil.rmtree(self.test_folder, ignore_errors=True)
        shutil.rmtree(self.output_folder, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
