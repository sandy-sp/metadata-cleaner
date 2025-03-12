import os
import shutil
from typing import Optional, Dict, Any
import pikepdf
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler


class DocumentHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for document files.
    """

    SUPPORTED_FORMATS = {"pdf", "docx", "txt"}

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a document file."""
        if not self.validate(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()
        if ext == "pdf":
            return self._extract_metadata_pdf(file_path)
        elif ext == "docx":
            return self._extract_metadata_docx(file_path)
        return None

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from a document file."""
        if not self.validate(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()
        if ext == "pdf":
            return self._remove_metadata_pdf(file_path, output_path)
        elif ext == "docx":
            return self._remove_metadata_docx(file_path, output_path)
        return None

    def _remove_metadata_pdf(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
        """Ensure PDF metadata removal works correctly without modifying the original."""
        try:
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Copy the original file before processing
            shutil.copyfile(file_path, output_path)

            with pikepdf.open(output_path) as pdf:
                pdf.remove_metadata()
                pdf.save(output_path)

            if not os.path.exists(output_path):
                logger.error(
                    f"❌ PDF metadata removal failed: Output file missing {output_path}"
                )
                return None

            logger.info(f"✅ PDF metadata successfully removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"❌ Failed to remove metadata from PDF: {e}", exc_info=True)
            return None


document_handler = DocumentHandler()
