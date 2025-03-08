import subprocess
import json
import shutil
import os
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from audio files using ExifTool.

Provides efficient metadata operations leveraging ExifTool's capabilities.
"""

EXIFTOOL_CMD = "exiftool"

def is_exiftool_available() -> bool:
    """Check if ExifTool is installed and available."""
    return shutil.which(EXIFTOOL_CMD) is not None

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from an audio file using ExifTool.

    Parameters:
        file_path (str): Path to the audio file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not is_exiftool_available():
        logger.error("ExifTool is not installed.")
        return None
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        result = subprocess.run([EXIFTOOL_CMD, "-j", file_path], capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)
        return metadata[0] if metadata else {}
    except Exception as e:
        logger.error(f"Error extracting metadata using ExifTool: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str) -> bool:
    """
    Removes all metadata from an audio file using ExifTool.

    Parameters:
        file_path (str): Path to the audio file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not is_exiftool_available():
        logger.error("ExifTool is not installed.")
        return False
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    try:
        subprocess.run([EXIFTOOL_CMD, "-all=", "-overwrite_original", file_path], check=True)
        logger.info(f"Metadata removed successfully from {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error removing metadata using ExifTool: {e}", exc_info=True)
        return False
