import os
import shutil
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
        try:
            audio = File(file_path, easy=True)
            return dict(audio) if audio else {}
        except Exception as e:
            logger.error(
                f"Failed to extract metadata from audio file {file_path}: {e}",
                exc_info=True,
            )
            return None

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from an audio file without modifying the original."""
        if not self.validate(file_path):
            return None

        output_path = self.prepare_output_path(file_path, output_path)
        try:
            shutil.copy2(file_path, output_path)
            audio = File(output_path)
            if audio is None:
                logger.warning(f"Unsupported audio container: {file_path}")
                os.remove(output_path)
                return None

            audio.delete()
            audio.save()
            logger.info(f"Audio metadata removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(
                f"Failed to remove metadata from audio file {file_path}: {e}",
                exc_info=True,
            )
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    def edit_metadata(
        self, file_path: str, metadata_changes: Dict[str, Any]
    ) -> Optional[str]:
        """Edit metadata for an audio file."""
        if not self.validate(file_path):
            return None

        try:
            audio = File(file_path, easy=True)
            if not audio:
                logger.warning(f"No metadata found or unsupported format: {file_path}")
                return None

            audio.update(metadata_changes)
            audio.save()
            logger.info(f"Metadata successfully updated: {file_path}")
            return file_path
        except Exception as e:
            logger.error(
                f"Failed to edit metadata for audio file {file_path}: {e}",
                exc_info=True,
            )
            return None


audio_handler = AudioHandler()
