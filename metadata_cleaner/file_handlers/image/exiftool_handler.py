import subprocess
import os
import shutil
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

def validate_file(file_path: str) -> bool:
    """Check if the file exists and is valid."""
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"❌ Not a valid file: {file_path}")
        return False
    return True

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from an image using ExifTool.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not is_exiftool_available():
        logger.error("❌ ExifTool is not installed.")
        return None
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using ExifTool: {file_path}")

    try:
        result = subprocess.run(
            [EXIFTOOL_CMD, "-json", file_path],
            capture_output=True, text=True, check=True
        )

        if not result.stdout.strip():
            logger.error(f"❌ ExifTool did not return metadata for {file_path}")
            return None

        import json
        metadata = json.loads(result.stdout)
        return metadata[0] if metadata else {}

    except json.JSONDecodeError:
        logger.error(f"❌ ExifTool returned invalid JSON for {file_path}.")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ ExifTool encountered an error: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from an image using ExifTool.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not is_exiftool_available():
        logger.error("❌ ExifTool is not installed.")
        return None
    if not validate_file(file_path):
        return None

    # Determine output path if not provided
    if not output_path:
        output_path = file_path  # ExifTool modifies files in place

    logger.info(f"📂 Removing metadata using ExifTool: {file_path}")

    try:
        result = subprocess.run(
            [EXIFTOOL_CMD, "-all=", "-overwrite_original", file_path],
            capture_output=True, text=True, check=True
        )

        # Verify metadata removal success
        if not validate_file(output_path):
            logger.error(f"❌ ExifTool failed to process: {output_path}")
            return None

        logger.info(f"✅ Metadata removed successfully using ExifTool: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ ExifTool encountered an error: {e}", exc_info=True)
        return None
