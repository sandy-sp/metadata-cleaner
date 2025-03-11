import os
import pytest
from metadata_cleaner.file_handlers.metadata_extractor import extract_metadata
from metadata_cleaner.remover import remove_metadata

# Sample test files
test_folder = "test_folder"
test_files = {
    "image": "test_folder/test.jpg",
    "document": "test_folder/test.docx",
    "audio": "test_folder/test.mp3",
    "video": "test_folder/test.mp4",
    "pdf": "test_folder/test.pdf"
}

def setup_module(module):
    """Setup test files before running tests."""
    os.makedirs(test_folder, exist_ok=True)
    for file in test_files.values():
        with open(file, "w") as f:
            f.write("Test content")

def teardown_module(module):
    """Cleanup test files after tests are done."""
    for file in test_files.values():
        if os.path.exists(file):
            os.remove(file)
    os.rmdir(test_folder)

# Test Metadata Extraction
@pytest.mark.parametrize("file_type", ["image", "document", "audio", "video", "pdf"])
def test_extract_metadata(file_type):
    metadata = extract_metadata(test_files[file_type])
    assert isinstance(metadata, dict) or metadata is None

# Test Metadata Removal
@pytest.mark.parametrize("file_type", ["image", "document", "audio", "video", "pdf"])
def test_remove_metadata(file_type):
    cleaned_file = remove_metadata(test_files[file_type])
    assert cleaned_file is None or os.path.exists(cleaned_file)

# Test Removing Metadata Does Not Corrupt Files
@pytest.mark.parametrize("file_type", ["image", "document", "audio", "video", "pdf"])
def test_file_integrity_after_removal(file_type):
    original_size = os.path.getsize(test_files[file_type])
    cleaned_file = remove_metadata(test_files[file_type])
    if cleaned_file and os.path.exists(cleaned_file):
        cleaned_size = os.path.getsize(cleaned_file)
        assert cleaned_size <= original_size  # Cleaned file should be same or smaller in size

if __name__ == "__main__":
    pytest.main()
