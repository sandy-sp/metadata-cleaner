import logging
import os

LOG_FILE = "metadata_cleaner.log"

# Ensure logs directory exists
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("metadata_cleaner")

def set_log_level(level_str):
    """
    Set the logging level based on the provided level string.
    """
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)
