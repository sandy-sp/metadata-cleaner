import os

# 🏠 Default output directory
DEFAULT_OUTPUT_FOLDER = "cleaned"

# 🛠 Enable or Disable Parallel Processing
ENABLE_PARALLEL_PROCESSING = True

# 📝 Logging Configuration
LOG_FILE_PATH = os.path.join("logs", "metadata_cleaner.log")
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

# 🔧 Supported File Formats
SUPPORTED_FORMATS = {
    "images": [".jpg", ".jpeg", ".png", ".tiff"],
    "documents": [".pdf", ".docx", ".doc"],
    "audio": [".mp3", ".wav", ".flac", ".ogg"],
    "videos": [".mp4", ".mkv", ".mov", ".avi"]
}
