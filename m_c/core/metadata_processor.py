import os
from typing import Dict, Optional, List
import concurrent.futures
from m_c.core.file_utils import validate_file
from m_c.core.logger import logger
from m_c.utils.tool_utils import ToolManager

class MetadataProcessor:
    def __init__(self):
        self.tools = ToolManager()

    def view_metadata(self, file_path: str) -> Optional[Dict]:
        """Extract metadata from a file using the best available tool."""
        if not validate_file(file_path):
            logger.error(f"File validation failed: {file_path}")
            return None

        tool = self.tools.get_best_tool(file_path)
        if not tool:
            logger.error(f"No tool available to extract metadata from {file_path}")
            return None

        try:
            metadata = tool.extract_metadata(file_path)
            if not metadata:
                logger.warning(f"No metadata found for: {file_path}")
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}", exc_info=True)
            return None

    def delete_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata and ensure the output directory exists."""
        if not validate_file(file_path):
            logger.error(f"Invalid file: {file_path}")
            return None

        tool = self.tools.get_best_tool(file_path)
        if not tool or not hasattr(tool, 'remove_metadata'):
            logger.error(f"No tool available to remove metadata from {file_path}")
            return None

        try:
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure output directory exists
            cleaned_file = tool.remove_metadata(file_path, output_path)

            if not cleaned_file or not os.path.exists(cleaned_file):
                logger.error(f"Metadata removal failed for: {file_path}")
                return None

            logger.info(f"✅ Metadata cleaned: {cleaned_file}")
            return cleaned_file
        except Exception as e:
            logger.error(f"Error removing metadata from {file_path}: {e}", exc_info=True)
            return None

    def edit_metadata(self, file_path: str, metadata_changes: Dict):
        """Edit metadata while preserving existing metadata."""
        existing_metadata = self.view_metadata(file_path)
        if not existing_metadata:
            logger.error(f"❌ Unable to retrieve existing metadata for {file_path}")
            return None

        updated_metadata = {**existing_metadata, **metadata_changes}

        tool = self.tools.get_best_tool(file_path)
        if not tool or not hasattr(tool, 'edit_metadata'):
            logger.error(f"❌ No available tool to edit metadata for {file_path}")
            return None

        try:
            return tool.edit_metadata(file_path, updated_metadata)
        except Exception as e:
            logger.error(f"❌ Error editing metadata: {e}", exc_info=True)
            return None

metadata_processor = MetadataProcessor()
