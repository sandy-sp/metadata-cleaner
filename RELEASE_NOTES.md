# Release Notes

## v3.7.2
**Release Date**: 2026-05-10

### Maintenance
- Expanded the installed-package smoke test to exercise JPEG, PDF, DOCX, and
  WAV files through the packaged `metadata-cleaner` CLI.
- Added smoke assertions for JSON metadata views, dry-run summaries, real
  cleaning output, and generated summary reports.

## v3.7.1
**Release Date**: 2026-05-10

### Maintenance
- Added generated WAV fixtures with real ID3 metadata tags.
- Expanded audio cleanup coverage to verify metadata is stripped from the
  cleaned copy while the original tagged source remains intact and playable.

## v3.7.0
**Release Date**: 2026-05-10

### Features
- Added per-file details to delete JSON summaries and summary files.
- Each processed file now reports its input path, status, output path, and
  failure reason when available.

## v3.6.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner delete --summary-file PATH` to write the final
  delete summary as JSON for audits, scheduled jobs, and CI pipelines.
- Summary files are written for successful, failed, dry-run, and no-supported-
  file outcomes.

## v3.5.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner view --json` for stable machine-readable metadata
  inspection, including invalid-input and no-metadata cases.

### Maintenance
- Improved CLI metadata formatting so non-JSON-native metadata values are
  rendered safely instead of causing formatting errors.

## v3.4.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner delete --json-summary` for machine-readable batch
  and single-file summaries.
- Added `metadata-cleaner delete --quiet` to suppress progress and human output
  for automation.

### Maintenance
- Updated the release workflow to attach the matching curated section from
  `RELEASE_NOTES.md` to GitHub Releases.

## v3.3.1
**Release Date**: 2026-05-10

### Maintenance
- Added a package smoke-test CI job that builds the wheel, installs it into a
  clean virtual environment, and runs the installed `metadata-cleaner` CLI.

## v3.3.0
**Release Date**: 2026-05-10

### Features
- Added global `--verbose` and `--log-file` CLI options.
- Added structured batch summaries for recursive metadata removal.
- Added script-friendly exit codes for success, usage/no-op, full failure, and
  partial failure cases.

### Maintenance
- Added Docker build verification to CI and fixed the Docker build context so
  `poetry.lock` is available to the Dockerfile.
- Added generated WAV coverage and optional FFmpeg/FFprobe video integration
  coverage.
- Replaced stale planning and self-improvement docs with current roadmap and
  maintenance guidance.
- Updated the release action and Docker base image through Dependabot.

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
