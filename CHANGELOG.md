# Changelog

## [Unreleased]

### Added

- Add shared typed-core native profile conformance fixtures for Alef-generated Ruby and Python suites.

- Add shared LibCST-backed Rust merge fixtures for independent edits, conflicts, malformed input, unsupported owners, and exact source preservation.

- Add Psych-backed native YAML fixtures for independent edits, conflicts, syntax rejection, unsupported sequences, and byte preservation.

- Add common typed analyze, diff2, and merge3 fixtures for installed Ruby/Psych and Python/LibCST bindings, including syntax rejection, conflicts, and byte preservation.

- Add common Python merge2 fixtures for current-preferred insertion with byte preservation, reversed direction, and rejection of reordered shared anchors.

- Add eleven shared typed JSON operation fixtures for generated Ruby/Python analysis, diff, merge, conflict and exact-byte checks.

### Fixed

- Include shared ast-merge and native Python crate changes in the Slice 1023 affected-case benchmark selection.

- Map the shared kernel CLI source directory to all benchmark operation capabilities so affected dev runs include every corpus case when CLI routing changes.

- Require exact unresolved review output for the typed Git absent-owner case now supported by the kernel; retain failure status and absence of merged output.
