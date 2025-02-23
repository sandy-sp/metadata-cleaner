import unittest
import os
import subprocess
from PIL import Image
from docx import Document
from PyPDF2 import PdfWriter
from metadata_cleaner.file_handlers.image_handler import remove_image_metadata
from metadata_cleaner.file_handlers.pdf_handler import remove_pdf_metadata
from metadata_cleaner.file_handlers.docx_handler import remove_docx_metadata
from metadata_cleaner.file_handlers.audio_handler import remove_audio_metadata
from metadata_cleaner.file_handlers.video_handler import remove_video_metadata
from typing import Optional

class TestFileHandlers(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create valid test files for each supported file type.
        """
        self.test_image: str = "test_image.jpg"
        self.test_pdf: str = "test_document.pdf"
        self.test_docx: str = "test_document.docx"
        self.test_audio: str = "test_audio.mp3"
        self.test_video: str = "test_video.mp4"

        # Create a valid JPG file
        img: Image = Image.new("RGB", (100, 100), color="blue")
        img.save(self.test_image, "JPEG")

        # Create a valid PDF file
        writer: PdfWriter = PdfWriter()
        writer.add_metadata({"/Author": "Test"})
        with open(self.test_pdf, "wb") as f:
            writer.write(f)

        # Create a valid DOCX file
        doc: Document = Document()
        doc.add_paragraph("This is a test document.")
        doc.save(self.test_docx)

        # Create a valid MP3 file using ffmpeg
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", self.test_audio, "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Create a valid MP4 file using ffmpeg
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3",
            "-vf", "format=yuv420p", self.test_video, "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def test_image_handler(self) -> None:
        """Test image metadata removal."""
        output_file: Optional[str] = remove_image_metadata(self.test_image)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_pdf_handler(self) -> None:
        """Test PDF metadata removal."""
        output_file: Optional[str] = remove_pdf_metadata(self.test_pdf)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_docx_handler(self) -> None:
        """Test DOCX metadata removal."""
        output_file: Optional[str] = remove_docx_metadata(self.test_docx)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_audio_handler(self) -> None:
        """Test audio metadata removal."""
        output_file: Optional[str] = remove_audio_metadata(self.test_audio)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_video_handler(self) -> None:
        """Test video metadata removal."""
        output_file: Optional[str] = remove_video_metadata(self.test_video)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

    def tearDown(self) -> None:
        """
        Clean up test files created during the tests.
        """
        for file in [self.test_image, self.test_pdf, self.test_docx, self.test_audio, self.test_video]:
            if os.path.exists(file):
                os.remove(file)
        # Optionally, remove any generated output files (e.g., *_cleaned.*)
        for file in os.listdir("."):
            if file.endswith("_cleaned.jpg") or file.endswith("_cleaned.pdf") or file.endswith("_cleaned.docx"):
                os.remove(file)

if __name__ == "__main__":
    unittest.main()
