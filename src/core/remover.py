import os
from src.logs.logger import logger
from src.file_handlers.image_handler import remove_image_metadata
from src.file_handlers.pdf_handler import remove_pdf_metadata
from src.file_handlers.docx_handler import remove_docx_metadata
from src.file_handlers.audio_handler import remove_audio_metadata
from src.file_handlers.video_handler import remove_video_metadata

def remove_metadata(file_path, output_path=None):
    """Detects file type and removes metadata accordingly."""
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    # Determine file type based on extension
    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"Processing file: {file_path} (Type: {ext})")

    try:
        if ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            cleaned_file = remove_image_metadata(file_path, output_path)
        
        elif ext == '.pdf':
            cleaned_file = remove_pdf_metadata(file_path, output_path)
        
        elif ext in ['.docx', '.doc']:
            cleaned_file = remove_docx_metadata(file_path, output_path)
        
        elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
            cleaned_file = remove_audio_metadata(file_path, output_path)
        
        elif ext in ['.mp4', '.mkv', '.mov', '.avi']:
            cleaned_file = remove_video_metadata(file_path, output_path)
        
        else:
            logger.warning(f"Unsupported file type: {ext}")
            raise ValueError("Unsupported file type!")

        logger.info(f"Metadata removed successfully. Cleaned file saved at: {cleaned_file}")
        return cleaned_file

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        raise
