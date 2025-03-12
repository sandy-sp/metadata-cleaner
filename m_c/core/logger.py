import logging
import os
from logging.handlers import RotatingFileHandler

# Define log directory and file
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
LOG_FILE = os.path.join(LOG_DIR, "metadata_cleaner.log")
LOG_LEVEL = os.getenv("METADATA_CLEANER_LOG_LEVEL", "INFO").upper()
LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5MB max log size
LOG_BACKUP_COUNT = 3  # Keep last 3 logs

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Initialize logger
logger = logging.getLogger("metadata_cleaner")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Create handlers
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=LOG_ROTATION_SIZE, backupCount=LOG_BACKUP_COUNT
)
console_handler = logging.StreamHandler()

# Set logging format
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Attach handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def set_log_level(level: str) -> None:
    """Dynamically set log level."""
    level = level.upper()
    if level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger.setLevel(getattr(logging, level))
        for handler in logger.handlers:
            handler.setLevel(getattr(logging, level))
    else:
        logger.warning(f"Invalid log level: {level}. Using default: {LOG_LEVEL}")
