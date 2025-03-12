import click
import json
from metadata_cleaner.core.metadata_processor import metadata_processor

@click.group()
def cli():
    """Metadata Cleaner - View, Remove, and Edit Metadata"""
    pass

@cli.command()
@click.argument("file")
def view(file):
    """View metadata of a file"""
    metadata = metadata_processor.view_metadata(file)
    if metadata:
        click.echo(json.dumps(metadata, indent=4))
    else:
        click.echo("No metadata found or unsupported file format.")

@cli.command()
@click.argument("file")
@click.option("--output", default=None, help="Output file path")
def delete(file, output):
    """Remove metadata from a file"""
    result = metadata_processor.delete_metadata(file, output)
    if result:
        click.echo(f"Metadata removed: {result}")
    else:
        click.echo("Failed to remove metadata.")

@cli.command()
@click.argument("file")
@click.option("--changes", type=str, help="JSON string of metadata changes")
def edit(file, changes):
    """Edit metadata of a file"""
    try:
        changes_dict = json.loads(changes)
        result = metadata_processor.edit_metadata(file, changes_dict)
        if result:
            click.echo(f"Metadata updated: {result}")
        else:
            click.echo("Failed to edit metadata.")
    except json.JSONDecodeError:
        click.echo("Invalid JSON format for metadata changes.")

if __name__ == "__main__":
    cli()
