import pymediainfo

def remove_video_metadata(file_path, output_path=None):
    """Removes metadata from video files using pymediainfo."""
    try:
        metadata = pymediainfo.MediaInfo.parse(file_path)
        metadata.delete()
    except Exception as e:
        print(f"Error removing metadata from {file_path}: {e}")

    return file_path
