# Repository Health Review

Last reviewed: 2026-05-16

This review captures the current maintenance, security, dependency, and
documentation state after the v3.18.14 public-readiness review.

## Current State

- `main` is clean and synced with `origin/main`.
- Open GitHub pull requests: none.
- Open GitHub issues: none.
- Open Dependabot security alerts: none.
- Open CodeQL/code scanning alerts: none.
- Recent CI, CodeQL, PyPI release, and Docker release workflows completed
  successfully for v3.18.13.
- Branch protection is enabled for `main` with required CI, Docker, package
  smoke, and CodeQL checks.
- The committed `poetry.lock` file is intentional. It documents the exact
  dependency set used by CI and releases and gives security scanners a stable
  target.
- Public-facing README, usage, API, architecture, maintenance, contributing,
  and security-policy docs describe the current CLI, Web UI, Docker image,
  automation outputs, optional tools, and privacy/safety model.
- Package metadata now links to documentation, changelog, and security policy;
  source distributions include public docs for offline review.

## Verification Snapshot

The following checks passed locally during this review:

```bash
poetry check --lock
poetry run flake8 m_c manage.py
poetry run pytest
poetry run pip-audit
poetry build
```

The full test suite result is `77 passed, 2 skipped` when FFmpeg/FFprobe are
not installed. The gated M4A audio and MP4 video integration tests run when
those tools are available. Package smoke coverage runs those tool-backed paths
in CI.

## Dependency Review

Runtime dependencies should stay narrow because this tool opens user-supplied
files. Previous v3.18.x maintenance removed unused runtime dependencies:

- `ffmpeg-python`: video handling calls the `ffmpeg` and `ffprobe` executables
  directly through `subprocess`.
- `pymupdf`: no current handler imports or uses PyMuPDF.

The latest dependency freshness check showed only non-security patch/minor
updates:

- `coverage`, `idna`, and `requests` have newer patch/minor releases available.

`pikepdf` v10 compatibility was evaluated and adopted in v3.18.10 with focused
PDF cleanup coverage for document info and XMP metadata removal. Patch/minor
development dependency updates can usually follow normal Dependabot review.

## Maintenance Findings

- A stale `tools/doc` gitlink was still tracked without a matching
  `.gitmodules` entry. This caused the recurring non-failing GitHub Actions
  checkout cleanup annotation. Removing the gitlink should make release logs
  quieter.
- The Web UI is local-only by default, stores files in a temporary workspace
  unless `--workspace` is supplied, and has traversal checks around managed file
  viewing/deletion.
- Release artifacts exclude `m_c/tests`; CI and package smoke coverage validate
  the package before release without shipping test code to users.
- The release workflow now verifies that the pushed version tag matches
  `pyproject.toml` before publishing to PyPI or creating a GitHub release.
- The legacy `MetadataProcessor.process_batch()` API now preserves one result
  slot per input file, returning `None` for failed files.
- Stale local remote-tracking refs from completed roadmap stages were pruned;
  the actual remote now only advertises `main`.
- FFmpeg/FFprobe-gated video integration coverage verifies metadata removal,
  original preservation, and stream-property preservation for a generated MP4
  fixture.
- FFmpeg-gated compressed audio integration coverage verifies M4A metadata
  removal, original preservation, and stream-property preservation for a
  generated fixture.

## Next Recommended Work

1. Re-run dependency/security review when Dependabot opens the next update.
2. Consider standalone executable packaging only after another release cycle of
   CLI and package-smoke stability.
