import click
import json
from m_c.core.metadata_processor import MetadataProcessor
from m_c.cli.utils import format_metadata_output


@click.command()
@click.argument("file")
def view_metadata(file):
    """Command to view metadata."""
    metadata = MetadataProcessor.view_metadata(file)
    click.echo(format_metadata_output(metadata))


@click.command()
@click.argument("file")
@click.option("--output", default=None, help="Output file path")
def delete_metadata(file, output):
    """Command to remove metadata."""
    result = MetadataProcessor.delete_metadata(file, output)
    if result:
        click.echo(f"Metadata removed: {result}")
    else:
        click.echo("Failed to remove metadata.")


@click.command()
@click.argument("file")
@click.option("--changes", type=str, help="JSON string of metadata changes")
def edit_metadata(file, changes):
    """Command to edit metadata."""
    try:
        changes_dict = json.loads(changes)
        result = MetadataProcessor.edit_metadata(file, changes_dict)
        if result:
            click.echo(f"Metadata updated: {result}")
        else:
            click.echo("Failed to edit metadata.")
    except json.JSONDecodeError:
        click.echo("Invalid JSON format for metadata changes.")
