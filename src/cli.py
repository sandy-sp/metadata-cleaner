import click

@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help="Path to the file to clean metadata from.")
@click.option('--output', '-o', type=click.Path(), help="Path to save the cleaned file.")
def main(file, output):
    """Simple CLI for metadata removal."""
    if not file:
        click.echo("Please provide a file path using --file or -f.")
        return

    click.echo(f"Processing file: {file}")
    if output:
        click.echo(f"Output will be saved to: {output}")

if __name__ == "__main__":
    main()
