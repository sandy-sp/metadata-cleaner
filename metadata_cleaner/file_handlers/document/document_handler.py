import os
from typing import Optional, Dict, Any
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.core.metadata_utils import (
    validate_file_path,
    get_safe_output_path,
    verify_file_integrity
)
from metadata_cleaner.file_handlers.document.pdf_handler import (
    extract_metadata as extract_pdf_metadata,
    remove_pdf_metadata
)
from metadata_cleaner.file_handlers.document.docx_handler import (
    extract_metadata as extract_docx_metadata,
    remove_docx_metadata
)

class DocumentHandler:
    """
    Unified handler for document metadata operations.
    
    Features:
    - Support for multiple document formats (PDF, DOCX)
    - Automatic format detection
    - Metadata extraction and removal
    - File integrity verification
    - Error handling and logging
    """

    SUPPORTED_FORMATS = {
        'pdf': {'.pdf'},
        'word': {'.docx', '.doc'},
    }

    def __init__(self):
        """Initialize the document handler."""
        self.all_formats = {ext for formats in self.SUPPORTED_FORMATS.values() for ext in formats}

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.all_formats

    def get_format_type(self, file_path: str) -> Optional[str]:
        """Determine the document format type."""
        ext = os.path.splitext(file_path)[1].lower()
        for format_type, extensions in self.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return format_type
        return None

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a document file.

        Returns:
            - Metadata dictionary if extraction succeeds.
            - None if extraction fails.
        """
        if not validate_file_path(file_path):
            return None

        if not self.is_supported(file_path):
            logger.error(f"❌ Unsupported document format: {file_path}")
            return None

        format_type = self.get_format_type(file_path)
        logger.info(f"📂 Extracting metadata from: {file_path}")

        try:
            if format_type == 'pdf':
                metadata = extract_pdf_metadata(file_path)
            elif format_type == 'word':
                metadata = extract_docx_metadata(file_path)
            else:
                logger.error(f"❌ No metadata extractor available for format: {format_type}")
                return None

            if metadata:
                logger.info(f"✅ Metadata extracted from {format_type.upper()} file: {file_path}")
                return metadata

            logger.warning(f"⚠️ No metadata found in: {file_path}")
            return {}

        except Exception as e:
            logger.error(f"❌ Error extracting metadata from {file_path}: {e}", exc_info=True)
            return None

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None, verify: bool = True) -> Optional[str]:
        """
        Remove metadata from a document file.

        Returns:
            - Path to the cleaned file if successful.
            - None if the process fails.
        """
        if not validate_file_path(file_path):
            return None

        if not self.is_supported(file_path):
            logger.error(f"❌ Unsupported document format: {file_path}")
            return None

        output_path = get_safe_output_path(file_path, output_path)
        format_type = self.get_format_type(file_path)

        logger.info(f"📂 Removing metadata from: {file_path}")

        try:
            if format_type == 'pdf':
                cleaned_file = remove_pdf_metadata(file_path, output_path)
            elif format_type == 'word':
                cleaned_file = remove_docx_metadata(file_path, output_path)
            else:
                logger.error(f"❌ No metadata remover available for format: {format_type}")
                return None

            if cleaned_file:
                logger.info(f"✅ Metadata removed from {format_type.upper()} file: {output_path}")

                if verify and not verify_file_integrity(file_path, output_path):
                    logger.error(f"⚠️ File integrity verification failed: {output_path}")
                    return None

                return output_path

            logger.error(f"❌ Failed to remove metadata from: {file_path}")
            return None

        except Exception as e:
            logger.error(f"❌ Error removing metadata from {file_path}: {e}", exc_info=True)
            return None

# Create a default instance
default_handler = DocumentHandler()

# Convenience functions using the default handler
def extract_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """Convenience function to extract metadata using the default handler."""
    return default_handler.extract_metadata(file_path)

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convenience function to remove metadata using the default handler."""
    return default_handler.remove_metadata(file_path, output_path)
