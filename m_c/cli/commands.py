import click
import json
from m_c.core.metadata_processor import MetadataProcessor
from m_c.cli.utils import format_metadata_output
from m_c.core.logger import logger

def validate_json(json_string):
    """Validates JSON input to prevent errors."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        logger.error("Invalid JSON format for metadata changes.")
        return None
@click.command()
@click.argument("file")
def view_metadata(file):
    """Command to view metadata."""
    try:
        metadata = MetadataProcessor().view_metadata(file)
        click.echo(format_metadata_output(metadata))
    except Exception as e:
        logger.error(f"Error viewing metadata for {file}: {e}")
        click.echo("Failed to retrieve metadata. Check logs for details.")

import sys
from tqdm import tqdm
from m_c.core.file_utils import get_supported_files

@click.command()
@click.argument("file")
@click.option("--output", default=None, help="Output file path")
@click.option("--dry-run", is_flag=True, help="Simulate execution without modifying files.")
def delete_metadata(file, output, dry_run):
    """Command to remove metadata."""
    files_to_process = get_supported_files(file)
    
    if not files_to_process:
        click.echo("No supported files found.")
        return

    if len(files_to_process) == 1:
        # Single file case
        try:
            result = MetadataProcessor().delete_metadata(files_to_process[0], output, dry_run=dry_run)
            if dry_run:
                 click.echo("Dry run complete. No files changed.")
            elif result:
                click.echo(f"Metadata removed: {result}")
            else:
                click.echo("Failed to remove metadata. Check logs for details.")
        except Exception as e:
            logger.error(f"Error deleting metadata from {files_to_process[0]}: {e}")
            click.echo("Metadata removal encountered an error. Check logs for details.")
    else:
        # Batch case
        click.echo(f"Processing {len(files_to_process)} files...")
        processor = MetadataProcessor()
        
        # Determine output strategy for batch
        # If output provided, it might imply a directory? Or specific file mapping?
        # Typically recursive delete keeps structure or saves to 'cleaned' folders relative to file.
        # The delete_metadata method handles output=None by creating 'cleaned/' dir.
        
        success_count = 0
        with tqdm(total=len(files_to_process)) as pbar:
            for f in files_to_process:
                try:
                    # For batch, we ignore the single --output flag usually, or use it as a root dest?
                    # Current delete_metadata implementation uses output=None to auto-generate.
                    # We will force output=None for batch to rely on auto-generation unless user specified directory logic which is complex.
                    # Let's rely on auto-gen logic.
                    res = processor.delete_metadata(f, None, dry_run=dry_run)
                    if res or dry_run:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Failed to process {f}: {e}")
                pbar.update(1)
        
        click.echo(f"Completed. Successfully processed {success_count}/{len(files_to_process)} files.")

@click.command()
@click.argument("file")
@click.option("--changes", type=str, help="JSON string of metadata changes")
def edit_metadata(file, changes):
    """Command to edit metadata."""
    changes_dict = validate_json(changes)
    if changes_dict is None:
        click.echo("Invalid JSON format. Please check and try again.")
        return
    
    try:
        result = MetadataProcessor().edit_metadata(file, changes_dict)
        if result:
            click.echo(f"Metadata updated: {result}")
        else:
            click.echo("Failed to edit metadata. Check logs for details.")
    except Exception as e:
        logger.error(f"Error editing metadata for {file}: {e}")
        click.echo("Metadata editing encountered an error. Check logs for details.")
