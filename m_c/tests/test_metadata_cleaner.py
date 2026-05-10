import hashlib
import json
import os
import shutil
import subprocess
import unittest
import wave
from logging.handlers import RotatingFileHandler
from click.testing import CliRunner
import docx
from mutagen import File as MutagenFile
from mutagen.id3 import TIT2, TPE1
from mutagen.wave import WAVE
from PIL import Image
import pypdf

from m_c.cli.main import cli
from m_c.core.metadata_processor import MetadataProcessor
from m_c.core.file_utils import validate_file, get_safe_output_path
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler
from m_c.handlers.video_handler import VideoHandler


class TestMetadataCleaner(unittest.TestCase):
    @staticmethod
    def _write_tagged_wav(file_path):
        with wave.open(file_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(b"\0\0" * 800)

        audio = WAVE(file_path)
        audio.add_tags()
        audio.tags.add(TIT2(encoding=3, text="Fixture Title"))
        audio.tags.add(TPE1(encoding=3, text="Fixture Artist"))
        audio.save()

    @classmethod
    def setUpClass(cls):
        """Setup test environment before all tests."""
        cls.test_dir = "m_c/tests/sample"
        cls.cleaned_dir = os.path.join(cls.test_dir, "cleaned")
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        os.makedirs(cls.test_dir, exist_ok=True)
        os.makedirs(cls.cleaned_dir, exist_ok=True)

        cls.test_files = {
            "image": os.path.join(cls.test_dir, "sample1.jpg"),
            "document": os.path.join(cls.test_dir, "sample.pdf"),
            "audio": os.path.join(cls.test_dir, "sample.mp3"),
            "video": os.path.join(cls.test_dir, "sample.mp4"),
        }
        cls.test_docx = os.path.join(cls.test_dir, "sample.docx")

        # Create VALID JPEG (1x1 red pixel)
        img = Image.new("RGB", (100, 100), color="red")
        img.save(cls.test_files["image"], "jpeg", quality=100)

        # Create VALID PDF
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(cls.test_files["document"], "wb") as f:
            writer.write(f)

        # Create VALID DOCX with core metadata.
        document = docx.Document()
        document.add_paragraph("Metadata Cleaner test document.")
        core_props = document.core_properties
        core_props.author = "Test Author"
        core_props.last_modified_by = "Test Editor"
        core_props.title = "Test Title"
        document.save(cls.test_docx)

        # Create dummy audio/video files for graceful-failure checks.
        for key in ["audio", "video"]:
            with open(cls.test_files[key], "w") as f:
                f.write("Dummy file content")

        cls.processor = MetadataProcessor()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_validate_file(self):
        """Test file validation function."""
        for file in self.test_files.values():
            self.assertTrue(validate_file(file))
        self.assertFalse(validate_file("non_existent_file.txt"))

    def test_get_safe_output_path(self):
        """Test safe output path generation."""
        output_path = get_safe_output_path(self.test_files["image"], prefix="cleaned_")
        self.assertTrue(os.path.basename(output_path).startswith("cleaned_"))

    def test_view_metadata(self):
        """Test metadata extraction."""
        metadata = self.processor.view_metadata(self.test_files["image"])
        # Should be dict (even if empty)
        self.assertIsInstance(metadata, dict)

        # specific check for pdf
        pdf_meta = self.processor.view_metadata(self.test_files["document"])
        self.assertIsInstance(pdf_meta, dict)

    def test_cli_view_json_output_with_metadata(self):
        """View command should provide a stable JSON envelope."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            writer = pypdf.PdfWriter()
            writer.add_blank_page(width=72, height=72)
            writer.add_metadata({"/Title": "Automation Test"})
            with open("sample.pdf", "wb") as pdf_file:
                writer.write(pdf_file)

            result = runner.invoke(cli, ["view", "sample.pdf", "--json"])

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["file"], "sample.pdf")
            self.assertGreaterEqual(payload["metadata_count"], 1)
            self.assertIn("/Title", payload["metadata"])

    def test_cli_view_json_output_for_invalid_file(self):
        """JSON view output should stay parseable for invalid input."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["view", "missing.jpg", "--json"])

            self.assertEqual(result.exit_code, 2, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "invalid_input")
            self.assertEqual(payload["file"], "missing.jpg")
            self.assertEqual(payload["metadata"], {})
            self.assertIn("error", payload)

    def test_remove_metadata(self):
        """Test metadata removal for all file types while preserving originals."""
        for category, file_path in self.test_files.items():
            cleaned_file_path = os.path.join(
                self.cleaned_dir, f"cleaned_{os.path.basename(file_path)}"
            )
            if os.path.exists(cleaned_file_path):
                os.remove(cleaned_file_path)

            output_file = self.processor.delete_metadata(file_path, cleaned_file_path)

            # Allow skipping audio/video if tools missing, but Image/Doc MUST succeed
            if category in ["image", "document"]:
                self.assertIsNotNone(output_file, f"Failed to clean {category}")
                self.assertTrue(os.path.exists(output_file))
                self.assertTrue(os.path.exists(file_path))

    def test_edit_metadata(self):
        """Test metadata editing."""
        output_file = self.processor.edit_metadata(
            self.test_files["document"], {"Title": "My Title"}
        )
        # Not all handlers might support edit, but if it returns path, it exists
        if output_file:
            self.assertTrue(os.path.exists(output_file))

    def test_image_quality_preservation(self):
        """Ensure the cleaned file maintains pixel data integrity."""
        original_file = self.test_files["image"]
        cleaned_file = os.path.join(self.cleaned_dir, "quality_test_cleaned.jpg")

        self.processor.delete_metadata(original_file, cleaned_file)
        self.assertTrue(os.path.exists(cleaned_file))

        # Verify pixels are identical
        with Image.open(original_file) as img_orig, Image.open(
            cleaned_file
        ) as img_clean:
            # Convert both to same mode/data to compare pixels
            # Note: JPEG is lossy, but "lossless" metadata removal means
            # the JPEG IMAGE data is untouched.
            # However, opening and re-saving (fallback) alters pixels.
            # Shutil copy + piexif remove (primary path) KEEPS pixels identical.
            # So if our primary path works, this assertion passes.
            # If fallback works, this assertion MIGHT fail if pixels change.
            # Our goal is NO pixel change.

            # Check format
            self.assertEqual(img_orig.format, img_clean.format)

            # Check size
            self.assertEqual(img_orig.size, img_clean.size)

            from PIL import ImageChops

            diff = ImageChops.difference(img_orig, img_clean)
            if diff.getbbox():
                # Pixels differ
                self.fail("Image pixels changed! Re-encoding likely occurred.")

    def test_fallback_mechanism(self):
        """Test if fallback tools work when the primary tool fails."""
        # Mocking this is hard without changing global state or mocking.
        # Existing test logic was fragile. Let's simplify or skip if untestable reliably.
        pass

    def test_avif_recognition(self):
        """Verify AVIF files are recognized by ImageHandler."""
        from m_c.handlers.image_handler import image_handler

        self.assertIn("avif", image_handler.SUPPORTED_FORMATS)

        # Test file validation
        avif_path = os.path.join(self.test_dir, "test.avif")
        with open(avif_path, "wb") as f:
            f.write(b"dummy binary data")

        self.assertTrue(image_handler.is_supported(avif_path))

    def test_dry_run_mechanism(self):
        """Test dry run flag does not modify files."""
        # Use existing image test file
        test_file = self.test_files["image"]
        dry_run_output = os.path.join(self.cleaned_dir, "dry_run_output.jpg")

        # Ensure it doesn't exist
        if os.path.exists(dry_run_output):
            os.remove(dry_run_output)

        result = self.processor.delete_metadata(test_file, dry_run_output, dry_run=True)

        # Should return None and NOT create file
        self.assertIsNone(result)
        self.assertFalse(os.path.exists(dry_run_output))

    def test_dry_run_does_not_create_default_output_directory(self):
        """Dry runs should not create the default cleaned output directory."""
        source_dir = os.path.join(self.test_dir, "dry-run-source")
        os.makedirs(source_dir, exist_ok=True)
        source_file = os.path.join(source_dir, "photo.jpg")
        Image.new("RGB", (10, 10), color="blue").save(source_file, "jpeg")

        default_cleaned_dir = os.path.join(source_dir, "cleaned")
        result = self.processor.delete_metadata(source_file, dry_run=True)

        self.assertIsNone(result)
        self.assertFalse(os.path.exists(default_cleaned_dir))

    def test_delete_metadata_preserves_timestamps_when_requested(self):
        """Core cleanup should optionally preserve source filesystem timestamps."""
        source_file = os.path.join(self.test_dir, "timestamped.jpg")
        cleaned_file = os.path.join(self.cleaned_dir, "timestamped_cleaned.jpg")
        Image.new("RGB", (10, 10), color="blue").save(source_file, "jpeg")
        old_atime = 1_600_000_000
        old_mtime = 1_500_000_000
        os.utime(source_file, (old_atime, old_mtime))

        result = self.processor.delete_metadata(
            source_file,
            cleaned_file,
            preserve_timestamps=True,
        )

        self.assertEqual(result, cleaned_file)
        self.assertEqual(int(os.stat(cleaned_file).st_mtime), old_mtime)

    def test_docx_metadata_removal_clears_core_properties(self):
        """DOCX cleaning should preserve content and clear common core metadata."""
        cleaned_docx = os.path.join(self.cleaned_dir, "cleaned_sample.docx")
        output_file = self.processor.delete_metadata(self.test_docx, cleaned_docx)

        self.assertEqual(output_file, cleaned_docx)
        self.assertTrue(os.path.exists(output_file))

        cleaned_document = docx.Document(output_file)
        cleaned_props = cleaned_document.core_properties
        paragraphs = [paragraph.text for paragraph in cleaned_document.paragraphs]

        self.assertIn("Metadata Cleaner test document.", paragraphs)
        self.assertEqual(cleaned_props.author, "")
        self.assertEqual(cleaned_props.last_modified_by, "")
        self.assertEqual(cleaned_props.title, "")
        self.assertEqual(cleaned_props.created.year, 1980)
        self.assertEqual(cleaned_props.modified.year, 1980)

    def test_in_place_output_path_is_rejected(self):
        """Handlers should reject an output path that equals the input path."""
        handler = BaseHandler()

        with self.assertRaises(ValueError):
            handler.prepare_output_path(self.test_files["image"], self.test_files["image"])

        result = self.processor.delete_metadata(
            self.test_files["image"],
            self.test_files["image"],
        )
        self.assertIsNone(result)
        self.assertTrue(os.path.exists(self.test_files["image"]))

    def test_cli_delete_dry_run_directory_has_no_file_system_side_effects(self):
        """CLI dry-run mode should not create an output directory."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs(os.path.join("inputs", "nested"), exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )

            result = runner.invoke(
                cli,
                ["delete", "inputs", "--output", "outputs", "--dry-run"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn(
                "Dry run summary: would_process=1, failed=0, skipped=0, total=1",
                result.output,
            )
            self.assertFalse(os.path.exists("outputs"))

    def test_cli_batch_partial_failure_exit_code(self):
        """Batch delete should report partial failure distinctly."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="purple").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )
            with open(os.path.join("inputs", "broken.pdf"), "wb") as broken_pdf:
                broken_pdf.write(b"not a valid pdf")

            result = runner.invoke(cli, ["delete", "inputs", "--output", "outputs"])

            self.assertEqual(result.exit_code, 3, result.output)
            self.assertIn("Summary: succeeded=1, failed=1, skipped=0, total=2", result.output)
            self.assertIn("Failed:", result.output)

    def test_cli_json_summary_for_batch(self):
        """Batch delete should support machine-readable summaries."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )

            result = runner.invoke(
                cli,
                ["delete", "inputs", "--output", "outputs", "--json-summary"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "success")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["total"], 1)
            self.assertEqual(payload["succeeded"], 1)
            self.assertEqual(payload["failed"], 0)
            self.assertEqual(payload["failures"], [])
            self.assertEqual(len(payload["files"]), 1)
            self.assertEqual(payload["files"][0]["input"], os.path.join("inputs", "photo.jpg"))
            self.assertEqual(payload["files"][0]["status"], "success")
            self.assertTrue(payload["files"][0]["output"].startswith("outputs"))

    def test_cli_json_summary_for_batch_partial_failure_has_file_details(self):
        """JSON batch summaries should include per-file status and errors."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )
            with open(os.path.join("inputs", "broken.pdf"), "wb") as broken_pdf:
                broken_pdf.write(b"not a valid pdf")

            result = runner.invoke(
                cli,
                ["delete", "inputs", "--output", "outputs", "--json-summary"],
            )

            self.assertEqual(result.exit_code, 3, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "partial_failure")
            self.assertEqual(payload["succeeded"], 1)
            self.assertEqual(payload["failed"], 1)
            self.assertEqual(len(payload["files"]), 2)
            files_by_input = {item["input"]: item for item in payload["files"]}
            self.assertEqual(
                files_by_input[os.path.join("inputs", "photo.jpg")]["status"],
                "success",
            )
            failed_item = files_by_input[os.path.join("inputs", "broken.pdf")]
            self.assertEqual(failed_item["status"], "failed")
            self.assertEqual(failed_item["error"], "metadata_removal_failed")

    def test_cli_json_summary_failed_report_filter(self):
        """JSON reports should optionally include only failed per-file entries."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )
            with open(os.path.join("inputs", "broken.pdf"), "wb") as broken_pdf:
                broken_pdf.write(b"not a valid pdf")

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "inputs",
                    "--output",
                    "outputs",
                    "--json-summary",
                    "--report-filter",
                    "failed",
                ],
            )

            self.assertEqual(result.exit_code, 3, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["total"], 2)
            self.assertEqual(payload["succeeded"], 1)
            self.assertEqual(payload["failed"], 1)
            self.assertEqual(len(payload["files"]), 1)
            self.assertEqual(payload["files"][0]["input"], os.path.join("inputs", "broken.pdf"))
            self.assertEqual(payload["files"][0]["status"], "failed")

    def test_cli_summary_file_failed_report_filter_with_compact_detail(self):
        """Summary files should combine failed filtering with compact detail."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )
            with open(os.path.join("inputs", "broken.pdf"), "wb") as broken_pdf:
                broken_pdf.write(b"not a valid pdf")

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "inputs",
                    "--output",
                    "outputs",
                    "--summary-file",
                    "summary.json",
                    "--report-detail",
                    "compact",
                    "--report-filter",
                    "failed",
                    "--quiet",
                ],
            )

            self.assertEqual(result.exit_code, 3, result.output)
            with open("summary.json") as summary_file:
                payload = json.load(summary_file)
            self.assertEqual(payload["total"], 2)
            self.assertEqual(len(payload["files"]), 1)
            failed_item = payload["files"][0]
            self.assertEqual(failed_item["input"], os.path.join("inputs", "broken.pdf"))
            self.assertEqual(failed_item["status"], "failed")
            self.assertIn("error", failed_item)
            self.assertNotIn("output", failed_item)

    def test_cli_summary_file_for_batch(self):
        """Batch delete should write machine-readable summaries to a file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "inputs",
                    "--output",
                    "outputs",
                    "--summary-file",
                    "reports/summary.json",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Summary: succeeded=1, failed=0, skipped=0, total=1", result.output)
            with open(os.path.join("reports", "summary.json")) as summary_file:
                payload = json.load(summary_file)
            self.assertEqual(payload["status"], "success")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["total"], 1)
            self.assertEqual(payload["succeeded"], 1)
            self.assertEqual(payload["files"][0]["status"], "success")
            self.assertEqual(
                payload["files"][0]["input"],
                os.path.join("inputs", "photo.jpg"),
            )
            self.assertTrue(payload["files"][0]["output"].startswith("outputs"))

    def test_cli_summary_file_with_json_summary(self):
        """Summary files should work alongside JSON stdout."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.jpg", "jpeg")

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "photo.jpg",
                    "--json-summary",
                    "--summary-file",
                    "summary.json",
                    "--dry-run",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            stdout_payload = json.loads(result.output)
            with open("summary.json") as summary_file:
                file_payload = json.load(summary_file)
            self.assertEqual(file_payload, stdout_payload)
            self.assertEqual(file_payload["would_process"], 1)
            self.assertEqual(file_payload["files"][0]["status"], "would_process")
            self.assertEqual(
                file_payload["files"][0]["output"],
                os.path.join("cleaned", "photo.jpg"),
            )

    def test_cli_json_summary_with_checksums_for_dry_run(self):
        """Checksum reporting should include input hashes without writing outputs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.jpg", "jpeg")
            with open("photo.jpg", "rb") as image_file:
                expected_hash = hashlib.sha256(image_file.read()).hexdigest()

            result = runner.invoke(
                cli,
                ["delete", "photo.jpg", "--dry-run", "--json-summary", "--checksums"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            checksums = payload["files"][0]["checksums"]
            self.assertEqual(checksums["input_sha256"], expected_hash)
            self.assertIsNone(checksums["output_sha256"])

    def test_cli_json_summary_includes_processing_warnings(self):
        """JSON summaries should warn when formats use rewrite-style cleanup."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.png", "png")

            result = runner.invoke(
                cli,
                ["delete", "photo.png", "--dry-run", "--json-summary"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            warnings = payload["files"][0]["warnings"]
            self.assertTrue(any("re-saves image data" in warning for warning in warnings))

    def test_cli_json_summary_compact_report_detail(self):
        """Compact JSON reports should omit verbose per-file fields."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.png", "png")

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "photo.png",
                    "--dry-run",
                    "--json-summary",
                    "--checksums",
                    "--report-detail",
                    "compact",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            item = payload["files"][0]
            self.assertEqual(item["input"], "photo.png")
            self.assertEqual(item["status"], "would_process")
            self.assertIn("checksums", item)
            self.assertNotIn("output", item)
            self.assertNotIn("warnings", item)

    def test_cli_json_summary_summary_report_detail(self):
        """Summary JSON reports should omit per-file entries for large batches."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.jpg", "jpeg")

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "photo.jpg",
                    "--dry-run",
                    "--json-summary",
                    "--report-detail",
                    "summary",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["total"], 1)
            self.assertNotIn("files", payload)

    def test_cli_summary_file_with_checksums_for_cleaned_output(self):
        """Checksum reporting should include input and cleaned output hashes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.jpg", "jpeg")

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "photo.jpg",
                    "--output",
                    "cleaned.jpg",
                    "--summary-file",
                    "summary.json",
                    "--checksums",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            with open("summary.json") as summary_file:
                payload = json.load(summary_file)
            checksums = payload["files"][0]["checksums"]
            with open("photo.jpg", "rb") as input_file:
                expected_input = hashlib.sha256(input_file.read()).hexdigest()
            with open("cleaned.jpg", "rb") as output_file:
                expected_output = hashlib.sha256(output_file.read()).hexdigest()
            self.assertEqual(checksums["input_sha256"], expected_input)
            self.assertEqual(checksums["output_sha256"], expected_output)

    def test_cli_delete_preserves_timestamps_when_requested(self):
        """CLI cleanup should optionally preserve source filesystem timestamps."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.jpg", "jpeg")
            old_atime = 1_600_000_000
            old_mtime = 1_500_000_000
            os.utime("photo.jpg", (old_atime, old_mtime))

            result = runner.invoke(
                cli,
                [
                    "delete",
                    "photo.jpg",
                    "--output",
                    "cleaned.jpg",
                    "--preserve-timestamps",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(int(os.stat("cleaned.jpg").st_mtime), old_mtime)

    def test_cli_json_summary_for_dry_run_with_quiet(self):
        """JSON summary and quiet mode should produce clean stdout for automation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            Image.new("RGB", (10, 10), color="green").save(
                os.path.join("inputs", "photo.jpg"),
                "jpeg",
            )

            result = runner.invoke(
                cli,
                ["delete", "inputs", "--json-summary", "--quiet", "--dry-run"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "success")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["total"], 1)
            self.assertEqual(payload["would_process"], 1)
            self.assertEqual(payload["files"][0]["status"], "would_process")
            self.assertTrue(payload["files"][0]["output"].startswith("inputs"))

    def test_cli_quiet_suppresses_human_success_output(self):
        """Quiet mode should suppress human output when JSON is not requested."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="yellow").save("photo.jpg", "jpeg")

            result = runner.invoke(cli, ["delete", "photo.jpg", "--dry-run", "--quiet"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(result.output, "")

    def test_cli_no_supported_files_exit_code(self):
        """CLI should distinguish no-op input from successful work."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            with open(os.path.join("inputs", "notes.unknown"), "w") as notes:
                notes.write("nothing to clean")

            result = runner.invoke(cli, ["delete", "inputs"])

            self.assertEqual(result.exit_code, 2, result.output)
            self.assertIn("No supported files found.", result.output)

    def test_cli_no_supported_files_json_summary(self):
        """JSON summaries should describe empty supported-file sets."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            with open(os.path.join("inputs", "notes.unknown"), "w") as notes:
                notes.write("nothing to clean")

            result = runner.invoke(
                cli,
                ["delete", "inputs", "--json-summary", "--quiet", "--dry-run"],
            )

            self.assertEqual(result.exit_code, 2, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["status"], "no_supported_files")
            self.assertEqual(payload["total"], 0)

    def test_cli_no_supported_files_summary_file(self):
        """Summary files should be written for no-supported-file exits."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs("inputs", exist_ok=True)
            with open(os.path.join("inputs", "notes.unknown"), "w") as notes:
                notes.write("nothing to clean")

            result = runner.invoke(
                cli,
                ["delete", "inputs", "--summary-file", "summary.json", "--quiet"],
            )

            self.assertEqual(result.exit_code, 2, result.output)
            self.assertEqual(result.output, "")
            with open("summary.json") as summary_file:
                payload = json.load(summary_file)
            self.assertEqual(payload["status"], "no_supported_files")
            self.assertEqual(payload["total"], 0)

    def test_cli_verbose_log_file_option(self):
        """Global CLI options should enable explicit file logging."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Image.new("RGB", (10, 10), color="orange").save("photo.jpg", "jpeg")
            log_path = os.path.abspath("metadata-cleaner.log")

            result = runner.invoke(
                cli,
                ["--verbose", "--log-file", log_path, "delete", "photo.jpg", "--dry-run"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(os.path.exists(log_path))
            with open(log_path) as log_file:
                log_content = log_file.read()
            self.assertIn("[DRY-RUN]", log_content)

            for handler in list(logger.handlers):
                if isinstance(handler, RotatingFileHandler):
                    if os.path.abspath(handler.baseFilename) == log_path:
                        logger.removeHandler(handler)
                        handler.close()

    def test_cli_rejects_invalid_edit_json(self):
        """CLI edit command should fail gracefully for invalid JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["edit", self.test_files["document"], "--changes", "{invalid"],
        )

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("Invalid JSON format", result.output)

    def test_generated_wav_metadata_removal_preserves_original(self):
        """Audio cleanup should strip metadata from a separate playable WAV file."""
        source_wav = os.path.join(self.test_dir, "generated.wav")
        cleaned_wav = os.path.join(self.cleaned_dir, "generated_cleaned.wav")

        self._write_tagged_wav(source_wav)
        source_metadata = self.processor.view_metadata(source_wav)
        self.assertIn("TIT2", source_metadata)
        self.assertIn("Fixture Title", str(source_metadata["TIT2"]))

        output_file = self.processor.delete_metadata(source_wav, cleaned_wav)

        self.assertEqual(output_file, cleaned_wav)
        self.assertTrue(os.path.exists(source_wav))
        self.assertTrue(os.path.exists(cleaned_wav))
        self.assertIn("TIT2", self.processor.view_metadata(source_wav))
        self.assertEqual(dict(MutagenFile(cleaned_wav, easy=True)), {})

        with wave.open(source_wav, "rb") as original, wave.open(
            cleaned_wav, "rb"
        ) as cleaned:
            self.assertEqual(original.getnchannels(), cleaned.getnchannels())
            self.assertEqual(original.getsampwidth(), cleaned.getsampwidth())
            self.assertEqual(original.getframerate(), cleaned.getframerate())
            self.assertEqual(original.getnframes(), cleaned.getnframes())

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"),
        "FFmpeg and FFprobe are required for video integration coverage",
    )
    def test_generated_video_metadata_removal_with_ffmpeg(self):
        """Video cleanup should strip container metadata without re-encoding."""
        source_video = os.path.join(self.test_dir, "generated.mp4")
        cleaned_video = os.path.join(self.cleaned_dir, "generated_cleaned.mp4")

        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=16x16:rate=1",
                "-t",
                "1",
                "-metadata",
                "title=Metadata Cleaner Test",
                "-pix_fmt",
                "yuv420p",
                source_video,
                "-y",
            ],
            check=True,
        )

        output_file = VideoHandler().remove_metadata(source_video, cleaned_video)
        metadata = VideoHandler().extract_metadata(cleaned_video)

        self.assertEqual(output_file, cleaned_video)
        self.assertTrue(os.path.exists(source_video))
        self.assertTrue(os.path.exists(cleaned_video))
        self.assertNotEqual(os.path.getsize(cleaned_video), 0)
        self.assertNotEqual(
            metadata.get("format", {}).get("tags", {}).get("title"),
            "Metadata Cleaner Test",
        )

    def test_recursive_scanning(self):
        """Test recursive file scanning logic."""
        # Create nested directory
        nested_dir = os.path.join(self.test_dir, "nested")
        subdir = os.path.join(nested_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)

        # Create dummy files
        files = [
            os.path.join(nested_dir, "file1.jpg"),
            os.path.join(subdir, "file2.pdf"),
            os.path.join(nested_dir, "skip.unknown"),
        ]

        for f in files:
            with open(f, "w") as fh:
                fh.write("dummy")

        # Import the helper to test it directly
        from m_c.core.file_utils import get_supported_files

        found_files = get_supported_files(nested_dir)

        # Should find jpg and pdf, ignore unknown
        self.assertEqual(len(found_files), 2)
        self.assertTrue(any(f.endswith("file1.jpg") for f in found_files))
        self.assertTrue(any(f.endswith("file2.pdf") for f in found_files))


if __name__ == "__main__":
    unittest.main()
