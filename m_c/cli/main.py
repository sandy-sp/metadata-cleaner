import json
import os
from dataclasses import dataclass, field
from typing import Optional

import click
from tqdm import tqdm

from m_c.cli.utils import format_metadata_output
from m_c.core.file_utils import get_safe_output_path, get_supported_files
from m_c.core.logger import configure_logging, logger
from m_c.core.metadata_processor import MetadataProcessor

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2
EXIT_PARTIAL_FAILURE = 3


@dataclass
class BatchSummary:
    total: int
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    failures: list[str] = field(default_factory=list)


def _echo_batch_summary(summary: BatchSummary, dry_run: bool) -> None:
    if dry_run:
        click.echo(
            "Dry run summary: "
            f"would_process={summary.succeeded}, "
            f"failed={summary.failed}, skipped={summary.skipped}, "
            f"total={summary.total}"
        )
    else:
        click.echo(
            "Summary: "
            f"succeeded={summary.succeeded}, failed={summary.failed}, "
            f"skipped={summary.skipped}, total={summary.total}"
        )

    for failure in summary.failures[:10]:
        click.echo(f"Failed: {failure}")

    if len(summary.failures) > 10:
        click.echo(f"Additional failures: {len(summary.failures) - 10}")


def _exit_for_summary(ctx: click.Context, summary: BatchSummary, dry_run: bool) -> None:
    if dry_run:
        ctx.exit(EXIT_SUCCESS if summary.failed == 0 else EXIT_PARTIAL_FAILURE)
    if summary.succeeded == summary.total:
        ctx.exit(EXIT_SUCCESS)
    if summary.succeeded == 0:
        ctx.exit(EXIT_FAILURE)
    ctx.exit(EXIT_PARTIAL_FAILURE)


def _parse_json_option(json_string: str) -> Optional[dict]:
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        logger.error("Invalid JSON format for metadata changes.")
        return None


def _batch_output_path(
    input_root: str,
    file_path: str,
    output_root: Optional[str],
    create_dirs: bool = True,
) -> str:
    if output_root is None:
        return get_safe_output_path(
            file_path,
            output_dir=os.path.join(os.path.dirname(file_path), "cleaned"),
            create_dirs=create_dirs,
        )

    base_root = input_root if os.path.isdir(input_root) else os.path.dirname(file_path)
    relative_path = os.path.relpath(file_path, start=base_root or ".")
    target_path = os.path.join(output_root, relative_path)
    return get_safe_output_path(target_path, create_dirs=create_dirs)


@click.group()
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
@click.option(
    "--log-file",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Write logs to a rotating file.",
)
def cli(verbose, log_file):
    """Metadata Cleaner - view, remove, and edit metadata."""
    configure_logging(verbose=verbose, log_file=log_file)


@cli.command()
@click.argument("file")
@click.pass_context
def view(ctx, file):
    """View metadata of a file."""
    if not os.path.isfile(file):
        click.echo("Error: file does not exist or is not a regular file.")
        ctx.exit(EXIT_USAGE)

    metadata = MetadataProcessor().view_metadata(file)
    click.echo(format_metadata_output(metadata))


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Output file path or batch directory.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed.")
@click.pass_context
def delete(ctx, path, output, dry_run):
    """Remove metadata from a file or supported files in a directory."""
    files_to_process = get_supported_files(path)
    if not files_to_process:
        click.echo("No supported files found.")
        ctx.exit(EXIT_USAGE)

    processor = MetadataProcessor()
    if len(files_to_process) == 1 and not os.path.isdir(path):
        result = processor.delete_metadata(files_to_process[0], output, dry_run=dry_run)
        if dry_run:
            click.echo("Dry run complete. No files changed.")
            ctx.exit(EXIT_SUCCESS)
        elif result:
            click.echo(f"Metadata removed: {result}")
            ctx.exit(EXIT_SUCCESS)
        else:
            click.echo("Metadata removal failed. Check logs for details.")
            ctx.exit(EXIT_FAILURE)

    summary = BatchSummary(total=len(files_to_process))
    click.echo(f"Processing {len(files_to_process)} files...")
    with tqdm(total=len(files_to_process)) as pbar:
        for file_path in files_to_process:
            try:
                output_path = _batch_output_path(
                    path,
                    file_path,
                    output,
                    create_dirs=not dry_run,
                )
                result = processor.delete_metadata(
                    file_path,
                    output_path,
                    dry_run=dry_run,
                )
                if result or dry_run:
                    summary.succeeded += 1
                else:
                    summary.failed += 1
                    summary.failures.append(file_path)
            except Exception as e:
                summary.failed += 1
                summary.failures.append(file_path)
                logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            pbar.update(1)

    _echo_batch_summary(summary, dry_run)
    _exit_for_summary(ctx, summary, dry_run)


@cli.command()
@click.argument("file")
@click.option("--changes", required=True, help="JSON object of metadata changes.")
@click.pass_context
def edit(ctx, file, changes):
    """Edit metadata for supported formats with editing support."""
    if not os.path.isfile(file):
        click.echo("Error: file does not exist or is not a regular file.")
        ctx.exit(EXIT_USAGE)

    changes_dict = _parse_json_option(changes)
    if changes_dict is None:
        click.echo("Invalid JSON format. Please check and try again.")
        ctx.exit(EXIT_USAGE)

    result = MetadataProcessor().edit_metadata(file, changes_dict)
    if result:
        click.echo(f"Metadata updated: {result}")
        ctx.exit(EXIT_SUCCESS)
    else:
        click.echo("Metadata editing failed or is unsupported for this file.")
        ctx.exit(EXIT_FAILURE)


if __name__ == "__main__":
    cli()
