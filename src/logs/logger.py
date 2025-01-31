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
        logging.FileHandler(LOG_PATH),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger("metadata_cleaner")
