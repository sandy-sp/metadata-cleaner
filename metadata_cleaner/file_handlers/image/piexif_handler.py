import os
import piexif
from PIL import Image, UnidentifiedImageError
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for EXIF metadata extraction and removal using Piexif.

Provides an alternative to ExifTool for metadata handling.
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
    Extracts EXIF metadata from an image using Piexif.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using Piexif: {file_path}")

    try:
        img = Image.open(file_path)
        exif_data = img.info.get("exif", None)
        return piexif.load(exif_data) if exif_data else {"message": "No EXIF metadata found."}
    except UnidentifiedImageError:
        logger.error(f"❌ Invalid image file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"❌ Piexif failed to extract metadata: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes EXIF metadata from an image using Piexif.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not validate_file(file_path):
        return None

    # Determine output path if not provided
    if not output_path:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_cleaned{ext}"

    logger.info(f"📂 Removing metadata using Piexif: {file_path}")

    try:
        img = Image.open(file_path)

        # Remove EXIF metadata
        if "exif" in img.info:
            img.info.pop("exif")

        # Create a new image without metadata
        img_data = list(img.getdata())
        img_without_exif = Image.new(img.mode, img.size)
        img_without_exif.putdata(img_data)

        # Save the cleaned image
        img_without_exif.save(output_path)

        # Verify output file existence
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"❌ Piexif failed to create output file: {output_path}")
            return None

        logger.info(f"✅ Metadata removed successfully using Piexif: {output_path}")
        return output_path

    except UnidentifiedImageError:
        logger.error(f"❌ Invalid image file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"❌ Piexif encountered an error: {e}", exc_info=True)
        return None
