# Architecture

Metadata Cleaner is a small Python CLI organized around file-type handlers.

## Entry Points

- `metadata-cleaner` is exposed by Poetry through `m_c.cli.main:cli`.
- `m_c.cli.main` owns command parsing, recursive file discovery, dry-run output,
  and batch output path mapping.
- `manage.py` provides local development shortcuts for install, test, lint,
  audit, and cleanup tasks.

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
  metadata removal, and `python-docx` for DOCX core property cleanup.
- `AudioHandler`: uses Mutagen and writes cleaned copies before modifying tags.
- `VideoHandler`: uses FFprobe for metadata reads and FFmpeg stream copy for
  metadata removal without re-encoding.

## Security And Privacy Notes

- File logging is opt-in through `METADATA_CLEANER_LOG_FILE`; by default logs go
  to stderr only.
- Cleaned outputs are written separately from originals.
- Dependency scanning is performed with `pip-audit` in CI.
- Static analysis is performed with CodeQL.
- Docker image builds are checked in CI so Dockerfile updates are tested before
  release.
- External ExifTool, FFprobe, and FFmpeg subprocess calls use timeouts so
  malformed files cannot make those tool invocations wait indefinitely.
- The project ignores local logs, local agent state, virtual environments, build
  artifacts, and caches.
