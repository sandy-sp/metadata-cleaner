import os
import pytest
from metadata_cleaner.remover import remove_metadata
from metadata_cleaner.file_handlers.metadata_extractor import extract_metadata

# Sample test directory
test_folder = "test_folder"
test_files = {
    "empty": "test_folder/empty.txt",
    "corrupt": "test_folder/corrupt.jpg",
    "unsupported": "test_folder/unsupported.xyz",
    "large": "test_folder/large.mp4"
}

def setup_module(module):
    """Setup test files before running edge case tests."""
    os.makedirs(test_folder, exist_ok=True)
    
    # Create an empty file
    open(test_files["empty"], "w").close()
    
    # Create a dummy corrupt file
    with open(test_files["corrupt"], "wb") as f:
        f.write(os.urandom(128))  # Random bytes
    
    # Create an unsupported format file
    with open(test_files["unsupported"], "w") as f:
        f.write("Unsupported file format")
    
    # Simulate a large file (10MB)
    with open(test_files["large"], "wb") as f:
        f.write(os.urandom(10 * 1024 * 1024))

def teardown_module(module):
    """Cleanup test files after tests are done."""
    for file in test_files.values():
        if os.path.exists(file):
            os.remove(file)
    os.rmdir(test_folder)

# Test empty file handling
def test_empty_file():
    result = remove_metadata(test_files["empty"])
    assert result is None  # Empty files should not be processed

# Test corrupted file handling
def test_corrupt_file():
    result = remove_metadata(test_files["corrupt"])
    assert result is None  # Corrupt files should fail gracefully

# Test unsupported file format handling
def test_unsupported_file():
    result = remove_metadata(test_files["unsupported"])
    assert result is None  # Unsupported formats should return None

# Test large file processing
def test_large_file():
    result = remove_metadata(test_files["large"])
    assert result is not None  # Large files should be processed successfully

if __name__ == "__main__":
    pytest.main()
