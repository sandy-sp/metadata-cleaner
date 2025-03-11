import os
from typing import Optional, Dict
from mutagen import File
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from audio files using Mutagen.

Mutagen provides a reliable method for modifying metadata when ExifTool is unavailable.
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
    Extract metadata from an audio file using Mutagen.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using Mutagen: {file_path}")

    try:
        audio = File(file_path, easy=True)
        if audio is None:
            logger.error(f"❌ Unsupported file format or corrupted file: {file_path}")
            return None

        return dict(audio)

    except Exception as e:
        logger.error(f"❌ Mutagen failed to extract metadata: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Remove metadata from an audio file using Mutagen.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not validate_file(file_path):
        return None

    # Determine output path if not provided
    if not output_path:
        output_path = file_path  # Mutagen modifies files in place

    logger.info(f"📂 Removing metadata using Mutagen: {file_path}")

    try:
        audio = File(file_path, easy=True)
        if audio is None:
            logger.error(f"❌ Unsupported file format or corrupted file: {file_path}")
            return None

        # Remove all metadata tags
        audio.delete()
        audio.save()

        # Verify that metadata was removed
        cleaned_audio = File(file_path, easy=True)
        if cleaned_audio and not cleaned_audio.tags:
            logger.info(f"✅ Metadata removed successfully using Mutagen: {file_path}")
            return output_path
        else:
            logger.warning(f"⚠️ Mutagen did not completely remove metadata: {file_path}")
            return None

    except Exception as e:
        logger.error(f"❌ Mutagen encountered an error: {e}", exc_info=True)
        return None
