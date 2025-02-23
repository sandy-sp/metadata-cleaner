import os
import click
from typing import Optional
from metadata_cleaner.logs.logger import logger, set_log_level
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="Path to the file to clean metadata from.")
@click.option('--folder', '-d', type=click.Path(exists=True), help="Path to a folder to clean metadata from all supported files.")
@click.option('--output', '-o', type=click.Path(), help="Path to save the cleaned file(s).")
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation prompts.")
@click.option('--config', '-c', type=click.Path(exists=True), help="Path to configuration file for selective metadata filtering.")
@click.option('--recursive', '-r', is_flag=True, help="Process files in subfolders recursively. (Default: False, only process top-level folder)")
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), help="Set the logging level.")
def main(file: Optional[str],
         folder: Optional[str],
         output: Optional[str],
         yes: bool,
         config: Optional[str],
         recursive: bool,
         log_level: Optional[str]) -> None:
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
    """
    try:
        if log_level:
            set_log_level(log_level.upper())
            logger.info(f"Log level set to {log_level.upper()}")

        if file:
            if not yes and not click.confirm(f"Do you want to process {file}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing single file: {file}")
            cleaned_file = remove_metadata(file, output, config)
            if cleaned_file:
                click.echo(f"✅ Metadata removed. Cleaned file saved at: {cleaned_file}")
            else:
                click.echo(f"⚠️ Failed to process file: {file}")

        elif folder:
            if not yes and not click.confirm(f"Do you want to process all files in {folder}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing folder: {folder}")
            cleaned_files = remove_metadata_from_folder(folder, output, config, recursive)

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
