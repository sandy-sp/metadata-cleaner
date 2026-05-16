import json
import os
import shutil
import subprocess
import wave
from pathlib import Path

import docx
from PIL import Image
import pypdf


CLI = os.environ.get("METADATA_CLEANER_CLI", "metadata-cleaner")
ROOT = Path("smoke-files")
CLEANED = Path("smoke-cleaned")
REPORT = Path("smoke-report.json")


def run_command(command):
    return subprocess.run(command, check=True, capture_output=True, text=True)


def run_cli(*args):
    return run_command([CLI, *args])


def read_json_output(*args):
    result = run_cli(*args, "--json")
    return json.loads(result.stdout)


def require_tool(name):
    if not shutil.which(name):
        raise AssertionError(f"{name} is required for package smoke coverage")


def write_fixtures():
    ROOT.mkdir(exist_ok=True)

    Image.new("RGB", (8, 8), color="white").save(ROOT / "photo.jpg", "jpeg")

    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/Title": "Smoke PDF"})
    with (ROOT / "document.pdf").open("wb") as pdf_file:
        writer.write(pdf_file)

    document = docx.Document()
    document.add_paragraph("Metadata Cleaner smoke document.")
    document.core_properties.title = "Smoke DOCX"
    document.save(ROOT / "document.docx")

    with wave.open(str(ROOT / "audio.wav"), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(b"\0\0" * 800)

    run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=8000",
            "-t",
            "1",
            "-metadata",
            "title=Smoke Audio",
            "-metadata",
            "artist=Smoke Artist",
            "-c:a",
            "aac",
            "-b:a",
            "32k",
            str(ROOT / "audio.m4a"),
            "-y",
        ]
    )

    run_command(
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
            "title=Smoke Video",
            "-pix_fmt",
            "yuv420p",
            str(ROOT / "video.mp4"),
            "-y",
        ]
    )


def assert_view_payloads():
    photo_payload = read_json_output("view", str(ROOT / "photo.jpg"))
    assert photo_payload["status"] == "success", photo_payload
    assert photo_payload["metadata"].get("FileType") == "JPEG", photo_payload

    pdf_payload = read_json_output("view", str(ROOT / "document.pdf"))
    assert pdf_payload["status"] == "success", pdf_payload
    assert pdf_payload["metadata"].get("/Title") == "Smoke PDF", pdf_payload

    docx_payload = read_json_output("view", str(ROOT / "document.docx"))
    assert docx_payload["status"] == "success", docx_payload
    assert docx_payload["metadata"].get("title") == "Smoke DOCX", docx_payload

    wav_payload = read_json_output("view", str(ROOT / "audio.wav"))
    assert wav_payload["status"] in {"success", "no_metadata"}, wav_payload

    m4a_payload = read_json_output("view", str(ROOT / "audio.m4a"))
    assert m4a_payload["status"] == "success", m4a_payload
    assert m4a_payload["metadata"].get("title") == ["Smoke Audio"], m4a_payload
    assert m4a_payload["metadata"].get("artist") == ["Smoke Artist"], m4a_payload

    video_payload = read_json_output("view", str(ROOT / "video.mp4"))
    assert video_payload["status"] == "success", video_payload
    video_title = video_payload["metadata"]["format"]["tags"].get("title")
    assert video_title == "Smoke Video", video_payload


def assert_delete_summary():
    source_video_payload = read_json_output("view", str(ROOT / "video.mp4"))
    source_video_stream = source_video_payload["metadata"]["streams"][0]

    dry_run = run_cli("delete", str(ROOT), "--dry-run", "--json-summary")
    dry_run_payload = json.loads(dry_run.stdout)
    assert dry_run_payload["status"] == "success", dry_run_payload
    assert dry_run_payload["total"] == 6, dry_run_payload
    assert dry_run_payload["would_process"] == 6, dry_run_payload

    run_cli(
        "delete",
        str(ROOT),
        "--output",
        str(CLEANED),
        "--summary-file",
        str(REPORT),
        "--quiet",
    )

    report = json.loads(REPORT.read_text())
    assert report["status"] == "success", report
    assert report["total"] == 6, report
    assert report["succeeded"] == 6, report
    assert len(report["files"]) == 6, report

    cleaned_audio = CLEANED / "audio.m4a"
    assert cleaned_audio.exists(), report
    cleaned_audio_payload = read_json_output("view", str(cleaned_audio))
    assert cleaned_audio_payload["status"] == "no_metadata", cleaned_audio_payload

    cleaned_video = CLEANED / "video.mp4"
    assert cleaned_video.exists(), report
    cleaned_video_payload = read_json_output("view", str(cleaned_video))
    cleaned_video_stream = cleaned_video_payload["metadata"]["streams"][0]
    cleaned_title = cleaned_video_payload["metadata"]["format"].get("tags", {}).get(
        "title"
    )
    assert cleaned_title != "Smoke Video", cleaned_video_payload
    assert source_video_stream["codec_type"] == "video", source_video_payload
    assert source_video_stream["codec_name"] == cleaned_video_stream["codec_name"], (
        cleaned_video_payload
    )
    assert source_video_stream["width"] == cleaned_video_stream["width"], (
        cleaned_video_payload
    )
    assert source_video_stream["height"] == cleaned_video_stream["height"], (
        cleaned_video_payload
    )


def main():
    require_tool("exiftool")
    require_tool("ffmpeg")
    require_tool("ffprobe")
    run_cli("--help")
    write_fixtures()
    assert_view_payloads()
    assert_delete_summary()


if __name__ == "__main__":
    main()
