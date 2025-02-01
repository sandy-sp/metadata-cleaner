from PIL import Image
import subprocess
import unittest
import os
import shutil
from docx import Document
from PyPDF2 import PdfWriter
from src.remover import remove_metadata, remove_metadata_from_folder

class TestMetadataRemover(unittest.TestCase):

    def setUp(self):
        """Create valid test files with actual content."""
        self.test_folder = "test_batch"
        self.output_folder = "test_batch_output"
        os.makedirs(self.test_folder, exist_ok=True)

        # ✅ Create a valid JPG file
        image_path = os.path.join(self.test_folder, "test_image.jpg")
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image_path, "JPEG")

        # ✅ Create a valid PDF file
        writer = PdfWriter()
        writer.add_metadata({"/Author": "Test"})
        with open(os.path.join(self.test_folder, "test_document.pdf"), "wb") as f:
            writer.write(f)

        # ✅ Create a valid DOCX file
        doc = Document()
        doc.add_paragraph("This is a test document.")
        doc.save(os.path.join(self.test_folder, "test_document.docx"))

        # ✅ Create a valid MP3 file
        mp3_path = os.path.join(self.test_folder, "test_audio.mp3")
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                        "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", mp3_path, "-y"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # ✅ Create a valid MP4 file
        mp4_path = os.path.join(self.test_folder, "test_video.mp4")
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=3",
                        "-vf", "format=yuv420p", mp4_path, "-y"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def test_batch_processing(self):
        """Test batch metadata removal."""
        cleaned_files = remove_metadata_from_folder(self.test_folder, self.output_folder)
        self.assertEqual(len(cleaned_files), 5)  # Expect all 5 files to be processed

        for file in cleaned_files:
            self.assertTrue(os.path.exists(file))

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_folder, ignore_errors=True)
        shutil.rmtree(self.output_folder, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
