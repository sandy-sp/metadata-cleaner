import os
import subprocess
import json
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

        from m_c.utils.tool_utils import ToolManager

        tools = ToolManager().check_tools()
        if not tools["FFprobe"] or not tools["FFmpeg"]:
            logger.error(
                "FFmpeg/FFprobe not found. Please install them to process videos."
            )
            return None

        return self._extract_metadata_ffmpeg(file_path)

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from a video file using FFmpeg."""
        if not self.validate(file_path):
            logger.error(f"Validation failed for {file_path}")
            return None

        from m_c.utils.tool_utils import ToolManager

        if not ToolManager().check_tools()["FFmpeg"]:
            logger.error("FFmpeg not found. Please install it to process videos.")
            return None

        try:
            output_path = self.prepare_output_path(file_path, output_path)

            logger.debug(f"Removing metadata from video file: {file_path}")

            command = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                file_path,
                "-map",
                "0",
                "-map_metadata",
                "-1",
                "-c",
                "copy",
                output_path,
                "-y",
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr.strip()}")
                return None

            if os.path.exists(output_path):
                logger.info(f"Video metadata removed: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Error processing video file {file_path}: {e}", exc_info=True)
        return None

    def _extract_metadata_ffmpeg(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using FFprobe."""
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
                timeout=60,
            )
            return json.loads(result.stdout) if result.stdout else {}
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed to extract metadata: {e}")
        except Exception as e:
            logger.error(f"Failed to extract metadata from video file: {e}")
        return None

    def _remove_metadata_ffmpeg(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
        """Remove metadata using FFmpeg with improved error handling."""
        try:
            if not output_path:
                output_path = self.prepare_output_path(file_path, output_path)

            command = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                file_path,
                "-map",
                "0",
                "-map_metadata",
                "-1",
                "-c",
                "copy",
                output_path,
                "-y",
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr.strip()}")
                return None

            return output_path if os.path.exists(output_path) else None
        except Exception as e:
            logger.error(f"Failed to remove metadata from video: {e}")
        return None


video_handler = VideoHandler()
