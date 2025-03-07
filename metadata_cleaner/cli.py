import os
import click
from typing import Optional
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
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), help="Set logging level.")
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
    🧹 Metadata Cleaner

    A powerful tool for removing metadata from files.

    Features:
    - Support for images, documents, audio, and video files
    - Batch processing with recursive folder support
    - Selective metadata filtering using config files
    - Quiet mode for automated workflows

    Usage Examples:
    - Clean a single file: metadata-cleaner --file path/to/file.jpg
    - Process a folder: metadata-cleaner --folder path/to/folder
    - List supported formats: metadata-cleaner --list-formats

    Parameters:
        File path to clean metadata from.
        Folder path containing files to process.
        Output directory for cleaned files.
        Skip confirmation prompts.
        Path to metadata filtering config file.
        Process subfolders recursively.
        Set logging level (DEBUG, INFO, WARNING, ERROR).
        List supported file formats.
        Suppress non-essential output.
        Remove GPS metadata from images.
        Preserve timestamp in images.
        Custom prefix for cleaned file names.
        Custom suffix for cleaned file names.
        Show version and exit.
    """
    try:
        if version:
            try:
                from importlib.metadata import version as get_version
                version = get_version('metadata-cleaner')
            except Exception:
                try:
                    from metadata_cleaner import __version__ as version
                except Exception:
                    logger.error("Could not retrieve version information")
                    version = "unknown version"
            click.echo(f"Metadata Cleaner v{version}")
            return

        if list_formats:
            click.echo("Supported file formats:")
            for category, extensions in SUPPORTED_FORMATS.items():
                click.echo(f"📁 {category.title()}: {', '.join(extensions)}")
            return

        if log_level:
            set_log_level(log_level.upper())
            logger.info(f"Log level set to {log_level.upper()}")

        if quiet:
            logger.setLevel('ERROR')

        if file:
            if not yes and not click.confirm(f"📌 Process file: {file}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing file: {file}")
            metadata_config = {}
            if remove_gps:
                metadata_config['GPS'] = 'remove'
            if keep_timestamp:
                metadata_config['Timestamp'] = 'exact'

            if config:
                import json
                with open(config, 'r') as f:
                    config_data = json.load(f)
                    metadata_config.update(config_data)

            cleaned_file = remove_metadata(file, output, metadata_config)
            if cleaned_file:
                click.echo(f"✅ Cleaned file saved at: {cleaned_file}")
            else:
                click.echo(f"⚠️  Failed to process file: {file}")

        elif folder:
            if not yes and not click.confirm(f"📁 Process folder: {folder}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing folder: {folder}")
            metadata_config = {}
            if remove_gps:
                metadata_config['GPS'] = 'remove'
            if keep_timestamp:
                metadata_config['Timestamp'] = 'exact'

            if config:
                import json
                with open(config, 'r') as f:
                    config_data = json.load(f)
                    metadata_config.update(config_data)

            cleaned_files = remove_metadata_from_folder(
                folder,
                output,
                metadata_config,
                recursive,
                prefix=prefix,
                suffix=suffix
            )

            click.echo("\n📊 Summary Report:")
            click.echo(f"✅ Processed {len(cleaned_files)} files")
            if cleaned_files:
                click.echo(f"Cleaned files saved in: {output if output else folder}")

        else:
            click.echo("❌ Please specify either --file or --folder to process.")

    except Exception as e:
        logger.error(f"CLI Error: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
