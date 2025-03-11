import os
import docx
import subprocess
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from DOCX files.

Uses python-docx for metadata extraction and applies multiple fallback methods for metadata removal,
including 7-Zip, dmeta, and python-docx.
"""

def extract_metadata(file_path: str) -> Optional[Dict[str, str]]:
    """
    Extracts metadata from a DOCX file.

    Parameters:
        file_path (str): Path to the DOCX file.

    Returns:
        Optional[Dict[str, str]]: Extracted metadata, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        doc = docx.Document(file_path)
        core_props = doc.core_properties
        metadata = {
            "author": core_props.author,
            "title": core_props.title,
            "subject": core_props.subject,
            "keywords": core_props.keywords,
            "last_modified_by": core_props.last_modified_by,
            "revision": core_props.revision,
            "created": core_props.created.isoformat() if core_props.created else None,
            "modified": core_props.modified.isoformat() if core_props.modified else None
        }
        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}", exc_info=True)
        return None

def remove_docx_metadata(file_path: str, output_path: Optional[str] = None) -> bool:
    """
    Removes metadata from a DOCX file using available tools.

    Parameters:
        file_path (str): Path to the DOCX file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    try:
        # Use 7-Zip first
        result = subprocess.run(['7z', 'd', file_path, 'docProps/*'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Metadata removed using 7-Zip from {file_path}")
            return True

        # Fallback to python-docx
        logger.warning("7-Zip failed, falling back to python-docx...")
        doc = Document(file_path)
        doc.core_properties.author = None
        doc.core_properties.title = None
        doc.core_properties.subject = None
        doc.core_properties.keywords = None
        doc.core_properties.last_modified_by = None
        doc.core_properties.revision = None
        doc.core_properties.created = None
        doc.core_properties.modified = None

        # Ensure output path
        output_path = output_path or file_path
        doc.save(output_path)
        logger.info(f"Metadata removed using python-docx from {file_path}")
        return True

        # Fallback to dmeta if python-docx fails
        logger.warning("python-docx failed, falling back to dmeta...")
    except Exception as e:
        logger.error(f"Error removing metadata using python-docx: {e}", exc_info=True)

    try:
        from dmeta.functions import clear
        clear(file_path, in_place=True)
        logger.info(f"Metadata removed using dmeta from {file_path}")
        return True
    except ImportError:
        logger.error("dmeta is not installed.")
    except Exception as e:
        logger.error(f"Error using dmeta: {e}", exc_info=True)

    return False
