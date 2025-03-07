import os
import json
from typing import Optional, Dict
from metadata_cleaner.file_handlers.image_handler import extract_image_metadata
from metadata_cleaner.file_handlers.pdf_handler import extract_pdf_metadata
from metadata_cleaner.file_handlers.docx_handler import extract_docx_metadata
from metadata_cleaner.file_handlers.audio_handler import extract_audio_metadata
from metadata_cleaner.file_handlers.video_handler import extract_video_metadata
from metadata_cleaner.config.settings import SUPPORTED_FORMATS
from metadata_cleaner.logs.logger import logger

# Mapping file extensions to metadata extraction functions
METADATA_EXTRACTOR_MAP = {
    **{ext: extract_image_metadata for ext in SUPPORTED_FORMATS["images"]},
    **{ext: extract_pdf_metadata for ext in SUPPORTED_FORMATS["documents"] if ext == ".pdf"},
    **{ext: extract_docx_metadata for ext in SUPPORTED_FORMATS["documents"] if ext in {".docx", ".doc"}},
    **{ext: extract_audio_metadata for ext in SUPPORTED_FORMATS["audio"]},
    **{ext: extract_video_metadata for ext in SUPPORTED_FORMATS["videos"]},
}

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a given file based on its type.

    Args:
        file_path (str): Path to the file.

    Returns:
        Optional[Dict]: Extracted metadata as a dictionary, or None if unsupported.
    """
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in METADATA_EXTRACTOR_MAP:
        logger.warning(f"⚠️ Unsupported file type for metadata extraction: {ext}")
        return None

    logger.info(f"Extracting metadata for: {file_path}")
    extractor_function = METADATA_EXTRACTOR_MAP[ext]

    try:
        metadata = extractor_function(file_path)
        return metadata if metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"❌ Error extracting metadata from {file_path}: {e}", exc_info=True)
        return None
