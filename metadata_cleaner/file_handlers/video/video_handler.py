import os
from typing import Optional, Dict
from metadata_cleaner.file_handlers.video.ffmpeg_video_handler import (
    extract_metadata as extract_metadata_ffmpeg,
    remove_metadata as remove_metadata_ffmpeg,
)
from metadata_cleaner.file_handlers.video.pyav_video_handler import (
    extract_metadata as extract_metadata_pyav,
    remove_metadata as remove_metadata_pyav,
)
from metadata_cleaner.file_handlers.video.hachoir_video_handler import extract_metadata as extract_metadata_hachoir
from metadata_cleaner.logs.logger import logger

"""
Video metadata handler that dynamically selects the best available tool.

Priority order:
1. FFmpeg (Preferred)
2. PyAV (Fallback)
3. Hachoir (Metadata Extraction Only)
"""

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
    Extracts metadata from a video file using the best available tool.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata from: {file_path}")

    # Try FFmpeg
    metadata = extract_metadata_ffmpeg(file_path)
    if metadata:
        logger.info("✅ Metadata extracted using FFmpeg.")
        return metadata

    # Try PyAV
    logger.warning("⚠️ FFmpeg failed, falling back to PyAV...")
    metadata = extract_metadata_pyav(file_path)
    if metadata:
        logger.info("✅ Metadata extracted using PyAV.")
        return metadata

    # Try Hachoir (only for extraction, no removal support)
    logger.warning("⚠️ PyAV failed, falling back to Hachoir...")
    metadata = extract_metadata_hachoir(file_path)
    if metadata:
        logger.info("✅ Metadata extracted using Hachoir.")
        return metadata

    logger.error("❌ All metadata extraction attempts failed.")
    return None

def remove_video_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a video file using the best available tool.

    Returns:
        - The output file path if removal succeeds.
        - None if all methods fail.
    """
    if not validate_file(file_path):
        return None

    # Determine output path if not provided
    if not output_path:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_cleaned{ext}"

    logger.info(f"📂 Removing metadata from: {file_path}")

    # Try FFmpeg
    if remove_metadata_ffmpeg(file_path, output_path):
        logger.info(f"✅ Metadata removed using FFmpeg: {output_path}")
        return output_path

    # Try PyAV
    logger.warning("⚠️ FFmpeg failed, falling back to PyAV...")
    if remove_metadata_pyav(file_path, output_path):
        logger.info(f"✅ Metadata removed using PyAV: {output_path}")
        return output_path

    logger.error("❌ All metadata removal attempts failed.")
    return None
