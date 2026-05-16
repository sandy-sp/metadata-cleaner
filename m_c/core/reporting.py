import os


def processing_warnings(file_path: str) -> list[str]:
    """Return format-specific processing warnings for reports and UI surfaces."""
    ext = os.path.splitext(file_path)[1].lower()
    warnings_by_extension = {
        ".png": [
            "PNG metadata removal re-saves image data; inspect output if "
            "pixel-perfect preservation matters."
        ],
        ".pdf": [
            "PDF metadata removal rewrites the document container while "
            "preserving content."
        ],
        ".docx": [
            "DOCX metadata removal rewrites the document package while "
            "preserving content."
        ],
        ".heic": [
            "HEIC metadata removal requires ExifTool and rewrites metadata on "
            "a copied file."
        ],
        ".heif": [
            "HEIF metadata removal requires ExifTool and rewrites metadata on "
            "a copied file."
        ],
        ".epub": [
            "EPUB metadata removal rewrites the book package while preserving "
            "content."
        ],
        ".odt": [
            "ODT metadata removal rewrites the document package while "
            "preserving content."
        ],
        ".mp3": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".wav": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".flac": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".ogg": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".aac": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".m4a": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".wma": ["Audio metadata removal rewrites tags on a copied audio file."],
        ".mp4": ["Video metadata removal remuxes the container with stream copy."],
        ".mkv": ["Video metadata removal remuxes the container with stream copy."],
        ".mov": ["Video metadata removal remuxes the container with stream copy."],
        ".avi": ["Video metadata removal remuxes the container with stream copy."],
        ".webm": ["Video metadata removal remuxes the container with stream copy."],
        ".flv": ["Video metadata removal remuxes the container with stream copy."],
    }
    return warnings_by_extension.get(ext, [])
