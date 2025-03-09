import json
import os
from typing import Optional, Dict, Any, List, Set
from functools import lru_cache
from metadata_cleaner.logs.logger import logger

"""
Enhanced metadata filtering utility for selective removal of metadata fields.

Features:
- Cached configuration loading
- Strict type validation
- Flexible rule inheritance
- Custom rule validation
- Support for rule templates
"""

# Default filtering rules with detailed documentation
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

    Raises:
        ValueError: If the configuration is invalid.
    """
    rules = DEFAULT_RULES.copy()

    if config_file:
        if not os.path.exists(config_file):
            logger.warning(f"Config file not found: {config_file}")
            return rules

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                custom_rules = json.load(f)
            
            # Validate and merge custom rules
            rules.update(validate_rules(custom_rules))
            logger.info(f"Loaded custom rules from: {config_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
        except ValueError as e:
            logger.error(f"Invalid rule configuration: {e}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}", exc_info=True)

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
            logger.warning(f"Unknown rule key: {key} (Ignoring)")
            continue  # Ignore invalid keys

        if isinstance(value, dict) and "mode" in value:
            if key in VALID_OPTIONS and value["mode"] not in VALID_OPTIONS[key]:
                logger.error(f"Invalid mode for {key}: {value['mode']} (Ignoring rule)")
                continue  # Ignore this rule instead of modifying it

        validated[key] = value

    return validated

def filter_exif_data(exif_dict: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter EXIF data based on rules.

    Args:
        exif_dict (Dict[str, Any]): Original EXIF data.
        rules (Dict[str, Any]): Filtering rules.

    Returns:
        Dict[str, Any]: Filtered EXIF data.
    """
    if not isinstance(exif_dict, dict):
        raise ValueError("Invalid EXIF data format")

    filtered = {k: v.copy() if isinstance(v, dict) else v for k, v in exif_dict.items()}

    try:
        # Process Orientation
        if not rules.get("Orientation", True):
            filtered.get("0th", {}).pop(274, None)
        
        # Process GPS data
        if "GPS" in filtered:
            gps_rules = rules.get("GPS", {})
            filtered["GPS"] = process_gps_data(filtered.get("GPS", {}), gps_rules)
        
        # Process Timestamp
        if "Exif" in filtered:
            timestamp_rules = rules.get("Timestamp", {})
            filtered["Exif"] = process_timestamp(filtered.get("Exif", {}), timestamp_rules)
        
        # Process Camera Settings
        camera_rules = rules.get("CameraSettings", {})
        filtered = process_camera_settings(filtered, camera_rules)
        
        # Remove additional metadata based on rules
        if not rules.get("Descriptions", True):
            filtered.pop("ImageDescription", None)
            filtered.pop("UserComment", None)
        
        if not rules.get("Thumbnail", True):
            filtered.pop("thumbnail", None)
        
        if not rules.get("Software", True):
            filtered.get("0th", {}).pop(305, None)  # Software tag
        
    except Exception as e:
        logger.error(f"Error filtering EXIF data: {e}", exc_info=True)
        return exif_dict  # Return original data if filtering fails

    return filtered

def process_gps_data(gps_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process GPS data according to rules.

    Args:
        gps_data (Dict[str, Any]): Original GPS data.
        rules (Dict[str, Any]): GPS filtering rules.

    Returns:
        Dict[str, Any]: Processed GPS data.
    """
    if not isinstance(gps_data, dict) or not gps_data:
        return {}

    mode = rules.get("mode", "whole_degrees")
    precision = rules.get("precision", 0)
    remove_altitude = rules.get("remove_altitude", True)

    processed = gps_data.copy()

    try:
        if remove_altitude:
            processed.pop(6, None)  # Altitude
            processed.pop(7, None)  # Altitude reference

        if mode == "remove":
            return {}

        if mode == "whole_degrees":
            for tag in [2, 4]:  # Latitude & Longitude
                if tag in processed and isinstance(processed[tag], tuple) and len(processed[tag]) == 2:
                    num, den = processed[tag]
                    degrees = round(float(num) / float(den), precision)
                    processed[tag] = (int(degrees * (10 ** precision)), 10 ** precision)

        return processed

    except Exception as e:
        logger.error(f"Error processing GPS data: {e}", exc_info=True)
        return {}  # Return empty dict if processing fails

def process_timestamp(exif_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process timestamp data according to rules.

    Args:
        exif_data (Dict[str, Any]): Original EXIF data containing timestamp.
        rules (Dict[str, Any]): Timestamp filtering rules.

    Returns:
        Dict[str, Any]: Processed EXIF data with modified timestamp.
    """
    if not isinstance(exif_data, dict):
        return {}

    mode = rules.get("mode", "date_only")
    date_format = rules.get("format", "%Y:%m:%d")
    
    try:
        # Process DateTimeOriginal (tag 36867)
        if 36867 in exif_data:
            if mode == "remove":
                exif_data.pop(36867)
            elif mode == "date_only":
                dt_str = exif_data[36867]
                if isinstance(dt_str, bytes):
                    dt_str = dt_str.decode('utf-8')
                date_part = dt_str.split()[0]
                exif_data[36867] = date_part.encode('utf-8')

        # Process other timestamp-related tags
        timestamp_tags = [36868, 306]  # DateTimeDigitized, DateTime
        if mode == "remove":
            for tag in timestamp_tags:
                exif_data.pop(tag, None)

        return exif_data

    except Exception as e:
        logger.error(f"Error processing timestamp: {e}", exc_info=True)
        return exif_data

def process_camera_settings(exif_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process camera settings according to rules.

    Args:
        exif_data (Dict[str, Any]): Original EXIF data.
        rules (Dict[str, Any]): Camera settings filtering rules.

    Returns:
        Dict[str, Any]: Processed EXIF data with modified camera settings.
    """
    if not isinstance(exif_data, dict):
        return {}

    mode = rules.get("mode", "all_except_make_model")
    preserve_fields = set(rules.get("preserve", ["Make", "Model"]))

    try:
        if mode == "remove":
            # Remove all camera-related tags
            camera_tags = {
                "0th": [271, 272, 305, 306],  # Make, Model, Software, DateTime
                "Exif": [33434, 33437, 34850, 34855, 37377, 37378, 37379, 37380]  # Various camera settings
            }
            
            for ifd in camera_tags:
                if ifd in exif_data:
                    for tag in camera_tags[ifd]:
                        exif_data[ifd].pop(tag, None)

        elif mode == "all_except_make_model":
            # Preserve only specified fields
            for ifd in exif_data:
                if isinstance(exif_data[ifd], dict):
                    tags_to_remove = []
                    for tag, value in exif_data[ifd].items():
                        tag_name = get_exif_tag_name(ifd, tag)
                        if tag_name not in preserve_fields:
                            tags_to_remove.append(tag)
                    
                    for tag in tags_to_remove:
                        exif_data[ifd].pop(tag, None)

        return exif_data

    except Exception as e:
        logger.error(f"Error processing camera settings: {e}", exc_info=True)
        return exif_data

def get_exif_tag_name(ifd: str, tag: int) -> str:
    """
    Get the name of an EXIF tag.

    Args:
        ifd (str): IFD section name.
        tag (int): Tag number.

    Returns:
        str: Tag name or empty string if not found.
    """
    # Common EXIF tags mapping
    EXIF_TAGS = {
        "0th": {
            271: "Make",
            272: "Model",
            305: "Software",
            306: "DateTime"
        },
        "Exif": {
            36867: "DateTimeOriginal",
            33434: "ExposureTime",
            33437: "FNumber",
            34850: "ExposureProgram",
            34855: "ISOSpeedRatings"
        }
    }
    
    return EXIF_TAGS.get(ifd, {}).get(tag, "")

def create_filter_template(name: str) -> Dict[str, Any]:
    """
    Create a predefined filter template.

    Args:
        name (str): Template name ("privacy", "minimal", "strict").

    Returns:
        Dict[str, Any]: Template configuration.
    """
    templates = {
        "privacy": {
            "Orientation": True,
            "GPS": {"mode": "remove"},
            "Timestamp": {"mode": "date_only"},
            "CameraSettings": {"mode": "all_except_make_model"},
            "Descriptions": False,
            "Thumbnail": False,
            "Software": False
        },
        "minimal": {
            "Orientation": True,
            "GPS": {"mode": "whole_degrees", "precision": 0},
            "Timestamp": {"mode": "date_only"},
            "CameraSettings": {"mode": "all"},
            "Descriptions": True,
            "Thumbnail": False,
            "Software": True
        },
        "strict": {
            "Orientation": False,
            "GPS": {"mode": "remove"},
            "Timestamp": {"mode": "remove"},
            "CameraSettings": {"mode": "remove"},
            "Descriptions": False,
            "Thumbnail": False,
            "Software": False
        }
    }
    
    return templates.get(name, DEFAULT_RULES.copy())
