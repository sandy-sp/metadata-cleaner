# Metadata Cleaner Usage

## Install

```bash
pip install metadata-cleaner
```

Requires Python 3.11 or newer. Video support needs `ffmpeg` and `ffprobe`;
AVIF, HEIC, and HEIF cleanup needs `exiftool`.

For local development:

```bash
poetry install --with dev
poetry run metadata-cleaner --help
```

## Global Options

Enable debug logs for any command:

```bash
metadata-cleaner --verbose view my_photo.jpg
```

Write logs to a rotating file:

```bash
metadata-cleaner --log-file ./metadata-cleaner.log delete sample.jpg
```

## Commands

View metadata:

```bash
metadata-cleaner view my_photo.jpg
```

Print metadata in a stable JSON envelope:

```bash
metadata-cleaner view my_photo.jpg --json
```

Write metadata JSON to a file:

```bash
metadata-cleaner view my_photo.jpg --json-output reports/metadata.json
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

Batch runs end with a structured summary:

```text
Summary: succeeded=12, failed=1, skipped=0, total=13
```

Print a machine-readable summary:

```bash
metadata-cleaner delete ./images --json-summary
```

Write the summary to a JSON file:

```bash
metadata-cleaner delete ./images --summary-file reports/summary.json
```

You can also use the shared JSON output option:

```bash
metadata-cleaner delete ./images --json-output reports/summary.json
```

Include SHA-256 checksums in JSON summaries:

```bash
metadata-cleaner delete ./images --summary-file reports/summary.json --checksums
```

Choose a different checksum algorithm:

```bash
metadata-cleaner delete ./images --json-summary --checksums --checksum-algorithm sha512
```

Control JSON report verbosity for large batches:

```bash
metadata-cleaner delete ./images --json-summary --report-detail compact
metadata-cleaner delete ./images --summary-file reports/summary.json --report-detail summary
```

List only failed per-file entries while preserving top-level counts:

```bash
metadata-cleaner delete ./images --json-summary --report-filter failed
```

Preserve source access and modification times on cleaned files:

```bash
metadata-cleaner delete ./images --output ./cleaned-images --preserve-timestamps
```

Start the local Web UI:

```bash
metadata-cleaner web
```

The Web UI creates cleaned copies and displays original metadata beside cleaned
metadata for local verification. Use the `Files` button to view or delete
uploaded originals and cleaned copies saved in the current local session.
By default the Web UI uses a temporary workspace that is removed when the server
stops. Use `--workspace ./metadata-cleaner-workspace` to keep uploaded originals
and cleaned copies between local sessions.

JSON summaries include top-level counts and per-file details:

```json
{
  "status": "partial_failure",
  "succeeded": 12,
  "failed": 1,
  "files": [
    {
      "input": "images/photo.jpg",
      "status": "success",
      "output": "cleaned-images/photo.jpg",
      "warnings": [
        "Format-specific processing notes describe copy, rewrite, re-save, "
        "tag deletion, or remux behavior when applicable."
      ],
      "checksums": {
        "input_sha256": "<sha256>",
        "output_sha256": "<sha256>"
      }
    }
  ]
}
```

Suppress human progress/output for automation:

```bash
metadata-cleaner delete ./images --json-summary --quiet
```

Preview work without creating files:

```bash
metadata-cleaner delete ./images --dry-run
```

Edit metadata for formats with editing support:

```bash
metadata-cleaner edit song.mp3 --changes '{"artist": "Unknown"}'
```

## Exit Codes

- `0`: command completed successfully.
- `1`: command ran but all processing failed.
- `2`: invalid input, unsupported single-file input, usage issue, or no
  supported files were found.
- `3`: batch processing completed with partial failures.

## Supported Formats

- Images: JPEG, PNG, TIFF, WebP, AVIF, HEIC, HEIF
- Documents: PDF, DOCX, EPUB, ODT, TXT
- Audio: MP3, WAV, FLAC, OGG, AAC, M4A, WMA
- Video: MP4, MKV, MOV, AVI, WebM, FLV

Some formats require system tools:

- AVIF cleanup uses ExifTool.
- HEIC and HEIF cleanup use ExifTool.
- Video metadata reads use FFprobe.
- Video metadata removal uses FFmpeg.

## Docker

Published release images include FFmpeg, FFprobe, and ExifTool:

```bash
docker run --rm -v "$(pwd):/data" ghcr.io/sandy-sp/metadata-cleaner:latest delete /data/photos
```

## Privacy Notes

Metadata removal writes cleaned copies and keeps originals unchanged. Some
formats are rewritten, re-saved, or remuxed during cleanup; JSON reports include
per-file processing notes for these cases. For high-risk publishing workflows,
inspect cleaned files with independent tools before release.

## Logging

Logs are written to stderr by default. To opt into file logging:

```bash
metadata-cleaner --log-file ./metadata-cleaner.log delete sample.jpg
```

To increase verbosity:

```bash
metadata-cleaner --verbose view sample.jpg
```

The environment variables `METADATA_CLEANER_LOG_FILE` and
`METADATA_CLEANER_LOG_LEVEL` are also supported for automation.
