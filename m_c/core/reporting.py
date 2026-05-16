import os


def processing_warnings(file_path: str) -> list[str]:
    """Return format-specific processing warnings for reports and UI surfaces."""
    ext = os.path.splitext(file_path)[1].lower()
    warnings_by_extension = {
        ".jpg": [
            "JPEG metadata removal copies the file first and removes EXIF "
            "tags in-place on the copy when possible; pixel data is not "
            "re-encoded on that path."
        ],
        ".jpeg": [
            "JPEG metadata removal copies the file first and removes EXIF "
            "tags in-place on the copy when possible; pixel data is not "
            "re-encoded on that path."
        ],
        ".png": [
            "PNG metadata removal re-saves image data with Pillow because PNG "
            "text chunks are not stripped in-place; inspect output if "
            "pixel-perfect binary preservation matters."
        ],
        ".tiff": [
            "TIFF metadata removal copies the file first and removes EXIF tags "
            "in-place on the copy when possible; Pillow re-save is used only "
            "as a fallback."
        ],
        ".webp": [
            "WebP metadata removal copies the file first and removes EXIF tags "
            "in-place on the copy when possible; Pillow re-save is used only "
            "as a fallback."
        ],
        ".pdf": [
            "PDF metadata removal rewrites the PDF container and removes "
            "document info/XMP metadata while preserving page content."
        ],
        ".docx": [
            "DOCX metadata removal rewrites the Office package and clears "
            "core properties while preserving document content."
        ],
        ".avif": [
            "AVIF metadata removal requires ExifTool and strips metadata on a "
            "copied file without intentionally re-encoding image pixels."
        ],
        ".heic": [
            "HEIC metadata removal requires ExifTool and strips metadata on a "
            "copied file without intentionally re-encoding image pixels."
        ],
        ".heif": [
            "HEIF metadata removal requires ExifTool and strips metadata on a "
            "copied file without intentionally re-encoding image pixels."
        ],
        ".epub": [
            "EPUB metadata removal rewrites the book package and neutralizes "
            "package metadata while preserving manifest content."
        ],
        ".odt": [
            "ODT metadata removal rewrites the OpenDocument package and clears "
            "meta.xml while preserving document content."
        ],
        ".mp3": [
            "Audio metadata removal copies the file first, then Mutagen deletes "
            "tags on the copy; audio frames are not intentionally re-encoded."
        ],
        ".wav": [
            "Audio metadata removal copies the file first, then Mutagen deletes "
            "tags on the copy; audio samples are not intentionally re-encoded."
        ],
        ".flac": [
            "FLAC metadata removal copies the file first, then Mutagen deletes "
            "Vorbis comments on the copy; audio frames are not intentionally "
            "re-encoded."
        ],
        ".ogg": [
            "Audio metadata removal copies the file first, then Mutagen deletes "
            "tags on the copy; audio frames are not intentionally re-encoded."
        ],
        ".aac": [
            "Audio metadata removal copies the file first, then Mutagen deletes "
            "tags on the copy; audio frames are not intentionally re-encoded."
        ],
        ".m4a": [
            "Audio metadata removal copies the file first, then Mutagen deletes "
            "tags on the copy; audio frames are not intentionally re-encoded."
        ],
        ".wma": [
            "Audio metadata removal copies the file first, then Mutagen deletes "
            "tags on the copy; audio frames are not intentionally re-encoded."
        ],
        ".mp4": [
            "Video metadata removal remuxes the container with FFmpeg stream "
            "copy; media streams are not intentionally re-encoded."
        ],
        ".mkv": [
            "Video metadata removal remuxes the container with FFmpeg stream "
            "copy; media streams are not intentionally re-encoded."
        ],
        ".mov": [
            "Video metadata removal remuxes the container with FFmpeg stream "
            "copy; media streams are not intentionally re-encoded."
        ],
        ".avi": [
            "Video metadata removal remuxes the container with FFmpeg stream "
            "copy; media streams are not intentionally re-encoded."
        ],
        ".webm": [
            "Video metadata removal remuxes the container with FFmpeg stream "
            "copy; media streams are not intentionally re-encoded."
        ],
        ".flv": [
            "Video metadata removal remuxes the container with FFmpeg stream "
            "copy; media streams are not intentionally re-encoded."
        ],
    }
    return warnings_by_extension.get(ext, [])
