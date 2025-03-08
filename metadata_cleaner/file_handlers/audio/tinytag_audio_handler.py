import os
from typing import Optional, Dict
from tinytag import TinyTag
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting metadata from audio files using TinyTag.

Provides a lightweight alternative for metadata extraction but does not support metadata removal.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extract metadata from an audio file using TinyTag.

    Parameters:
        file_path (str): Path to the audio file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
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
        logger.error(f"Error extracting metadata using TinyTag: {e}", exc_info=True)
        return None
