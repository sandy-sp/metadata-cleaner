import subprocess
import shutil

def remove_video_metadata(file_path, output_path=None):
    """Removes metadata from video files using FFmpeg."""
    try:
        if not output_path:
            output_path = file_path.replace(".", "_cleaned.")

        # Use FFmpeg to re-encode the file and strip metadata
        command = [
            "ffmpeg", "-i", file_path, "-map_metadata", "-1",
            "-c:v", "libx264", "-c:a", "aac", output_path, "-y"
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"Error removing metadata from {file_path}: {e}")
        return None
