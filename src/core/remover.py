import os
from src.file_handlers.image_handler import remove_image_metadata
from src.file_handlers.pdf_handler import remove_pdf_metadata
from src.file_handlers.docx_handler import remove_docx_metadata
from src.file_handlers.audio_handler import remove_audio_metadata
from src.file_handlers.video_handler import remove_video_metadata

def remove_metadata(file_path, output_path=None):
    """Detects file type and removes metadata accordingly."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file type based on extension
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.jpg', '.jpeg', '.png', '.tiff']:
        return remove_image_metadata(file_path, output_path)
    
    elif ext == '.pdf':
        return remove_pdf_metadata(file_path, output_path)
    
    elif ext in ['.docx', '.doc']:
        return remove_docx_metadata(file_path, output_path)
    
    elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
        return remove_audio_metadata(file_path, output_path)
    
    elif ext in ['.mp4', '.mkv', '.mov', '.avi']:
        return remove_video_metadata(file_path, output_path)

    else:
        raise ValueError("Unsupported file type!")

