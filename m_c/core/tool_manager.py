import shutil
from metadata_cleaner.handlers import image_handler, document_handler, audio_handler, video_handler

class ToolManager:
    def __init__(self):
        self.tools = {
            "image": image_handler,
            "document": document_handler,
            "audio": audio_handler,
            "video": video_handler
        }
        self.available_tools = self.check_tools()

    def check_tools(self):
        """Check if external tools are available on the system."""
        return {
            "ExifTool": shutil.which("exiftool") is not None,
            "FFmpeg": shutil.which("ffmpeg") is not None,
            "Mutagen": True  # Python module, always available if installed
        }

    def get_best_tool(self, file_path: str):
        """Return the best available tool based on file type."""
        ext = file_path.split('.')[-1].lower()
        if ext in ["jpg", "jpeg", "png", "tiff", "webp"]:
            return self.tools["image"]
        elif ext in ["pdf", "docx", "txt"]:
            return self.tools["document"]
        elif ext in ["mp3", "wav", "flac"]:
            return self.tools["audio"]
        elif ext in ["mp4", "mkv", "avi"]:
            return self.tools["video"]
        else:
            return None

tool_manager = ToolManager()
