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
            logger.error(f"Failed to extract metadata from audio file {file_path}: {e}", exc_info=True)
            return None

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from an audio file and save it."""
        if not self.validate(file_path):
            return None
        
        try:
            audio = File(file_path, easy=True)
            if not audio:
                logger.warning(f"No metadata found or unsupported format: {file_path}")
                return None
            
            audio.delete()
            audio.save()
            if File(file_path):
                logger.info(f"✅ Metadata successfully removed: {file_path}")
                return file_path
            else:
                logger.error(f"❌ Audio file was not saved properly after metadata removal: {file_path}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to remove metadata from audio file {file_path}: {e}", exc_info=True)
            return None

    def edit_metadata(self, file_path: str, metadata_changes: Dict[str, Any]) -> Optional[str]:
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
            logger.info(f"✅ Metadata successfully updated: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to edit metadata for audio file {file_path}: {e}", exc_info=True)
            return None

audio_handler = AudioHandler()
