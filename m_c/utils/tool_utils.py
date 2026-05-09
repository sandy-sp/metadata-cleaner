import shutil
from pathlib import Path
from m_c.handlers.image_handler import ImageHandler
from m_c.handlers.document_handler import DocumentHandler
from m_c.handlers.audio_handler import AudioHandler
from m_c.handlers.video_handler import VideoHandler
from m_c.core.logger import logger


class ToolManager:
    """Manages tool availability and selection."""

    _cached_tools = None  # Cache for tool availability

    def check_tools(self):
        """Check available tools and cache the results."""
        if self._cached_tools is None:
            self._cached_tools = {
                "ExifTool": shutil.which("exiftool") is not None,
                "FFmpeg": shutil.which("ffmpeg") is not None,
                "FFprobe": shutil.which("ffprobe") is not None,
                "Mutagen": True,  # Mutagen is a Python module, always available if installed
            }
        logger.info(f"Tool Availability Check: {self._cached_tools}")
        return self._cached_tools

    def get_best_tool(self, file_path: str):
        """Return best tool for given file type."""
        ext = Path(file_path).suffix.lower().lstrip(".")
        if ext in ImageHandler.SUPPORTED_FORMATS:
            return ImageHandler()
        elif ext in DocumentHandler.SUPPORTED_FORMATS:
            return DocumentHandler()
        elif ext in AudioHandler.SUPPORTED_FORMATS:
            return AudioHandler()
        elif ext in VideoHandler.SUPPORTED_FORMATS:
            return VideoHandler()
        logger.warning(f"No tool found for file type: {ext}")
        return None


tool_manager = ToolManager()
