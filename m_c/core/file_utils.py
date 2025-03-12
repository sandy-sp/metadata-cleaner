import os
import hashlib
from typing import Optional
from metadata_cleaner.core.logger import logger

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
    """Generate SHA-256 checksum for file integrity verification."""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error generating checksum for {file_path}: {e}")
        return None

def get_safe_output_path(input_path: str, output_dir: Optional[str] = None, prefix: str = "", suffix: str = "") -> str:
    """Generate a safe output path to avoid overwriting files."""
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    output_name = f"{prefix}{name}{suffix}{ext}"
    output_path = os.path.join(output_dir, output_name)
    
    counter = 1
    while os.path.exists(output_path):
        output_name = f"{prefix}{name}{suffix}_{counter}{ext}"
        output_path = os.path.join(output_dir, output_name)
        counter += 1
    
    return output_path
