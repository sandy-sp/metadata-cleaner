from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import shutil
from typing import Optional
from metadata_cleaner.logs.logger import logger

def remove_audio_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from MP3 (and similar) audio files using Mutagen.

    Parameters:
        file_path (str): The path to the audio file.
        output_path (Optional[str]): The destination path for the cleaned file.
                                     If None, the original file path is returned after processing.

    Returns:
        Optional[str]: The path to the cleaned file if successful, otherwise None.
    """
    try:
        audio = MP3(file_path, ID3=EasyID3)
        audio.delete()
        audio.save()

        if output_path:
            shutil.copy(file_path, output_path)  # Copy file to the specified output directory
            return output_path
        return file_path

    except Exception as e:
        logger.error(f"Error removing metadata from {file_path}: {e}", exc_info=True)
        return None
