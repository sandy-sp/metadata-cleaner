import os
from typing import Dict, Optional, List
import concurrent.futures
from m_c.core.tool_manager import ToolManager
from m_c.core.file_utils import validate_file
from m_c.core.logger import logger

class MetadataProcessor:
    def __init__(self):
        self.tools = ToolManager()

    def view_metadata(self, file_path: str) -> Optional[Dict]:
        """Extract metadata from a file using the best available tool."""
        if not validate_file(file_path):
            return None
        
        tool = self.tools.get_best_tool(file_path)
        if not tool:
            logger.error(f"No tool available to extract metadata from {file_path}")
            return None
        
        return tool.extract_metadata(file_path)

    def delete_metadata(self, file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Remove metadata from a file using the best tool."""
        if not validate_file(file_path):
            return None

        tool = self.tools.get_best_tool(file_path)
        if not tool:
            logger.error(f"No tool available to remove metadata from {file_path}")
            return None

        return tool.remove_metadata(file_path, output_path)

    def edit_metadata(self, file_path: str, metadata_changes: Dict):
        """
        Edits metadata for a given file while preserving existing metadata.

        Args:
            file_path (str): Path to the file.
            metadata_changes (Dict): Dictionary of metadata fields to update.

        Returns:
            str: Path to the modified file if successful, None otherwise.
        """
        existing_metadata = self.view_metadata(file_path)
        if not existing_metadata:
            logger.error(f"❌ Unable to retrieve existing metadata for {file_path}")
            return None

        # Merge existing metadata with new changes
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

    def process_batch(files: List[str]):
        """Process multiple files in parallel for metadata removal."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(metadata_processor.delete_metadata, files))
        return results

metadata_processor = MetadataProcessor()
