import os
from tqdm import tqdm
from src.logs.logger import logger
from src.file_handlers.image_handler import remove_image_metadata
from src.file_handlers.pdf_handler import remove_pdf_metadata
from src.file_handlers.docx_handler import remove_docx_metadata
from src.file_handlers.audio_handler import remove_audio_metadata
from src.file_handlers.video_handler import remove_video_metadata

SUPPORTED_EXTENSIONS = {
    ".jpg": remove_image_metadata, ".jpeg": remove_image_metadata, ".png": remove_image_metadata, ".tiff": remove_image_metadata,
    ".pdf": remove_pdf_metadata,
    ".docx": remove_docx_metadata, ".doc": remove_docx_metadata,
    ".mp3": remove_audio_metadata, ".wav": remove_audio_metadata, ".flac": remove_audio_metadata, ".ogg": remove_audio_metadata,
    ".mp4": remove_video_metadata, ".mkv": remove_video_metadata, ".mov": remove_video_metadata, ".avi": remove_video_metadata
}

def remove_metadata(file_path, output_path=None):
    """Removes metadata from a single file and logs detailed errors."""
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

        cleaned_file = remover_function(file_path, output_path)

        if cleaned_file and os.path.exists(cleaned_file):
            logger.info(f"Metadata removed successfully: {cleaned_file}")
            return cleaned_file
        else:
            logger.error(f"Failed to process file: {file_path}")
            return None

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None


def remove_metadata_from_folder(folder_path, output_folder=None):
    """Removes metadata from all supported files in a folder with a progress bar and summary report."""
    if not os.path.exists(folder_path):
        logger.error(f"Folder not found: {folder_path}")
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    files_to_process = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                files_to_process.append(file_path)

    processed_files = []
    failed_files = []
    with tqdm(total=len(files_to_process), desc="Processing Files", unit="file") as pbar:
        for file_path in files_to_process:
            output_path = os.path.join(output_folder, os.path.basename(file_path)) if output_folder else None
            try:
                cleaned_file = remove_metadata(file_path, output_path)
                if cleaned_file:
                    processed_files.append(cleaned_file)
                else:
                    failed_files.append(file_path)
            except Exception as e:
                logger.error(f"Skipping {file_path}: {e}")
                failed_files.append(file_path)
            pbar.update(1)

    logger.info("\n📊 **Summary Report:**")
    logger.info(f"✅ Successfully processed: {len(processed_files)} files")
    logger.info(f"❌ Failed to process: {len(failed_files)} files")

    if failed_files:
        logger.info("\n⚠️ Failed Files:")
        for file in failed_files:
            logger.info(f"  - {file}")

    return processed_files
