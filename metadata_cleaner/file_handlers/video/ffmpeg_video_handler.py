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

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a video file using FFprobe.

    Parameters:
        file_path (str): Path to the video file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not is_ffmpeg_available():
        logger.error("FFmpeg is not installed.")
        return None
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        result = subprocess.run([FFPROBE_CMD, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path], capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)
        return metadata if metadata else {}
    except Exception as e:
        logger.error(f"Error extracting metadata using FFprobe: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> bool:
    """
    Removes all metadata from a video file using FFmpeg.

    Parameters:
        file_path (str): Path to the video file.
        output_path (Optional[str]): Destination path for the cleaned video.
                                     If None, overwrites the original file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not is_ffmpeg_available():
        logger.error("FFmpeg is not installed.")
        return False
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    try:
        if not output_path:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_cleaned{ext}"
        
        command = [
            FFMPEG_CMD, "-i", file_path, "-map_metadata", "-1",
            "-c:v", "copy", "-c:a", "copy", output_path, "-y"
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        logger.info(f"Metadata removed successfully using FFmpeg: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error removing metadata using FFmpeg: {e}", exc_info=True)
        return False
