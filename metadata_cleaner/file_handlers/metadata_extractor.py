import os
import json
import importlib
from typing import Optional, Dict
from metadata_cleaner.config.settings import SUPPORTED_FORMATS
from metadata_cleaner.logs.logger import logger

"""
Universal Metadata Extractor & Remover

This module dynamically selects the appropriate metadata extraction and removal 
function based on file type. If no suitable handler is found, a warning is logged.

Improvements:
- Dynamic Importing: Uses importlib to load extractors dynamically.
- Improved Error Handling: Logs detailed errors with traceback.
- Enhanced Logging: Logs success/failure consistently.
- Proper Type Hinting: Adds clarity to return types.
"""

# Mapping file extensions to metadata extraction functions
METADATA_EXTRACTOR_MAP = {
    **{ext: "metadata_cleaner.file_handlers.image.extract_metadata" for ext in SUPPORTED_FORMATS["images"]},
    **{".pdf": "metadata_cleaner.file_handlers.document.pdf_handler.extract_metadata"},
    **{ext: "metadata_cleaner.file_handlers.document.docx_handler.extract_metadata" for ext in {".docx", ".doc"}},
    **{ext: "metadata_cleaner.file_handlers.audio.audio_handler.extract_metadata" for ext in SUPPORTED_FORMATS["audio"]},
    **{ext: "metadata_cleaner.file_handlers.video.video_handler.extract_metadata" for ext in SUPPORTED_FORMATS["videos"]},
}

# Function to dynamically import functions from their paths
def dynamic_import(path):
    module_name, function_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)

# Updated FILE_HANDLER_MAP with actual function references
FILE_HANDLER_MAP = {
    **{ext: dynamic_import("metadata_cleaner.file_handlers.image.image_handler.remove_image_metadata") for ext in SUPPORTED_FORMATS["images"]},
    **{".pdf": dynamic_import("metadata_cleaner.file_handlers.document.pdf_handler.remove_pdf_metadata")},
    **{ext: dynamic_import("metadata_cleaner.file_handlers.document.docx_handler.remove_docx_metadata") for ext in {".docx", ".doc"}},
    **{ext: dynamic_import("metadata_cleaner.file_handlers.audio.audio_handler.remove_audio_metadata") for ext in SUPPORTED_FORMATS["audio"]},
    **{ext: dynamic_import("metadata_cleaner.file_handlers.video.video_handler.remove_video_metadata") for ext in SUPPORTED_FORMATS["videos"]},
}

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
    Extract metadata from a given file based on its type.

    Args:
        file_path (str): Path to the file.

    Returns:
        Optional[Dict]: Extracted metadata as a dictionary, or None if unsupported.
    """
    if not validate_file(file_path):
        return None

    ext = os.path.splitext(file_path)[1].lower()
    extractor_module = METADATA_EXTRACTOR_MAP.get(ext)

    if not extractor_module:
        logger.warning(f"⚠️ Unsupported file type for metadata extraction: {ext}")
        return None

    try:
        module_name, function_name = extractor_module.rsplit(".", 1)
        module = importlib.import_module(module_name)
        extractor_function = getattr(module, function_name)

        logger.info(f"📂 Extracting metadata for: {file_path}")
        metadata = extractor_function(file_path)

        return metadata if metadata else {"message": "No metadata found."}

    except Exception as e:
        logger.error(f"❌ Error extracting metadata from {file_path}: {e}", exc_info=True)
        return None
