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

def remove_video_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Remove metadata from a video file dynamically based on available tools.

    Parameters:
        file_path (str): Path to the video file.
        output_path (Optional[str]): Path where the cleaned file should be saved.
                                   If None, will use original filename with '_cleaned' suffix.

    Returns:
        Optional[str]: Path to the cleaned file if successful, None if failed.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    # Handle output path
    if not output_path:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_cleaned{ext}"
    
    logger.info(f"Attempting to remove metadata from: {file_path}")
    
    # Try FFmpeg first
    if remove_metadata_ffmpeg(file_path, output_path):
        logger.info("Metadata removed successfully using FFmpeg.")
        return output_path
    
    # Fall back to PyAV
    logger.warning("FFmpeg failed, falling back to PyAV...")
    if remove_metadata_pyav(file_path, output_path):
        logger.info("Metadata removed successfully using PyAV.")
        return output_path
    
    logger.error("All metadata removal attempts failed.")
    return None
