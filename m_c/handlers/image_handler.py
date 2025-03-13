import os
import shutil
from typing import Optional, Dict, Any
from PIL import Image
import piexif
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler
from PIL import UnidentifiedImageError, ImageFile

class ImageHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for image files.
    Uses ExifTool and Piexif.
    """

    SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "tiff", "webp"}

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata with fallback methods."""
        if not self.validate(file_path):
            return None
        try:
            from m_c.utils.tool_utils import ToolManager
            if ToolManager().check_tools()["ExifTool"]:
                return self._extract_metadata_exiftool(file_path)
        except Exception:
            logger.warning(f"ExifTool failed, using fallback method for {file_path}")
        return self._extract_metadata_piexif(file_path) or {}

    ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow processing truncated images

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from an image file and save a new cleaned copy without corrupting it."""
        if not self.validate(file_path):
            logger.error(f"🚨 Validation failed for {file_path}")
            return None

        try:
            logger.debug(f"🔍 Attempting to open image file: {file_path}")

            with Image.open(file_path) as img:
                img = img.convert("RGB")  # Convert to ensure compatibility
                exif_data = img.info.get("exif")

                # Save image WITHOUT EXIF data
                if exif_data:
                    img.save(output_path, "jpeg", exif=None)
                else:
                    img.save(output_path, "jpeg")  # No metadata in the first place

            if os.path.exists(output_path):
                logger.info(f"✅ Image metadata removed successfully: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Image was not saved properly: {output_path}")

        except UnidentifiedImageError:
            logger.error(f"❌ Cannot identify image file {file_path}. Possible corruption or unsupported format.")
        except Exception as e:
            logger.error(f"❌ Error processing image file {file_path}: {e}", exc_info=True)

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
            if os.path.exists(output_path):
                return output_path
            logger.warning(f"Retrying metadata removal using ExifTool for {file_path}")
            return self._remove_metadata_exiftool(file_path, output_path)
        except Exception as e:
            logger.error(f"Piexif failed to remove metadata: {e}")
        return None

    def _extract_metadata_piexif(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using Piexif with corruption handling."""
        try:
            img = Image.open(file_path)
            exif_data = img.info.get("exif", None)
            if exif_data is None:
                logger.warning(f"No EXIF data found for {file_path}")
                return {}
            return piexif.load(exif_data)
        except UnidentifiedImageError:
            logger.error(f"❌ Cannot identify image file {file_path}. Possible corruption or unsupported format.")
        except Exception as e:
            logger.error(f"Failed to extract metadata with Piexif: {e}")
        return None

image_handler = ImageHandler()
