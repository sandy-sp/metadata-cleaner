import os
from typing import Optional, Dict
from metadata_cleaner.file_handlers.video.ffmpeg_video_handler import extract_metadata as extract_metadata_ffmpeg, remove_metadata as remove_metadata_ffmpeg
from metadata_cleaner.file_handlers.video.pyav_video_handler import extract_metadata as extract_metadata_pyav, remove_metadata as remove_metadata_pyav
from metadata_cleaner.file_handlers.video.hachoir_video_handler import extract_metadata as extract_metadata_hachoir
from metadata_cleaner.logs.logger import logger

"""
Module for dynamically handling video metadata extraction and removal.

Uses FFmpeg as the primary tool, with PyAV and Hachoir as fallbacks.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extract metadata from a video file dynamically based on available tools.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    logger.info(f"Attempting to extract metadata from: {file_path}")

    # Try FFmpeg first
    metadata = extract_metadata_ffmpeg(file_path)
    if metadata:
        logger.info("Metadata extracted successfully using FFmpeg.")
        return metadata

    # Try PyAV before Hachoir (for better metadata details)
    logger.warning("FFmpeg failed, falling back to PyAV...")
    metadata = extract_metadata_pyav(file_path)
    if metadata:
        logger.info("Metadata extracted successfully using PyAV.")
        return metadata

    # Fallback to Hachoir as last resort
    logger.warning("Falling back to Hachoir...")
    metadata = extract_metadata_hachoir(file_path)
    if metadata:
        logger.info("Metadata extracted successfully using Hachoir.")
        return metadata

    logger.error("All metadata extraction attempts failed.")
    return None

def remove_metadata_ffmpeg(file_path: str, output_path: Optional[str] = None) -> bool:
    """
    Remove metadata from a video file using FFmpeg.
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

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"FFmpeg failed to create output file: {output_path}")
            return False

        logger.info(f"Metadata removed successfully using FFmpeg: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error removing metadata using FFmpeg: {e}", exc_info=True)
        return False

def remove_metadata(file_path: str) -> bool:
    """
    Remove metadata from a video file dynamically based on available tools.

    Parameters:
        file_path (str): Path to the video file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    logger.info(f"Attempting to remove metadata from: {file_path}")
    
    if remove_metadata_ffmpeg(file_path):
        logger.info("Metadata removed successfully using FFmpeg.")
        return True
    
    logger.warning("FFmpeg failed, falling back to PyAV...")
    if remove_metadata_pyav(file_path):
        return True
    
    logger.error("All metadata removal attempts failed.")
    return False
