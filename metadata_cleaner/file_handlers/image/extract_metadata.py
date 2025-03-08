import os
from typing import Optional, Dict
from metadata_cleaner.file_handlers.image.exiftool_handler import extract_metadata as extract_metadata_exiftool
from metadata_cleaner.file_handlers.image.piexif_handler import extract_metadata as extract_metadata_piexif
from metadata_cleaner.logs.logger import logger

"""
Module for dynamically extracting metadata from images based on available tools.

If ExifTool is installed, it is used as the primary metadata extractor.
Otherwise, it falls back to piexif.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from an image dynamically based on available tools.

    Parameters:
        file_path (str): Path to the image file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if os.path.exists(file_path):
        logger.info(f"Attempting to extract metadata from: {file_path}")
        
        metadata = extract_metadata_exiftool(file_path)
        
        if metadata:
            logger.info("Metadata extracted successfully using ExifTool.")
            return metadata
        else:
            logger.warning("ExifTool failed, falling back to piexif...")
            return extract_metadata_piexif(file_path)
    else:
        logger.error(f"File not found: {file_path}")
        return None
