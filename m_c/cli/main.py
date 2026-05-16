import json
import os
from dataclasses import dataclass, field
from typing import Optional

import click
from tqdm import tqdm

from m_c.cli.utils import format_metadata_output
from m_c.core.file_utils import (
    SUPPORTED_CHECKSUM_ALGORITHMS,
    get_file_checksum,
    get_safe_output_path,
    get_supported_files,
    is_supported_file,
)
from m_c.core.logger import configure_logging, logger
from m_c.core.metadata_processor import MetadataProcessor
from m_c.core.reporting import processing_warnings

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
    if summary.skipped == summary.total:
        return "unsupported_input"
    if dry_run:
        return "success" if summary.failed == 0 else "partial_failure"
    if summary.succeeded == summary.total:
        return "success"
    if summary.succeeded == 0:
        return "failure"
    return "partial_failure"


def _report_files(
    files: list[dict],
    report_detail: str,
    report_filter: str = "all",
) -> list[dict]:
    if report_filter == "failed":
        files = [item for item in files if item["status"] == "failed"]

    if report_detail == "full":
        return files

    compact_files = []
    for item in files:
        compact_item = {
            "input": item["input"],
            "status": item["status"],
        }
        if "error" in item:
            compact_item["error"] = item["error"]
        if "checksums" in item:
            compact_item["checksums"] = item["checksums"]
        compact_files.append(compact_item)
    return compact_files


def _summary_payload(
    summary: BatchSummary,
    dry_run: bool,
    report_detail: str = "full",
    report_filter: str = "all",
) -> dict:
    payload = {
        "status": _summary_status(summary, dry_run),
        "dry_run": dry_run,
        "total": summary.total,
        "succeeded": summary.succeeded,
        "failed": summary.failed,
        "skipped": summary.skipped,
        "would_process": summary.succeeded if dry_run else None,
        "failures": summary.failures,
    }
    if report_detail != "summary":
        payload["files"] = _report_files(
            summary.files,
            report_detail,
            report_filter=report_filter,
        )
    return payload


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


def _write_json_output_file(
    json_output_file: Optional[str],
    payload: dict,
    quiet: bool = False,
) -> bool:
    if not json_output_file:
        return True
    if _write_json_payload(json_output_file, payload):
        return True
    if not quiet:
        click.echo(f"Failed to write JSON output file: {json_output_file}")
    return False


def _write_summary_file(
    summary_file: Optional[str],
    summary: BatchSummary,
    dry_run: bool,
    report_detail: str = "full",
    report_filter: str = "all",
    quiet: bool = False,
) -> bool:
    if not summary_file:
        return True

    if _write_json_payload(
        summary_file,
        _summary_payload(
            summary,
            dry_run,
            report_detail=report_detail,
            report_filter=report_filter,
        ),
    ):
        return True

    if not quiet:
        click.echo(f"Failed to write summary file: {summary_file}")
    return False


def _echo_batch_summary(
    summary: BatchSummary,
    dry_run: bool,
    json_summary: bool = False,
    report_detail: str = "full",
    report_filter: str = "all",
    quiet: bool = False,
) -> None:
    if json_summary:
        _echo_json(
            _summary_payload(
                summary,
                dry_run,
                report_detail=report_detail,
                report_filter=report_filter,
            )
        )
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


def _processing_warnings(file_path: str) -> list[str]:
    return processing_warnings(file_path)


def _record_file_result(
    summary: BatchSummary,
    input_path: str,
    status: str,
    output_path: Optional[str] = None,
    error: Optional[str] = None,
    include_checksums: bool = False,
    checksum_algorithm: str = "sha256",
) -> None:
    item = {
        "input": input_path,
        "status": status,
        "output": output_path,
    }
    warnings = _processing_warnings(input_path)
    if warnings:
        item["warnings"] = warnings
    if include_checksums:
        input_key = f"input_{checksum_algorithm}"
        output_key = f"output_{checksum_algorithm}"
        item["checksums"] = {
            input_key: get_file_checksum(input_path, checksum_algorithm),
            output_key: (
                get_file_checksum(output_path, checksum_algorithm)
                if output_path and os.path.exists(output_path)
                else None
            ),
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
@click.option(
    "--json-output",
    "json_output_file",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Write the JSON metadata payload to a file.",
)
@click.pass_context
def view(ctx, file, json_output, json_output_file):
    """View metadata of a file."""
    if not os.path.isfile(file):
        message = "file does not exist or is not a regular file"
        payload = _metadata_payload(file, {}, "invalid_input")
        payload["error"] = message
        if json_output:
            _echo_json(payload)
        else:
            click.echo(f"Error: {message}.")
        if not _write_json_output_file(json_output_file, payload):
            ctx.exit(EXIT_FAILURE)
        ctx.exit(EXIT_USAGE)

    if not is_supported_file(file):
        message = "unsupported file type"
        payload = _metadata_payload(file, {}, "unsupported_file_type")
        payload["error"] = message
        if json_output:
            _echo_json(payload)
        else:
            click.echo(f"Error: {message}.")
        if not _write_json_output_file(json_output_file, payload):
            ctx.exit(EXIT_FAILURE)
        ctx.exit(EXIT_USAGE)

    metadata = MetadataProcessor().view_metadata(file)
    status = "success" if metadata else "no_metadata"
    payload = _metadata_payload(file, metadata, status)
    if json_output:
        _echo_json(payload)
    else:
        click.echo(format_metadata_output(metadata))
    if not _write_json_output_file(json_output_file, payload):
        ctx.exit(EXIT_FAILURE)


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Output file path or batch directory.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed.")
@click.option("--json-summary", is_flag=True, help="Print final summary as JSON.")
@click.option(
    "--checksums",
    is_flag=True,
    help="Include checksums in JSON summaries and summary files.",
)
@click.option(
    "--checksum-algorithm",
    type=click.Choice(SUPPORTED_CHECKSUM_ALGORITHMS),
    default="sha256",
    show_default=True,
    help="Checksum algorithm to use when --checksums is enabled.",
)
@click.option(
    "--report-detail",
    type=click.Choice(["full", "compact", "summary"]),
    default="full",
    show_default=True,
    help="Control detail level for JSON summaries and summary files.",
)
@click.option(
    "--report-filter",
    type=click.Choice(["all", "failed"]),
    default="all",
    show_default=True,
    help="Filter per-file entries in JSON summaries and summary files.",
)
@click.option(
    "--preserve-timestamps",
    is_flag=True,
    help="Copy source access and modification times to cleaned outputs.",
)
@click.option(
    "--summary-file",
    "--json-output",
    "summary_file",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Write final JSON summary to a file.",
)
@click.option("--quiet", is_flag=True, help="Suppress progress and human output.")
@click.pass_context
def delete(
    ctx,
    path,
    output,
    dry_run,
    json_summary,
    checksums,
    checksum_algorithm,
    report_detail,
    report_filter,
    preserve_timestamps,
    summary_file,
    quiet,
):
    """Remove metadata from a file or supported files in a directory."""
    if os.path.isfile(path) and not is_supported_file(path):
        summary = BatchSummary(total=1, skipped=1)
        _record_file_result(
            summary,
            path,
            "unsupported",
            None,
            "unsupported_file_type",
            include_checksums=checksums,
            checksum_algorithm=checksum_algorithm,
        )
        if json_summary:
            _echo_batch_summary(
                summary,
                dry_run,
                json_summary=True,
                report_detail=report_detail,
                report_filter=report_filter,
            )
        elif not quiet:
            click.echo("Unsupported file type.")
        if not _write_summary_file(
            summary_file,
            summary,
            dry_run,
            report_detail=report_detail,
            report_filter=report_filter,
            quiet=quiet,
        ):
            ctx.exit(EXIT_FAILURE)
        ctx.exit(EXIT_USAGE)

    files_to_process = get_supported_files(path)
    if not files_to_process:
        summary = BatchSummary(total=0)
        if json_summary:
            _echo_batch_summary(
                summary,
                dry_run,
                json_summary=True,
                report_detail=report_detail,
                report_filter=report_filter,
            )
        elif not quiet:
            click.echo("No supported files found.")
        if not _write_summary_file(
            summary_file,
            summary,
            dry_run,
            report_detail=report_detail,
            report_filter=report_filter,
            quiet=quiet,
        ):
            ctx.exit(EXIT_FAILURE)
        ctx.exit(EXIT_USAGE)

    processor = MetadataProcessor()
    if len(files_to_process) == 1 and not os.path.isdir(path):
        input_file = files_to_process[0]
        planned_output = _single_output_path(input_file, output)
        result = processor.delete_metadata(
            input_file,
            output,
            dry_run=dry_run,
            preserve_timestamps=preserve_timestamps,
        )
        summary = BatchSummary(total=1)
        if dry_run:
            summary.succeeded = 1
            _record_file_result(
                summary,
                input_file,
                "would_process",
                planned_output,
                include_checksums=checksums,
                checksum_algorithm=checksum_algorithm,
            )
            if json_summary:
                _echo_batch_summary(
                    summary,
                    dry_run,
                    json_summary=True,
                    report_detail=report_detail,
                    report_filter=report_filter,
                )
            elif not quiet:
                click.echo("Dry run complete. No files changed.")
            if not _write_summary_file(
                summary_file,
                summary,
                dry_run,
                report_detail=report_detail,
                report_filter=report_filter,
                quiet=quiet,
            ):
                ctx.exit(EXIT_FAILURE)
            ctx.exit(EXIT_SUCCESS)
        elif result:
            summary.succeeded = 1
            _record_file_result(
                summary,
                input_file,
                "success",
                result,
                include_checksums=checksums,
                checksum_algorithm=checksum_algorithm,
            )
            if json_summary:
                _echo_batch_summary(
                    summary,
                    dry_run,
                    json_summary=True,
                    report_detail=report_detail,
                    report_filter=report_filter,
                )
            elif not quiet:
                click.echo(f"Metadata removed: {result}")
            if not _write_summary_file(
                summary_file,
                summary,
                dry_run,
                report_detail=report_detail,
                report_filter=report_filter,
                quiet=quiet,
            ):
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
                include_checksums=checksums,
                checksum_algorithm=checksum_algorithm,
            )
            if json_summary:
                _echo_batch_summary(
                    summary,
                    dry_run,
                    json_summary=True,
                    report_detail=report_detail,
                    report_filter=report_filter,
                )
            elif not quiet:
                click.echo("Metadata removal failed. Check logs for details.")
            if not _write_summary_file(
                summary_file,
                summary,
                dry_run,
                report_detail=report_detail,
                report_filter=report_filter,
                quiet=quiet,
            ):
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
                    preserve_timestamps=preserve_timestamps,
                )
                if result or dry_run:
                    summary.succeeded += 1
                    _record_file_result(
                        summary,
                        file_path,
                        "would_process" if dry_run else "success",
                        output_path if dry_run else result,
                        include_checksums=checksums,
                        checksum_algorithm=checksum_algorithm,
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
                        include_checksums=checksums,
                        checksum_algorithm=checksum_algorithm,
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
                    include_checksums=checksums,
                    checksum_algorithm=checksum_algorithm,
                )
                logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            pbar.update(1)

    _echo_batch_summary(
        summary,
        dry_run,
        json_summary=json_summary,
        report_detail=report_detail,
        report_filter=report_filter,
        quiet=quiet,
    )
    if not _write_summary_file(
        summary_file,
        summary,
        dry_run,
        report_detail=report_detail,
        report_filter=report_filter,
        quiet=quiet,
    ):
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


@cli.command()
@click.option("--host", default="127.0.0.1", show_default=True, help="Local bind host.")
@click.option("--port", default=8765, show_default=True, type=int, help="Local port.")
@click.option("--open-browser", is_flag=True, help="Open the Web UI in a browser.")
@click.option(
    "--workspace",
    type=click.Path(file_okay=False, path_type=str),
    default=None,
    help="Directory for temporary uploads and cleaned copies.",
)
def web(host, port, open_browser, workspace):
    """Start the local Web UI."""
    from m_c.web.server import run_web_server

    try:
        run_web_server(
            host=host,
            port=port,
            open_browser=open_browser,
            workspace=workspace,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
