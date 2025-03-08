import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

"""
Logger configuration for Metadata Cleaner.

This module sets up logging for the application. Log messages are written to both
console and a file located in the "logs" directory. It provides flexible
logging options, including log rotation and custom log levels.
"""

# Default log directory and file
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
LOG_FILE: str = os.path.join(LOG_DIR, "metadata_cleaner.log")
LOG_LEVEL: str = os.getenv("METADATA_CLEANER_LOG_LEVEL", "INFO").upper()
LOG_ROTATION_SIZE: int = int(os.getenv("METADATA_CLEANER_LOG_SIZE", "10485760"))  # 10MB log rotation
LOG_BACKUP_COUNT: int = int(os.getenv("METADATA_CLEANER_LOG_BACKUPS", "5"))  # Keep last 5 log files

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Initialize logger
logger = logging.getLogger("metadata_cleaner")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Create handlers
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_ROTATION_SIZE, backupCount=LOG_BACKUP_COUNT)
console_handler = logging.StreamHandler()

# Set logging format
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Attach handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def set_log_level(level: str) -> None:
    """Dynamically sets the log level."""
    level = level.upper()
    if level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger.setLevel(getattr(logging, level))
        for handler in logger.handlers:
            handler.setLevel(getattr(logging, level))
    else:
        logger.warning(f"Invalid log level: {level}. Using default: {LOG_LEVEL}")

def get_current_log_path() -> str:
    """Returns the current log file path."""
    return LOG_FILE

def disable_console_logging() -> None:
    """Disables logging to the console."""
    global logger
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)

def enable_debug_logging() -> None:
    """Enables debug-level logging."""
    set_log_level("DEBUG")

def enable_log_rotation(max_size: int = LOG_ROTATION_SIZE, backup_count: int = LOG_BACKUP_COUNT) -> None:
    """Enables log file rotation."""
    global logger
    for handler in logger.handlers[:]:
        if isinstance(handler, RotatingFileHandler):
            logger.removeHandler(handler)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=max_size, backupCount=backup_count)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
