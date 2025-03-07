import os
import json
import concurrent.futures
from typing import List, Optional, Dict
from tqdm import tqdm
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.config.settings import SUPPORTED_FORMATS
from metadata_cleaner.file_handlers.image_handler import extract_image_metadata, remove_image_metadata
from metadata_cleaner.file_handlers.pdf_handler import extract_pdf_metadata, remove_pdf_metadata
from metadata_cleaner.file_handlers.docx_handler import extract_docx_metadata, remove_docx_metadata
from metadata_cleaner.file_handlers.audio_handler import extract_audio_metadata, remove_audio_metadata
from metadata_cleaner.file_handlers.video_handler import extract_video_metadata, remove_video_metadata

# Mapping file extensions to metadata extraction functions
METADATA_EXTRACTOR_MAP = {
    **{ext: extract_image_metadata for ext in SUPPORTED_FORMATS["images"]},
    **{ext: extract_pdf_metadata for ext in SUPPORTED_FORMATS["documents"] if ext == ".pdf"},
    **{ext: extract_docx_metadata for ext in SUPPORTED_FORMATS["documents"] if ext in {".docx", ".doc"}},
    **{ext: extract_audio_metadata for ext in SUPPORTED_FORMATS["audio"]},
    **{ext: extract_video_metadata for ext in SUPPORTED_FORMATS["videos"]},
}

FILE_HANDLER_MAP = {
    **{ext: remove_image_metadata for ext in SUPPORTED_FORMATS["images"]},
    **{ext: remove_pdf_metadata for ext in SUPPORTED_FORMATS["documents"] if ext == ".pdf"},
    **{ext: remove_docx_metadata for ext in SUPPORTED_FORMATS["documents"] if ext in {".docx", ".doc"}},
    **{ext: remove_audio_metadata for ext in SUPPORTED_FORMATS["audio"]},
    **{ext: remove_video_metadata for ext in SUPPORTED_FORMATS["videos"]},
}

def load_metadata_config(config_file: Optional[str]) -> Dict:
    """
    Loads metadata filtering configuration from a JSON file.

    Args:
        config_file (Optional[str]): Path to JSON config file.

    Returns:
        Dict: Parsed metadata filtering rules.
    """
    metadata_config = {}
    if config_file:
        try:
            with open(config_file, 'r') as f:
                metadata_config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading config file {config_file}: {e}")
    return metadata_config


def extract_metadata(file_path: str) -> Optional[Dict]:
    """
    Extracts metadata from a given file based on its type.

    Args:
        file_path (str): Path to the file.

    Returns:
        Optional[Dict]: Extracted metadata as a dictionary, or None if unsupported.
    """
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in METADATA_EXTRACTOR_MAP:
        logger.warning(f"⚠️ Unsupported file type for metadata extraction: {ext}")
        return None

    logger.info(f"Extracting metadata for: {file_path}")
    extractor_function = METADATA_EXTRACTOR_MAP[ext]

    try:
        metadata = extractor_function(file_path)
        return metadata if metadata else {"message": "No metadata found."}
    except Exception as e:
        logger.error(f"❌ Error extracting metadata from {file_path}: {e}", exc_info=True)
        return None

def dry_run_metadata_removal(file_path: str) -> Optional[Dict]:
    """
    Simulates metadata removal without modifying the file.

    Args:
        file_path (str): Path to the file.

    Returns:
        Optional[Dict]: Metadata differences before and after simulated removal.
    """
    original_metadata = extract_metadata(file_path)
    if not original_metadata:
        return {"message": "No metadata found before removal."}
    
    simulated_clean_file = remove_metadata(file_path, output_folder=None, dry_run=True)
    cleaned_metadata = extract_metadata(simulated_clean_file) if simulated_clean_file else {}
    
    return {
        "before_removal": original_metadata,
        "after_removal": cleaned_metadata if cleaned_metadata else {"message": "Metadata successfully removed."}
    }

def remove_metadata(file_path: str, output_folder: Optional[str] = None, dry_run: bool = False) -> Optional[str]:
    """
    Remove metadata from a single file with dry-run support.

    Args:
        file_path (str): Path to the file to be processed.
        output_folder (Optional[str]): Destination folder for cleaned file.
        dry_run (bool): If True, simulate metadata removal without modifying the file.

    Returns:
        Optional[str]: The path to the cleaned file if successful, else None.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in FILE_HANDLER_MAP:
        logger.warning(f"Unsupported file type: {ext}")
        return None

    logger.info(f"Processing file: {file_path}")
    remover_function = FILE_HANDLER_MAP[ext]

    try:
        if dry_run:
            logger.info(f"Dry-run mode: Simulating metadata removal for {file_path}")
            return file_path  # Return the same file path as a placeholder

        cleaned_file = remover_function(file_path, output_folder)
        if cleaned_file and os.path.exists(cleaned_file):
            logger.info(f"✅ Metadata removed successfully: {cleaned_file}")
            return cleaned_file
        else:
            logger.error(f"❌ Failed to process file: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
        return None

def remove_metadata_from_folder(folder_path: str,
                                output_folder: Optional[str] = None,
                                config_file: Optional[str] = None,
                                recursive: bool = False,
                                prefix: Optional[str] = None,
                                suffix: Optional[str] = None) -> List[str]:
    """
    Remove metadata from all supported files within a folder.

    Args:
        folder_path (str): Path to the folder containing files.
        output_folder (Optional[str]): Destination folder for cleaned files.
        config_file (Optional[str]): Path to metadata filtering config file.
        recursive (bool): If True, process files in subfolders recursively.
        prefix (Optional[str]): Custom prefix for cleaned file names.
        suffix (Optional[str]): Custom suffix for cleaned file names.

    Returns:
        List[str]: A list of successfully cleaned file paths.
    """
    if not os.path.exists(folder_path):
        logger.error(f"❌ Folder not found: {folder_path}")
        return []

    output_folder = output_folder or os.path.join(folder_path, "cleaned")
    os.makedirs(output_folder, exist_ok=True)

    files_to_process = []
    for root, _, files in os.walk(folder_path) if recursive else [(folder_path, [], os.listdir(folder_path))]:
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in FILE_HANDLER_MAP:
                files_to_process.append(file_path)

    processed_files = []
    failed_files = []

    with tqdm(total=len(files_to_process), desc="Processing Files", unit="file") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {
                executor.submit(remove_metadata, file_path, output_folder): file_path
                for file_path in files_to_process
            }

            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                if result:
                    processed_files.append(result)
                else:
                    failed_files.append(future_to_file[future])
                pbar.update(1)

    logger.info("\n📊 Summary Report:")
    logger.info(f"✅ Successfully processed: {len(processed_files)} files")
    if failed_files:
        logger.warning(f"❌ Failed to process: {len(failed_files)} files")
        for file in failed_files:
            logger.warning(f"  - {file}")

    return processed_files
