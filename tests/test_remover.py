import os
import subprocess
import unittest
import shutil
from typing import Optional
from PIL import Image
from docx import Document
from PyPDF2 import PdfWriter
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder

class TestMetadataRemover(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create valid test files for each supported file type in a test folder.
        """
        self.test_folder: str = "test_batch"
        self.output_folder: str = "test_batch_output"
        os.makedirs(self.test_folder, exist_ok=True)

        # Create a valid JPG file
        image_path: str = os.path.join(self.test_folder, "test_image.jpg")
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image_path, "JPEG")

        # Create a valid PDF file
        pdf_path: str = os.path.join(self.test_folder, "test_document.pdf")
        writer: PdfWriter = PdfWriter()
        writer.add_metadata({"/Author": "Test"})
        with open(pdf_path, "wb") as f:
            writer.write(f)

        # Create a valid DOCX file
        docx_path: str = os.path.join(self.test_folder, "test_document.docx")
        doc = Document()
        doc.add_paragraph("This is a test document.")
        doc.save(docx_path)

        # Create a valid MP3 file using ffmpeg
        self.test_audio: str = os.path.join(self.test_folder, "test_audio.mp3")
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", self.test_audio, "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Create a valid MP4 file using ffmpeg
        self.test_video: str = os.path.join(self.test_folder, "test_video.mp4")
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3",
            "-vf", "format=yuv420p", self.test_video, "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def test_batch_processing(self) -> None:
        """
        Test batch metadata removal for all supported file types in the test folder.

        Verifies that the number of processed files matches the number of created files and that each output file exists.
        """
        cleaned_files: list = remove_metadata_from_folder(self.test_folder, self.output_folder)
        # We expect 5 files to be processed.
        self.assertEqual(len(cleaned_files), 5, "Expected 5 files to be processed in batch mode.")

        for file_path in cleaned_files:
            self.assertTrue(os.path.exists(file_path), f"Cleaned file does not exist: {file_path}")

    def tearDown(self) -> None:
        """
        Clean up test directories created during the tests.
        """
        shutil.rmtree(self.test_folder, ignore_errors=True)
        shutil.rmtree(self.output_folder, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
