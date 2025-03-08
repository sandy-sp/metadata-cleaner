import os
from typing import Optional, Dict
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting metadata from video files using Hachoir.

Provides a lightweight alternative for metadata extraction but does not support metadata removal.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a video file using Hachoir.

    Parameters:
        file_path (str): Path to the video file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        parser = createParser(file_path)
        if not parser:
            logger.error(f"Failed to create parser for {file_path}")
            return None
        
        metadata = extractMetadata(parser)
        if not metadata:
            logger.error(f"Failed to extract metadata for {file_path}")
            return None
        
        return {item.key: item.value for item in metadata.exportPlaintext()} if metadata else {}
    except Exception as e:
        logger.error(f"Error extracting metadata using Hachoir: {e}", exc_info=True)
        return None
