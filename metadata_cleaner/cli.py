import os
import json
import click
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger, set_log_level
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder, dry_run_metadata_removal
from metadata_cleaner.config.settings import SUPPORTED_FORMATS
from metadata_cleaner.file_handlers.metadata_extractor import extract_metadata

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="File path to clean metadata from.")
@click.option('--folder', '-d', type=click.Path(exists=True), help="Folder path containing files to process.")
@click.option('--output', '-o', type=click.Path(), help="Output directory for cleaned files.")
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation prompts.")
@click.option('--config', '-c', type=click.Path(exists=True), help="Path to metadata filtering config file.")
@click.option('--recursive', '-r', is_flag=True, help="Process subfolders recursively.")
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
              help="Set logging level.")
@click.option('--view-metadata', is_flag=True, help="View metadata for a specified file.")
@click.option('--dry-run', is_flag=True, help="Simulate metadata removal without modifying the file.")
@click.option('--list-formats', is_flag=True, help="List supported file formats.")
@click.option('--quiet', '-q', is_flag=True, help="Suppress non-essential output.")
@click.option('--remove-gps', is_flag=True, help="Remove GPS metadata from images.")
@click.option('--keep-timestamp', is_flag=True, help="Preserve timestamp in images.")
@click.option('--prefix', type=str, help="Custom prefix for cleaned file names.")
@click.option('--suffix', type=str, help="Custom suffix for cleaned file names.")
@click.option('--version', is_flag=True, help="Show version and exit.")
def main(file: Optional[str],
         folder: Optional[str],
         output: Optional[str],
         yes: bool,
         config: Optional[str],
         recursive: bool,
         log_level: Optional[str],
         view_metadata: bool,
         dry_run: bool,
         list_formats: bool,
         quiet: bool,
         remove_gps: bool,
         keep_timestamp: bool,
         prefix: Optional[str],
         suffix: Optional[str],
         version: bool) -> None:
    """
    🧹 Metadata Cleaner - CLI

    A powerful command-line tool for removing metadata from images, documents, audio, and video files.
    """
    try:
        if version:
            display_version()
            return

        if list_formats:
            display_supported_formats()
            return

        if log_level:
            set_log_level(log_level.upper())
            logger.info(f"Log level set to {log_level.upper()}")

        if quiet:
            logger.setLevel('ERROR')

        if file:
            process_file(file, output, yes, config, view_metadata, dry_run, remove_gps, keep_timestamp, prefix, suffix)
        elif folder:
            process_folder(folder, output, yes, config, recursive, remove_gps, keep_timestamp, prefix, suffix)
        else:
            click.echo("❌ Please specify either --file or --folder to process.")

    except Exception as e:
        logger.error(f"CLI Error: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}")

def display_version():
    """Displays the current version of Metadata Cleaner."""
    try:
        from importlib.metadata import version as get_version
        tool_version = get_version('metadata-cleaner')
    except Exception:
        try:
            from metadata_cleaner import __version__ as tool_version
        except Exception:
            logger.error("Could not retrieve version information")
            tool_version = "unknown version"
    click.echo(f"Metadata Cleaner v{tool_version}")

def display_supported_formats():
    """Lists all supported file formats."""
    click.echo("📁 Supported File Formats:")
    for category, extensions in SUPPORTED_FORMATS.items():
        click.echo(f"📂 {category.title()}: {', '.join(extensions)}")

def process_file(file: str, output: Optional[str], yes: bool, config: Optional[str], 
                 view_metadata: bool, dry_run: bool, remove_gps: bool, 
                 keep_timestamp: bool, prefix: Optional[str], suffix: Optional[str]):
    """Processes a single file for metadata operations."""
    if view_metadata:
        metadata = extract_metadata(file)
        click.echo(f"🔍 Metadata for {file}:\n" + json.dumps(metadata, indent=4))
        return

    if dry_run:
        metadata_comparison = dry_run_metadata_removal(file)
        click.echo(f"📝 Dry-Run Metadata Removal for {file}:\n" + json.dumps(metadata_comparison, indent=4))
        return

    if not yes and not click.confirm(f"📌 Process file: {file}?", default=True):
        click.echo("❌ Operation cancelled.")
        return

    metadata_config = load_metadata_config(config, remove_gps, keep_timestamp)
    cleaned_file = remove_metadata(file, output, metadata_config, prefix, suffix)

    if cleaned_file:
        click.echo(f"✅ Cleaned file saved at: {cleaned_file}")
    else:
        click.echo(f"⚠️ Failed to process file: {file}")

def process_folder(folder: str, output: Optional[str], yes: bool, config: Optional[str],
                   recursive: bool, remove_gps: bool, keep_timestamp: bool,
                   prefix: Optional[str], suffix: Optional[str]):
    """Processes all supported files in a folder."""
    if not yes and not click.confirm(f"📁 Process folder: {folder}?", default=True):
        click.echo("❌ Operation cancelled.")
        return

    metadata_config = load_metadata_config(config, remove_gps, keep_timestamp)
    cleaned_files = remove_metadata_from_folder(folder, output, recursive)

    click.echo("\n📊 Summary Report:")
    click.echo(f"✅ Processed {len(cleaned_files)} files")
    if cleaned_files:
        click.echo(f"Cleaned files saved in: {output if output else folder}")

def load_metadata_config(config_path: Optional[str], remove_gps: bool, keep_timestamp: bool) -> Dict:
    """Loads metadata filtering configuration from a JSON file or CLI options."""
    metadata_config = {}
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                metadata_config.update(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading config file {config_path}: {e}")
            click.echo(f"⚠️ Invalid config file: {config_path}. Using default settings.")

    if remove_gps:
        metadata_config['GPS'] = 'remove'
    if keep_timestamp:
        metadata_config['Timestamp'] = 'exact'

    return metadata_config

if __name__ == "__main__":
    main()
