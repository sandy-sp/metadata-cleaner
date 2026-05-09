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

## `delete_metadata(file_path: str, output_path: str | None = None, dry_run: bool = False) -> str | None`

Remove metadata and write a cleaned copy. When `output_path` is omitted, the
cleaned file is written under a `cleaned/` directory next to the source file.

```python
from m_c.core.metadata_processor import MetadataProcessor

cleaned_file = MetadataProcessor().delete_metadata("image.jpg")
print(cleaned_file)
```

## `edit_metadata(file_path: str, metadata_changes: dict) -> str | None`

Edit metadata for formats whose handler supports editing. Currently this is most
useful for audio files through Mutagen.

```python
from m_c.core.metadata_processor import MetadataProcessor

updated_file = MetadataProcessor().edit_metadata(
    "song.mp3",
    {"artist": "Unknown"},
)
print(updated_file)
```
