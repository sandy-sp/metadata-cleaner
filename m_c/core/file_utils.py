import os
import hashlib
import logging
from typing import Optional

logger = logging.getLogger("metadata_cleaner")

def validate_file(file_path: str) -> bool:
    """Check if the file exists and is accessible."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"Not a valid file: {file_path}")
        return False
    if os.path.getsize(file_path) == 0:
        logger.error(f"Empty file: {file_path}")
        return False
    return True

def get_file_checksum(file_path: str) -> Optional[str]:
    """Generate SHA-256 checksum for file integrity verification using chunking."""
    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error generating checksum for {file_path}: {e}")
        return None

def get_safe_output_path(input_path: str, output_dir: Optional[str] = None, prefix: str = "", suffix: str = "") -> str:
    """Generate a safe output path to avoid overwriting files."""
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    output_dir = output_dir or os.path.dirname(input_path)
    output_name = f"{prefix}{name}{suffix}{ext}"
    output_path = os.path.join(output_dir, output_name)
    
    counter = 1
    while os.path.exists(output_path):
        output_name = f"{prefix}{name}{suffix}_{counter}{ext}"
        output_path = os.path.join(output_dir, output_name)
        counter += 1
    
    return output_path
