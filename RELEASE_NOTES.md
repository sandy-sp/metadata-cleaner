# Release Notes

## v3.1.0
**Release Date**: 2025-12-18

### 🚀 Key Features
- **📂 Recursive Directory Scanning**: The `delete` command now accepts directories and finds all supported files recursively.
- **🛡️ Safety & Quality**: 
    - **Lossless Video**: Enforced `ffmpeg -c copy` for true lossless metadata removal.
    - **Dry-Run**: Added `--dry-run` flag.
- **🐍 Task Runner**: Added `manage.py` for cross-platform development (Linux/Win/Mac).
- **🐳 Docker**: Added production `Dockerfile`.

### 🛠️ Improvements
- **Dependencies**: Removed unused libs.
- **Tests**: Enhanced suite with recursive and dry-run tests.
