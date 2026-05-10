# Metadata Cleaner Roadmap

This roadmap tracks possible future work after the v3.2.0 security and
maintenance release. Items here are intentionally not promises for a specific
release; they should be validated against user demand, maintenance cost, and
privacy risk before implementation.

## Near Term

### Stronger Fixture Coverage
- Add video integration tests that run when FFmpeg and FFprobe are installed.
- Add fixture assertions for additional audio containers beyond WAV when their
  metadata can be generated without external system tools.
- Add installed-package smoke coverage for optional system-tool paths when
  those tools are available in CI.

### CLI Usability
- Add optional file output targets for machine-readable command output.
- Add configurable verbosity levels for per-file report payloads if users need
  compact reports for very large batches.

### File Format Support
- Evaluate HEIC/HEIF support with a clear dependency strategy.
- Evaluate ODT and EPUB metadata cleanup.
- Expand audio/video tests before expanding advertised format support.

## Medium Term

### Privacy and Safety
- Add clearer warnings for formats that require re-saving rather than lossless
  metadata stripping.
- Add optional checksum algorithms beyond SHA-256 only if users need them.
- Add timestamp preservation coverage for additional handlers as new formats are
  added.

### Packaging
- Add a Docker image publishing workflow after Docker builds are covered in CI.
- Consider standalone executables only after the CLI test suite is broader.

## Longer Term

### Desktop Interface
- Consider a small desktop UI only if CLI usage shows enough demand.
- Keep all processing local by default.
- Reuse the existing CLI/core processor rather than creating separate cleaning
  logic for the UI.

### Performance
- Benchmark large directory runs before adding concurrency.
- If concurrency is added, keep output path generation deterministic and make
  failure reporting explicit.
