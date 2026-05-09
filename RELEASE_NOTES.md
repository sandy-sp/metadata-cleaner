# Release Notes

## v3.2.0
**Release Date**: 2026-05-09

### Security
- Refreshed the dependency lockfile to patched versions for Pillow, pypdf,
  urllib3, requests, lxml, filelock, pytest, Black, Pygments, and pip.
- Added CI dependency auditing with `pip-audit`.
- Added CodeQL scanning workflow for Python.
- Added Dependabot configuration for Python, GitHub Actions, and Docker updates.

### Privacy and Safety
- Removed tracked generated memory/log artifacts from the repository.
- Made file logging opt-in with `METADATA_CLEANER_LOG_FILE`.
- Prevented metadata removal from writing over the input file.
- Fixed dry-run mode so it does not create output directories.

### Maintenance
- Migrated package metadata to modern `[project]` configuration.
- Added package metadata checks to CI and release workflows.
- Expanded tests for DOCX metadata cleanup, CLI dry-run behavior, invalid JSON
  handling, and in-place output protection.

## v3.1.0
**Release Date**: 2025-12-18

### Key Features
- **Recursive Directory Scanning**: The `delete` command now accepts directories and finds all supported files recursively.
- **Safety & Quality**:
  - **Lossless Video**: Enforced `ffmpeg -c copy` for true lossless metadata removal.
  - **Dry-Run**: Added `--dry-run` flag.
- **Task Runner**: Added `manage.py` for cross-platform development.
- **Docker**: Added production `Dockerfile`.

### Improvements
- **Dependencies**: Removed unused libs.
- **Tests**: Enhanced suite with recursive and dry-run tests.
