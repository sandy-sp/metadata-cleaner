import os
from typing import Optional, Dict, Any
from mutagen import File
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler


class AudioHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for audio files.
    Uses Mutagen for metadata processing.
    """

    SUPPORTED_FORMATS = {"mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"}

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from an audio file."""
        if not self.validate(file_path):
            return None
        return self._extract_metadata_mutagen(file_path)

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from an audio file."""
        if not self.validate(file_path):
            return None
        return self._remove_metadata_mutagen(file_path, output_path)

    def _extract_metadata_mutagen(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using Mutagen."""
        try:
            audio = File(file_path, easy=True)
            return dict(audio) if audio else None
        except Exception as e:
            logger.error(f"Failed to extract metadata from audio file: {e}")
            return None

    def _remove_metadata_mutagen(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
        """Remove metadata using Mutagen."""
        try:
            audio = File(file_path, easy=True)
            if not audio:
                return None

            audio.delete()
            audio.save()
            return file_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from audio file: {e}")
            return None


audio_handler = AudioHandler()
