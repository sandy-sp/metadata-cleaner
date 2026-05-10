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
returns exit code `2` with `status` set to `invalid_input`.

Use `metadata-cleaner delete PATH --json-summary` to print a machine-readable
summary to stdout, or `metadata-cleaner delete PATH --summary-file report.json`
to write the same summary payload to a file. Delete summaries include top-level
counts plus a `files` list with each input path, per-file status, output path,
format-specific processing warnings, and failure reason when available.

Pass `--checksums` with `delete` to include SHA-256 hashes in each per-file
result. Dry-run summaries include input hashes and leave output hashes empty;
completed cleaning summaries include both input and output hashes when files are
available.

Use `--report-detail full|compact|summary` to control JSON verbosity. `full` is
the default and preserves all per-file fields, `compact` keeps minimal per-file
status fields, and `summary` omits per-file entries.
