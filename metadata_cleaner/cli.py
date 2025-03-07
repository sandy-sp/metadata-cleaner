import os
import json
import click
from typing import Optional, Dict
from metadata_cleaner.logs.logger import logger, set_log_level
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder
from metadata_cleaner.config.settings import SUPPORTED_FORMATS


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="File path to clean metadata from.")
@click.option('--folder', '-d', type=click.Path(exists=True), help="Folder path containing files to process.")
@click.option('--output', '-o', type=click.Path(), help="Output directory for cleaned files.")
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation prompts.")
@click.option('--config', '-c', type=click.Path(exists=True), help="Path to metadata filtering config file.")
@click.option('--recursive', '-r', is_flag=True, help="Process subfolders recursively.")
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
              help="Set logging level.")
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

    Features:
    - Support for various file formats
    - Batch processing with recursive folder support
    - Selective metadata filtering using config files
    - Quiet mode for automation
    - Custom prefix and suffix for output filenames

    Usage Examples:
    - Clean a single file: metadata-cleaner --file path/to/file.jpg
    - Process a folder: metadata-cleaner --folder path/to/folder
    - List supported formats: metadata-cleaner --list-formats
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
            process_single_file(file, output, yes, config, remove_gps, keep_timestamp, prefix, suffix)
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


def load_metadata_config(config_path: Optional[str], remove_gps: bool, keep_timestamp: bool) -> Dict:
    """
    Loads metadata filtering configuration, either from a provided JSON file or from CLI options.

    Args:
        config_path (Optional[str]): Path to JSON config file.
        remove_gps (bool): Flag to remove GPS metadata from images.
        keep_timestamp (bool): Flag to preserve timestamp metadata.

    Returns:
        Dict: Parsed metadata filtering rules.
    """
    metadata_config = {}

    if config_path:
        try:
            with open(config_path, 'r') as f:
                metadata_config.update(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading config file {config_path}: {e}")
            click.echo(f"⚠️ Invalid config file: {config_path}. Using default settings.")

    if remove_gps:
        metadata_config['GPS'] = 'remove'
    if keep_timestamp:
        metadata_config['Timestamp'] = 'exact'

    return metadata_config


def process_single_file(file: str, output: Optional[str], yes: bool, config: Optional[str],
                        remove_gps: bool, keep_timestamp: bool, prefix: Optional[str], suffix: Optional[str]):
    """
    Processes a single file to remove metadata.

    Args:
        file (str): File path to clean metadata from.
        output (Optional[str]): Output directory.
        yes (bool): Whether to skip confirmation prompts.
        config (Optional[str]): Path to config file.
        remove_gps (bool): Flag to remove GPS metadata.
        keep_timestamp (bool): Flag to preserve timestamp metadata.
        prefix (Optional[str]): Custom prefix for cleaned filenames.
        suffix (Optional[str]): Custom suffix for cleaned filenames.
    """
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
    """
    Processes all supported files in a folder.

    Args:
        folder (str): Folder path to process.
        output (Optional[str]): Output directory.
        yes (bool): Whether to skip confirmation prompts.
        config (Optional[str]): Path to config file.
        recursive (bool): Whether to process files recursively.
        remove_gps (bool): Flag to remove GPS metadata.
        keep_timestamp (bool): Flag to preserve timestamp metadata.
        prefix (Optional[str]): Custom prefix for cleaned filenames.
        suffix (Optional[str]): Custom suffix for cleaned filenames.
    """
    if not yes and not click.confirm(f"📁 Process folder: {folder}?", default=True):
        click.echo("❌ Operation cancelled.")
        return

    metadata_config = load_metadata_config(config, remove_gps, keep_timestamp)
    cleaned_files = remove_metadata_from_folder(folder, output, metadata_config, recursive, prefix, suffix)

    click.echo("\n📊 Summary Report:")
    click.echo(f"✅ Processed {len(cleaned_files)} files")
    if cleaned_files:
        click.echo(f"Cleaned files saved in: {output if output else folder}")


if __name__ == "__main__":
    main()
