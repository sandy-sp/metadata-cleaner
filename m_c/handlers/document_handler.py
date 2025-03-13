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
        try:
            if ext == ".pdf":
                return self._extract_metadata_pdf(file_path)
            elif ext == ".docx":
                return self._extract_metadata_docx(file_path)
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}", exc_info=True)
        return None

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from a document file without corrupting content."""
        if not self.validate(file_path):
            logger.error(f"🚨 Validation failed for {file_path}")
            return None

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_cleaned{ext}"

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copyfile(file_path, output_path)

            if ext == ".pdf":
                with pikepdf.open(output_path) as pdf:
                    pdf.remove_metadata()
                    pdf.save(output_path)
            elif ext == ".docx":
                return self._remove_metadata_docx(file_path, output_path)

            if os.path.exists(output_path):
                logger.info(f"✅ Document metadata removed successfully: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Document was not saved properly: {output_path}")
        except Exception as e:
            logger.error(f"❌ Error processing document file {file_path}: {e}", exc_info=True)
        return None

    def _remove_metadata_pdf(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Ensure PDF metadata removal works correctly without modifying the original."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copyfile(file_path, output_path)

            with pikepdf.open(output_path) as pdf:
                pdf.remove_metadata()
                pdf.save(output_path)

            logger.info(f"✅ PDF metadata successfully removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from PDF: {e}", exc_info=True)
            return None

document_handler = DocumentHandler()
