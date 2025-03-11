import os
from typing import Optional, Dict
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting metadata from video files using Hachoir.

Hachoir is a lightweight alternative for metadata extraction.
⚠️ NOTE: Hachoir **cannot remove metadata**—only extracts it.
"""

def validate_file(file_path: str) -> bool:
    """Centralized file validation."""
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"❌ Not a valid file: {file_path}")
        return False
    return True

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a video file using Hachoir.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using Hachoir: {file_path}")

    try:
        parser = createParser(file_path)
        if not parser:
            logger.error(f"❌ Failed to create parser for {file_path}")
            return None

        metadata = extractMetadata(parser)
        if not metadata:
            logger.error(f"❌ Failed to extract metadata for {file_path}")
            return None

        return {item.key: item.value for item in metadata.exportPlaintext()} if metadata else {}
    except Exception as e:
        logger.error(f"❌ Hachoir failed to extract metadata: {e}", exc_info=True)
        return None
