import os
from typing import Optional, Dict
from metadata_cleaner.file_handlers.audio.exiftool_audio_handler import extract_metadata as extract_metadata_exiftool, remove_metadata as remove_metadata_exiftool
from metadata_cleaner.file_handlers.audio.mutagen_audio_handler import extract_metadata as extract_metadata_mutagen, remove_metadata as remove_metadata_mutagen
from metadata_cleaner.file_handlers.audio.tinytag_audio_handler import extract_metadata as extract_metadata_tinytag
from metadata_cleaner.logs.logger import logger

"""
Module for dynamically handling audio metadata extraction and removal.

Uses ExifTool as the primary tool, with Mutagen and TinyTag as fallbacks.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extract metadata from an audio file dynamically based on available tools.

    Parameters:
        file_path (str): Path to the audio file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    logger.info(f"Attempting to extract metadata from: {file_path}")
    
    metadata = extract_metadata_exiftool(file_path)
    if metadata:
        logger.info("Metadata extracted successfully using ExifTool.")
        return metadata
    
    logger.warning("ExifTool failed, falling back to Mutagen...")
    metadata = extract_metadata_mutagen(file_path)
    if metadata:
        return metadata
    
    logger.warning("Falling back to TinyTag...")
    metadata = extract_metadata_tinytag(file_path)
    if metadata:
        return metadata
    
    logger.error("All metadata extraction attempts failed.")
    return None

def remove_metadata(file_path: str) -> bool:
    """
    Remove metadata from an audio file dynamically based on available tools.

    Parameters:
        file_path (str): Path to the audio file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    logger.info(f"Attempting to remove metadata from: {file_path}")
    
    if remove_metadata_exiftool(file_path):
        logger.info("Metadata removed successfully using ExifTool.")
        return True
    
    logger.warning("ExifTool failed, falling back to Mutagen...")
    if remove_metadata_mutagen(file_path):
        return True
    
    logger.error("All metadata removal attempts failed.")
    return False
