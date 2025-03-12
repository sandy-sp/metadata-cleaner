import os
import logging

"""
Configuration settings for Metadata Cleaner.

These settings include:
- Default output directories
- Logging configurations
- Supported file formats
- Parallel processing settings
"""

def get_env_variable(var_name, default, cast_type=str):
    """Retrieve environment variable and cast it to the appropriate type."""
    value = os.getenv(var_name, default)
    try:
        return cast_type(value)
    except ValueError:
        logging.warning(f"Invalid value for {var_name}. Using default: {default}")
        return default

# Default output directory for cleaned files
DEFAULT_OUTPUT_FOLDER = get_env_variable("METADATA_CLEANER_OUTPUT_DIR", "cleaned_files")

# Logging configuration
LOG_LEVEL = get_env_variable("METADATA_CLEANER_LOG_LEVEL", "INFO").upper()

# Supported file formats
SUPPORTED_FORMATS = {
    "images": {".jpg", ".jpeg", ".png", ".tiff", ".webp"},
    "documents": {".pdf", ".docx", ".txt"},
    "audio": {".mp3", ".wav", ".flac"},
    "videos": {".mp4", ".mkv", ".avi"},
}

# Parallel processing settings
ENABLE_PARALLEL_PROCESSING = get_env_variable("METADATA_CLEANER_PARALLEL", "True", str).lower() in {"true", "1", "yes"}
MAX_WORKERS = get_env_variable("METADATA_CLEANER_WORKERS", 4, int)
