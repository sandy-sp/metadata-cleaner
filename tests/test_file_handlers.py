import unittest
import os
import subprocess
import shutil
from PIL import Image
from docx import Document
from pypdf import PdfReader, PdfWriter
from mutagen.mp3 import MP3
from typing import Optional
from metadata_cleaner.file_handlers.image_handler import remove_image_metadata
from metadata_cleaner.file_handlers.pdf_handler import remove_pdf_metadata
from metadata_cleaner.file_handlers.docx_handler import remove_docx_metadata
from metadata_cleaner.file_handlers.audio_handler import remove_audio_metadata
from metadata_cleaner.file_handlers.video_handler import remove_video_metadata


class TestFileHandlers(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create valid test files for each supported file type.
        """
        self.test_folder = "test_files"
        os.makedirs(self.test_folder, exist_ok=True)

        self.test_image = os.path.join(self.test_folder, "test_image.jpg")
        self.test_pdf = os.path.join(self.test_folder, "test_document.pdf")
        self.test_docx = os.path.join(self.test_folder, "test_document.docx")
        self.test_audio = os.path.join(self.test_folder, "test_audio.mp3")
        self.test_video = os.path.join(self.test_folder, "test_video.mp4")

        # Create a valid JPG file with EXIF metadata
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(self.test_image, "JPEG")

        # Create a valid PDF file with metadata
        writer = PdfWriter()
        writer.add_metadata({"/Author": "Test Author"})
        with open(self.test_pdf, "wb") as f:
            writer.write(f)

        # Create a valid DOCX file with metadata
        doc = Document()
        doc.add_paragraph("This is a test document.")
        doc.core_properties.author = "Test Author"
        doc.save(self.test_docx)

        # Create a valid MP3 file using FFmpeg (skip if FFmpeg is missing)
        if shutil.which("ffmpeg"):
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", self.test_audio, "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Create a valid MP4 file using FFmpeg (skip if FFmpeg is missing)
        if shutil.which("ffmpeg"):
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3",
                "-vf", "format=yuv420p", self.test_video, "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def test_image_handler(self) -> None:
        """Test image metadata removal."""
        output_file: Optional[str] = remove_image_metadata(self.test_image)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

        # Verify metadata removal
        img = Image.open(output_file)
        self.assertNotIn("exif", img.info, "EXIF metadata not removed from image.")

    def test_pdf_handler(self) -> None:
        """Test PDF metadata removal."""
        output_file: Optional[str] = remove_pdf_metadata(self.test_pdf)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

        # Verify metadata removal
        reader = PdfReader(output_file)
        self.assertFalse(reader.metadata, "Metadata not removed from PDF.")

    def test_docx_handler(self) -> None:
        """Test DOCX metadata removal."""
        output_file: Optional[str] = remove_docx_metadata(self.test_docx)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

        # Verify metadata removal
        doc = Document(output_file)
        self.assertFalse(doc.core_properties.author, "Metadata not removed from DOCX.")

    def test_audio_handler(self) -> None:
        """Test audio metadata removal."""
        if not shutil.which("ffmpeg"):
            self.skipTest("FFmpeg not found, skipping audio test.")

        output_file: Optional[str] = remove_audio_metadata(self.test_audio)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

        # Verify metadata removal
        audio = MP3(output_file)
        self.assertFalse(audio.tags, "Metadata not removed from MP3.")

    def test_video_handler(self) -> None:
        """Test video metadata removal."""
        if not shutil.which("ffmpeg"):
            self.skipTest("FFmpeg not found, skipping video test.")

        output_file: Optional[str] = remove_video_metadata(self.test_video)
        self.assertIsNotNone(output_file)
        self.assertTrue(os.path.exists(output_file))

    def tearDown(self) -> None:
        """
        Clean up test files created during the tests.
        """
        shutil.rmtree(self.test_folder, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
