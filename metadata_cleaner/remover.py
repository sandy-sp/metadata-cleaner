import os
import concurrent.futures
import json
from typing import List, Optional, Dict, Any
from tqdm import tqdm
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.file_handlers.image_handler import remove_image_metadata
from metadata_cleaner.file_handlers.pdf_handler import remove_pdf_metadata
from metadata_cleaner.file_handlers.docx_handler import remove_docx_metadata
from metadata_cleaner.file_handlers.audio_handler import remove_audio_metadata
from metadata_cleaner.file_handlers.video_handler import remove_video_metadata
from metadata_cleaner.config.settings import SUPPORTED_FORMATS

# Mapping of supported file extensions to their corresponding removal functions
SUPPORTED_EXTENSIONS = {
    ".jpg": remove_image_metadata,
    ".jpeg": remove_image_metadata,
    ".png": remove_image_metadata,
    ".tiff": remove_image_metadata,
    ".webp": remove_image_metadata,
    ".heic": remove_image_metadata,
    ".pdf": remove_pdf_metadata,
    ".docx": remove_docx_metadata,
    ".doc": remove_docx_metadata,
    ".mp3": remove_audio_metadata,
    ".wav": remove_audio_metadata,
    ".flac": remove_audio_metadata,
    ".ogg": remove_audio_metadata,
    ".mp4": remove_video_metadata,
    ".mkv": remove_video_metadata,
    ".mov": remove_video_metadata,
    ".avi": remove_video_metadata
}

def remove_metadata(file_path: str, 
                   output_path: Optional[str] = None, 
                   config_file: Optional[str] = None,
                   prefix: Optional[str] = None,
                   suffix: Optional[str] = None) -> Optional[str]:
    """
    Remove metadata from a single file.

    Parameters:
        file_path (str): Path to the file to be processed.
        output_path (Optional[str]): Custom output path. If None, a default naming scheme is used.
        config_file (Optional[str]): Path to a JSON configuration file for selective metadata filtering.
        prefix (Optional[str]): Custom prefix for the cleaned file name.
        suffix (Optional[str]): Custom suffix for the cleaned file name.

    Returns:
        Optional[str]: The path to the cleaned file if successful, else None.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Unsupported file type: {ext}")
            raise ValueError(f"Unsupported file type: {ext}")

        logger.info(f"Processing file: {file_path}")
        remover_function = SUPPORTED_EXTENSIONS[ext]

        # Prepare metadata configuration
        metadata_config = {}
        if config_file:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                metadata_config.update(config_data)

        # Apply CLI-specific metadata options if provided
        # (These would be passed through from the CLI)
        # Example:
        # if remove_gps:
        #     metadata_config['GPS'] = 'remove'
        # if keep_timestamp:
        #     metadata_config['Timestamp'] = 'exact'

        # Determine output path with custom naming options
        if output_path:
            base, ext = os.path.splitext(os.path.basename(file_path))
            output_filename = f"{prefix}{base}{suffix}{ext}" if prefix or suffix else f"{base}_cleaned{ext}"
            output_path = os.path.join(output_path, output_filename)
        else:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_cleaned{ext}"

        # For image files, pass along the config for selective filtering.
        if ext in [".jpg", ".jpeg", ".png", ".tiff", ".webp", ".heic"]:
            cleaned_file = remover_function(file_path, output_path, metadata_config)
        else:
            cleaned_file = remover_function(file_path, output_path)

        if cleaned_file and os.path.exists(cleaned_file):
            logger.info(f"Metadata removed successfully: {cleaned_file}")
            return cleaned_file
        else:
            logger.error(f"Failed to process file: {file_path}")
            return None

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
        return None

def process_file(file_path: str,
                output_folder: str,
                config_file: Optional[str] = None,
                prefix: Optional[str] = None,
                suffix: Optional[str] = None) -> Optional[str]:
    """
    Process a single file and remove its metadata.

    Parameters:
        file_path (str): Path to the file.
        output_folder (str): Folder where the cleaned file will be saved.
        config_file (Optional[str]): Configuration file for metadata filtering (for images).
        prefix (Optional[str]): Custom prefix for the cleaned file name.
        suffix (Optional[str]): Custom suffix for the cleaned file name.

    Returns:
        Optional[str]: The path to the cleaned file if successful, else None.
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            # Prepare metadata configuration
            metadata_config = {}
            if config_file:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    metadata_config.update(config_data)

            # Determine output path with custom naming options
            base, ext = os.path.splitext(os.path.basename(file_path))
            output_filename = f"{prefix}{base}{suffix}{ext}" if prefix or suffix else f"{base}_cleaned{ext}"
            output_path = os.path.join(output_folder, output_filename)

            remover_function = SUPPORTED_EXTENSIONS[ext]
            if ext in [".jpg", ".jpeg", ".png", ".tiff", ".webp", ".heic"]:
                cleaned_file = remover_function(file_path, output_path, metadata_config)
            else:
                cleaned_file = remover_function(file_path, output_path)

            if cleaned_file and os.path.exists(cleaned_file):
                logger.info(f"✅ Metadata removed: {cleaned_file}")
                return cleaned_file
            else:
                logger.error(f"❌ Failed to process: {file_path}")
                return None
        else:
            logger.warning(f"⚠️ Unsupported file type: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}", exc_info=True)
        return None

def remove_metadata_from_folder(folder_path: str,
                                  output_folder: Optional[str] = None,
                                  config_file: Optional[str] = None,
                                  recursive: bool = False,
                                  prefix: Optional[str] = None,
                                  suffix: Optional[str] = None) -> List[str]:
    """
    Remove metadata from all supported files within a folder.

    Parameters:
        folder_path (str): Path to the folder containing files.
        output_folder (Optional[str]): Folder to save cleaned files. If None, a 'cleaned' subfolder is created.
        config_file (Optional[str]): Configuration file for selective metadata filtering (applied to images).
        recursive (bool): If True, process files in subfolders recursively.
        prefix (Optional[str]): Custom prefix for cleaned file names.
        suffix (Optional[str]): Custom suffix for cleaned file names.

    Returns:
        List[str]: A list of paths to successfully cleaned files.
    """
    if not os.path.exists(folder_path):
        logger.error(f"❌ Folder not found: {folder_path}")
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not output_folder:
        output_folder = os.path.join(folder_path, "cleaned")
    os.makedirs(output_folder, exist_ok=True)

    files_to_process = []
    if recursive:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    files_to_process.append(file_path)
    else:
        # Process only files in the immediate folder
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    files_to_process.append(file_path)

    processed_files: List[str] = []
    failed_files: List[str] = []

    with tqdm(total=len(files_to_process), desc="Processing Files", unit="file") as pbar:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_file = {
                executor.submit(process_file, file_path, output_folder, config_file, prefix, suffix): file_path
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
    logger.info(f"❌ Failed to process: {len(failed_files)} files")
    if failed_files:
        logger.info("⚠️ Failed Files:")
        for file in failed_files:
            logger.info(f"  - {file}")

    return processed_files
