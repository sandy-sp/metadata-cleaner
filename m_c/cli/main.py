import click
import json
import os
from m_c.core.metadata_processor import MetadataProcessor
from m_c.core.logger import logger

def validate_file_existence(file_path):
    """Check if the provided file exists."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        click.echo("❌ Error: File does not exist.")
        return False
    return True

@click.group()
def cli():
    """Metadata Cleaner - View, Remove, and Edit Metadata"""
    pass

@cli.command()
@click.argument("file")
def view(file):
    """View metadata of a file."""
    if not validate_file_existence(file):
        return
    
    try:
        metadata = MetadataProcessor().view_metadata(file)
        if metadata:
            click.echo(json.dumps(metadata, indent=4))
        else:
            click.echo("⚠️ No metadata found or unsupported file format.")
    except Exception as e:
        logger.error(f"Error viewing metadata for {file}: {e}")
        click.echo("Error occurred while retrieving metadata. Check logs for details.")

@cli.command()
@click.argument("file")
@click.option("--output", default=None, help="Output file path")
def delete(file, output):
    """Remove metadata from a file."""
    if not validate_file_existence(file):
        return
    
    try:
        result = MetadataProcessor().delete_metadata(file, output)
        if result:
            click.echo(f"✅ Metadata removed: {result}")
        else:
            click.echo("⚠️ Metadata removal failed. Check logs for details.")
    except Exception as e:
        logger.error(f"Error removing metadata from {file}: {e}")
        click.echo("Error occurred while removing metadata. Check logs for details.")

if __name__ == "__main__":
    cli()
