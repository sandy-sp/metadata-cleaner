import json
import os
import shutil
import subprocess
from typing import Optional
from m_c.core.logger import logger
from m_c.core.file_utils import validate_file


class BaseHandler:
    """
    Base class for all metadata handlers.
    Provides common validation and format checking.
    """

    SUPPORTED_FORMATS = set()
    EXIFTOOL_TIMEOUT_SECONDS = 60

    def prepare_output_path(
        self, file_path: str, output_path: Optional[str] = None
    ) -> str:
        """Return a writable output path and refuse destructive in-place edits."""
        if output_path is None:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_cleaned{ext}"

        if os.path.abspath(file_path) == os.path.abspath(output_path):
            raise ValueError("Output path must be different from input path")

        output_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(output_dir, exist_ok=True)
        return output_path

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower().strip(".")
        if ext in self.SUPPORTED_FORMATS:
            return True
        logger.warning(f"Unsupported file format: {file_path}")
        return False

    def validate(self, file_path: str) -> bool:
        """Validate file existence and format."""
        if not validate_file(file_path):
            logger.error(f"File not found or inaccessible: {file_path}")
            return False
        if not self.is_supported(file_path):
            return False
        return True

    def _extract_metadata_exiftool(self, file_path: str):
        """Extract metadata using ExifTool."""
        try:
            result = subprocess.run(
                ["exiftool", "-j", file_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=self.EXIFTOOL_TIMEOUT_SECONDS,
            )
            data = json.loads(result.stdout)
            return data[0] if data else {}
        except subprocess.TimeoutExpired:
            logger.error(
                "ExifTool extraction timed out for "
                f"{file_path} after {self.EXIFTOOL_TIMEOUT_SECONDS}s"
            )
            return None
        except Exception as e:
            logger.error(f"ExifTool extraction failed for {file_path}: {e}")
            return None

    def _remove_metadata_exiftool(
        self, file_path: str, output_path: Optional[str] = None
    ):
        """Remove metadata using ExifTool."""
        target = self.prepare_output_path(file_path, output_path)
        shutil.copy2(file_path, target)

        try:
            subprocess.run(
                ["exiftool", "-all=", "-overwrite_original", target],
                check=True,
                capture_output=True,
                text=True,
                timeout=self.EXIFTOOL_TIMEOUT_SECONDS,
            )
            return target
        except subprocess.TimeoutExpired:
            logger.error(
                "ExifTool removal timed out for "
                f"{file_path} after {self.EXIFTOOL_TIMEOUT_SECONDS}s"
            )
            if os.path.exists(target):
                os.remove(target)
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"ExifTool removal failed for {file_path}: {e.stderr}")
            if os.path.exists(target):
                os.remove(target)
            return None
        except Exception as e:
            logger.error(f"ExifTool removal failed for {file_path}: {e}")
            if os.path.exists(target):
                os.remove(target)
            return None
