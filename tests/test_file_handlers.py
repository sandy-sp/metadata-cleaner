import unittest
import os
from src.file_handlers.image_handler import remove_image_metadata
from src.file_handlers.pdf_handler import remove_pdf_metadata
from src.file_handlers.docx_handler import remove_docx_metadata
from src.file_handlers.audio_handler import remove_audio_metadata
from src.file_handlers.video_handler import remove_video_metadata

class TestFileHandlers(unittest.TestCase):

    def setUp(self):
        """Create dummy test files."""
        self.test_image = "test_image.jpg"
        self.test_pdf = "test_document.pdf"
        self.test_docx = "test_document.docx"
        self.test_audio = "test_audio.mp3"
        self.test_video = "test_video.mp4"
        
        open(self.test_image, 'a').close()
        open(self.test_pdf, 'a').close()
        open(self.test_docx, 'a').close()
        open(self.test_audio, 'a').close()
        open(self.test_video, 'a').close()

    def test_image_handler(self):
        """Test image metadata removal."""
        output_file = remove_image_metadata(self.test_image)
        self.assertTrue(os.path.exists(output_file))

    def test_pdf_handler(self):
        """Test PDF metadata removal."""
        output_file = remove_pdf_metadata(self.test_pdf)
        self.assertTrue(os.path.exists(output_file))

    def test_docx_handler(self):
        """Test DOCX metadata removal."""
        output_file = remove_docx_metadata(self.test_docx)
        self.assertTrue(os.path.exists(output_file))

    def test_audio_handler(self):
        """Test audio metadata removal."""
        output_file = remove_audio_metadata(self.test_audio)
        self.assertTrue(os.path.exists(output_file))

    def test_video_handler(self):
        """Test video metadata removal."""
        output_file = remove_video_metadata(self.test_video)
        self.assertTrue(os.path.exists(output_file))

    def tearDown(self):
        """Clean up test files."""
        for file in [self.test_image, self.test_pdf, self.test_docx, self.test_audio, self.test_video]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    unittest.main()
