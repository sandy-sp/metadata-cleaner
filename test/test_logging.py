import os
import pytest
import logging
from metadata_cleaner.logs.logger import logger, get_current_log_path
from metadata_cleaner.remover import remove_metadata

# Sample test file
test_folder = "test_folder"
test_file = "test_folder/test.jpg"
test_log_file = get_current_log_path()

def setup_module(module):
    """Setup test file before running logging tests."""
    os.makedirs(test_folder, exist_ok=True)
    with open(test_file, "w") as f:
        f.write("Test content")
    
    # Clear the log file before each test run
    if os.path.exists(test_log_file):
        open(test_log_file, 'w').close()

def teardown_module(module):
    """Cleanup test files and logs after tests are done."""
    if os.path.exists(test_file):
        os.remove(test_file)
    os.rmdir(test_folder)
    if os.path.exists(test_log_file):
        open(test_log_file, 'w').close()

# Test log file captures metadata removal process
def test_log_metadata_removal():
    remove_metadata(test_file)
    with open(test_log_file, "r") as log:
        log_content = log.read()
    assert "Removing metadata from" in log_content
    assert "✅ Metadata removed successfully" in log_content

# Test log records errors
def test_log_error_handling():
    remove_metadata("non_existent_file.jpg")
    with open(test_log_file, "r") as log:
        log_content = log.read()
    assert "❌ File not found" in log_content

# Test changing log level dynamically
def test_change_log_level():
    logger.setLevel(logging.DEBUG)
    assert logger.level == logging.DEBUG
    logger.setLevel(logging.INFO)
    assert logger.level == logging.INFO

if __name__ == "__main__":
    pytest.main()
