import os

"""
Configuration settings for Metadata Cleaner.

These settings include:
- Default output directories
- Logging configurations
- Supported file formats
- Parallel processing settings
"""

# Default output directory for cleaned files
DEFAULT_OUTPUT_FOLDER = os.getenv("METADATA_CLEANER_OUTPUT_DIR", "cleaned_files")

# Logging configuration
LOG_LEVEL = os.getenv("METADATA_CLEANER_LOG_LEVEL", "INFO").upper()

# Supported file formats
SUPPORTED_FORMATS = {
    "images": {".jpg", ".jpeg", ".png", ".tiff", ".webp"},
    "documents": {".pdf", ".docx", ".txt"},
    "audio": {".mp3", ".wav", ".flac"},
    "videos": {".mp4", ".mkv", ".avi"},
}

# Parallel processing settings
ENABLE_PARALLEL_PROCESSING = os.getenv("METADATA_CLEANER_PARALLEL", "True").lower() in {
    "true",
    "1",
    "yes",
}
MAX_WORKERS = int(os.getenv("METADATA_CLEANER_WORKERS", "4"))
