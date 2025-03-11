import subprocess
import json
import shutil
import os
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from video files using FFmpeg.

Provides efficient metadata operations leveraging FFmpeg's capabilities.
"""

FFMPEG_CMD = "ffmpeg"
FFPROBE_CMD = "ffprobe"

def is_ffmpeg_available() -> bool:
    """Check if FFmpeg is installed and available."""
    return shutil.which(FFMPEG_CMD) is not None and shutil.which(FFPROBE_CMD) is not None

def validate_file(file_path: str) -> bool:
    """Centralized file validation."""
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"❌ Not a valid file: {file_path}")
        return False
    return True

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a video file using FFprobe.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not is_ffmpeg_available():
        logger.error("❌ FFmpeg is not installed.")
        return None
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using FFmpeg: {file_path}")

    try:
        result = subprocess.run(
            [FFPROBE_CMD, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path],
            capture_output=True, text=True, check=True
        )
        metadata = json.loads(result.stdout)
        return metadata if metadata else {}
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFprobe failed: {e}", exc_info=True)
        return None
    except json.JSONDecodeError:
        logger.error("❌ Failed to parse metadata output from FFprobe.")
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a video file using FFmpeg.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not is_ffmpeg_available():
        logger.error("❌ FFmpeg is not installed.")
        return None
    if not validate_file(file_path):
        return None

    # Determine output path if not provided
    if not output_path:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_cleaned{ext}"

    logger.info(f"📂 Removing metadata using FFmpeg: {file_path}")

    try:
        command = [
            FFMPEG_CMD, "-i", file_path, "-map_metadata", "-1",
            "-c:v", "copy", "-c:a", "copy", output_path, "-y"
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        # Verify output file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"❌ FFmpeg failed to create output file: {output_path}")
            return None

        logger.info(f"✅ Metadata removed successfully using FFmpeg: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg encountered an error: {e}", exc_info=True)
        return None
