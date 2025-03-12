import click
import json
import os
from m_c.core.metadata_processor import MetadataProcessor

@click.group()
def cli():
    """Metadata Cleaner - View, Remove, and Edit Metadata"""
    pass

@cli.command()
@click.argument("file")
def view(file):
    """View metadata of a file"""
    if not os.path.exists(file):
        click.echo("❌ Error: File does not exist.")
        return

    metadata = MetadataProcessor().view_metadata(file)
    if metadata:
        click.echo(json.dumps(metadata, indent=4))
    else:
        click.echo("⚠️ No metadata found or unsupported file format.")

@cli.command()
@click.argument("file")
@click.option("--output", default=None, help="Output file path")
def delete(file, output):
    """Remove metadata from a file"""
    if not os.path.exists(file):
        click.echo("❌ Error: File does not exist.")
        return

    result = MetadataProcessor().delete_metadata(file, output)
    if result:
        click.echo(f"✅ Metadata removed: {result}")
    else:
        click.echo("⚠️ Metadata removal failed. Check logs for details.")

if __name__ == "__main__":
    cli()
