# Metadata Cleaner

[![CI](https://github.com/sandy-sp/metadata-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/sandy-sp/metadata-cleaner/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/release/sandy-sp/metadata-cleaner.svg)](https://github.com/sandy-sp/metadata-cleaner/releases)
[![PyPI version](https://badge.fury.io/py/metadata-cleaner.svg)](https://pypi.org/project/metadata-cleaner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Metadata Cleaner is a privacy-focused local tool for viewing and removing
metadata from images, documents, audio, and video files. It writes cleaned
copies by default, keeps originals unchanged, and includes CLI, JSON automation,
Docker, and a local Web UI for side-by-side metadata checks.

## Highlights

- View metadata before cleaning.
- Remove metadata into separate cleaned copies.
- Compare original and cleaned metadata in a local-only Web UI.
- Process individual files or recursive folders.
- Generate machine-readable JSON reports for automation.
- Add SHA-256, SHA-512, or BLAKE2b checksums to reports.
- Preserve source timestamps on cleaned outputs when needed.
- Publish-ready CI coverage for Python, package smoke tests, Docker builds,
  CodeQL, and dependency audits.

## Supported Files

- Images: JPG, JPEG, PNG, TIFF, WEBP, AVIF, HEIC, HEIF
- Documents: PDF, DOCX, EPUB, ODT, TXT
- Audio: MP3, WAV, FLAC, OGG, AAC, M4A, WMA
- Video: MP4, MKV, MOV, AVI, WEBM, FLV

Some formats need system tools for best coverage:

- `ffmpeg` and `ffprobe` are required for video metadata handling.
- `exiftool` is required for AVIF, HEIC, and HEIF cleanup and improves image
  metadata coverage.
- The published Docker image includes these optional tools.

## Install

Requires Python 3.11 or newer.

```bash
pip install metadata-cleaner
metadata-cleaner --help
```

Use Docker when you want the optional system tools preinstalled:

```bash
docker run --rm -v "$(pwd):/data" ghcr.io/sandy-sp/metadata-cleaner:latest delete /data/photos
```

For development:

```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install --with dev
poetry run metadata-cleaner --help
```

## Quick Start

View metadata:

```bash
metadata-cleaner view sample.jpg
```

Clean one file:

```bash
metadata-cleaner delete sample.jpg
```

By default, the cleaned copy is written under a `cleaned/` directory next to the
source file. To choose the output path:

```bash
metadata-cleaner delete sample.jpg --output cleaned/sample.jpg
```

Preview a folder run without writing files:

```bash
metadata-cleaner delete ./photos --dry-run
```

Clean a folder recursively:

```bash
metadata-cleaner delete ./photos --output ./cleaned-photos
```

## Local Web UI

Start a single-page local Web UI:

```bash
metadata-cleaner web
```

The Web UI binds to `127.0.0.1` by default, shows original metadata beside
cleaned-copy metadata, and lets you download cleaned files. The `Files` button
lists uploaded originals and cleaned copies from the current local session with
view and delete actions.

Temporary Web UI files are stored in a temporary directory unless you provide a
workspace:

```bash
metadata-cleaner web --workspace ./metadata-cleaner-workspace
```

## Automation

Print metadata as JSON:

```bash
metadata-cleaner view sample.jpg --json
```

Write metadata JSON to a file:

```bash
metadata-cleaner view sample.jpg --json-output reports/metadata.json
```

Write a delete summary report:

```bash
metadata-cleaner delete ./photos --summary-file reports/summary.json
```

The shared `--json-output reports/summary.json` option writes the same delete
summary payload.

Add checksums:

```bash
metadata-cleaner delete ./photos --summary-file reports/summary.json --checksums
metadata-cleaner delete ./photos --json-summary --checksums --checksum-algorithm sha512
```

Use compact reports for large jobs:

```bash
metadata-cleaner delete ./photos --json-summary --report-detail compact
metadata-cleaner delete ./photos --json-summary --report-filter failed
```

Summary reports include per-file status, output paths, optional checksums,
failure reasons, and format-specific processing notes that explain whether a
handler copies, rewrites, re-saves, uses ExifTool, deletes audio tags, or remuxes
video with FFmpeg stream copy.

## Safety Model

- Originals are not modified by metadata removal.
- Handlers reject in-place cleanup where input and output paths are the same.
- EPUB and ODT ZIP packages are checked against archive safety limits before
  metadata XML is read or rewritten.
- ExifTool, FFmpeg, and FFprobe subprocess calls use bounded timeouts.
- Logs go to stderr by default; file logging is opt-in.
- The Web UI is local-only by default and scopes file viewing/deletion to its
  managed workspace.

This tool removes common metadata fields using format-specific libraries and
system tools. It is not a guarantee that every possible identifying byte,
watermark, hidden payload, or content-derived signal has been removed. For
high-risk publishing workflows, inspect outputs with independent tools before
release.

## Edit Metadata

Editing is available only where handlers support it, currently most useful for
audio files through Mutagen:

```bash
metadata-cleaner edit song.mp3 --changes '{"artist": "Unknown"}'
```

Use metadata removal when you need a cleaned copy. Editing may modify the target
file in place.

## Development Checks

```bash
python3 manage.py test
python3 manage.py lint
python3 manage.py check
```

CI runs tests, lint, `pip-audit`, package smoke coverage, Docker builds, and
CodeQL on protected branches and pull requests.

## Resources

- [Usage Guide](https://github.com/sandy-sp/metadata-cleaner/blob/main/docs/USAGE.md)
- [API Reference](https://github.com/sandy-sp/metadata-cleaner/blob/main/docs/API_REFERENCE.md)
- [Architecture](https://github.com/sandy-sp/metadata-cleaner/blob/main/docs/ARCHITECTURE.md)
- [Maintenance And Security](https://github.com/sandy-sp/metadata-cleaner/blob/main/docs/MAINTENANCE.md)
- [Roadmap](https://github.com/sandy-sp/metadata-cleaner/blob/main/docs/PLANNED_FEATURES.md)
- [Release Notes](https://github.com/sandy-sp/metadata-cleaner/blob/main/RELEASE_NOTES.md)
- [Security Policy](https://github.com/sandy-sp/metadata-cleaner/blob/main/SECURITY.md)
- [Contributing](https://github.com/sandy-sp/metadata-cleaner/blob/main/CONTRIBUTING.md)
