import os
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
