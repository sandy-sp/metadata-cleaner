from datetime import datetime
import os
import shutil
from typing import Optional, Dict, Any
import pikepdf
import pypdf

try:
    import docx
except ImportError:
    docx = None

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
            elif ext == ".txt":
                return {}
        except Exception as e:
            logger.error(
                f"Failed to extract metadata from {file_path}: {e}", exc_info=True
            )
        return None

    def _extract_metadata_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF using pypdf."""
        try:
            reader = pypdf.PdfReader(file_path)
            meta = reader.metadata
            if meta:
                return dict(meta)
            return {}
        except Exception as e:
            logger.error(f"pypdf extraction failed for {file_path}: {e}")
            return None

    def _extract_metadata_docx(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from DOCX using python-docx."""
        if docx is None:
            logger.warning("python-docx is not installed, cannot extract DOCX metadata")
            return None
        try:
            doc = docx.Document(file_path)
            core_props = doc.core_properties
            return {
                "author": core_props.author,
                "created": core_props.created,
                "modified": core_props.modified,
                "last_modified_by": core_props.last_modified_by,
                "title": core_props.title,
            }
        except Exception as e:
            logger.error(f"docx extraction failed for {file_path}: {e}")
            return None

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from a document file without corrupting content."""
        if not self.validate(file_path):
            logger.error(f"Validation failed for {file_path}")
            return None

        ext = os.path.splitext(file_path)[1].lower()
        try:
            output_path = self.prepare_output_path(file_path, output_path)
            if ext == ".pdf":
                return self._remove_metadata_pdf(file_path, output_path)
            elif ext == ".docx":
                return self._remove_metadata_docx(file_path, output_path)
            elif ext == ".txt":
                shutil.copy2(file_path, output_path)
                return output_path
        except Exception as e:
            logger.error(
                f"Error processing document file {file_path}: {e}", exc_info=True
            )
        return None

    def _remove_metadata_pdf(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
        """Ensure PDF metadata removal works correctly without modifying the original."""
        try:
            with pikepdf.open(file_path) as pdf:
                try:
                    del pdf.Root.Metadata
                except (AttributeError, KeyError):
                    pass

                try:
                    del pdf.trailer["/Info"]
                except (AttributeError, KeyError):
                    pass

                pdf.save(output_path)

            logger.info(f"PDF metadata removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from PDF: {e}", exc_info=True)
            return None

    def _remove_metadata_docx(self, file_path: str, output_path: str) -> Optional[str]:
        """Clear common DOCX core properties and save to a new file."""
        if docx is None:
            logger.warning("python-docx is not installed, cannot clean DOCX metadata")
            return None

        try:
            document = docx.Document(file_path)
            core_props = document.core_properties
            core_props.author = ""
            core_props.category = ""
            core_props.comments = ""
            core_props.identifier = ""
            core_props.keywords = ""
            core_props.language = ""
            core_props.last_modified_by = ""
            core_props.subject = ""
            core_props.title = ""
            core_props.version = ""
            core_props.revision = 1
            neutral_date = datetime(1980, 1, 1)
            core_props.created = neutral_date
            core_props.modified = neutral_date
            document.save(output_path)
            logger.info(f"DOCX metadata removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from DOCX: {e}", exc_info=True)
            return None


document_handler = DocumentHandler()
