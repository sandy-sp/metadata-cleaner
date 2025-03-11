import os
import pytest
import json
from click.testing import CliRunner
from metadata_cleaner.cli import main

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
    
    # Ensure folder is empty before removing
    if os.path.exists(test_folder) and not os.listdir(test_folder):
        os.rmdir(test_folder)

# Test CLI Help Command
def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output

# Test CLI Metadata Removal
@pytest.mark.parametrize("file_type", ["image", "document", "audio", "video", "pdf"])
def test_cli_remove_metadata(file_type):
    runner = CliRunner()
    result = runner.invoke(main, ["--file", test_files[file_type], "--yes"])
    assert result.exit_code == 0
    assert "✅ Cleaned file saved at" in result.output

# Test CLI Folder Processing
def test_cli_folder_processing():
    runner = CliRunner()
    result = runner.invoke(main, ["--folder", test_folder, "--yes"])
    assert result.exit_code == 0
    assert "✅ Processed" in result.output

# Test CLI Recursive Processing
def test_cli_recursive_processing():
    runner = CliRunner()
    result = runner.invoke(main, ["--folder", test_folder, "--recursive", "--yes"])
    assert result.exit_code == 0
    assert "✅ Processed" in result.output

# Test CLI Dry Run
def test_cli_dry_run():
    runner = CliRunner()
    result = runner.invoke(main, ["--file", test_files["image"], "--dry-run"])
    assert result.exit_code == 0
    assert "📝 Dry-Run Metadata Removal" in result.output

# Test CLI Remove GPS Data
def test_cli_remove_gps():
    runner = CliRunner()
    result = runner.invoke(main, ["--file", test_files["image"], "--remove-gps", "--yes"])
    assert result.exit_code == 0
    assert "✅ Cleaned file saved at" in result.output

# Test CLI Preserve Timestamp
def test_cli_keep_timestamp():
    runner = CliRunner()
    result = runner.invoke(main, ["--file", test_files["image"], "--keep-timestamp", "--yes"])
    assert result.exit_code == 0
    assert "✅ Cleaned file saved at" in result.output

if __name__ == "__main__":
    pytest.main()
