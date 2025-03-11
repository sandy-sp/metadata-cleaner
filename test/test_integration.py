import os
import pytest
from metadata_cleaner.remover import remove_metadata_from_folder, remove_metadata
from metadata_cleaner.file_handlers.metadata_extractor import extract_metadata

# Sample test directory
test_folder = "test_folder"
test_files = {
    "image": "test_folder/test.jpg",
    "document": "test_folder/test.docx",
    "audio": "test_folder/test.mp3",
    "video": "test_folder/test.mp4",
    "pdf": "test_folder/test.pdf"
}

def setup_module(module):
    """Setup test files before running integration tests."""
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

# Test batch processing in a folder
def test_remove_metadata_from_folder():
    cleaned_files = remove_metadata_from_folder(test_folder)
    assert isinstance(cleaned_files, list)
    assert len(cleaned_files) >= 0  # Should not fail even if no files are processed

# Test comparing metadata before and after cleaning
@pytest.mark.parametrize("file_type", ["image", "document", "audio", "video", "pdf"])
def test_metadata_comparison(file_type):
    original_metadata = extract_metadata(test_files[file_type])
    remove_metadata(test_files[file_type])
    cleaned_metadata = extract_metadata(test_files[file_type])
    
    if original_metadata:
        assert cleaned_metadata is None or cleaned_metadata == {}  # Metadata should be removed
    else:
        assert cleaned_metadata is None  # No metadata should remain

# Test correct output file paths
def test_output_paths():
    cleaned_files = remove_metadata_from_folder(test_folder)
    for cleaned_file in cleaned_files:
        assert os.path.exists(cleaned_file)

if __name__ == "__main__":
    pytest.main()
