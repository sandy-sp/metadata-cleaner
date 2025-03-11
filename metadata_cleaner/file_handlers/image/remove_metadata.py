import os
from typing import Optional
from metadata_cleaner.file_handlers.image.exiftool_handler import remove_metadata as remove_metadata_exiftool
from metadata_cleaner.file_handlers.image.piexif_handler import remove_metadata as remove_metadata_piexif
from metadata_cleaner.logs.logger import logger

"""
Module for dynamically removing metadata from images based on available tools.

If ExifTool is installed, it is used as the primary metadata remover.
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

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from an image dynamically based on available tools.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Removing metadata from: {file_path}")

    cleaned_file = remove_metadata_exiftool(file_path, output_path)
    if cleaned_file:
        logger.info(f"✅ Metadata removed successfully using ExifTool: {cleaned_file}")
        return cleaned_file

    logger.warning("⚠️ ExifTool failed, falling back to Piexif...")
    cleaned_file = remove_metadata_piexif(file_path, output_path)
    if cleaned_file:
        logger.info(f"✅ Metadata removed successfully using Piexif: {cleaned_file}")
        return cleaned_file

    logger.error(f"❌ All metadata removal attempts failed: {file_path}")
    return None
