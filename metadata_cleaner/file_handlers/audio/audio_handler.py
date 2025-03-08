import os
from typing import Optional, Dict, Any
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.core.metadata_utils import (
    validate_file_path,
    get_safe_output_path,
    verify_file_integrity
)
from metadata_cleaner.file_handlers.audio.exiftool_audio_handler import (
    extract_metadata as extract_metadata_exiftool,
    remove_metadata as remove_metadata_exiftool,
    is_exiftool_available
)
from metadata_cleaner.file_handlers.audio.mutagen_audio_handler import (
    extract_metadata as extract_metadata_mutagen,
    remove_metadata as remove_metadata_mutagen
)
from metadata_cleaner.file_handlers.audio.tinytag_audio_handler import (
    extract_metadata as extract_metadata_tinytag
)

class AudioHandler:
    """
    Unified handler for audio metadata operations.
    
    Features:
    - Support for multiple audio formats (MP3, WAV, FLAC, etc.)
    - Automatic tool selection (ExifTool/Mutagen/TinyTag)
    - Metadata extraction and removal
    - File integrity verification
    - Error handling and logging
    """

    def __init__(self, use_exiftool: bool = True):
        """
        Initialize the audio handler.

        Args:
            use_exiftool (bool): Whether to prefer ExifTool over other tools when available.
        """
        self.use_exiftool = use_exiftool and is_exiftool_available()
        self.supported_formats = {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma'}

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from an audio file.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[Dict[str, Any]]: Extracted metadata or None if extraction fails.
        """
        if not validate_file_path(file_path):
            return None

        if not self.is_supported(file_path):
            logger.error(f"Unsupported audio format: {file_path}")
            return None

        try:
            # Try ExifTool first if available and enabled
            if self.use_exiftool:
                metadata = extract_metadata_exiftool(file_path)
                if metadata:
                    logger.info(f"Metadata extracted using ExifTool: {file_path}")
                    return metadata

            # Try Mutagen next
            metadata = extract_metadata_mutagen(file_path)
            if metadata:
                logger.info(f"Metadata extracted using Mutagen: {file_path}")
                return metadata

            # Fall back to TinyTag (read-only)
            metadata = extract_metadata_tinytag(file_path)
            if metadata:
                logger.info(f"Metadata extracted using TinyTag: {file_path}")
                return metadata

            logger.warning(f"No metadata found in: {file_path}")
            return {}

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}", exc_info=True)
            return None

    def remove_metadata(self, 
                       file_path: str, 
                       output_path: Optional[str] = None,
                       verify: bool = True) -> Optional[str]:
        """
        Remove metadata from an audio file.

        Args:
            file_path (str): Path to the audio file.
            output_path (Optional[str]): Custom output path.
            verify (bool): Whether to verify file integrity after removal.

        Returns:
            Optional[str]: Path to cleaned file if successful, None otherwise.
        """
        if not validate_file_path(file_path):
            return None

        if not self.is_supported(file_path):
            logger.error(f"Unsupported audio format: {file_path}")
            return None

        # Generate safe output path if not provided
        output_path = output_path or get_safe_output_path(file_path)

        try:
            # Try ExifTool first if available and enabled
            if self.use_exiftool:
                result = remove_metadata_exiftool(file_path, output_path)
                if result:
                    logger.info(f"Metadata removed using ExifTool: {output_path}")
                    if verify and not verify_file_integrity(file_path, output_path):
                        logger.error(f"File integrity verification failed: {output_path}")
                        return None
                    return output_path

            # Fall back to Mutagen
            result = remove_metadata_mutagen(file_path, output_path)
            if result:
                logger.info(f"Metadata removed using Mutagen: {output_path}")
                if verify and not verify_file_integrity(file_path, output_path):
                    logger.error(f"File integrity verification failed: {output_path}")
                    return None
                return output_path

            logger.error(f"Failed to remove metadata from: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error removing metadata from {file_path}: {e}", exc_info=True)
            return None

# Create a default instance
default_handler = AudioHandler()

# Convenience functions using the default handler
def extract_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """Convenience function to extract metadata using default handler."""
    return default_handler.extract_metadata(file_path)

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convenience function to remove metadata using default handler."""
    return default_handler.remove_metadata(file_path, output_path)
