import json


def format_metadata_output(metadata):
    """Formats metadata output for CLI display."""
    if metadata:
        return json.dumps(metadata, indent=4)
    return "No metadata found or unsupported file format."
