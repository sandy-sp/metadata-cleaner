# Metadata Cleaner Roadmap

This roadmap tracks possible future work after the v3.2.0 security and
maintenance release. Items here are intentionally not promises for a specific
release; they should be validated against user demand, maintenance cost, and
privacy risk before implementation.

## Near Term

### Stronger Fixture Coverage
- Add generated audio fixtures with real metadata tags where practical.
- Add video integration tests that run when FFmpeg and FFprobe are installed.
- Add package smoke tests that install the built wheel and run the CLI.
- Add Docker build verification in CI.

### CLI Usability
- Add richer batch reports that can be exported as JSON.
- Add a `--quiet` flag for automation that only needs machine-readable output.

### File Format Support
- Evaluate HEIC/HEIF support with a clear dependency strategy.
- Evaluate ODT and EPUB metadata cleanup.
- Expand audio/video tests before expanding advertised format support.

## Medium Term

### Privacy and Safety
- Add optional checksum reporting for input/output integrity checks.
- Add a `--preserve-timestamps` option if users need cleaned files to retain
  filesystem timestamps.
- Add clearer warnings for formats that require re-saving rather than lossless
  metadata stripping.

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
