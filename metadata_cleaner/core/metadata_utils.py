import os
import json
import shutil
import hashlib
from typing import Optional, Dict, Any
from functools import lru_cache
from metadata_cleaner.logs.logger import logger

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
    Validate file path exists and is accessible.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if file is valid and accessible, False otherwise.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            logger.error(f"Not a file: {file_path}")
            return False
            
        if not os.access(file_path, os.R_OK):
            logger.error(f"No read permission for file: {file_path}")
            return False
            
        if os.path.getsize(file_path) == 0:
            logger.error(f"Empty file: {file_path}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating file path: {e}")
        return False

def ensure_output_folder(output_folder: str) -> bool:
    """
    Ensure that the output folder exists and is writable.

    Args:
        output_folder (str): The path to the output folder.

    Returns:
        bool: True if folder is ready for writing, False otherwise.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)
        if not os.access(output_folder, os.W_OK):
            logger.error(f"No write permission for folder: {output_folder}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error creating output folder: {e}")
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
    return os.path.splitext(file_path)[1].lower()

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
        except FileNotFoundError:
            logger.error(f"File missing for integrity check: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""

    original_hash = get_file_hash(original_path)
    processed_hash = get_file_hash(processed_path)

    if not original_hash or not processed_hash:
        logger.error("Integrity check failed due to missing files.")
        return False  # Explicitly return False if files are missing

    return original_hash == processed_hash

def backup_metadata(file_path: str) -> Optional[str]:
    """
    Create backup of original metadata.

    Args:
        file_path (str): Path to the file.

    Returns:
        Optional[str]: Path to backup file if successful, None otherwise.
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
            logger.info(f"Metadata backup created: {backup_path}")
            return backup_path
    except Exception as e:
        logger.error(f"Failed to backup metadata: {e}")
    return None

def restore_metadata_from_backup(file_path: str, backup_path: str) -> bool:
    """
    Restore metadata from backup file.

    Args:
        file_path (str): Path to the target file.
        backup_path (str): Path to the backup file.

    Returns:
        bool: True if restoration successful, False otherwise.
    """
    if not all(validate_file_path(p) for p in [file_path, backup_path]):
        return False

    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Import here to avoid circular imports
        from metadata_cleaner.file_handlers.metadata_extractor import apply_metadata
        return apply_metadata(file_path, metadata)
    except Exception as e:
        logger.error(f"Failed to restore metadata: {e}")
        return False

def safe_copy_file(source_path: str, dest_path: str) -> bool:
    """
    Safely copy a file with error handling and verification.

    Args:
        source_path (str): Path to source file.
        dest_path (str): Path to destination file.

    Returns:
        bool: True if copy successful and verified, False otherwise.
    """
    if not validate_file_path(source_path):
        return False

    try:
        # Ensure destination directory exists
        dest_dir = os.path.dirname(dest_path)
        if not ensure_output_folder(dest_dir):
            return False

        # Copy file with metadata preservation
        shutil.copy2(source_path, dest_path)

        # Verify copy
        if not os.path.exists(dest_path):
            logger.error(f"Copy failed - destination file not found: {dest_path}")
            return False

        if os.path.getsize(source_path) != os.path.getsize(dest_path):
            logger.error(f"Copy failed - size mismatch for: {dest_path}")
            return False

        return True
    except Exception as e:
        logger.error(f"Error copying file {source_path} to {dest_path}: {e}")
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

    # Construct initial output path
    output_name = f"{prefix}{name}{suffix}{ext}"
    output_path = os.path.join(output_dir, output_name)

    # Handle file name conflicts
    counter = 1
    while os.path.exists(output_path):
        output_name = f"{prefix}{name}{suffix}_{counter}{ext}"
        output_path = os.path.join(output_dir, output_name)
        counter += 1

    return output_path

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get detailed information about a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        Dict[str, Any]: Dictionary containing file information.
    """
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'extension': get_file_extension(file_path),
            'permissions': oct(stat.st_mode)[-3:],
            'is_readable': os.access(file_path, os.R_OK),
            'is_writable': os.access(file_path, os.W_OK),
            'path': os.path.abspath(file_path),
            'filename': os.path.basename(file_path)
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {}

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
                logger.debug(f"Removed temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {temp_file}: {e}")

class FileOperation:
    """Context manager for safe file operations with cleanup."""
    
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.temp_files = []
        self.success = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.success:
            # Clean up output file if operation failed
            if os.path.exists(self.output_path):
                try:
                    os.remove(self.output_path)
                except Exception as e:
                    logger.error(f"Failed to clean up output file: {e}")
        
        # Clean up any temporary files
        cleanup_temp_files(self.temp_files)

        # Log any exceptions
        if exc_type is not None:
            logger.error(f"Error during file operation: {exc_val}")
            return False  # Re-raise the exception
        return True

def is_file_locked(file_path: str) -> bool:
    """
    Check if a file is locked or in use.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if file is locked, False otherwise.
    """
    try:
        with open(file_path, 'rb') as f:
            if os.name == 'nt':  # Windows
                import msvcrt
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:  # More specific error
                    return True
            else:  # Unix-based
                import fcntl
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except OSError:
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking file lock: {e}")
        return False  # Assume unlocked unless proven otherwise

