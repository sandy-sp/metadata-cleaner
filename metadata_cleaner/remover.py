import os
import json
import concurrent.futures
from typing import List, Optional, Dict
from tqdm import tqdm
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.config.settings import SUPPORTED_FORMATS, ENABLE_PARALLEL_PROCESSING
from metadata_cleaner.core.metadata_filter import load_filter_rules
from metadata_cleaner.file_handlers.metadata_extractor import extract_metadata
from metadata_cleaner.file_handlers.metadata_extractor import METADATA_EXTRACTOR_MAP
from metadata_cleaner.file_handlers.metadata_extractor import FILE_HANDLER_MAP

"""
Metadata Cleaner - Core Remover

This module:
- Dynamically extracts and removes metadata from files.
- Supports dry-run mode for simulation.
- Handles batch folder processing with parallel execution.
"""

def load_metadata_config(config_file: Optional[str]) -> Dict:
    """Loads metadata filtering configuration from a JSON file."""
    metadata_config = {}
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                metadata_config = json.load(f)
            logger.info(f"✅ Loaded metadata config from {config_file}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"❌ Error reading config file {config_file}: {e}")
    return metadata_config

def dry_run_metadata_removal(file_path: str) -> Optional[Dict]:
    """Simulates metadata removal without modifying the file."""
    original_metadata = extract_metadata(file_path)
    if not original_metadata:
        return {"message": "No metadata found before removal."}

    simulated_clean_file = remove_metadata(file_path, output_folder=None, dry_run=True)
    cleaned_metadata = extract_metadata(simulated_clean_file) if simulated_clean_file else {}

    return {
        "before_removal": original_metadata,
        "after_removal": cleaned_metadata if cleaned_metadata else {"message": "Metadata successfully removed."}
    }

def remove_metadata(file_path: str, output_folder: Optional[str] = None, config_file: Optional[str] = None) -> Optional[str]:
    """
    Removes metadata from a single file.

    Args:
        file_path (str): Path to the file.
        output_folder (Optional[str]): Directory to save cleaned file.
        config_file (Optional[str]): Path to metadata filtering config file.

    Returns:
        Optional[str]: Path to the cleaned file if successful, else None.
    """
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].lower()
    remover_function = FILE_HANDLER_MAP.get(ext)

    if not remover_function:
        logger.warning(f"⚠️ Unsupported file type for metadata removal: {ext}")
        return None

    if output_folder is None:
        output_folder = os.path.join(os.path.dirname(file_path), "cleaned_files")
    
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, os.path.basename(file_path))

    try:
        cleaned_file = remover_function(file_path, output_path)
        if cleaned_file and os.path.exists(cleaned_file):
            logger.info(f"✅ Metadata removed successfully: {cleaned_file}")
            return cleaned_file
        else:
            logger.error(f"❌ Failed to remove metadata from: {file_path}")
            return None
    except Exception as e:
        logger.error(f"❌ Error processing file {file_path}: {e}", exc_info=True)
        return None

def remove_metadata_from_folder(folder_path: str, output_folder: Optional[str] = None, recursive: bool = False) -> List[str]:
    """
    Removes metadata from all supported files in a folder.

    Args:
        folder_path (str): Folder containing files.
        output_folder (Optional[str]): Destination folder.
        recursive (bool): Whether to process subfolders recursively.

    Returns:
        List[str]: Paths to successfully cleaned files.
    """
    if not os.path.exists(folder_path):
        logger.error(f"❌ Folder not found: {folder_path}")
        return []

    output_folder = output_folder or os.path.join(folder_path, "cleaned")
    os.makedirs(output_folder, exist_ok=True)

    files_to_process = []
    for root, _, files in os.walk(folder_path) if recursive else [(folder_path, [], os.listdir(folder_path))]:
        for f in files:
            file_path = os.path.join(root, f)
            if os.path.isfile(file_path) and os.path.splitext(f)[1].lower() in FILE_HANDLER_MAP:
                files_to_process.append(file_path)

    processed_files = []
    failed_files = []

    with tqdm(total=len(files_to_process), desc="Processing Files", unit="file") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4 if ENABLE_PARALLEL_PROCESSING else 1) as executor:
            future_to_file = {executor.submit(remove_metadata, file_path, output_folder): file_path for file_path in files_to_process}

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result and os.path.exists(result):
                        processed_files.append(result)
                    else:
                        failed_files.append(file_path)
                        logger.error(f"❌ Failed to process file: {file_path}")
                except Exception as e:
                    failed_files.append(file_path)
                    logger.error(f"❌ Error processing file {file_path}: {e}")
                pbar.update(1)

    logger.info("\n📊 Summary Report:")
    logger.info(f"✅ Successfully processed: {len(processed_files)} files")
    if failed_files:
        logger.warning(f"❌ Failed to process: {len(failed_files)} files")
        for file in failed_files:
            logger.warning(f"  - {file}")

    return processed_files
