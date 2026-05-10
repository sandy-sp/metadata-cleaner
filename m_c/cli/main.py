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
    files: list[dict] = field(default_factory=list)


def _summary_status(summary: BatchSummary, dry_run: bool) -> str:
    if summary.total == 0:
        return "no_supported_files"
    if dry_run:
        return "success" if summary.failed == 0 else "partial_failure"
    if summary.succeeded == summary.total:
        return "success"
    if summary.succeeded == 0:
        return "failure"
    return "partial_failure"


def _summary_payload(summary: BatchSummary, dry_run: bool) -> dict:
    return {
        "status": _summary_status(summary, dry_run),
        "dry_run": dry_run,
        "total": summary.total,
        "succeeded": summary.succeeded,
        "failed": summary.failed,
        "skipped": summary.skipped,
        "would_process": summary.succeeded if dry_run else None,
        "failures": summary.failures,
        "files": summary.files,
    }


def _metadata_payload(file_path: str, metadata: Optional[dict], status: str) -> dict:
    metadata = metadata or {}
    return {
        "status": status,
        "file": file_path,
        "metadata_count": len(metadata),
        "metadata": metadata,
    }


def _echo_json(payload: dict) -> None:
    click.echo(json.dumps(payload, default=str, sort_keys=True))


def _write_json_payload(file_path: str, payload: dict) -> bool:
    try:
        output_dir = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(output_dir, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as output_file:
            json.dump(payload, output_file, default=str, indent=2, sort_keys=True)
            output_file.write("\n")
        return True
    except OSError as exc:
        logger.error(f"Failed to write JSON output to {file_path}: {exc}")
        return False


def _write_summary_file(
    summary_file: Optional[str],
    summary: BatchSummary,
    dry_run: bool,
    quiet: bool = False,
) -> bool:
    if not summary_file:
        return True

    if _write_json_payload(summary_file, _summary_payload(summary, dry_run)):
        return True

    if not quiet:
        click.echo(f"Failed to write summary file: {summary_file}")
    return False


def _echo_batch_summary(
    summary: BatchSummary,
    dry_run: bool,
    json_summary: bool = False,
    quiet: bool = False,
) -> None:
    if json_summary:
        _echo_json(_summary_payload(summary, dry_run))
        return

    if quiet:
        return

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


def _single_output_path(file_path: str, output_path: Optional[str]) -> str:
    if output_path:
        return output_path
    return os.path.join(os.path.dirname(file_path), "cleaned", os.path.basename(file_path))


def _record_file_result(
    summary: BatchSummary,
    input_path: str,
    status: str,
    output_path: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    item = {
        "input": input_path,
        "status": status,
        "output": output_path,
    }
    if error:
        item["error"] = error
    summary.files.append(item)


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
@click.option("--json", "json_output", is_flag=True, help="Print a JSON metadata payload.")
@click.pass_context
def view(ctx, file, json_output):
    """View metadata of a file."""
    if not os.path.isfile(file):
        message = "file does not exist or is not a regular file"
        if json_output:
            payload = _metadata_payload(file, {}, "invalid_input")
            payload["error"] = message
            _echo_json(payload)
        else:
            click.echo(f"Error: {message}.")
        ctx.exit(EXIT_USAGE)

    metadata = MetadataProcessor().view_metadata(file)
    if json_output:
        status = "success" if metadata else "no_metadata"
        _echo_json(_metadata_payload(file, metadata, status))
    else:
        click.echo(format_metadata_output(metadata))


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Output file path or batch directory.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed.")
@click.option("--json-summary", is_flag=True, help="Print final summary as JSON.")
@click.option(
    "--summary-file",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Write final summary as JSON to a file.",
)
@click.option("--quiet", is_flag=True, help="Suppress progress and human output.")
@click.pass_context
def delete(ctx, path, output, dry_run, json_summary, summary_file, quiet):
    """Remove metadata from a file or supported files in a directory."""
    files_to_process = get_supported_files(path)
    if not files_to_process:
        summary = BatchSummary(total=0)
        if json_summary:
            _echo_batch_summary(summary, dry_run, json_summary=True)
        elif not quiet:
            click.echo("No supported files found.")
        if not _write_summary_file(summary_file, summary, dry_run, quiet):
            ctx.exit(EXIT_FAILURE)
        ctx.exit(EXIT_USAGE)

    processor = MetadataProcessor()
    if len(files_to_process) == 1 and not os.path.isdir(path):
        input_file = files_to_process[0]
        planned_output = _single_output_path(input_file, output)
        result = processor.delete_metadata(input_file, output, dry_run=dry_run)
        summary = BatchSummary(total=1)
        if dry_run:
            summary.succeeded = 1
            _record_file_result(
                summary,
                input_file,
                "would_process",
                planned_output,
            )
            if json_summary:
                _echo_batch_summary(summary, dry_run, json_summary=True)
            elif not quiet:
                click.echo("Dry run complete. No files changed.")
            if not _write_summary_file(summary_file, summary, dry_run, quiet):
                ctx.exit(EXIT_FAILURE)
            ctx.exit(EXIT_SUCCESS)
        elif result:
            summary.succeeded = 1
            _record_file_result(summary, input_file, "success", result)
            if json_summary:
                _echo_batch_summary(summary, dry_run, json_summary=True)
            elif not quiet:
                click.echo(f"Metadata removed: {result}")
            if not _write_summary_file(summary_file, summary, dry_run, quiet):
                ctx.exit(EXIT_FAILURE)
            ctx.exit(EXIT_SUCCESS)
        else:
            summary.failed = 1
            summary.failures.append(input_file)
            _record_file_result(
                summary,
                input_file,
                "failed",
                planned_output,
                "metadata_removal_failed",
            )
            if json_summary:
                _echo_batch_summary(summary, dry_run, json_summary=True)
            elif not quiet:
                click.echo("Metadata removal failed. Check logs for details.")
            if not _write_summary_file(summary_file, summary, dry_run, quiet):
                ctx.exit(EXIT_FAILURE)
            ctx.exit(EXIT_FAILURE)

    summary = BatchSummary(total=len(files_to_process))
    if not quiet and not json_summary:
        click.echo(f"Processing {len(files_to_process)} files...")
    with tqdm(total=len(files_to_process), disable=quiet or json_summary) as pbar:
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
                    _record_file_result(
                        summary,
                        file_path,
                        "would_process" if dry_run else "success",
                        output_path if dry_run else result,
                    )
                else:
                    summary.failed += 1
                    summary.failures.append(file_path)
                    _record_file_result(
                        summary,
                        file_path,
                        "failed",
                        output_path,
                        "metadata_removal_failed",
                    )
            except Exception as e:
                summary.failed += 1
                summary.failures.append(file_path)
                _record_file_result(
                    summary,
                    file_path,
                    "failed",
                    None,
                    str(e),
                )
                logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            pbar.update(1)

    _echo_batch_summary(
        summary,
        dry_run,
        json_summary=json_summary,
        quiet=quiet,
    )
    if not _write_summary_file(summary_file, summary, dry_run, quiet):
        ctx.exit(EXIT_FAILURE)
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
