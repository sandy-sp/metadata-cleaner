import os
import subprocess
from typing import Optional, Dict, Any
from m_c.core.logger import logger
from m_c.core.file_utils import validate_file
from m_c.utils.tool_utils import ToolManager

class VideoHandler:
    """
    Handles metadata extraction, removal, and editing for video files.
    """
    SUPPORTED_FORMATS = {"mp4", "mkv", "mov", "avi", "webm", "flv"}

    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        return ext in self.SUPPORTED_FORMATS

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a video file using FFmpeg."""
        if not validate_file(file_path) or not self.is_supported(file_path):
            return None

        if not ToolManager.available_tools["FFmpeg"]:
            logger.error("FFmpeg is not installed or available.")
            return None

        return self._extract_metadata_ffmpeg(file_path)

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from a video file using FFmpeg."""
        if not validate_file(file_path) or not self.is_supported(file_path):
            return None

        if not ToolManager.available_tools["FFmpeg"]:
            logger.error("FFmpeg is not installed or available.")
            return None

        return self._remove_metadata_ffmpeg(file_path, output_path)

    def _extract_metadata_ffmpeg(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using FFmpeg."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path],
                capture_output=True, text=True, check=True
            )
            return result.stdout if result.stdout else None
        except Exception as e:
            logger.error(f"FFmpeg failed to extract metadata: {e}")
            return None

    def _remove_metadata_ffmpeg(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Remove metadata using FFmpeg."""
        try:
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_cleaned{ext}"

            command = [
                "ffmpeg", "-i", file_path, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", output_path, "-y"
            ]

            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return output_path
        except Exception as e:
            logger.error(f"FFmpeg failed to remove metadata: {e}")
            return None

video_handler = VideoHandler()
