import os
from typing import Optional, Dict, Any
from PIL import Image
import piexif
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler


class ImageHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for image files.
    Uses ExifTool and Piexif.
    """

    SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "tiff", "webp"}

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Try extracting metadata with a fallback method if ExifTool is missing."""
        if not self.validate(file_path):
            return None

        try:
            if ToolManager().check_tools()["ExifTool"]:
                return self._extract_metadata_exiftool(file_path)
        except Exception:
            logger.warning(f"ExifTool failed, using fallback method for {file_path}")
        
        # Ensure a fallback method is used
        metadata = self._extract_metadata_piexif(file_path)
        if metadata is None:
            logger.warning(f"Fallback metadata extraction failed for {file_path}")
        
        return metadata

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from an image file."""
        if not self.validate(file_path):
            return None
        return self._remove_metadata_piexif(file_path, output_path)

    def _extract_metadata_piexif(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using Piexif."""
        try:
            img = Image.open(file_path)
            exif_data = img.info.get("exif", None)
            return piexif.load(exif_data) if exif_data else None
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return None

    def _remove_metadata_piexif(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
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
            logger.error(f"Failed to remove metadata: {e}")
            return None


image_handler = ImageHandler()
