import json
import os
from typing import Optional

import click
from tqdm import tqdm

from m_c.cli.utils import format_metadata_output
from m_c.core.file_utils import get_safe_output_path, get_supported_files
from m_c.core.logger import logger
from m_c.core.metadata_processor import MetadataProcessor


def _parse_json_option(json_string: str) -> Optional[dict]:
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        logger.error("Invalid JSON format for metadata changes.")
        return None


def _batch_output_path(
    input_root: str, file_path: str, output_root: Optional[str]
) -> str:
    if output_root is None:
        return get_safe_output_path(
            file_path,
            output_dir=os.path.join(os.path.dirname(file_path), "cleaned"),
        )

    base_root = input_root if os.path.isdir(input_root) else os.path.dirname(file_path)
    relative_path = os.path.relpath(file_path, start=base_root or ".")
    target_path = os.path.join(output_root, relative_path)
    return get_safe_output_path(target_path)


@click.group()
def cli():
    """Metadata Cleaner - view, remove, and edit metadata."""


@cli.command()
@click.argument("file")
def view(file):
    """View metadata of a file."""
    if not os.path.isfile(file):
        click.echo("Error: file does not exist or is not a regular file.")
        return

    metadata = MetadataProcessor().view_metadata(file)
    click.echo(format_metadata_output(metadata))


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Output file path or batch directory.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed.")
def delete(path, output, dry_run):
    """Remove metadata from a file or supported files in a directory."""
    files_to_process = get_supported_files(path)
    if not files_to_process:
        click.echo("No supported files found.")
        return

    processor = MetadataProcessor()
    if len(files_to_process) == 1 and not os.path.isdir(path):
        result = processor.delete_metadata(files_to_process[0], output, dry_run=dry_run)
        if dry_run:
            click.echo("Dry run complete. No files changed.")
        elif result:
            click.echo(f"Metadata removed: {result}")
        else:
            click.echo("Metadata removal failed. Check logs for details.")
        return

    success_count = 0
    click.echo(f"Processing {len(files_to_process)} files...")
    with tqdm(total=len(files_to_process)) as pbar:
        for file_path in files_to_process:
            try:
                output_path = _batch_output_path(path, file_path, output)
                result = processor.delete_metadata(
                    file_path,
                    output_path,
                    dry_run=dry_run,
                )
                if result or dry_run:
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            pbar.update(1)

    if dry_run:
        click.echo(f"Dry run complete. {success_count} files would be processed.")
    else:
        click.echo(
            f"Completed. Successfully processed {success_count}/{len(files_to_process)} files."
        )


@cli.command()
@click.argument("file")
@click.option("--changes", required=True, help="JSON object of metadata changes.")
def edit(file, changes):
    """Edit metadata for supported formats with editing support."""
    if not os.path.isfile(file):
        click.echo("Error: file does not exist or is not a regular file.")
        return

    changes_dict = _parse_json_option(changes)
    if changes_dict is None:
        click.echo("Invalid JSON format. Please check and try again.")
        return

    result = MetadataProcessor().edit_metadata(file, changes_dict)
    if result:
        click.echo(f"Metadata updated: {result}")
    else:
        click.echo("Metadata editing failed or is unsupported for this file.")


if __name__ == "__main__":
    cli()
