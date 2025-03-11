import os
from typing import Optional, Dict
from mutagen import File
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from audio files using Mutagen.

Provides an alternative method for metadata operations when ExifTool is unavailable.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extract metadata from an audio file using Mutagen.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        audio = File(file_path, easy=True)
        if audio is None:
            logger.error(f"Unsupported file format or file is corrupted: {file_path}")
            return None
        return dict(audio)
    except Exception as e:
        logger.error(f"Error extracting metadata using Mutagen: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str) -> bool:
    """
    Remove metadata from an audio file using Mutagen.

    Parameters:
        file_path (str): Path to the audio file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    try:
        audio = File(file_path, easy=True)
        if audio is None:
            logger.error(f"Unsupported file format or file is corrupted: {file_path}")
            return False

        # Remove all tags
        audio.delete()
        audio.save()

        # Create a new file without metadata
        output_path = os.path.join(os.path.dirname(file_path), f"cleaned_{os.path.basename(file_path)}")
        audio_data = audio.info.pprint().encode('utf-8')

        with open(output_path, 'wb') as f:
            f.write(audio_data)

        logger.info(f"Metadata removed successfully from {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error removing metadata using Mutagen: {e}", exc_info=True)
        return False
