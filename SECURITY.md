# Security Policy

Metadata Cleaner handles local user files, so security and privacy issues are
taken seriously.

## Supported Versions

Security fixes are targeted at the latest released version on PyPI and the
current `main` branch.

## Reporting A Vulnerability

Please do not open a public issue for a vulnerability if it includes exploit
details or sensitive sample files.

Report security issues privately through GitHub's private vulnerability
reporting when available, or contact the maintainer through the email listed in
`pyproject.toml`.

Helpful reports include:

- affected version or commit
- operating system and Python version
- file type and tool path involved
- whether optional tools such as ExifTool, FFmpeg, or FFprobe were installed
- minimal reproduction steps that do not include private user files

## Scope

In scope:

- crashes, hangs, or resource exhaustion caused by malformed files
- path traversal or unintended file deletion in CLI or Web UI flows
- dependency vulnerabilities in the released package or Docker image
- incorrect behavior that modifies originals during metadata removal

Out of scope:

- claims that a file may still contain non-standard metadata not supported by
  the relevant parser
- issues requiring public exposure of the local-only Web UI against documented
  defaults
- vulnerabilities in external tools such as ExifTool or FFmpeg unless this
  project invokes them unsafely

## Privacy Expectations

Metadata removal keeps originals unchanged and writes cleaned copies. This tool
does not guarantee removal of every possible hidden payload, watermark, or
content-derived signal. For high-risk publishing workflows, verify cleaned files
with independent tools before release.
