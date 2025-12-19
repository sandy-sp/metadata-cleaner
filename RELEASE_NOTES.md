# Release Notes - Metadata Cleaner v3.1.0

This release introduces significant improvements to stability, usability, and cross-platform compatibility.

## 🚀 Key Features

### 1. 📂 Recursive Directory Scanning
- The `delete` command now accepts directories.
- Automatically finds all supported files (`.jpg`, `.mp4`, `.pdf`, etc.) in subfolders.
- Displays a real-time progress bar using `tqdm`.

### 2. 🛡️ Safety & Quality
- **Strinct Stream Copy for Videos**: Refactored `VideoHandler` to strictly use `ffmpeg -c copy`. It guarantees **0% quality loss** and preserves all streams (video, audio, subtitles) while removing global metadata.
- **Dry-Run Mode**: Added `--dry-run` flag to simulate operations without modifying files.

### 3. 🐍 Cross-Platform Task Runner
- Replaced legacy Bash scripts with a unified `manage.py` script.
- Works on **Linux, Windows, and macOS**.
- Commands: `install`, `test`, `lint`, `clean`, `check`.

### 4. 🐳 Docker Support
- Added a production-ready `Dockerfile` (based on python:3.9-slim).
- Includes all dependencies (`ffmpeg`, `exiftool`).
- Easy to run: `docker run -v $(pwd):/data metadata-cleaner delete /data`.

## 🛠️ Internal Improvements
- **Dependencies**: Removed unused libraries (`tinytag`, `hachoir`).
- **Tests**: Enhanced test suite with recursive scanning and dry-run verification.
- **CI/CD**: Improved `pyproject.toml` to exclude tool directories from tests.
