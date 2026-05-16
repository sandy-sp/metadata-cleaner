# Contributing

Thanks for helping improve Metadata Cleaner. The project is intentionally small
and privacy-focused, so changes should stay conservative and easy to audit.

## Development Setup

```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install --with dev
poetry run metadata-cleaner --help
```

Optional system tools improve local coverage:

- ExifTool for AVIF, HEIC, HEIF, and broader image metadata paths
- FFmpeg and FFprobe for video and generated compressed-audio fixtures

## Verification

Run these before opening a pull request:

```bash
poetry check --lock
poetry run pytest
poetry run flake8 m_c manage.py .github/scripts/package_smoke.py
poetry run pip-audit
poetry build
```

If FFmpeg or FFprobe are not installed, the generated M4A and MP4 integration
tests skip locally. CI package-smoke coverage installs those tools and exercises
the built wheel.

## Pull Request Guidelines

- Keep changes scoped to one behavior or maintenance theme.
- Prefer cleaned-copy behavior over in-place mutation.
- Add focused tests for metadata removal, unsupported inputs, and machine-
  readable output changes.
- Update `README.md`, `docs/USAGE.md`, `docs/API_REFERENCE.md`, and
  `RELEASE_NOTES.md` when user-visible behavior changes.
- Do not commit private sample files, large binary fixtures, logs, caches, or
  local Web UI workspaces.

## Release Notes

Each release needs a matching `RELEASE_NOTES.md` section named `## vX.Y.Z`.
The release workflow verifies that the pushed tag matches `pyproject.toml` and
uses that section as the GitHub Release body.
