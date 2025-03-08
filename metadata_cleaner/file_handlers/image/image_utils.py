import os
from PIL import Image
from typing import Optional
from metadata_cleaner.logs.logger import logger

"""
Utility functions for image handling in Metadata Cleaner.

Provides helper functions such as verifying image formats,
converting images, and ensuring valid file paths.
"""

def is_valid_image(file_path: str) -> bool:
    """
    Checks if a file is a valid image.

    Parameters:
        file_path (str): Path to the image file.

    Returns:
        bool: True if the file is a valid image, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception as e:
        logger.error(f"Invalid image file: {file_path} - {e}")
        return False

def convert_image_format(file_path: str, output_format: str) -> Optional[str]:
    """
    Converts an image to a different format.

    Parameters:
        file_path (str): Path to the image file.
        output_format (str): Desired output format (e.g., 'JPEG', 'PNG').

    Returns:
        Optional[str]: Path to the converted image if successful, otherwise None.
    """
    if not is_valid_image(file_path):
        return None
    try:
        base, _ = os.path.splitext(file_path)
        output_path = f"{base}.{output_format.lower()}"
        with Image.open(file_path) as img:
            img.save(output_path, format=output_format)
        logger.info(f"Image converted successfully: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting image format: {e}", exc_info=True)
        return None
