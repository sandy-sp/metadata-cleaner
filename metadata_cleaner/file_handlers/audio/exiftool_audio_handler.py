import subprocess
import json
import shutil
import os
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from audio files using ExifTool.

ExifTool provides efficient metadata operations and is preferred when available.
"""

EXIFTOOL_CMD = "exiftool"

def is_exiftool_available() -> bool:
    """Check if ExifTool is installed and available."""
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
    Extracts metadata from an audio file using ExifTool.

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
            [EXIFTOOL_CMD, "-j", file_path],
            capture_output=True, text=True, check=True
        )

        if not result.stdout.strip():
            logger.error(f"❌ ExifTool did not return metadata for {file_path}")
            return None

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
    Removes all metadata from an audio file using ExifTool.

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
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_cleaned{ext}"

    logger.info(f"📂 Removing metadata using ExifTool: {file_path}")

    try:
        subprocess.run(
            [EXIFTOOL_CMD, "-all=", "-overwrite_original", file_path],
            capture_output=True, text=True, check=True
        )

        # Verify output file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"❌ ExifTool failed to create output file: {output_path}")
            return None

        logger.info(f"✅ Metadata removed successfully using ExifTool: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ ExifTool encountered an error: {e}", exc_info=True)
        return None
