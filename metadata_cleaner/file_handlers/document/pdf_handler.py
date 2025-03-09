import os
from typing import Optional, Dict
import fitz  # PyMuPDF
import pikepdf
from pypdf import PdfReader, PdfWriter
from metadata_cleaner.file_handlers.document.exiftool_pdf_handler import extract_metadata as exiftool_extract_metadata, remove_metadata as exiftool_remove_metadata
from metadata_cleaner.logs.logger import logger

"""
PDF handler module for metadata extraction and removal.

Uses ExifTool as the primary method, with PyMuPDF (fitz), pikepdf, and PyPDF as fallbacks.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a PDF file dynamically based on available tools.

    Parameters:
        file_path (str): Path to the PDF file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    logger.info(f"Attempting to extract metadata from: {file_path}")
    
    metadata = exiftool_extract_metadata(file_path)
    if metadata:
        logger.info("Metadata extracted successfully using ExifTool.")
        return metadata
    
    logger.warning("ExifTool failed, falling back to PyMuPDF...")
    try:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        return metadata if metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"PyMuPDF failed: {e}")
    
    logger.warning("Falling back to pikepdf...")
    try:
        with pikepdf.open(file_path) as pdf:
            metadata = pdf.docinfo
            return dict(metadata) if metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"pikepdf failed: {e}")
    
    logger.warning("Falling back to PyPDF...")
    try:
        reader = PdfReader(file_path)
        return reader.metadata if reader.metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"PyPDF failed: {e}")
    
    logger.error("All metadata extraction attempts failed.")
    return None

def remove_pdf_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a PDF dynamically based on available tools.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    logger.info(f"Attempting to remove metadata from: {file_path}")

    if exiftool_remove_metadata(file_path):
        logger.info("Metadata removed successfully using ExifTool.")
        return file_path

    logger.warning("ExifTool failed, falling back to PyMuPDF...")
    try:
        doc = fitz.open(file_path)
        doc.set_metadata({})
        output_path = output_path or file_path
        doc.save(output_path)
        doc.close()

        # Verify that the cleaned file is readable
        try:
            test_doc = fitz.open(output_path)
            test_doc.close()
        except Exception:
            logger.error("Metadata removal resulted in a corrupted PDF file.")
            return None

        logger.info("Metadata removed using PyMuPDF.")
        return output_path
    except Exception as e:
        logger.error(f"PyMuPDF failed: {e}")

    return None