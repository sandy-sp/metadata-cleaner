import os
from typing import Optional, Dict, Any
from PIL import Image
import piexif
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler
from PIL import Image, UnidentifiedImageError, ImageFile


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
            from m_c.utils.tool_utils import ToolManager

            if ToolManager().check_tools()["ExifTool"]:
                return self._extract_metadata_exiftool(file_path)
        except Exception:
            logger.warning(f"ExifTool failed, using fallback method for {file_path}")

        # Ensure a fallback method is used
        metadata = self._extract_metadata_piexif(file_path)
        if metadata is None:
            logger.warning(f"Fallback metadata extraction failed for {file_path}")
            return {}

        return metadata

    # Allow truncated images to be processed (optional)
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from an image file using Piexif."""
        if not self.validate(file_path):
            return None

        try:
            with Image.open(file_path) as img:
                img.info.pop("exif", None)  # Remove EXIF metadata
                
                if not output_path:
                    base, ext = os.path.splitext(file_path)
                    output_path = f"{base}_cleaned{ext}"

                img.save(output_path)

                if not os.path.exists(output_path):
                    logger.warning(f"Retrying metadata removal using ExifTool for {file_path}")
                    return self._remove_metadata_exiftool(file_path, output_path)

                return output_path
        except UnidentifiedImageError:
            logger.error(f"Cannot identify image file: {file_path}. It may be corrupted or unsupported.")
            return None
        except Exception as e:
            logger.error(f"Error removing metadata from {file_path}: {e}", exc_info=True)
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

            if not os.path.exists(output_path):
                logger.warning(
                    f"Retrying metadata removal using ExifTool for {file_path}"
                )
                return self._remove_metadata_exiftool(file_path, output_path)

            return output_path
        except Exception as e:
            logger.error(f"Piexif failed to remove metadata: {e}")
            return None


image_handler = ImageHandler()
