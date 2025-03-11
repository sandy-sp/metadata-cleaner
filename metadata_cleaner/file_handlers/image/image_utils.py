import os
from PIL import Image, UnidentifiedImageError
from typing import Optional
from metadata_cleaner.logs.logger import logger

"""
Utility functions for image handling in Metadata Cleaner.

Provides helper functions such as verifying image formats,
converting images, and ensuring valid file paths.
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

def is_valid_image(file_path: str) -> bool:
    """
    Checks if a file is a valid image.

    Returns:
        - True if the file is a valid image.
        - False if the file is not a valid image.
    """
    if not validate_file(file_path):
        return False

    try:
        with Image.open(file_path) as img:
            img.verify()  # Verifies if this is an actual image file
        return True
    except UnidentifiedImageError:
        logger.error(f"❌ Invalid image file: {file_path}")
        return False
    except Exception as e:
        logger.error(f"❌ Error verifying image file: {e}", exc_info=True)
        return False

def convert_image_format(file_path: str, output_format: str) -> Optional[str]:
    """
    Converts an image to a different format.

    Returns:
        - Path to the converted image if successful.
        - None if conversion fails.
    """
    if not is_valid_image(file_path):
        return None

    logger.info(f"📂 Converting image format: {file_path} → {output_format}")

    try:
        base, _ = os.path.splitext(file_path)
        output_path = f"{base}.{output_format.lower()}"

        with Image.open(file_path) as img:
            img.convert("RGB").save(output_path, format=output_format.upper())

        # Verify output file existence
        if not os.path.exists(output_path):
            logger.error(f"❌ Image conversion failed: {output_path}")
            return None

        logger.info(f"✅ Image converted successfully: {output_path}")
        return output_path

    except UnidentifiedImageError:
        logger.error(f"❌ Invalid image file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"❌ Error converting image format: {e}", exc_info=True)
        return None
