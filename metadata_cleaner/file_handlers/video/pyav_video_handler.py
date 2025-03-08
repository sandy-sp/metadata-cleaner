import os
import av
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from video files using PyAV.

Provides an alternative method for metadata operations when FFmpeg is unavailable.
"""

def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a video file using PyAV.

    Parameters:
        file_path (str): Path to the video file.

    Returns:
        Optional[Dict]: Extracted metadata, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        container = av.open(file_path)
        metadata = {
            "format": container.format.name,
            "duration": container.duration / av.time_base if container.duration else None,
            "metadata": dict(container.metadata),
        }
        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata using PyAV: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> bool:
    """
    Remove metadata from a video file using PyAV.

    Parameters:
        file_path (str): Path to the video file.
        output_path (Optional[str]): Destination path for the cleaned video.
                                     If None, overwrites the original file.

    Returns:
        bool: True if metadata removal is successful, False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    try:
        if not output_path:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_cleaned{ext}"
        
        input_container = av.open(file_path)
        output_container = av.open(output_path, mode='w', format=input_container.format.name)
        
        for stream in input_container.streams:
            output_container.add_stream(template=stream)
        
        for packet in input_container.demux():
            output_container.mux(packet)
        
        output_container.metadata.clear()
        output_container.close()
        
        logger.info(f"Metadata removed successfully using PyAV: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error removing metadata using PyAV: {e}", exc_info=True)
        return False
