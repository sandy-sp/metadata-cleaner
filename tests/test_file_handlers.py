import unittest
import os
import subprocess
from PIL import Image
from docx import Document
from PyPDF2 import PdfWriter
from src.file_handlers.image_handler import remove_image_metadata
from src.file_handlers.pdf_handler import remove_pdf_metadata
from src.file_handlers.docx_handler import remove_docx_metadata
from src.file_handlers.audio_handler import remove_audio_metadata
from src.file_handlers.video_handler import remove_video_metadata

class TestFileHandlers(unittest.TestCase):

    def setUp(self):
        """Create valid test files."""
        self.test_image = "test_image.jpg"
        self.test_pdf = "test_document.pdf"
        self.test_docx = "test_document.docx"
        self.test_audio = "test_audio.mp3"
        self.test_video = "test_video.mp4"

        # ✅ Create a valid JPG file
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(self.test_image, "JPEG")

        # ✅ Create a valid PDF
        writer = PdfWriter()
        writer.add_metadata({"/Author": "Test"})
        with open(self.test_pdf, "wb") as f:
            writer.write(f)

        # ✅ Create a valid DOCX file
        doc = Document()
        doc.add_paragraph("This is a test document.")
        doc.save(self.test_docx)

        # ✅ Create a valid MP3 file
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                        "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", self.test_audio, "-y"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # ✅ Create a valid MP4 file
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3",
                        "-vf", "format=yuv420p", self.test_video, "-y"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
