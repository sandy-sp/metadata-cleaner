# Metadata Cleaner Roadmap

This roadmap tracks possible future work after the v3.18.x maintenance and
format-support sequence. Items here are intentionally not promises for a
specific release; they should be validated against user demand, maintenance
cost, and privacy risk before implementation.

## Near Term

### Maintenance Readiness
- Keep release automation guarded so version tags, package metadata, PyPI
  releases, GitHub releases, and Docker images cannot drift.
- Periodically prune stale remote branches after merged roadmap stages.
- Re-run repository health reviews when dependency alerts, packaging changes,
  or format-support changes land.

### Stronger Fixture Coverage
- Add video integration tests that run when FFmpeg and FFprobe are installed.
- Add fixture assertions for additional audio containers beyond WAV/FLAC when
  their metadata can be generated without external system tools.
- Keep installed-package smoke coverage current as optional system-tool behavior
  expands.

### CLI Usability
- Keep machine-readable file output targets consistent as new JSON surfaces are
  added.
- Add additional report filters only if users need more targeted automation
  views.
- Keep the programmatic API behavior aligned with CLI batch reporting.

### File Format Support
- Expand audio/video tests before expanding advertised format support.

## Medium Term

### Privacy and Safety
- Keep per-file processing notes current as handlers gain more precise
  lossless/rewrite/remux detection.

### Packaging
- Consider standalone executables only after the CLI test suite is broader.

## Longer Term

### Desktop Interface
- Consider a small desktop UI only if CLI and local Web UI usage show enough
  demand.
- Keep all processing local by default.
- Reuse the existing CLI/core processor rather than creating separate cleaning
  logic for the UI.

### Performance
- Benchmark large directory runs before adding concurrency.
- If concurrency is added, keep output path generation deterministic and make
  failure reporting explicit.
