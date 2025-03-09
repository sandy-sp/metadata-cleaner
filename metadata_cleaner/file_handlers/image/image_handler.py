import os
from typing import Optional, Dict, Any
from PIL import Image
import piexif 
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.core.metadata_filter import load_filter_rules, filter_exif_data
from metadata_cleaner.file_handlers.image.exiftool_handler import (
    extract_metadata as extract_metadata_exiftool,
    remove_metadata as remove_metadata_exiftool,
    is_exiftool_available
)
from metadata_cleaner.file_handlers.image.piexif_handler import (
    extract_metadata as extract_metadata_piexif,
    remove_metadata as remove_metadata_piexif
)
from metadata_cleaner.core.metadata_utils import (
    validate_file_path,
    get_safe_output_path,
    verify_file_integrity
)

class ImageHandler:
    """
    Unified handler for image metadata operations.
    
    Features:
    - Automatic tool selection (ExifTool/Piexif)
    - Metadata extraction and removal
    - Selective filtering
    - File integrity verification
    - Error handling and logging
    """

    def __init__(self, use_exiftool: bool = True):
        """
        Initialize the image handler.

        Args:
            use_exiftool (bool): Whether to prefer ExifTool over Piexif when available.
        """
        self.use_exiftool = use_exiftool and is_exiftool_available()
        self.supported_formats = {'.jpg', '.jpeg', '.tiff', '.png', '.webp', '.heic'}

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from an image file.

        Args:
            file_path (str): Path to the image file.

        Returns:
            Optional[Dict[str, Any]]: Extracted metadata or None if extraction fails.
        """
        if not validate_file_path(file_path):
            return None

        if not self.is_supported(file_path):
            logger.error(f"Unsupported image format: {file_path}")
            return None

        if not is_exiftool_available():
            logger.warning("ExifTool not found. Falling back to Piexif.")
            return extract_metadata_piexif(file_path)

        try:
            metadata = extract_metadata_exiftool(file_path)
            if metadata:
                logger.info(f"Metadata extracted using ExifTool: {file_path}")
                return metadata
            else:
                logger.warning("ExifTool failed to extract metadata. Falling back to Piexif.")
                return extract_metadata_piexif(file_path)
        except Exception as e:
            logger.error(f"Error extracting metadata using ExifTool: {e}", exc_info=True)
            return extract_metadata_piexif(file_path)

    def remove_image_metadata(self, 
                       file_path: str, 
                       output_path: Optional[str] = None,
                       config_file: Optional[str] = None,
                       verify: bool = True) -> Optional[str]:
        """
        Remove metadata from an image file.

        Args:
            file_path (str): Path to the image file.
            output_path (Optional[str]): Custom output path.
            config_file (Optional[str]): Path to metadata filtering config.
            verify (bool): Whether to verify file integrity after removal.

        Returns:
            Optional[str]: Path to cleaned file if successful, None otherwise.
        """
        if not validate_file_path(file_path):
            return None

        if not self.is_supported(file_path):
            logger.error(f"Unsupported image format: {file_path}")
            return None

        # Generate safe output path if not provided
        output_path = output_path or get_safe_output_path(file_path)

        try:
            # Load filtering rules if config provided
            rules = load_filter_rules(config_file) if config_file else None

            # Try ExifTool first if available and enabled
            if self.use_exiftool:
                result = remove_metadata_exiftool(file_path, output_path)
                if result:
                    logger.info(f"Metadata removed using ExifTool: {output_path}")
                    if verify and not verify_file_integrity(file_path, output_path):
                        logger.error(f"File integrity verification failed: {output_path}")
                        return None
                    return output_path

            # Fall back to Piexif
            result = remove_metadata_piexif(file_path, output_path)
            if result:
                logger.info(f"Metadata removed using Piexif: {output_path}")
                if verify and not verify_file_integrity(file_path, output_path):
                    logger.error(f"File integrity verification failed: {output_path}")
                    return None
                return output_path

            logger.error(f"Failed to remove metadata from: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error removing metadata from {file_path}: {e}", exc_info=True)
            return None

    def filter_metadata(self, 
                       file_path: str, 
                       rules: Dict[str, Any],
                       output_path: Optional[str] = None) -> Optional[str]:
        """
        Selectively filter metadata from an image file.

        Args:
            file_path (str): Path to the image file.
            rules (Dict[str, Any]): Metadata filtering rules.
            output_path (Optional[str]): Custom output path.

        Returns:
            Optional[str]: Path to filtered file if successful, None otherwise.
        """
        metadata = self.extract_metadata(file_path)
        if not metadata:
            return None

        try:
            filtered_metadata = filter_exif_data(metadata, rules)
            output_path = output_path or get_safe_output_path(file_path)

            img = Image.open(file_path)
            
            # Convert dictionary to binary EXIF
            exif_bytes = piexif.dump(filtered_metadata)
            
            img.save(output_path, exif=exif_bytes)  # Save correctly formatted EXIF data
            logger.info(f"Metadata filtered successfully: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error filtering metadata: {e}", exc_info=True)
            return None

# Create a default instance
default_handler = ImageHandler()

# Convenience functions using the default handler
def extract_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """Convenience function to extract metadata using default handler."""
    return default_handler.extract_metadata(file_path)

def remove_image_metadata(file_path: str, output_path: Optional[str] = None,
                   config_file: Optional[str] = None) -> Optional[str]:
    """Convenience function to remove metadata using default handler."""
    return default_handler.remove_metadata(file_path, output_path, config_file)

def filter_metadata(file_path: str, rules: Dict[str, Any],
                   output_path: Optional[str] = None) -> Optional[str]:
    """Convenience function to filter metadata using default handler."""
    return default_handler.filter_metadata(file_path, rules, output_path)
