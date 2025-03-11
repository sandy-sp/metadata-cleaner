import os
import json
import pytest
from metadata_cleaner.core.metadata_filter import load_filter_rules

# Sample configuration files
test_folder = "test_config"
valid_config = "test_config/valid_config.json"
invalid_config = "test_config/invalid_config.json"

def setup_module(module):
    """Setup test configuration files before running tests."""
    os.makedirs(test_folder, exist_ok=True)
    
    # Create a valid config file
    valid_rules = {
        "GPS": {"mode": "remove"},
        "Timestamp": {"mode": "date_only"},
        "CameraSettings": {"mode": "all_except_make_model"}
    }
    with open(valid_config, "w") as f:
        json.dump(valid_rules, f, indent=4)
    
    # Create an invalid config file
    with open(invalid_config, "w") as f:
        f.write("INVALID_JSON_CONTENT")

def teardown_module(module):
    """Cleanup test configuration files after tests are done."""
    if os.path.exists(valid_config):
        os.remove(valid_config)
    if os.path.exists(invalid_config):
        os.remove(invalid_config)
    os.rmdir(test_folder)

# Test valid configuration file loading
def test_valid_config_loading():
    rules = load_filter_rules(valid_config)
    assert isinstance(rules, dict)
    assert "GPS" in rules
    assert "Timestamp" in rules
    assert "CameraSettings" in rules

# Test invalid configuration file handling
def test_invalid_config_handling():
    rules = load_filter_rules(invalid_config)
    assert isinstance(rules, dict)  # Should return default rules instead of crashing

if __name__ == "__main__":
    pytest.main()
