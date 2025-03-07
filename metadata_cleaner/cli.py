import os
import click
from typing import Optional
from metadata_cleaner.logs.logger import logger, set_log_level
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder
from metadata_cleaner.config.settings import SUPPORTED_FORMATS

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="Path to the file to clean metadata from.")
@click.option('--folder', '-d', type=click.Path(exists=True), help="Path to a folder to clean metadata from all supported files.")
@click.option('--output', '-o', type=click.Path(), help="Path to save the cleaned file(s).")
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation prompts.")
@click.option('--config', '-c', type=click.Path(exists=True), help="Path to configuration file for selective metadata filtering.")
@click.option('--recursive', '-r', is_flag=True, help="Process files in subfolders recursively. (Default: False, only process top-level folder)")
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), help="Set the logging level.")
@click.option('--list-formats', is_flag=True, help="List supported file formats and exit.")
@click.option('--quiet', '-q', is_flag=True, help="Suppress all non-essential output.")
@click.option('--remove-gps', is_flag=True, help="Remove GPS metadata from images.")
@click.option('--keep-timestamp', is_flag=True, help="Keep the timestamp (DateTimeOriginal) in images.")
@click.option('--prefix', type=str, help="Custom prefix for cleaned file names.")
@click.option('--suffix', type=str, help="Custom suffix for cleaned file names.")
@click.option('--version', is_flag=True, help="Show the version and exit.")
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
    Command-line interface for Metadata Cleaner.

    Parameters:
        file (Optional[str]): Path to a single file to clean metadata from.
        folder (Optional[str]): Path to a folder to clean metadata from all supported files.
        output (Optional[str]): Custom output directory or file path for cleaned files.
        yes (bool): If True, skip confirmation prompts.
        config (Optional[str]): Path to a JSON configuration file for selective metadata filtering.
        recursive (bool): If True, process files in subfolders recursively.
        log_level (Optional[str]): Logging level (DEBUG, INFO, WARNING, ERROR).
        list_formats (bool): List supported file formats and exit.
        quiet (bool): Suppress all non-essential output.
        remove_gps (bool): Remove GPS metadata from images.
        keep_timestamp (bool): Keep the timestamp (DateTimeOriginal) in images.
        prefix (Optional[str]): Custom prefix for cleaned file names.
        suffix (Optional[str]): Custom suffix for cleaned file names.
        version (bool): Show the version and exit.
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
                click.echo(f"{category.title()}: {', '.join(extensions)}")
            return

        if log_level:
            set_log_level(log_level.upper())
            logger.info(f"Log level set to {log_level.upper()}")

        if quiet:
            logger.setLevel('ERROR')

        if file:
            if not yes and not click.confirm(f"Do you want to process {file}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing single file: {file}")
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
                click.echo(f"✅ Metadata removed. Cleaned file saved at: {cleaned_file}")
            else:
                click.echo(f"⚠️ Failed to process file: {file}")

        elif folder:
            if not yes and not click.confirm(f"Do you want to process all files in {folder}?", default=True):
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
            click.echo(f"✅ Successfully processed: {len(cleaned_files)} files")
            if cleaned_files:
                click.echo(f"Cleaned files saved in: {output if output else folder}")

        else:
            click.echo("❌ Please specify either --file or --folder to process.")

    except Exception as e:
        logger.error(f"CLI Error: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
