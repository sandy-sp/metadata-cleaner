import json
import os
from typing import Optional, Dict, Any
from metadata_cleaner.logs.logger import logger

"""
Metadata filtering utility for selective removal of metadata fields.

This module provides functionality to load and apply metadata filtering rules.
"""

# Default filtering rules
DEFAULT_RULES: Dict[str, Any] = {
    "Orientation": True,  # Preserve orientation by default
    "GPS": "whole_degrees",  # Options: "exact", "whole_degrees", "remove"
    "Timestamp": "date_only",  # Options: "exact", "date_only", "remove"
    "CameraSettings": "all_except_make_model",  # Options: "all", "all_except_make_model", "remove"
    "Descriptions": False,
    "Thumbnail": False,
    "ImageMetrics": False
}

def load_filter_rules(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load filtering rules from a JSON config file.

    If no config file is provided or the file is missing/invalid,
    return the default rules.

    Parameters:
        config_file (Optional[str]): Path to the configuration JSON file.

    Returns:
        Dict[str, Any]: A dictionary of filtering rules.
    """
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
                return rules
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading config file {config_file}: {e}", exc_info=True)
            return DEFAULT_RULES
    else:
        return DEFAULT_RULES

def filter_exif_data(exif_dict: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter the EXIF data dictionary based on provided rules.

    This implementation demonstrates processing key metadata fields.

    Parameters:
        exif_dict (Dict[str, Any]): The original EXIF data dictionary.
        rules (Dict[str, Any]): A dictionary of filtering rules.

    Returns:
        Dict[str, Any]: The filtered EXIF data dictionary.
    """
    # Remove Orientation if specified
    if not rules.get("Orientation", True):
        exif_dict.get("0th", {}).pop(274, None)
    
    # Process GPS data (located in the "GPS" section)
    if "GPS" in exif_dict:
        gps_rule = rules.get("GPS", "whole_degrees")
        if gps_rule == "remove":
            exif_dict["GPS"] = {}
        elif gps_rule == "whole_degrees":
            for tag, value in exif_dict["GPS"].items():
                if isinstance(value, tuple) and len(value) == 2:
                    num, den = value
                    exif_dict["GPS"][tag] = (int(num / den), 1)
    
    # Process Timestamp (DateTimeOriginal is tag 36867 in the "Exif" IFD)
    if "Exif" in exif_dict and 36867 in exif_dict["Exif"]:
        ts_rule = rules.get("Timestamp", "date_only")
        dt_str = exif_dict["Exif"][36867]
        dt_str = dt_str.decode("utf-8") if isinstance(dt_str, bytes) else dt_str
        if ts_rule == "date_only":
            exif_dict["Exif"][36867] = dt_str.split(" ")[0].encode("utf-8")
        elif ts_rule == "remove":
            del exif_dict["Exif"][36867]
    
    return exif_dict
