import os
from typing import Optional, Dict
from metadata_cleaner.file_handlers.image.exiftool_handler import extract_metadata as extract_metadata_exiftool
from metadata_cleaner.file_handlers.image.piexif_handler import extract_metadata as extract_metadata_piexif
from metadata_cleaner.logs.logger import logger

"""
Module for dynamically extracting metadata from images based on available tools.

If ExifTool is installed, it is used as the primary metadata extractor.
Otherwise, it falls back to Piexif.
"""

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
    Extracts metadata from an image dynamically based on available tools.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata from: {file_path}")

    metadata = extract_metadata_exiftool(file_path)
    if metadata:
        logger.info(f"✅ Metadata extracted successfully using ExifTool.")
        return metadata

    logger.warning("⚠️ ExifTool failed, falling back to Piexif...")
    metadata = extract_metadata_piexif(file_path)
    if metadata:
        logger.info(f"✅ Metadata extracted successfully using Piexif.")
        return metadata

    logger.error(f"❌ All metadata extraction attempts failed: {file_path}")
    return None
