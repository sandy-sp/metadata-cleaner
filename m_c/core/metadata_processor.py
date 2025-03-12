import os
import concurrent.futures
from typing import Dict, Optional, List
from m_c.core.file_utils import validate_file
from m_c.core.logger import logger
from m_c.utils.tool_utils import ToolManager
from m_c.core.file_utils import get_safe_output_path


class MetadataProcessor:
    def __init__(self):
        self.tools = ToolManager()

    def view_metadata(self, file_path: str) -> Optional[Dict]:
        """Extract metadata from a file using the best available tool."""
        if not validate_file(file_path):
            logger.error(f"File validation failed: {file_path}")
            return {}

        tool = self.tools.get_best_tool(file_path)
        if not tool:
            logger.error(f"No tool available to extract metadata from {file_path}")
            return {}

        try:
            metadata = tool.extract_metadata(file_path)
            if metadata is None:
                logger.warning(f"No metadata found for {file_path}")
                return {}

            return metadata
        except Exception as e:
            logger.error(
                f"Error extracting metadata from {file_path}: {e}", exc_info=True
            )
            return {}

    def delete_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Ensure the cleaned file is correctly saved without modifying the original."""
        if not validate_file(file_path):
            logger.error(f"Invalid file: {file_path}")
            return None

        # Ensure output path is set correctly in 'cleaned/' directory
        if output_path is None:
            cleaned_dir = os.path.join(os.path.dirname(file_path), "cleaned")
            os.makedirs(cleaned_dir, exist_ok=True)
            output_path = os.path.join(cleaned_dir, os.path.basename(file_path))

        tool = self.tools.get_best_tool(file_path)
        if not tool or not hasattr(tool, "remove_metadata"):
            logger.error(f"No tool available to remove metadata from {file_path}")
            return None

        try:
            logger.info(
                f"Removing metadata from: {file_path}, saving to: {output_path}"
            )
            cleaned_file = tool.remove_metadata(file_path, output_path)

            if not cleaned_file or not os.path.exists(cleaned_file):
                logger.error(
                    f"❌ Metadata removal failed: {file_path}. Expected output: {output_path}"
                )
                return None

            logger.info(f"✅ Metadata successfully removed: {cleaned_file}")
            return cleaned_file
        except Exception as e:
            logger.error(
                f"❌ Error removing metadata from {file_path}: {e}", exc_info=True
            )
            return None

    def process_batch(self, files: List[str]) -> List[Optional[str]]:
        """Process multiple files sequentially for metadata removal to ensure correct execution."""
        logger.info(f"Processing batch of {len(files)} files sequentially.")

        results = []
        for file in files:
            logger.info(f"Processing file: {file}")
            try:
                output_path = get_safe_output_path(file, output_dir="cleaned_files")
                result = self.delete_metadata(file, output_path)
                if result:
                    results.append(result)
                    logger.info(f"✅ Successfully processed: {file} -> {result}")
                else:
                    logger.error(f"❌ Failed to process file: {file}")
            except Exception as e:
                logger.error(f"❌ Error processing file {file}: {e}", exc_info=True)
                results.append(None)

        logger.info(
            f"Batch processing completed. {len([r for r in results if r])} out of {len(files)} files cleaned successfully."
        )
        return results

    def edit_metadata(self, file_path: str, metadata_changes: Dict):
        """Ensure metadata editing works even if no initial metadata exists."""
        existing_metadata = self.view_metadata(file_path)
        if not existing_metadata:
            logger.error(f"❌ Cannot edit metadata: No metadata found in {file_path}")
            return file_path

        updated_metadata = {**existing_metadata, **metadata_changes}

        tool = self.tools.get_best_tool(file_path)
        if not tool or not hasattr(tool, "edit_metadata"):
            logger.error(f"❌ No available tool to edit metadata for {file_path}")
            return file_path

        try:
            return tool.edit_metadata(file_path, updated_metadata)
        except Exception as e:
            logger.error(f"❌ Error editing metadata: {e}", exc_info=True)
            return file_path


metadata_processor = MetadataProcessor()
