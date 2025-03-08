import os
import shutil
from typing import Optional

"""
Utility functions for file handling and metadata processing.

This module provides helper functions to manage output directories,
copy files while ensuring metadata removal, and retrieve file extensions.
"""

def ensure_output_folder(output_folder: str) -> None:
    """
    Ensure that the output folder exists. If it does not, create it.

    Parameters:
        output_folder (str): The path to the output folder.
    """
    os.makedirs(output_folder, exist_ok=True)

def copy_file_without_metadata(original_path: str, output_path: str) -> Optional[str]:
    """
    Copy a file to a new location while ensuring metadata is stripped.

    Parameters:
        original_path (str): Path to the original file.
        output_path (str): Destination path for the copied file.

    Returns:
        Optional[str]: The output path if the file was successfully copied; otherwise, None.
    """
    try:
        shutil.copy2(original_path, output_path)  # Ensures timestamps and permissions are preserved
        return output_path
    except Exception as e:
        print(f"❌ Error copying file {original_path} to {output_path}: {e}")
        return None

def get_file_extension(file_path: str) -> str:
    """
    Return the lowercase file extension of the given file.

    Parameters:
        file_path (str): The file path.

    Returns:
        str: The file extension in lowercase (e.g., '.jpg').
    """
    return os.path.splitext(file_path)[1].lower()
