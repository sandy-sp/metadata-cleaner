import shutil

class ToolManager:
    """Manages tool availability and selection."""

    _cached_tools = None  # Cache for tool availability

    def check_tools(self):
        """Check for available tools and cache the results."""
        if self._cached_tools is None:
            self._cached_tools = {
                "ExifTool": shutil.which("exiftool") is not None,
                "FFmpeg": shutil.which("ffmpeg") is not None,
                "Mutagen": True  # Mutagen is a Python module, always available if installed
            }
        return self._cached_tools

    def get_best_tool(self, file_path: str):
        """Returns the best tool object for the given file type."""
        ext = file_path.split('.')[-1].lower()
        tools = self.check_tools()

        if ext in ["jpg", "jpeg", "png", "tiff", "webp"]:
            from m_c.handlers.image_handler import ImageHandler
            return ImageHandler
        elif ext in ["pdf", "docx", "txt"]:
            from m_c.handlers.document_handler import DocumentHandler
            return DocumentHandler
        elif ext in ["mp3", "wav", "flac"]:
            from m_c.handlers.audio_handler import AudioHandler
            return AudioHandler
        elif ext in ["mp4", "mkv", "avi"]:
            from m_c.handlers.video_handler import VideoHandler
            return VideoHandler
        return None

tool_manager = ToolManager()
