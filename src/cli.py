import os
import click
from src.logs.logger import logger
from src.remover import remove_metadata, remove_metadata_from_folder

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="Path to the file to clean metadata from.")
@click.option('--folder', '-d', type=click.Path(exists=True), help="Path to a folder to clean metadata from all supported files.")
@click.option('--output', '-o', type=click.Path(), help="Path to save the cleaned file(s).")
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation prompts.")
def main(file, folder, output, yes):
    """CLI for metadata removal. Supports single file or batch processing with interactivity."""
    try:
        if file:
            if not yes and not click.confirm(f"Do you want to process {file}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing single file: {file}")
            cleaned_file = remove_metadata(file, output)
            if cleaned_file:
                click.echo(f"✅ Metadata removed. Cleaned file saved at: {cleaned_file}")
            else:
                click.echo(f"⚠️ Failed to process file: {file}")

        elif folder:
            if not yes and not click.confirm(f"Do you want to process all files in {folder}?", default=True):
                click.echo("❌ Operation cancelled.")
                return

            logger.info(f"Processing folder: {folder}")
            cleaned_files = remove_metadata_from_folder(folder, output)

            # Display summary report
            click.echo("\n📊 **Summary Report:**")
            click.echo(f"✅ Successfully processed: {len(cleaned_files)} files")

            if cleaned_files:
                click.echo(f"Cleaned files saved in: {output if output else folder}")

        else:
            click.echo("❌ Please specify either --file or --folder to process.")

    except Exception as e:
        logger.error(f"CLI Error: {e}")
        click.echo(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
