import os
import piexif
from PIL import Image, UnidentifiedImageError
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for EXIF metadata extraction and removal using Piexif.

Provides an alternative to ExifTool for metadata handling.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts EXIF metadata from an image using Piexif.

    Parameters:
        file_path (str): Path to the image file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    try:
        img = Image.open(file_path)
        exif_data = img.info.get("exif", None)
        return piexif.load(exif_data) if exif_data else {"message": "No EXIF metadata found."}
    except UnidentifiedImageError:
        logger.error(f"Invalid image file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error extracting metadata using Piexif: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes EXIF metadata from an image using Piexif.

    Parameters:
        file_path (str): Path to the image file.
        output_path (Optional[str]): Destination path for the cleaned image.
                                     If None, overwrites the original file.

    Returns:
        Optional[str]: Path to the cleaned file if successful; otherwise, None.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        img = Image.open(file_path)
        img_data = list(img.getdata())
        img_without_exif = Image.new(img.mode, img.size)
        img_without_exif.putdata(img_data)
        
        if not output_path:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_cleaned{ext}"
        
        img_without_exif.save(output_path)
        logger.info(f"Metadata removed successfully using Piexif: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error removing metadata using Piexif: {e}", exc_info=True)
        return None
