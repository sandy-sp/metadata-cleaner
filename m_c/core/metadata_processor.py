import os
import concurrent.futures
from typing import Dict, Optional, List
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
            return tool.extract_metadata(file_path)
        except Exception as e:
            logger.error(
                f"Error extracting metadata from {file_path}: {e}", exc_info=True
            )
            return None

    def delete_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Ensure the cleaned file is correctly saved."""
        if not validate_file(file_path):
            logger.error(f"Invalid file: {file_path}")
            return None

        tool = self.tools.get_best_tool(file_path)
        if not tool or not hasattr(tool, "remove_metadata"):
            logger.error(f"No tool available to remove metadata from {file_path}")
            return None

        try:
            cleaned_file = tool.remove_metadata(file_path, output_path)
            if not cleaned_file or not os.path.exists(cleaned_file):
                logger.error(
                    f"Metadata removal failed: Output file missing {cleaned_file}"
                )
                return None

            return cleaned_file
        except Exception as e:
            logger.error(f"Error removing metadata from {file_path}: {e}")
            return None

    def process_batch(self, files: List[str]) -> List[Optional[str]]:
        """Process multiple files in parallel for metadata removal."""
        logger.info(f"Processing batch of {len(files)} files in parallel.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.delete_metadata, files))

        logger.info(
            f"Batch processing completed. {sum(1 for r in results if r)} files cleaned."
        )
        return results

    def edit_metadata(self, file_path: str, metadata_changes: Dict):
        """Ensure metadata editing works even if no initial metadata exists."""
        existing_metadata = self.view_metadata(file_path)
        if not existing_metadata:
            logger.error(f"❌ Cannot edit metadata: No metadata found in {file_path}")
            return file_path  # Return the original file path instead of None

        updated_metadata = {**existing_metadata, **metadata_changes}

        tool = self.tools.get_best_tool(file_path)
        if not tool or not hasattr(tool, 'edit_metadata'):
            logger.error(f"❌ No available tool to edit metadata for {file_path}")
            return file_path

        try:
            return tool.edit_metadata(file_path, updated_metadata)
        except Exception as e:
            logger.error(f"❌ Error editing metadata: {e}")
            return file_path


metadata_processor = MetadataProcessor()
