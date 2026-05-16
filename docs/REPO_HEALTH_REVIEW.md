# Repository Health Review

Last reviewed: 2026-05-16

This review captures the current maintenance, security, dependency, and
documentation state after the v3.18.10 release.

## Current State

- `main` is clean and synced with `origin/main`.
- Open GitHub pull requests: none.
- Open GitHub issues: none.
- Open Dependabot security alerts: none.
- Open CodeQL/code scanning alerts: none.
- Branch protection is enabled for `main` with required CI, Docker, package
  smoke, and CodeQL checks.
- The committed `poetry.lock` file is intentional. It documents the exact
  dependency set used by CI and releases and gives security scanners a stable
  target.

## Verification Snapshot

The following checks passed locally during this review:

```bash
poetry check --lock
poetry run flake8 m_c manage.py
poetry run pytest
poetry run pip-audit
poetry build
```

The full test suite result was `76 passed, 1 skipped`.

## Dependency Review

Runtime dependencies should stay narrow because this tool opens user-supplied
files. During this review, two unused runtime dependencies were identified and
removed from `pyproject.toml`:

- `ffmpeg-python`: video handling calls the `ffmpeg` and `ffprobe` executables
  directly through `subprocess`.
- `pymupdf`: no current handler imports or uses PyMuPDF.

The current dependency freshness check showed these non-security updates:

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

## Next Recommended Work

Re-run this review when the next dependency/security alert, format support
change, or packaging update lands.
