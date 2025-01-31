import click
import os
from src.logs.logger import logger
from src.core.remover import remove_metadata, remove_metadata_from_folder

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="Path to the file to clean metadata from.")
@click.option('--folder', '-d', type=click.Path(exists=True), help="Path to a folder to clean metadata from all supported files.")
@click.option('--output', '-o', type=click.Path(), help="Path to save the cleaned file(s).")
def main(file, folder, output):
    """CLI for metadata removal. Supports single file or batch processing."""
    try:
        if file:
            logger.info(f"Processing single file: {file}")
            cleaned_file = remove_metadata(file, output)
            click.echo(f"Metadata removed. Cleaned file saved at: {cleaned_file}")

        elif folder:
            logger.info(f"Processing folder: {folder}")
            cleaned_files = remove_metadata_from_folder(folder, output)
            click.echo(f"Processed {len(cleaned_files)} files. Cleaned files saved in: {output if output else folder}")

        else:
            click.echo("Please specify either --file or --folder to process.")
    
    except Exception as e:
        logger.error(f"CLI Error: {e}")
        click.echo(f"Error: {e}")

if __name__ == "__main__":
    main()
