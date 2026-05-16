# Maintenance And Security

This project handles user files, so maintenance should prioritize predictable
behavior, conservative dependency updates, and privacy-preserving defaults.

## Regular Checks

Run these before merging non-trivial changes:

```bash
poetry check --lock
poetry run pytest
poetry run flake8 m_c manage.py
poetry run pip-audit
poetry build
```

The CI workflow mirrors these checks, builds the Docker image, and smoke-tests
the built wheel in a clean virtual environment. Tagged releases also publish a
Docker image to GitHub Container Registry.

Public-facing docs should be reviewed before feature releases. At minimum,
confirm that `README.md`, `docs/USAGE.md`, `docs/API_REFERENCE.md`,
`docs/ARCHITECTURE.md`, and `RELEASE_NOTES.md` describe the current command
surface and safety model.

Record broader review checkpoints in
[`docs/REPO_HEALTH_REVIEW.md`](REPO_HEALTH_REVIEW.md) when dependency posture,
branch protection, packaging, or roadmap priorities are re-evaluated.

## Dependency Updates

`poetry.lock` is committed intentionally. It pins the exact dependency versions
used by CI, releases, and local reproducibility checks. This is not a security
risk by itself; it is a security control because scanners can inspect the exact
resolved package set.

When Dependabot opens a dependency update:

1. Confirm the PR only changes expected dependency files.
2. Wait for CI, CodeQL, and the Docker build to pass.
3. Read the release notes for runtime-impacting updates.
4. Merge low-risk patches quickly.
5. Treat runtime, Python-version, and Docker-base updates as compatibility
   changes that may need extra testing.

## Branch Protection

The `main` branch should require the CI and CodeQL checks before changes are
merged. Recommended required checks:

- `Python 3.11`
- `Python 3.12`
- `Python 3.13`
- `Docker build`
- `Package smoke`
- `Analyze Python`

Allowing administrators to bypass protection is acceptable for a small personal
project, but force pushes and branch deletion should stay disabled.

## Release Process

1. Update `pyproject.toml`.
2. Add a matching `RELEASE_NOTES.md` section for the target tag, such as
   `## vX.Y.Z`.
3. Run the full local verification suite.
4. Push the release-prep commit and wait for GitHub checks.
5. Create and push an annotated tag:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

The release workflow publishes to PyPI and creates the GitHub release using the
matching `RELEASE_NOTES.md` section as the release body. The Docker publishing
workflow runs for the same version tags and publishes `ghcr.io/sandy-sp/metadata-cleaner`
with `vX.Y.Z`, `X.Y.Z`, `X.Y`, and `latest` tags.

Before pushing a release tag, confirm that the tag matches `pyproject.toml`
exactly. The release workflow enforces this check before publishing.

## Branch Housekeeping

After merged feature and maintenance PRs, prune stale local remote-tracking refs
with:

```bash
git fetch --prune
```

If old remote branches remain visible on GitHub after their PRs are merged or
closed, delete only branches that are clearly merged, obsolete, and not owned by
an active Dependabot PR.
