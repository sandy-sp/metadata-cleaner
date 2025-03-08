import subprocess
import os
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for ExifTool integration in Metadata Cleaner.

This module provides functions to extract and remove metadata from images using ExifTool.
"""

EXIFTOOL_CMD = "exiftool"

def is_exiftool_available() -> bool:
    """Check if ExifTool is installed and available on the system."""
    return shutil.which(EXIFTOOL_CMD) is not None

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from an image using ExifTool.

    Parameters:
        file_path (str): Path to the image file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    try:
        result = subprocess.run([EXIFTOOL_CMD, "-json", file_path], capture_output=True, text=True)
        if result.returncode == 0:
            import json
            metadata = json.loads(result.stdout)
            return metadata[0] if metadata else {}
        else:
            logger.error(f"ExifTool failed to extract metadata: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error extracting metadata using ExifTool: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from an image using ExifTool.

    Parameters:
        file_path (str): Path to the image file.
        output_path (Optional[str]): Destination path for the cleaned image.
                                     If None, overwrites the original file.

    Returns:
        Optional[str]: Path to the cleaned file if successful; otherwise, None.
    """
    try:
        if output_path is None:
            output_path = file_path
        result = subprocess.run([EXIFTOOL_CMD, "-all=", "-overwrite_original", file_path], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Metadata removed successfully from {file_path}")
            return output_path
        else:
            logger.error(f"ExifTool failed to remove metadata: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error removing metadata using ExifTool: {e}", exc_info=True)
        return None
