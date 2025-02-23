import os
import json
import tempfile
import piexif
from PIL import Image
from metadata_cleaner.core.metadata_filter import load_filter_rules, filter_exif_data

def create_exif_dict():
    """
    Create a dummy Exif dictionary with:
    - Orientation (tag 274) in "0th"
    - DateTimeOriginal (tag 36867) in "Exif"
    - Some GPS data in "GPS"
    """
    return {
        "0th": {274: 1},
        "Exif": {36867: "2025:02:23 10:00:00"},
        "GPS": {1: b"N", 2: ((40, 1), (26, 1), (0, 1))},
        "1st": {},
        "thumbnail": None
    }

def test_default_rules():
    """Test filtering using default rules (no config file provided)."""
    exif = create_exif_dict()
    rules = load_filter_rules()  # should load DEFAULT_RULES
    filtered = filter_exif_data(exif.copy(), rules)
    # With default rules, Orientation is preserved.
    assert 274 in filtered["0th"], "Orientation should be preserved by default"
    # GPS should be processed as whole_degrees.
    gps_data = filtered["GPS"]
    for tag, value in gps_data.items():
        if isinstance(value, tuple) and len(value) == 2:
            num, den = value
            assert isinstance(num, int), "GPS values should be converted to whole degrees"
    # Timestamp should be converted to date-only.
    timestamp = filtered["Exif"].get(36867, b"").decode("utf-8")
    assert len(timestamp.split(" ")) == 1, "Timestamp should be date only by default"

def test_remove_orientation():
    """Test that Orientation is removed when configured."""
    exif = create_exif_dict()
    rules = {"Orientation": False, "GPS": "whole_degrees", "Timestamp": "date_only",
             "CameraSettings": "all_except_make_model", "Descriptions": False,
             "Thumbnail": False, "ImageMetrics": False}
    filtered = filter_exif_data(exif.copy(), rules)
    assert 274 not in filtered["0th"], "Orientation should be removed"

def test_remove_gps():
    """Test that GPS data is removed when configured."""
    exif = create_exif_dict()
    rules = {"Orientation": True, "GPS": "remove", "Timestamp": "date_only",
             "CameraSettings": "all_except_make_model", "Descriptions": False,
             "Thumbnail": False, "ImageMetrics": False}
    filtered = filter_exif_data(exif.copy(), rules)
    assert filtered["GPS"] == {}, "GPS data should be removed"

def test_exact_gps():
    """Test that GPS data is unchanged when 'exact' is set."""
    exif = create_exif_dict()
    rules = {"Orientation": True, "GPS": "exact", "Timestamp": "date_only",
             "CameraSettings": "all_except_make_model", "Descriptions": False,
             "Thumbnail": False, "ImageMetrics": False}
    filtered = filter_exif_data(exif.copy(), rules)
    original_gps = create_exif_dict()["GPS"]
    assert filtered["GPS"] == original_gps, "GPS data should remain unchanged for 'exact'"

def test_timestamp_exact():
    """Test that Timestamp is preserved when 'exact' is set."""
    exif = create_exif_dict()
    rules = {"Orientation": True, "GPS": "whole_degrees", "Timestamp": "exact",
             "CameraSettings": "all_except_make_model", "Descriptions": False,
             "Thumbnail": False, "ImageMetrics": False}
    filtered = filter_exif_data(exif.copy(), rules)
    timestamp = filtered["Exif"].get(36867, b"")
    ts_str = timestamp.decode("utf-8") if isinstance(timestamp, bytes) else timestamp
    assert ts_str == "2025:02:23 10:00:00", "Timestamp should remain unchanged for 'exact'"

def test_timestamp_remove():
    """Test that Timestamp is removed when configured."""
    exif = create_exif_dict()
    rules = {"Orientation": True, "GPS": "whole_degrees", "Timestamp": "remove",
             "CameraSettings": "all_except_make_model", "Descriptions": False,
             "Thumbnail": False, "ImageMetrics": False}
    filtered = filter_exif_data(exif.copy(), rules)
    assert 36867 not in filtered["Exif"], "Timestamp should be removed"

def test_invalid_config_file():
    """Test that an invalid config file returns default rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_path = os.path.join(tmpdir, "invalid.json")
        with open(invalid_path, "w") as f:
            f.write("not a valid json")
        rules = load_filter_rules(invalid_path)
        expected_default = {
            "Orientation": True,
            "GPS": "whole_degrees",
            "Timestamp": "date_only",
            "CameraSettings": "all_except_make_model",
            "Descriptions": False,
            "Thumbnail": False,
            "ImageMetrics": False
        }
        assert rules == expected_default, "Invalid config should load default rules"
