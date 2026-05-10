# Metadata Cleaner

[![CI](https://github.com/sandy-sp/metadata-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/sandy-sp/metadata-cleaner/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/release/sandy-sp/metadata-cleaner.svg)](https://github.com/sandy-sp/metadata-cleaner/releases)
[![PyPI version](https://badge.fury.io/py/metadata-cleaner.svg)](https://pypi.org/project/metadata-cleaner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Metadata Cleaner is a privacy-focused CLI for viewing and removing metadata from
local files. It writes cleaned copies by default and avoids modifying originals
in-place.

## Supported Files

- Images: JPG, JPEG, PNG, TIFF, WEBP, AVIF
- Documents: PDF, DOCX, TXT
- Audio: MP3, WAV, FLAC, OGG, AAC, M4A, WMA
- Video: MP4, MKV, MOV, AVI, WEBM, FLV

Video support requires `ffmpeg` and `ffprobe`. AVIF and broader metadata
coverage benefit from `exiftool`.

## Installation

Requires Python 3.11 or newer.

```bash
pip install metadata-cleaner
metadata-cleaner --help
```

For development:

```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install --with dev
poetry run metadata-cleaner --help
```

## CLI Usage

View metadata:

```bash
metadata-cleaner view sample.jpg
```

Print metadata for automation:

```bash
metadata-cleaner view sample.jpg --json
```

Remove metadata from one file:

```bash
metadata-cleaner delete sample.jpg
```

Write to a specific file:

```bash
metadata-cleaner delete sample.jpg --output cleaned/sample.jpg
```

Process a folder recursively:

```bash
metadata-cleaner delete ./photos --output ./cleaned-photos
```

Preview a run without writing files:

```bash
metadata-cleaner delete ./photos --dry-run
```

Write a JSON summary report:

```bash
metadata-cleaner delete ./photos --summary-file reports/summary.json
```

Summary reports include per-file status and output paths for audit trails.
Add `--checksums` to include SHA-256 input/output hashes.

Edit metadata where supported:

```bash
metadata-cleaner edit song.mp3 --changes '{"artist": "Unknown"}'
```

## Development Checks

```bash
python3 manage.py test
python3 manage.py lint
python3 manage.py check
```

CI runs tests, lint, and `pip-audit` on pull requests and pushes to `main`.

## Docker

```bash
docker build -t metadata-cleaner .
docker run --rm -v "$(pwd)/photos:/data" metadata-cleaner delete /data
```

## Logging

By default, logs go to stderr only. To write a log file, opt in explicitly:

```bash
METADATA_CLEANER_LOG_FILE=./metadata-cleaner.log metadata-cleaner delete sample.jpg
```

Use debug logging when needed:

```bash
METADATA_CLEANER_LOG_LEVEL=DEBUG metadata-cleaner view sample.jpg
```

## Resources

- [API Reference](docs/API_REFERENCE.md)
- [Usage Guide](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
