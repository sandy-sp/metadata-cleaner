import os
import json
import shutil
import hashlib
from typing import Optional, Dict, Any
from functools import lru_cache
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.config.settings import SUPPORTED_FORMATS, ALL_SUPPORTED_EXTENSIONS

"""
Core utility functions for file handling and metadata processing.

This module provides essential helper functions for:
- File operations and validation
- Metadata backup and restoration
- Checksum verification
- Path handling and validation
"""

def validate_file_path(file_path: str) -> bool:
    """
    Validate that the file path exists and is accessible.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if the file is valid and accessible, False otherwise.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return False
        if not os.path.isfile(file_path):
            logger.error(f"❌ Not a file: {file_path}")
            return False
        if not os.access(file_path, os.R_OK):
            logger.error(f"❌ No read permission for file: {file_path}")
            return False
        if os.path.getsize(file_path) == 0:
            logger.error(f"❌ Empty file: {file_path}")
            return False
        return True
    except Exception as e:
        logger.error(f"❌ Error validating file path: {e}", exc_info=True)
        return False

def ensure_output_folder(output_folder: str) -> bool:
    """
    Ensure that the output folder exists and is writable.

    Args:
        output_folder (str): The path to the output folder.

    Returns:
        bool: True if the folder is ready for writing, False otherwise.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)
        if not os.access(output_folder, os.W_OK):
            logger.error(f"❌ No write permission for folder: {output_folder}")
            return False
        return True
    except Exception as e:
        logger.error(f"❌ Error creating output folder: {e}", exc_info=True)
        return False

@lru_cache(maxsize=1000)
def get_file_extension(file_path: str) -> str:
    """
    Return the lowercase file extension of the given file.

    Args:
        file_path (str): The file path.

    Returns:
        str: The file extension in lowercase (e.g., '.jpg').
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALL_SUPPORTED_EXTENSIONS:
        logger.warning(f"⚠️ Unsupported file format detected: {ext}")
    return ext

def verify_file_integrity(original_path: str, processed_path: str) -> bool:
    """
    Verify file integrity using SHA-256 checksums.

    Args:
        original_path (str): Path to the original file.
        processed_path (str): Path to the processed file.

    Returns:
        bool: True if files match (excluding metadata), False otherwise.
    """
    def get_file_hash(file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"❌ Error calculating hash for {file_path}: {e}", exc_info=True)
            return ""

    original_hash = get_file_hash(original_path)
    processed_hash = get_file_hash(processed_path)

    return original_hash == processed_hash if original_hash and processed_hash else False

def backup_metadata(file_path: str) -> Optional[str]:
    """
    Create a backup of the original metadata.

    Args:
        file_path (str): Path to the file.

    Returns:
        Optional[str]: Path to the backup file if successful, None otherwise.
    """
    if not validate_file_path(file_path):
        return None

    backup_path = f"{file_path}.metadata.bak"
    try:
        from metadata_cleaner.file_handlers.metadata_extractor import extract_metadata
        metadata = extract_metadata(file_path)
        if metadata:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ Metadata backup created: {backup_path}")
            return backup_path
    except Exception as e:
        logger.error(f"❌ Failed to backup metadata: {e}", exc_info=True)
    return None

def restore_metadata_from_backup(file_path: str, backup_path: str) -> bool:
    """
    Restore metadata from a backup file.

    Args:
        file_path (str): Path to the target file.
        backup_path (str): Path to the backup file.

    Returns:
        bool: True if restoration was successful, False otherwise.
    """
    if not all(validate_file_path(p) for p in [file_path, backup_path]):
        return False

    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        from metadata_cleaner.file_handlers.metadata_extractor import apply_metadata
        return apply_metadata(file_path, metadata)
    except Exception as e:
        logger.error(f"❌ Failed to restore metadata: {e}", exc_info=True)
        return False

def get_safe_output_path(input_path: str, output_dir: Optional[str] = None, 
                         prefix: str = "", suffix: str = "") -> str:
    """
    Generate a safe output path that doesn't overwrite existing files.

    Args:
        input_path (str): Original file path.
        output_dir (Optional[str]): Output directory. If None, use input directory.
        prefix (str): Prefix for output filename.
        suffix (str): Suffix for output filename (before extension).

    Returns:
        str: Safe output path.
    """
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

def cleanup_temp_files(temp_files: list) -> None:
    """
    Safely clean up temporary files.

    Args:
        temp_files (list): List of temporary file paths to remove.
    """
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.debug(f"🗑 Removed temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to remove temporary file {temp_file}: {e}")

