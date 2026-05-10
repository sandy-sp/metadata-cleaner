# Metadata Cleaner Usage

## Install

```bash
pip install metadata-cleaner
```

For local development:

```bash
poetry install --with dev
poetry run metadata-cleaner --help
```

## Commands

View metadata:

```bash
metadata-cleaner view my_photo.jpg
```

Remove metadata from one file:

```bash
metadata-cleaner delete my_photo.jpg
```

Remove metadata and choose an output file:

```bash
metadata-cleaner delete my_photo.jpg --output cleaned/my_photo.jpg
```

Process a directory recursively:

```bash
metadata-cleaner delete ./images --output ./cleaned-images
```

Preview work without creating files:

```bash
metadata-cleaner delete ./images --dry-run
```

Edit metadata for formats with editing support:

```bash
metadata-cleaner edit song.mp3 --changes '{"artist": "Unknown"}'
```

## Supported Formats

- Images: JPEG, PNG, TIFF, WebP, AVIF
- Documents: PDF, DOCX, TXT
- Audio: MP3, WAV, FLAC, OGG, AAC, M4A, WMA
- Video: MP4, MKV, MOV, AVI, WebM, FLV

Some formats require system tools:

- AVIF cleanup uses ExifTool.
- Video metadata reads use FFprobe.
- Video metadata removal uses FFmpeg.

## Logging

Logs are written to stderr by default. To opt into file logging:

```bash
METADATA_CLEANER_LOG_FILE=./metadata-cleaner.log metadata-cleaner delete sample.jpg
```

To increase verbosity:

```bash
METADATA_CLEANER_LOG_LEVEL=DEBUG metadata-cleaner view sample.jpg
```
