import os
from typing import Optional
from metadata_cleaner.file_handlers.image.exiftool_handler import remove_metadata as remove_metadata_exiftool
from metadata_cleaner.file_handlers.image.piexif_handler import remove_metadata as remove_metadata_piexif
from metadata_cleaner.logs.logger import logger

"""
Module for dynamically removing metadata from images based on available tools.

If ExifTool is installed, it is used as the primary metadata remover.
Otherwise, it falls back to piexif.
"""

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from an image dynamically based on available tools.

    Parameters:
        file_path (str): Path to the image file.
        output_path (Optional[str]): Destination path for the cleaned image.
                                     If None, overwrites the original file.

    Returns:
        Optional[str]: Path to the cleaned file if successful; otherwise, None.
    """
    if os.path.exists(file_path):
        logger.info(f"Attempting to remove metadata from: {file_path}")
        
        cleaned_file = remove_metadata_exiftool(file_path, output_path)
        
        if cleaned_file:
            logger.info(f"Metadata removed using ExifTool: {cleaned_file}")
            return cleaned_file
        else:
            logger.warning("ExifTool failed, falling back to piexif...")
            return remove_metadata_piexif(file_path, output_path)
    else:
        logger.error(f"File not found: {file_path}")
        return None
