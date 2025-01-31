import os
import unittest
from src.remover import remove_metadata
from src.file_handlers.image_handler import remove_image_metadata
from src.file_handlers.pdf_handler import remove_pdf_metadata
from src.file_handlers.docx_handler import remove_docx_metadata
from src.file_handlers.audio_handler import remove_audio_metadata
from src.file_handlers.video_handler import remove_video_metadata

class TestAllFileFormats(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test files."""
        cls.test_folder = "test_folder"
        cls.files = {
            "image": "test.jpg",
            "pdf": "test.pdf",
            "docx": "test.docx",
            "audio": "test.mp3",
            "video": "test.mp4",
        }

    def test_image_metadata_removal(self):
        """Test metadata removal for an image file."""
        file_path = os.path.join(self.test_folder, self.files["image"])
        cleaned_file = remove_image_metadata(file_path)
        self.assertTrue(os.path.exists(cleaned_file))

    def test_pdf_metadata_removal(self):
        """Test metadata removal for a PDF file."""
        file_path = os.path.join(self.test_folder, self.files["pdf"])
        cleaned_file = remove_pdf_metadata(file_path)
        self.assertTrue(os.path.exists(cleaned_file))

    def test_docx_metadata_removal(self):
        """Test metadata removal for a DOCX file."""
        file_path = os.path.join(self.test_folder, self.files["docx"])
        cleaned_file = remove_docx_metadata(file_path)
        self.assertTrue(os.path.exists(cleaned_file))

    def test_audio_metadata_removal(self):
        """Test metadata removal for an audio file."""
        file_path = os.path.join(self.test_folder, self.files["audio"])
        cleaned_file = remove_audio_metadata(file_path)
        self.assertTrue(os.path.exists(cleaned_file))

    def test_video_metadata_removal(self):
        """Test metadata removal for a video file."""
        file_path = os.path.join(self.test_folder, self.files["video"])
        cleaned_file = remove_video_metadata(file_path)
        self.assertTrue(os.path.exists(cleaned_file))

    @classmethod
    def tearDownClass(cls):
        """Clean up test files."""
        for file in cls.files.values():
            cleaned_file = os.path.join(cls.test_folder, file)
            if os.path.exists(cleaned_file):
                os.remove(cleaned_file)

if __name__ == "__main__":
    unittest.main()
