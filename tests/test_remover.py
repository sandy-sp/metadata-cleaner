import unittest
import os
from src.core.remover import remove_metadata

class TestMetadataRemover(unittest.TestCase):

    def setUp(self):
        """Create sample test files before each test."""
        self.test_image = "test_image.jpg"
        self.test_pdf = "test_document.pdf"
        self.test_docx = "test_document.docx"
        self.test_audio = "test_audio.mp3"
        self.test_video = "test_video.mp4"
        
        # Create dummy files
        open(self.test_image, 'a').close()
        open(self.test_pdf, 'a').close()
        open(self.test_docx, 'a').close()
        open(self.test_audio, 'a').close()
        open(self.test_video, 'a').close()

    def test_remove_image_metadata(self):
        """Test metadata removal for images."""
        output_file = remove_metadata(self.test_image)
        self.assertTrue(os.path.exists(output_file))

    def test_remove_pdf_metadata(self):
        """Test metadata removal for PDFs."""
        output_file = remove_metadata(self.test_pdf)
        self.assertTrue(os.path.exists(output_file))

    def test_remove_docx_metadata(self):
        """Test metadata removal for DOCX files."""
        output_file = remove_metadata(self.test_docx)
        self.assertTrue(os.path.exists(output_file))

    def test_remove_audio_metadata(self):
        """Test metadata removal for audio files."""
        output_file = remove_metadata(self.test_audio)
        self.assertTrue(os.path.exists(output_file))

    def test_remove_video_metadata(self):
        """Test metadata removal for video files."""
        output_file = remove_metadata(self.test_video)
        self.assertTrue(os.path.exists(output_file))

    def test_invalid_file(self):
        """Test invalid file handling."""
        with self.assertRaises(FileNotFoundError):
            remove_metadata("non_existent_file.jpg")

    def tearDown(self):
        """Clean up test files after each test."""
        for file in [self.test_image, self.test_pdf, self.test_docx, self.test_audio, self.test_video]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    unittest.main()
