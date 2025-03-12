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
        """Returns the best tool available for the given file type."""
        ext = file_path.split('.')[-1].lower()
        
        # Ensure tools are checked only once per session
        tools = self.check_tools()

        if ext in ["jpg", "jpeg", "png", "tiff", "webp"]:
            return "ExifTool" if tools["ExifTool"] else "Piexif"
        elif ext in ["pdf", "docx", "txt"]:
            return "PyMuPDF"
        elif ext in ["mp3", "wav", "flac"]:
            return "Mutagen"
        elif ext in ["mp4", "mkv", "avi"]:
            return "FFmpeg"
        return None  # No suitable tool found

tool_manager = ToolManager()
