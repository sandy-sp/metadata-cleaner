# Release Notes

## v3.15.0
**Release Date**: 2026-05-10

### Features
- Added HEIC and HEIF file discovery plus ExifTool-backed metadata cleanup.
- HEIC/HEIF dry-run and JSON reports now include processing warnings that
  explain the external-tool dependency.

### Maintenance
- Documented the HEIC/HEIF support strategy without adding a new image codec
  dependency.
- Added tests for HEIC/HEIF recognition, HEIC cleanup routing, and CLI warning
  output.

## v3.14.0
**Release Date**: 2026-05-10

### Features
- Added EPUB metadata viewing and cleanup through the package OPF metadata
  document referenced by `META-INF/container.xml`.
- EPUB cleanup neutralizes identifying package metadata while preserving
  required EPUB fields and book contents.

### Maintenance
- Added generated EPUB fixture coverage for metadata extraction, cleanup, and
  CLI processing warnings.

## v3.13.0
**Release Date**: 2026-05-10

### Features
- Added ODT metadata viewing and cleanup using the standard OpenDocument
  `meta.xml` package metadata.
- ODT cleanup clears package metadata while preserving the rest of the
  document package contents.

### Maintenance
- Added generated ODT fixture coverage for metadata extraction, cleanup, and
  CLI processing warnings.

## v3.12.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner delete --report-filter all|failed` to filter
  per-file entries in JSON summaries and summary files.
- `failed` reports keep top-level totals intact while listing only failed
  per-file entries, which is useful for very large batch runs.

## v3.11.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner delete --report-detail full|compact|summary` to
  control JSON summary verbosity for large batch and automation workflows.
- `full` preserves the existing report shape, `compact` keeps per-file status
  with minimal fields, and `summary` omits per-file entries entirely.

## v3.10.0
**Release Date**: 2026-05-10

### Features
- Added per-file processing warnings to delete JSON summaries and summary
  files for formats that rewrite, re-save, or remux data while removing
  metadata.
- Warnings are available during dry runs as well as completed cleaning runs.

## v3.9.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner delete --preserve-timestamps` to copy source access
  and modification times to cleaned outputs.
- Added programmatic support through
  `MetadataProcessor.delete_metadata(..., preserve_timestamps=True)`.

## v3.8.0
**Release Date**: 2026-05-10

### Features
- Added `metadata-cleaner delete --checksums` to include SHA-256 integrity
  hashes in JSON summaries and summary files.
- Checksum reporting covers input files for dry runs and both input/output
  files for completed cleaning operations.

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
