import os
from typing import Optional
from m_c.core.logger import logger
from m_c.core.file_utils import validate_file

class BaseHandler:
    """
    Base class for all metadata handlers.
    Provides common validation and format checking.
    """

    SUPPORTED_FORMATS = set()

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
        import subprocess
        import json
        try:
            result = subprocess.run(
                ["exiftool", "-j", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            return data[0] if data else {}
        except Exception as e:
            logger.error(f"ExifTool extraction failed for {file_path}: {e}")
            return None

    def _remove_metadata_exiftool(self, file_path: str, output_path: Optional[str] = None):
        """Remove metadata using ExifTool."""
        import subprocess
        import shutil
        
        if output_path and output_path != file_path:
            shutil.copy(file_path, output_path)
            target = output_path
        else:
            target = file_path
            
        try:
            # -all= removes all metadata
            # -overwrite_original forces inplace update (we copied already if needed)
            subprocess.run(
                ["exiftool", "-all=", "-overwrite_original", target],
                check=True,
                capture_output=True
            )
            return target
        except subprocess.CalledProcessError as e:
            logger.error(f"ExifTool removal failed for {file_path}: {e}")
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
            return None
