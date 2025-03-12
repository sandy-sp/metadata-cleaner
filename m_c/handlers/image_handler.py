import os
from typing import Optional, Dict, Any
from PIL import Image
import piexif
from m_c.core.logger import logger
from m_c.core.file_utils import validate_file
from m_c.core.tool_manager import tool_manager

class ImageHandler:
    """
    Handles metadata extraction, removal, and editing for image files.
    """
    SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "tiff", "webp", "heic"}

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        return ext in self.SUPPORTED_FORMATS

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from an image file using the best available tool."""
        if not validate_file(file_path) or not self.is_supported(file_path):
            return None

        if tool_manager.available_tools["ExifTool"]:
            return self._extract_metadata_exiftool(file_path)
        
        return self._extract_metadata_piexif(file_path)

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from an image file."""
        if not validate_file(file_path) or not self.is_supported(file_path):
            return None

        if tool_manager.available_tools["ExifTool"]:
            return self._remove_metadata_exiftool(file_path, output_path)
        
        return self._remove_metadata_piexif(file_path, output_path)

    def _extract_metadata_exiftool(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using ExifTool."""
        import subprocess
        try:
            result = subprocess.run(["exiftool", "-json", file_path], capture_output=True, text=True, check=True)
            return result.stdout if result.stdout else None
        except Exception as e:
            logger.error(f"ExifTool failed to extract metadata: {e}")
            return None

    def _remove_metadata_exiftool(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Remove metadata using ExifTool."""
        import subprocess
        try:
            subprocess.run(["exiftool", "-all=", "-overwrite_original", file_path], check=True)
            return file_path
        except Exception as e:
            logger.error(f"ExifTool failed to remove metadata: {e}")
            return None

    def _extract_metadata_piexif(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using Piexif."""
        try:
            img = Image.open(file_path)
            exif_data = img.info.get("exif", None)
            return piexif.load(exif_data) if exif_data else None
        except Exception as e:
            logger.error(f"Piexif failed to extract metadata: {e}")
            return None

    def _remove_metadata_piexif(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Remove metadata using Piexif."""
        try:
            img = Image.open(file_path)
            img.info.pop("exif", None)
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_cleaned{ext}"
            img.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Piexif failed to remove metadata: {e}")
            return None

image_handler = ImageHandler()
