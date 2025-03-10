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

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Remove metadata from an audio file using TinyTag.
    Note: This function creates a new file without metadata rather than modifying the original.

    Parameters:
        file_path (str): Path to the input audio file.
        output_path (Optional[str]): Path where the cleaned file should be saved.
                                   If None, will use original filename with '_cleaned' suffix.

    Returns:
        Optional[str]: Path to the cleaned file if successful, None if failed.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    try:
        # If no output path specified, create one
        if output_path is None:
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            name, ext = os.path.splitext(file_name)
            output_path = os.path.join(file_dir, f"{name}_cleaned{ext}")

        # Read the original file's raw audio data
        with open(file_path, 'rb') as f:
            audio_data = f.read()

        # Create a new file with just the audio data
        # Note: This is a simplified approach and may not work for all audio formats
        with open(output_path, 'wb') as f:
            # Skip any ID3v2 header if present (for MP3 files)
            if audio_data.startswith(b'ID3'):
                # ID3v2 header is 10 bytes + extended header
                size_bytes = audio_data[6:10]
                header_size = 10 + ((size_bytes[0] & 0x7F) << 21 | 
                                  (size_bytes[1] & 0x7F) << 14 |
                                  (size_bytes[2] & 0x7F) << 7 |
                                  (size_bytes[3] & 0x7F))
                audio_data = audio_data[header_size:]
            
            # Write the audio data
            f.write(audio_data)

        logger.info(f"Created clean copy at: {output_path}")
        return output_path

    except Exception as e:
        logger.error("TinyTag does not support metadata removal.")
    return False