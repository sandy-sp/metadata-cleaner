# Release Notes

## v3.18.11
**Release Date**: 2026-05-16

### Maintenance
- Added a release workflow guard that verifies the pushed tag matches the
  version in `pyproject.toml` before publishing.
- Fixed the legacy programmatic batch API so failed files preserve their result
  slot as `None`.
- Refreshed the repository health review and roadmap after the v3.18.x
  maintenance sequence.

## v3.18.10
**Release Date**: 2026-05-16

### Maintenance
- Updated the pikepdf compatibility range to v10 and refreshed the lockfile.
- Added PDF cleanup coverage confirming document-info and XMP metadata removal
  while preserving PDF pages.

## v3.18.9
**Release Date**: 2026-05-16

### Security
- Added ZIP archive safety limits for EPUB and ODT metadata extraction and
  cleanup paths.
- Oversized archive entries, excessive entry counts, and excessive total
  uncompressed archive sizes now fail before package members are parsed or
  rewritten.

## v3.18.8
**Release Date**: 2026-05-16

### Security
- Added bounded ExifTool subprocess timeouts for metadata extraction and
  metadata removal paths.
- Timed-out ExifTool removals now clean up copied partial outputs before
  returning failure.

## v3.18.7
**Release Date**: 2026-05-16

### CLI
- Added explicit unsupported single-file handling for `view` and `delete`
  commands.
- Machine-readable output now returns `unsupported_file_type` for unsupported
  `view` input and `unsupported_input` summaries for unsupported `delete`
  input, instead of reporting those files as no-metadata or processing
  failures.

## v3.18.6
**Release Date**: 2026-05-16

### Maintenance
- Added a repository health review checkpoint covering current security,
  dependency, branch protection, packaging, and roadmap status.
- Removed unused runtime dependencies on `ffmpeg-python` and `pymupdf`,
  reducing install size and dependency attack surface.
- Removed the stale `tools/doc` gitlink that caused non-failing GitHub Actions
  checkout cleanup annotations.
- Excluded test modules from release artifacts while keeping CI and package
  smoke coverage in place.

## v3.18.5
**Release Date**: 2026-05-16

### Maintenance
- Expanded per-file processing warnings to more precisely describe copy-first,
  package rewrite, image re-save, ExifTool, audio tag deletion, and FFmpeg
  stream-copy remux paths.
- Added warning coverage for JPEG, FLAC, and video dry-run JSON summaries.

## v3.18.4
**Release Date**: 2026-05-16

### Features
- Added `metadata-cleaner view --json-output FILE` to write metadata JSON
  envelopes directly to disk.
- Added `metadata-cleaner delete --json-output FILE` as a consistent alias for
  writing final JSON summaries.

### Maintenance
- Added CLI coverage for JSON output files on successful and invalid `view`
  calls, plus the `delete --json-output` summary alias.

## v3.18.3
**Release Date**: 2026-05-16

### Maintenance
- Added generated FLAC fixture coverage for Mutagen-backed audio metadata
  extraction and cleanup.
- Verified FLAC cleanup strips Vorbis comments on a copied file while
  preserving the original file metadata and basic stream properties.

## v3.18.2
**Release Date**: 2026-05-16

### Maintenance
- Expanded installed-package smoke coverage to install FFmpeg, FFprobe, and
  ExifTool in CI before testing the built wheel.
- Added smoke assertions for ExifTool-backed JPEG metadata viewing and
  FFmpeg-backed MP4 metadata viewing/removal from the installed CLI.

## v3.18.1
**Release Date**: 2026-05-16

### Features
- Added a local file browser to the Web UI for uploaded originals and cleaned
  copies.
- Added per-file `View` and `Delete` actions for files saved in the current Web
  UI workspace.

### Security
- Scoped Web UI file viewing and deletion to managed upload and cleaned-copy
  directories with filename validation.

## v3.18.0
**Release Date**: 2026-05-15

### Features
- Added `metadata-cleaner web`, a local-only single-page Web UI bound to
  `127.0.0.1` by default.
- The Web UI shows original metadata, creates a cleaned copy, and then shows
  cleaned metadata for side-by-side verification.
- Cleaned copies can be downloaded from the local session without modifying the
  original uploaded file.

### Maintenance
- Shared format-specific processing warnings between CLI reports and the Web UI.
- Added Web API and CLI command coverage for the local Web UI flow.
- Updated CI and release workflows to Poetry 2.3.4.

## v3.17.1
**Release Date**: 2026-05-11

### Maintenance
- Updated the Docker image publishing workflow to `docker/metadata-action@v6`
  for Node 24-compatible GitHub Actions runtime support.

## v3.17.0
**Release Date**: 2026-05-11

### Features
- Added a GitHub Container Registry publishing workflow for tagged releases.
- Docker release images are published as `ghcr.io/sandy-sp/metadata-cleaner`
  with version, minor-version, and `latest` tags.

### Maintenance
- Documented published Docker image usage and release-process behavior.

## v3.16.1
**Release Date**: 2026-05-11

### Maintenance
- Added timestamp-preservation regression coverage for ODT and EPUB cleanup.
- Confirmed package-rewrite document handlers honor
  `preserve_timestamps=True` after metadata removal.

## v3.16.0
**Release Date**: 2026-05-11

### Features
- Added `metadata-cleaner delete --checksum-algorithm sha256|sha512|blake2b`
  for configurable checksum reporting.
- `--checksums` keeps SHA-256 as the default while using algorithm-specific
  report keys such as `input_sha512` and `output_blake2b` when requested.

### Maintenance
- Added direct checksum helper coverage and CLI JSON summary coverage for
  SHA-512 checksum reports.

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
