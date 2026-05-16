# Architecture

Metadata Cleaner is a small Python CLI organized around file-type handlers.

## Entry Points

- `metadata-cleaner` is exposed by Poetry through `m_c.cli.main:cli`.
- `m_c.cli.main` owns command parsing, recursive file discovery, dry-run output,
  and batch output path mapping.
- `manage.py` provides local development shortcuts for install, test, lint,
  audit, and cleanup tasks.
- `metadata-cleaner web` runs a local-only single-page Web UI that reuses the
  same core processor and writes cleaned copies into a managed workspace.

## Core Flow

1. CLI resolves one file or a recursive set of supported files.
2. `MetadataProcessor` validates the source file and asks `ToolManager` for the
   best handler.
3. The handler extracts, removes, or edits metadata.
4. Metadata removal writes to a separate output path. Handlers refuse destructive
   in-place output paths.

## Handlers

- `ImageHandler`: uses ExifTool when available for AVIF, `piexif` for lossless
  EXIF removal from JPEG/WebP/TIFF, and Pillow fallback re-save for other
  images. ExifTool subprocess calls use bounded timeouts.
- `DocumentHandler`: uses `pypdf` for PDF metadata reads, `pikepdf` for PDF
  metadata removal, and `python-docx` for DOCX core property cleanup. EPUB and
  ODT ZIP packages are checked against entry-count and uncompressed-size limits
  before package members are parsed or rewritten.
- `AudioHandler`: uses Mutagen and writes cleaned copies before modifying tags.
- `VideoHandler`: uses FFprobe for metadata reads and FFmpeg stream copy for
  metadata removal without re-encoding.

## Security And Privacy Notes

- File logging is opt-in through `METADATA_CLEANER_LOG_FILE`; by default logs go
  to stderr only.
- Cleaned outputs are written separately from originals.
- The Web UI binds to localhost by default, rejects public bind hosts, and
  scopes managed file viewing/deletion to upload and cleaned-copy directories.
- Dependency scanning is performed with `pip-audit` in CI.
- Static analysis is performed with CodeQL.
- Docker image builds and installed-package smoke tests are checked in CI so
  Dockerfile and packaging updates are tested before release.
- External ExifTool, FFprobe, and FFmpeg subprocess calls use timeouts so
  malformed files cannot make those tool invocations wait indefinitely.
- EPUB and ODT ZIP package handling enforces archive safety limits to reduce
  zip-bomb style denial-of-service risk.
- The project ignores local logs, local agent state, virtual environments, build
  artifacts, and caches.

## Release Coverage

The package smoke workflow installs the built wheel in a clean virtual
environment and exercises JPEG, PDF, DOCX, WAV, M4A, and MP4 paths with FFmpeg,
FFprobe, and ExifTool available. Release tags publish to PyPI and GitHub
Container Registry after tests, lint, package checks, and dependency audit pass.
