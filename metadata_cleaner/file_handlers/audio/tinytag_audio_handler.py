import os
from typing import Optional, Dict
from tinytag import TinyTag
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting metadata from audio files using TinyTag.

TinyTag is a lightweight alternative for metadata extraction but does not support metadata removal.
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
    Extract metadata from an audio file using TinyTag.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using TinyTag: {file_path}")

    try:
        tag = TinyTag.get(file_path)
        metadata = {
            'title': tag.title,
            'artist': tag.artist,
            'album': tag.album,
            'year': tag.year,
            'duration': tag.duration,
            'track': tag.track,
            'genre': tag.genre
        }
        return {k: v for k, v in metadata.items() if v is not None}  # Remove empty fields

    except Exception as e:
        logger.error(f"❌ TinyTag failed to extract metadata: {e}", exc_info=True)
        return None

# 🔴 TinyTag does NOT support metadata removal. This function has been removed.
