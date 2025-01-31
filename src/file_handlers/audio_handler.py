from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

def remove_audio_metadata(file_path, output_path=None):
    """Removes metadata from MP3 and other audio files."""
    try:
        audio = MP3(file_path, ID3=EasyID3)
        audio.delete()
        audio.save()
    except Exception as e:
        print(f"Error removing metadata from {file_path}: {e}")

    return file_path
