# Metadata Cleaner API Reference

The main programmatic entry point is `m_c.core.metadata_processor.MetadataProcessor`.

## `view_metadata(file_path: str) -> dict`

Extract metadata from a supported file. Returns an empty dictionary when the file
has no metadata or the format is unsupported.

```python
from m_c.core.metadata_processor import MetadataProcessor

metadata = MetadataProcessor().view_metadata("image.jpg")
print(metadata)
```

## `delete_metadata(file_path: str, output_path: str | None = None, dry_run: bool = False, preserve_timestamps: bool = False) -> str | None`

Remove metadata and write a cleaned copy. When `output_path` is omitted, the
cleaned file is written under a `cleaned/` directory next to the source file.
When `dry_run=True`, the method returns `None` and does not create output files
or directories. Pass `preserve_timestamps=True` to copy the source access and
modification times to the cleaned file after metadata removal.

```python
from m_c.core.metadata_processor import MetadataProcessor

cleaned_file = MetadataProcessor().delete_metadata("image.jpg")
print(cleaned_file)
```

## `edit_metadata(file_path: str, metadata_changes: dict) -> str | None`

Edit metadata for formats whose handler supports editing. Currently this is most
useful for audio files through Mutagen. Editing may modify the target file in
place; use metadata removal when you need a cleaned copy.

```python
from m_c.core.metadata_processor import MetadataProcessor

updated_file = MetadataProcessor().edit_metadata(
    "song.mp3",
    {"artist": "Unknown"},
)
print(updated_file)
```

## CLI Exit Codes

The CLI returns stable exit codes for automation:

- `0`: success.
- `1`: processing failure.
- `2`: invalid input, usage error, or no supported files.
- `3`: partial batch failure.

## Machine-Readable CLI Output

Use `metadata-cleaner view FILE --json` to get a stable JSON envelope with
`status`, `file`, `metadata_count`, and `metadata` fields. Invalid file input
returns exit code `2` with `status` set to `invalid_input`. Use
`metadata-cleaner view FILE --json-output report.json` to write that envelope
to a file.

Use `metadata-cleaner delete PATH --json-summary` to print a machine-readable
summary to stdout, or `metadata-cleaner delete PATH --summary-file report.json`
to write the same summary payload to a file. `--json-output report.json` is a
shared alias for the delete summary file. Delete summaries include top-level
counts plus a `files` list with each input path, per-file status, output path,
format-specific processing notes, and failure reason when available. Processing
notes describe copy, rewrite, re-save, ExifTool, tag deletion, or stream-copy
remux behavior when applicable.

Pass `--checksums` with `delete` to include hashes in each per-file result.
SHA-256 is the default. Use `--checksum-algorithm sha256|sha512|blake2b` to
select the report algorithm. Dry-run summaries include input hashes and leave
output hashes empty; completed cleaning summaries include both input and output
hashes when files are available.

Use `--report-detail full|compact|summary` to control JSON verbosity. `full` is
the default and preserves all per-file fields, `compact` keeps minimal per-file
status fields, and `summary` omits per-file entries.

Use `--report-filter all|failed` to control which per-file entries are included
when per-file entries are present. `failed` keeps aggregate counts unchanged and
lists only failed file entries.

## Local Web UI

Use `metadata-cleaner web` to start a local-only single-page Web UI on
`127.0.0.1`. The Web UI accepts a selected file, displays the original metadata,
creates a cleaned copy, and then displays cleaned-copy metadata for comparison.
The original file is never modified. The local file browser lists uploaded
originals and cleaned copies from the current Web UI workspace, and supports
viewing or deleting those managed files.
