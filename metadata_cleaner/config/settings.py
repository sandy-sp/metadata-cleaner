import os
from typing import Dict, Set

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
ENABLE_PARALLEL_PROCESSING: bool = os.getenv("METADATA_CLEANER_PARALLEL", "True").lower() in ("true", "1", "yes")
MAX_WORKERS: int = int(os.getenv("METADATA_CLEANER_WORKERS", "4"))  # Limit parallel workers

# Logging configuration
LOG_DIR: str = os.getenv("METADATA_CLEANER_LOG_DIR", "logs")
LOG_FILE: str = os.path.join(LOG_DIR, "metadata_cleaner.log")
LOG_LEVEL: str = os.getenv("METADATA_CLEANER_LOG_LEVEL", "INFO")  # Options: DEBUG, INFO, WARNING, ERROR
LOG_ROTATION_SIZE: int = int(os.getenv("METADATA_CLEANER_LOG_SIZE", "10485760"))  # 10MB log rotation
LOG_BACKUP_COUNT: int = int(os.getenv("METADATA_CLEANER_LOG_BACKUPS", "5"))  # Keep last 5 log files

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Supported file formats, organized by file category
SUPPORTED_FORMATS: Dict[str, Set[str]] = {
    "images": {".jpg", ".jpeg", ".png", ".tiff", ".webp", ".heic"},
    "documents": {".pdf", ".docx", ".doc", ".odt", ".epub"},
    "audio": {".mp3", ".wav", ".flac", ".ogg", ".aac"},
    "videos": {".mp4", ".mkv", ".mov", ".avi", ".webm"},
}

# Flatten all supported extensions into a set for easy checking
ALL_SUPPORTED_EXTENSIONS: Set[str] = {ext for exts in SUPPORTED_FORMATS.values() for ext in exts}
