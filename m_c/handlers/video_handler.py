import os
import subprocess
from typing import Optional, Dict, Any
from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler

class VideoHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for video files.
    Uses FFmpeg for metadata processing.
    """

    SUPPORTED_FORMATS = {"mp4", "mkv", "mov", "avi", "webm", "flv"}

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a video file using FFmpeg."""
        if not self.validate(file_path):
            return None
        return self._extract_metadata_ffmpeg(file_path)

    def remove_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from a video file using FFmpeg."""
        if not self.validate(file_path):
            logger.error(f"🚨 Validation failed for {file_path}")
            return None

        try:
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_cleaned{ext}"

            logger.debug(f"🔍 Removing metadata from video file: {file_path}")

            command = [
                "ffmpeg",
                "-i", file_path,
                "-map_metadata", "-1",
                "-c:v", "copy",
                "-c:a", "copy",
                output_path,
                "-y"
            ]

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if "moov atom not found" in result.stderr or "Invalid data found" in result.stderr:
                logger.error(f"❌ FFmpeg failed: {result.stderr.strip()}")
                return None

            if os.path.exists(output_path):
                logger.info(f"✅ Video metadata removed successfully: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Video was not saved properly: {output_path}")

        except Exception as e:
            logger.error(f"❌ Error processing video file {file_path}: {e}", exc_info=True)
        if not self.validate(file_path):
            return None
        return self._remove_metadata_ffmpeg(file_path, output_path)

    def _extract_metadata_ffmpeg(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using FFmpeg."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    file_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout if result.stdout else None
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed to extract metadata: {e}")
        except Exception as e:
            logger.error(f"Failed to extract metadata from video file: {e}")
        return None

    def _remove_metadata_ffmpeg(self, file_path: str, output_path: Optional[str]) -> Optional[str]:
        """Remove metadata using FFmpeg with improved error handling."""
        try:
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_cleaned{ext}"

            command = [
                "ffmpeg",
                "-i",
                file_path,
                "-map_metadata",
                "-1",
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                output_path,
                "-y",
            ]

            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if "moov atom not found" in result.stderr or "Invalid data found" in result.stderr:
                logger.error(f"❌ FFmpeg failed: {result.stderr.strip()}")
                return None  # Fail gracefully instead of crashing

            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from video: {e}")
        return None

video_handler = VideoHandler()
