import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.getenv("METADATA_CLEANER_LOG_FILE")
LOG_LEVEL = os.getenv("METADATA_CLEANER_LOG_LEVEL", "INFO").upper()
LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5MB max log size
LOG_BACKUP_COUNT = 3  # Keep last 3 logs

# Configure logging format
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Initialize logger
logger = logging.getLogger("metadata_cleaner")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logger.propagate = False

formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if LOG_FILE:
        os.makedirs(os.path.dirname(os.path.abspath(LOG_FILE)), exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=LOG_ROTATION_SIZE, backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def set_log_level(level: str) -> None:
    """Dynamically set log level."""
    level = level.upper()
    if level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger.setLevel(getattr(logging, level))
        for handler in logger.handlers:
            handler.setLevel(getattr(logging, level))
    else:
        logger.warning(f"Invalid log level: {level}. Using default: {LOG_LEVEL}")
