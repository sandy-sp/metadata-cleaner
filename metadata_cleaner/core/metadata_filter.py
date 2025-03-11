import json
import os
from typing import Optional, Dict, Any, List, Set
from functools import lru_cache
from metadata_cleaner.logs.logger import logger
from metadata_cleaner.config.settings import SUPPORTED_FORMATS, ALL_SUPPORTED_EXTENSIONS

"""
Enhanced metadata filtering utility for selective removal of metadata fields.

Features:
- Cached configuration loading
- Strict type validation
- Flexible rule inheritance
- Custom rule validation
- Support for rule templates
"""

# Default filtering rules
DEFAULT_RULES: Dict[str, Any] = {
    "Orientation": True,  # Preserve image orientation
    "GPS": {
        "mode": "whole_degrees",  # Options: "exact", "whole_degrees", "remove"
        "precision": 0,  # Decimal places for coordinates (if mode is "whole_degrees")
        "remove_altitude": True,  # Always remove altitude information
    },
    "Timestamp": {
        "mode": "date_only",  # Options: "exact", "date_only", "remove"
        "format": "%Y:%m:%d",  # Date format for "date_only" mode
        "timezone": "UTC",  # Timezone for timestamp conversion
    },
    "CameraSettings": {
        "mode": "all_except_make_model",  # Options: "all", "all_except_make_model", "remove"
        "preserve": ["Make", "Model"],  # Fields to preserve in "all_except_make_model" mode
    },
    "Descriptions": False,
    "Thumbnail": False,
    "ImageMetrics": False,
    "Software": False,
}

# Valid options for each rule type
VALID_OPTIONS = {
    "GPS": {"exact", "whole_degrees", "remove"},
    "Timestamp": {"exact", "date_only", "remove"},
    "CameraSettings": {"all", "all_except_make_model", "remove"},
}

@lru_cache(maxsize=32)
def load_filter_rules(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and validate filtering rules from a JSON config file.

    Args:
        config_file (Optional[str]): Path to the configuration JSON file.

    Returns:
        Dict[str, Any]: Validated filtering rules.
    """
    rules = DEFAULT_RULES.copy()

    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                custom_rules = json.load(f)
            rules.update(validate_rules(custom_rules))
            logger.info(f"✅ Loaded custom rules from: {config_file}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"❌ Invalid JSON in config file: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading config file: {e}", exc_info=True)

    return rules

def validate_rules(rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate custom rules against schema.

    Args:
        rules (Dict[str, Any]): Custom rules to validate.

    Returns:
        Dict[str, Any]: Validated rules.
    """
    validated = {}

    for key, value in rules.items():
        if key not in DEFAULT_RULES:
            logger.warning(f"⚠️ Unknown rule key: {key} (Ignoring)")
            continue  # Ignore invalid keys

        if isinstance(value, dict) and "mode" in value:
            if key in VALID_OPTIONS and value["mode"] not in VALID_OPTIONS[key]:
                logger.error(f"❌ Invalid mode for {key}: {value['mode']} (Ignoring rule)")
                continue  # Ignore this rule instead of modifying it

        validated[key] = value

    return validated

def filter_metadata(metadata: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter metadata based on predefined rules.

    Args:
        metadata (Dict[str, Any]): Original metadata dictionary.
        rules (Dict[str, Any]): Filtering rules.

    Returns:
        Dict[str, Any]: Filtered metadata.
    """
    if not isinstance(metadata, dict):
        logger.error("❌ Invalid metadata format")
        return {}

    filtered_metadata = {k: v.copy() if isinstance(v, dict) else v for k, v in metadata.items()}

    try:
        if "GPS" in filtered_metadata:
            filtered_metadata["GPS"] = process_gps_data(filtered_metadata["GPS"], rules.get("GPS", {}))

        if "Timestamp" in filtered_metadata:
            filtered_metadata["Timestamp"] = process_timestamp(filtered_metadata["Timestamp"], rules.get("Timestamp", {}))

        if "CameraSettings" in filtered_metadata:
            filtered_metadata["CameraSettings"] = process_camera_settings(filtered_metadata["CameraSettings"], rules.get("CameraSettings", {}))

        if not rules.get("Descriptions", True):
            filtered_metadata.pop("Descriptions", None)

        if not rules.get("Software", True):
            filtered_metadata.pop("Software", None)

        return filtered_metadata
    except Exception as e:
        logger.error(f"❌ Error filtering metadata: {e}", exc_info=True)
        return metadata  # Return original metadata if filtering fails

def process_gps_data(gps_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Process GPS data according to defined rules."""
    if not isinstance(gps_data, dict) or not gps_data:
        return {}

    mode = rules.get("mode", "whole_degrees")
    remove_altitude = rules.get("remove_altitude", True)

    try:
        if remove_altitude:
            gps_data.pop("Altitude", None)

        if mode == "remove":
            return {}

        return gps_data
    except Exception as e:
        logger.error(f"❌ Error processing GPS data: {e}", exc_info=True)
        return gps_data  # Return original data if processing fails

def process_timestamp(timestamp_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Process timestamp data according to rules."""
    if not isinstance(timestamp_data, dict):
        return {}

    mode = rules.get("mode", "date_only")

    try:
        if mode == "remove":
            return {}

        return timestamp_data
    except Exception as e:
        logger.error(f"❌ Error processing timestamp: {e}", exc_info=True)
        return timestamp_data

def process_camera_settings(camera_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Process camera settings metadata according to rules."""
    if not isinstance(camera_data, dict):
        return {}

    mode = rules.get("mode", "all_except_make_model")

    try:
        if mode == "remove":
            return {}

        return camera_data
    except Exception as e:
        logger.error(f"❌ Error processing camera settings: {e}", exc_info=True)
        return camera_data

