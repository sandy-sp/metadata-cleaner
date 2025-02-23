import json
import os

# Default filtering rules
DEFAULT_RULES = {
    "Orientation": True,             # Preserve orientation by default
    "GPS": "whole_degrees",          # Options: "exact", "whole_degrees", "remove"
    "Timestamp": "date_only",        # Options: "exact", "date_only", "remove"
    "CameraSettings": "all_except_make_model",  # Options: "all", "all_except_make_model", "remove"
    "Descriptions": False,
    "Thumbnail": False,
    "ImageMetrics": False
}

def load_filter_rules(config_file=None):
    """
    Load filtering rules from a JSON config file. If no file is provided or file is missing,
    return the default rules.
    """
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            try:
                rules = json.load(f)
                return rules
            except Exception as e:
                print(f"Error reading config file {config_file}: {e}")
                return DEFAULT_RULES
    else:
        return DEFAULT_RULES

def filter_exif_data(exif_dict, rules):
    """
    Filter the exif dictionary based on provided rules.
    This basic implementation demonstrates processing a few key fields.
    """
    # Process Orientation: Exif tag 274 (if set to False, remove it)
    if not rules.get("Orientation", True):
        if "0th" in exif_dict and 274 in exif_dict["0th"]:
            del exif_dict["0th"][274]
    
    # Process GPS data (located in the "GPS" section)
    if "GPS" in exif_dict:
        gps_rule = rules.get("GPS", "whole_degrees")
        if gps_rule == "remove":
            exif_dict["GPS"] = {}
        elif gps_rule == "whole_degrees":
            # Naively convert rational numbers to whole degrees if possible
            for tag, value in exif_dict["GPS"].items():
                try:
                    if isinstance(value, tuple) and len(value) == 2:
                        num, den = value
                        exif_dict["GPS"][tag] = (int(num / den), 1)
                except Exception:
                    pass
        # For "exact", leave the GPS data as-is.

    # Process Timestamp (e.g., DateTimeOriginal is tag 36867 in the "Exif" IFD)
    if "Exif" in exif_dict and 36867 in exif_dict["Exif"]:
        ts_rule = rules.get("Timestamp", "date_only")
        dt = exif_dict["Exif"][36867]
        dt_str = dt.decode("utf-8") if isinstance(dt, bytes) else dt
        if ts_rule == "date_only":
            date_only = dt_str.split(" ")[0] if " " in dt_str else dt_str
            exif_dict["Exif"][36867] = date_only.encode("utf-8")
        elif ts_rule == "remove":
            del exif_dict["Exif"][36867]

    # Placeholders for additional rules (CameraSettings, Descriptions, Thumbnail, ImageMetrics)
    # Extend as needed.

    return exif_dict
