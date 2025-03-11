import os
import av
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger

"""
Handler for extracting and removing metadata from video files using PyAV.

Provides an alternative method for metadata operations when FFmpeg is unavailable.
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
    Extracts metadata from a video file using PyAV.

    Returns:
        - Metadata dictionary if extraction succeeds.
        - None if extraction fails.
    """
    if not validate_file(file_path):
        return None

    logger.info(f"📂 Extracting metadata using PyAV: {file_path}")

    try:
        container = av.open(file_path)
        metadata = {
            "format": container.format.name,
            "duration": container.duration / av.time_base if container.duration else None,
            "metadata": dict(container.metadata),
        }
        return metadata
    except Exception as e:
        logger.error(f"❌ PyAV failed to extract metadata: {e}", exc_info=True)
        return None

def remove_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a video file using PyAV.

    Returns:
        - The output file path if removal succeeds.
        - None if the process fails.
    """
    if not validate_file(file_path):
        return None

    # Determine output path if not provided
    if not output_path:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_cleaned{ext}"

    logger.info(f"📂 Removing metadata using PyAV: {file_path}")

    try:
        input_container = av.open(file_path)
        output_container = av.open(output_path, mode='w', format=input_container.format.name)

        for stream in input_container.streams:
            output_container.add_stream(template=stream)

        for packet in input_container.demux():
            output_container.mux(packet)

        # Ensure metadata is cleared
        output_container.metadata.clear()
        output_container.close()

        # Verify output file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"❌ PyAV failed to create output file: {output_path}")
            return None

        logger.info(f"✅ Metadata removed successfully using PyAV: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ PyAV encountered an error: {e}", exc_info=True)
        return None
