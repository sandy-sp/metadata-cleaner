import os
import shutil
from typing import Optional, Dict, Any
from PIL import Image
import piexif
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler
from PIL import UnidentifiedImageError
from PIL.Image import DecompressionBombError

Image.MAX_IMAGE_PIXELS = 100_000_000


class ImageHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for image files.
    Uses ExifTool and Piexif.
    """

    EXIFTOOL_ONLY_FORMATS = {"avif", "heic", "heif"}
    SUPPORTED_FORMATS = {
        "jpg",
        "jpeg",
        "png",
        "tiff",
        "webp",
        *EXIFTOOL_ONLY_FORMATS,
    }

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

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from an image file strictly preserving quality/format."""
        if not self.validate(file_path):
            logger.error(f"Validation failed for {file_path}")
            return None

        output_path = self.prepare_output_path(file_path, output_path)

        try:
            logger.debug(f"Processing image: {file_path}")
            ext = os.path.splitext(file_path)[1].lower()

            if ext.strip(".") in self.EXIFTOOL_ONLY_FORMATS:
                logger.info(f"Using ExifTool for {ext.upper().strip('.')}: {file_path}")
                return self._remove_metadata_exiftool(file_path, output_path)

            if ext in {".jpg", ".jpeg", ".webp", ".tiff", ".tif"}:
                try:
                    shutil.copy2(file_path, output_path)
                    piexif.remove(output_path)
                    logger.info(f"Image metadata removed losslessly: {output_path}")
                    return output_path
                except Exception as e:
                    logger.debug(f"Piexif failed ({e}), falling back to Pillow re-save")
                    if os.path.exists(output_path):
                        os.remove(output_path)

            with Image.open(file_path) as img:
                img.load()
                save_format = img.format
                image_without_metadata = Image.new(img.mode, img.size)
                image_without_metadata.putdata(list(img.getdata()))

                if "transparency" in img.info:
                    image_without_metadata.info["transparency"] = img.info[
                        "transparency"
                    ]

                image_without_metadata.save(output_path, format=save_format)

            if os.path.exists(output_path):
                logger.info(f"Image metadata removed by re-save: {output_path}")
                return output_path

        except DecompressionBombError:
            logger.error(f"Image is too large to process safely: {file_path}")
        except UnidentifiedImageError:
            logger.error(f"Cannot identify image file {file_path}")
        except Exception as e:
            logger.error(f"Error processing image file {file_path}: {e}", exc_info=True)

        if os.path.exists(output_path):
            os.remove(output_path)
        return None

    def _remove_metadata_piexif(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
        """Remove metadata using Piexif."""
        try:
            img = Image.open(file_path)
            img.info.pop("exif", None)
            output_path = self.prepare_output_path(file_path, output_path)
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
            logger.error(
                f"Cannot identify image file {file_path}. "
                "Possible corruption or unsupported format."
            )
        except Exception as e:
            logger.error(f"Failed to extract metadata with Piexif: {e}")
        return None


image_handler = ImageHandler()
