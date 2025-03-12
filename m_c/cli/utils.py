import json
from m_c.core.logger import logger

def format_metadata_output(metadata):
    """Formats metadata output for CLI display with error handling."""
    try:
        if metadata:
            return json.dumps(metadata, indent=4)
        return "No metadata found or unsupported file format."
    except (TypeError, ValueError) as e:
        logger.error(f"Error formatting metadata output: {e}")
        return "Error occurred while formatting metadata output."
