import os
from typing import Optional, Dict
import fitz  # PyMuPDF
import pikepdf
from pypdf import PdfReader, PdfWriter
from metadata_cleaner.file_handlers.document.exiftool_pdf_handler import (
    extract_metadata as exiftool_extract_metadata,
    remove_metadata as exiftool_remove_metadata,
    is_exiftool_available
)
from metadata_cleaner.logs.logger import logger

"""
PDF handler module for metadata extraction and removal.

Uses ExifTool as the primary method, with PyMuPDF (fitz), pikepdf, and PyPDF as fallbacks.
"""

def validate_file(file_path: str) -> bool:
    """Check if the file exists and is valid."""
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"❌ Not a valid file: {file_path}")
        return False
    return True

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a PDF file dynamically based on available tools.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata from: {file_path}")

    if is_exiftool_available():
        metadata = exiftool_extract_metadata(file_path)
        if metadata:
            logger.info("✅ Metadata extracted using ExifTool.")
            return metadata

    logger.warning("⚠️ ExifTool failed, falling back to PyMuPDF...")
    try:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        return metadata if metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"❌ PyMuPDF failed: {e}", exc_info=True)

    logger.warning("⚠️ Falling back to pikepdf...")
    try:
        with pikepdf.open(file_path) as pdf:
            metadata = pdf.docinfo
            return dict(metadata) if metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"❌ pikepdf failed: {e}", exc_info=True)

    logger.warning("⚠️ Falling back to PyPDF...")
    try:
        reader = PdfReader(file_path)
        return reader.metadata if reader.metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"❌ PyPDF failed: {e}", exc_info=True)

    logger.error("❌ All metadata extraction attempts failed.")
    return None

def remove_pdf_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a PDF dynamically based on available tools.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Removing metadata from: {file_path}")

    if is_exiftool_available():
        cleaned_file = exiftool_remove_metadata(file_path)
        if cleaned_file:
            logger.info("✅ Metadata removed using ExifTool.")
            return cleaned_file

    logger.warning("⚠️ ExifTool failed, falling back to PyMuPDF...")
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
            logger.error("❌ Metadata removal resulted in a corrupted PDF file.")
            return None

        logger.info("✅ Metadata removed using PyMuPDF.")
        return output_path
    except Exception as e:
        logger.error(f"❌ PyMuPDF failed: {e}", exc_info=True)

    logger.warning("⚠️ PyMuPDF failed, falling back to pikepdf...")
    try:
        with pikepdf.open(file_path) as pdf:
            pdf.save(output_path or file_path)
        logger.info("✅ Metadata removed using pikepdf.")
        return output_path or file_path
    except Exception as e:
        logger.error(f"❌ pikepdf failed: {e}", exc_info=True)

    logger.warning("⚠️ Pikepdf failed, falling back to PyPDF...")
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({})
        
        output_path = output_path or file_path
        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info("✅ Metadata removed using PyPDF.")
        return output_path
    except Exception as e:
        logger.error(f"❌ PyPDF failed: {e}", exc_info=True)

    logger.error("❌ All metadata removal attempts failed.")
    return None
