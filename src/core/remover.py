import os
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
    """Removes metadata from a single file."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        logger.warning(f"Unsupported file type: {ext}")
        raise ValueError(f"Unsupported file type: {ext}")

    logger.info(f"Processing file: {file_path}")
    remover_function = SUPPORTED_EXTENSIONS[ext]
    
    try:
        cleaned_file = remover_function(file_path, output_path)
        logger.info(f"Metadata removed successfully: {cleaned_file}")
        return cleaned_file
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        raise

def remove_metadata_from_folder(folder_path, output_folder=None):
    """Removes metadata from all supported files in a folder."""
    if not os.path.exists(folder_path):
        logger.error(f"Folder not found: {folder_path}")
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    processed_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            if ext in SUPPORTED_EXTENSIONS:
                output_path = os.path.join(output_folder, file) if output_folder else None
                try:
                    cleaned_file = remove_metadata(file_path, output_path)
                    processed_files.append(cleaned_file)
                except Exception as e:
                    logger.error(f"Skipping {file}: {e}")

    return processed_files
