import logging
import os
from typing import Any, Optional

"""
Logger configuration for Metadata Cleaner.

This module sets up logging for the application. Log messages are written to both
the console and a file located in the "logs" directory. It provides flexible
logging options, including custom log paths and log rotation.
"""

# Default log file name
LOG_FILE: str = "metadata_cleaner.log"

# Default log directory
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

# Default log file path
DEFAULT_LOG_PATH: str = os.path.join(LOG_DIR, LOG_FILE)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(DEFAULT_LOG_PATH),
        logging.StreamHandler()
    ]
)

# Create the main logger
logger: logging.Logger = logging.getLogger("metadata_cleaner")

def set_log_level(level_str: str) -> None:
    """
    Set the logging level for the Metadata Cleaner logger.

    Parameters:
        level_str (str): The desired logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR').
    """
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)

def set_custom_log_path(log_path: str) -> None:
    """
    Set a custom log file path.

    Parameters:
        log_path (str): Path to the custom log file.
    """
    # Remove the default file handler if it exists
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    
    # Add the new file handler with the custom path
    new_handler = logging.FileHandler(log_path)
    new_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(new_handler)

def enable_log_rotation(max_size: int = 10 * 1024 * 1024,  # 10MB
                        backup_count: int = 5) -> None:
    """
    Enable log file rotation.

    Parameters:
        max_size (int): Maximum size of the log file before rotation.
        backup_count (int): Number of backup files to keep.
    """
    from logging.handlers import RotatingFileHandler

    # Remove existing file handlers
    for handler in logger.handlers:
        if isinstance(handler, (logging.FileHandler, RotatingFileHandler)):
            logger.removeHandler(handler)

    # Add rotating file handler
    handler = RotatingFileHandler(
        DEFAULT_LOG_PATH,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

def get_current_log_path() -> str:
    """
    Get the current log file path.

    Returns:
        str: Path to the current log file.
    """
    for handler in logger.handlers:
        if isinstance(handler, (logging.FileHandler, RotatingFileHandler)):
            return handler.baseFilename
    return DEFAULT_LOG_PATH

def disable_console_logging() -> None:
    """
    Disable console logging.
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)

def enable_debug_logging() -> None:
    """
    Enable debug-level logging.
    """
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)

# Example usage:
if __name__ == "__main__":
    # Set custom log path
    set_custom_log_path("/custom/log/path.log")
    
    # Enable log rotation
    enable_log_rotation(max_size=5 * 1024 * 1024, backup_count=3)
    
    # Disable console logging
    disable_console_logging()
    
    # Enable debug logging
    enable_debug_logging()
    
    logger.info("Custom logging configuration applied.")
