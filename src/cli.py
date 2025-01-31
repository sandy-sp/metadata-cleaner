import click
from src.core.remover import remove_metadata

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), required=True, help="Path to the file to clean metadata from.")
@click.option('--output', '-o', type=click.Path(), help="Path to save the cleaned file.")
def main(file, output):
    """CLI for metadata removal."""
    try:
        cleaned_file = remove_metadata(file, output)
        click.echo(f"Metadata removed. Cleaned file saved at: {cleaned_file}")
    except Exception as e:
        click.echo(f"Error: {e}")

if __name__ == "__main__":
    main()
