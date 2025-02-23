import logging
import os
from typing import Any

"""
Logger configuration for Metadata Cleaner.

This module sets up logging for the application. Log messages are written both
to the console and to a file located in the "logs" directory.
"""

LOG_FILE: str = "metadata_cleaner.log"

# Ensure that the logs directory exists
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH: str = os.path.join(LOG_DIR, LOG_FILE)

# Configure logging: messages will be output to both a file and the console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

logger: logging.Logger = logging.getLogger("metadata_cleaner")

def set_log_level(level_str: str) -> None:
    """
    Set the logging level for the Metadata Cleaner logger.

    Parameters:
        level_str (str): The desired logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR').
    """
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)
