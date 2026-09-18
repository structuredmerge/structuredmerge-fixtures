# Changelog

## [Unreleased]

### Added

- Add shared typed-core native profile conformance fixtures for Alef-generated Ruby and Python suites.

- Add shared LibCST-backed Rust merge fixtures for independent edits, conflicts, malformed input, unsupported owners, and exact source preservation.

- Add Psych-backed native YAML fixtures for independent edits, conflicts, syntax rejection, unsupported sequences, and byte preservation.

- Add common typed analyze, diff2, and merge3 fixtures for installed Ruby/Psych and Python/LibCST bindings, including syntax rejection, conflicts, and byte preservation.

- Add common Python merge2 fixtures for current-preferred insertion with byte preservation, reversed direction, and rejection of reordered shared anchors.

- Add eleven shared typed JSON operation fixtures for generated Ruby/Python analysis, diff, merge, conflict and exact-byte checks.

- Map the installed typed-core JSON benchmark adapter and descriptor to JSON-family cases in the retained Slice 1023 changed-path selector.

- Expand the typed benchmark adapter changed-path mapping to Bash, Go, Rust and TypeScript alongside JSON-family cases.

- Map shared typed-core changes to all retained operation families so affected-dev selection does not silently omit cases when facade validation changes.

- Map typed benchmark and LibCST conformance helper changes to Python corpus coverage without changing benchmark cases or oracles.

- Map installed Ruby/Psych benchmark adapter and shared Ruby conformance helper changes to the retained affected-case selector.

- Add twelve cross-runtime typed capability manifest fixtures separating declared scope, parser eligibility, and default approval.

- Add twenty portable CLI discovery and argument-rejection cases with a bounded real-process runner, exact output and file-state evidence, and failure/cleanup self-tests.

- Add explicit typed-kernel real-Git CLI fixtures distinguishing Git status from driver error/conflict outcomes and checking clean writes, conflict policies, and preservation on failure.

- Add twelve portable CLI conflict-review cases and a bounded real-process runner checking exact source digests, role byte ranges, errors, and source preservation.

### Fixed

- Include shared ast-merge and native Python crate changes in the Slice 1023 affected-case benchmark selection.

- Map the shared kernel CLI source directory to all benchmark operation capabilities so affected dev runs include every corpus case when CLI routing changes.

- Require exact unresolved review output for the typed Git absent-owner case now supported by the kernel; retain failure status and absence of merged output.
