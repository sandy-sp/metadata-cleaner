import os
import subprocess
import docx
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from DOCX files.

Uses python-docx for metadata extraction and applies multiple fallback methods for metadata removal,
including 7-Zip, dmeta, and python-docx.
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

def extract_metadata(file_path: str) -> Optional[Dict[str, str]]:
    """
    Extracts metadata from a DOCX file.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata from: {file_path}")

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
        return {k: v for k, v in metadata.items() if v is not None}  # Remove empty fields

    except Exception as e:
        logger.error(f"❌ Error extracting metadata from DOCX: {e}", exc_info=True)
        return None

def remove_docx_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a DOCX file using available tools.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Removing metadata from: {file_path}")

    # Try 7-Zip first
    try:
        result = subprocess.run(
            ['7z', 'd', file_path, 'docProps/*'],
            capture_output=True, text=True, check=True
        )
        if result.returncode == 0:
            logger.info(f"✅ Metadata removed using 7-Zip: {file_path}")
            return file_path
        else:
            logger.warning("⚠️ 7-Zip failed, falling back to python-docx...")
    except FileNotFoundError:
        logger.warning("⚠️ 7-Zip is not installed, falling back to python-docx...")
    except Exception as e:
        logger.error(f"❌ 7-Zip encountered an error: {e}", exc_info=True)

    # Fall back to python-docx
    try:
        doc = docx.Document(file_path)
        core_props = doc.core_properties
        core_props.author = None
        core_props.title = None
        core_props.subject = None
        core_props.keywords = None
        core_props.last_modified_by = None
        core_props.revision = None
        core_props.created = None
        core_props.modified = None

        # Ensure output path
        output_path = output_path or file_path
        doc.save(output_path)

        logger.info(f"✅ Metadata removed using python-docx: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ Error removing metadata using python-docx: {e}", exc_info=True)

    # Fall back to dmeta
    try:
        from dmeta.functions import clear
        clear(file_path, in_place=True)
        logger.info(f"✅ Metadata removed using dmeta: {file_path}")
        return file_path
    except ImportError:
        logger.warning("⚠️ dmeta is not installed, skipping fallback method.")
    except Exception as e:
        logger.error(f"❌ dmeta encountered an error: {e}", exc_info=True)

    logger.error(f"❌ All metadata removal attempts failed for: {file_path}")
    return None
