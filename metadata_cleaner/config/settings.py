import os
from typing import Dict, Set
import multiprocessing

"""
Configuration settings for Metadata Cleaner.

These settings include:
- Default output directories
- Logging configurations (with rotation support)
- Supported file formats, grouped by category
- Parallel processing controls
- Environment-based configuration overrides
"""

# Default output directory for cleaned files
DEFAULT_OUTPUT_FOLDER: str = os.getenv("METADATA_CLEANER_OUTPUT_DIR", "cleaned")

# Enable or disable parallel processing (default: enabled)
def str_to_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}

ENABLE_PARALLEL_PROCESSING: bool = str_to_bool(os.getenv("METADATA_CLEANER_PARALLEL", "True"))  # Enable parallel processing
MAX_WORKERS: int = min(int(os.getenv("METADATA_CLEANER_WORKERS", "4")), multiprocessing.cpu_count())

# Logging configuration
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
LOG_FILE: str = os.path.join(LOG_DIR, "metadata_cleaner.log")
LOG_LEVEL: str = os.getenv("METADATA_CLEANER_LOG_LEVEL", "INFO").upper()  # Options: DEBUG, INFO, WARNING, ERROR
LOG_ROTATION_SIZE: int = int(os.getenv("METADATA_CLEANER_LOG_SIZE", "10485760"))  # 10MB log rotation
LOG_BACKUP_COUNT: int = int(os.getenv("METADATA_CLEANER_LOG_BACKUPS", "5"))  # Keep last 5 log files

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Supported file formats, updated based on `file_handlers/`
SUPPORTED_FORMATS: Dict[str, Set[str]] = {
    "images": {".jpg", ".jpeg", ".png", ".tiff", ".webp", ".heic", ".bmp", ".gif"},
    "documents": {".pdf", ".docx", ".doc", ".odt", ".epub", ".csv", ".md", ".txt"},
    "audio": {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma", ".aiff"},
    "videos": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"},
}

# Flatten all supported extensions into a set for easy checking
ALL_SUPPORTED_EXTENSIONS: Set[str] = {ext for exts in SUPPORTED_FORMATS.values() for ext in exts}

# Function to validate supported formats
def validate_supported_formats() -> None:
    """Ensures that all file extensions are lowercase and correctly formatted."""
    for category, extensions in SUPPORTED_FORMATS.items():
        assert all(ext.startswith(".") for ext in extensions), f"Invalid format in {category}: {extensions}"
        assert all(ext.lower() == ext for ext in extensions), f"Extensions should be lowercase in {category}: {extensions}"

# Run validation on startup
validate_supported_formats()
