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

@click.command()
@click.argument("file")
@click.option("--output", default=None, help="Output file path")
def delete_metadata(file, output):
    """Command to remove metadata."""
    try:
        result = MetadataProcessor().delete_metadata(file, output)
        if result:
            click.echo(f"Metadata removed: {result}")
        else:
            click.echo("Failed to remove metadata. Check logs for details.")
    except Exception as e:
        logger.error(f"Error deleting metadata from {file}: {e}")
        click.echo("Metadata removal encountered an error. Check logs for details.")

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
