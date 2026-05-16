# Publishing Guide

Follow these steps to build and publish `metadata-cleaner`.

## 1. Install Dependencies

Install project and development dependencies with Poetry.

```bash
poetry install --with dev
```

## 2. Verify Locally

Run the same checks used by CI and the release workflow.

```bash
poetry check --lock
poetry run pytest
poetry run flake8 m_c manage.py
poetry run pip-audit
```

## 3. Build the Package

Generate the source distribution and wheel in `dist/`.

```bash
poetry build
```

## 4. Publish a Release

The GitHub release workflow publishes to PyPI when a `v*` tag is pushed.

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Before tagging, update `pyproject.toml`, add a matching `RELEASE_NOTES.md`
section such as `## vX.Y.Z`, run the full verification suite, and make sure
`PYPI_API_TOKEN` is configured in the repository secrets. The release workflow
verifies that the pushed tag matches the `pyproject.toml` version and uses the
matching release-notes section as the GitHub Release body. The companion Docker
workflow publishes the same version tag to GitHub Container Registry.
