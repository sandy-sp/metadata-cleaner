import os
from typing import Optional, Dict, Any
import fitz  # PyMuPDF
import pikepdf
from pypdf import PdfReader, PdfWriter
from m_c.core.logger import logger
from m_c.core.file_utils import validate_file
from m_c.core.tool_manager import tool_manager

class DocumentHandler:
    """
    Handles metadata extraction, removal, and editing for document files.
    """
    SUPPORTED_FORMATS = {"pdf", "docx", "txt"}

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        return ext in self.SUPPORTED_FORMATS

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a document file using the best available tool."""
        if not validate_file(file_path) or not self.is_supported(file_path):
            return None
        
        ext = file_path.split('.')[-1].lower()
        if ext == "pdf":
            return self._extract_metadata_pdf(file_path)
        elif ext == "docx":
            return self._extract_metadata_docx(file_path)
        else:
            return None

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from a document file."""
        if not validate_file(file_path) or not self.is_supported(file_path):
            return None
        
        ext = file_path.split('.')[-1].lower()
        if ext == "pdf":
            return self._remove_metadata_pdf(file_path, output_path)
        elif ext == "docx":
            return self._remove_metadata_docx(file_path, output_path)
        else:
            return None

    def _extract_metadata_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a PDF file."""
        try:
            doc = fitz.open(file_path)
            return doc.metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata from PDF: {e}")
            return None

    def _remove_metadata_pdf(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Remove metadata from a PDF file."""
        try:
            with pikepdf.open(file_path) as pdf:
                pdf.save(output_path or file_path)
            return output_path or file_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from PDF: {e}")
            return None

    def _extract_metadata_docx(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            core_props = doc.core_properties
            return {k: v for k, v in vars(core_props).items() if v is not None}
        except Exception as e:
            logger.error(f"Failed to extract metadata from DOCX: {e}")
            return None

    def _remove_metadata_docx(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Remove metadata from a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            core_props = doc.core_properties
            for prop in vars(core_props):
                setattr(core_props, prop, None)
            output_path = output_path or file_path
            doc.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from DOCX: {e}")
            return None

document_handler = DocumentHandler()
