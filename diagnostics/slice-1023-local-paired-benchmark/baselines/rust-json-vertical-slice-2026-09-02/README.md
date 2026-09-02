# Rust JSON Vertical Slice: 2026-09-02

This directory records the first TreeHaver-only Rust JSON vertical slice against
the exact Ruby golden-master `micro` corpus and the affected `dev` selection.
The candidate uses `json-merge` for merge behavior and TreeHaver's
tree-sitter-language-pack provider for JSON, JSONC, and JSON5 parsing.

## Correctness

The seven-case `micro` profile produced five correct clean outcomes and two true
conflicts. Safety, preservation, and reliability gates pass, with no false
auto-merges and no unverified preservation requirements.

The affected `dev` profile selected nine direct JSON-family cases and two
deterministic neighbors. All nine direct cases pass. The YAML and TOML neighbors
are recorded as unsupported coverage because this adapter descriptor claims
only the JSON family; they do not enter quality denominators.

The ordinary Rust Git adapter now delegates JSON, JSONC, and JSON5 to the same
`json-merge` substrate. It no longer has a serde document parser, recursive
value merger, canonical renderer, or string-based owner-range scanner.

## Performance

Performance was measured only after correctness passed and does not affect any
quality gate. Across the seven cold candidate operations, Rust took 16,238,504
ns and Ruby took 1,815,901,095 ns in this run. Across 35 requests in one
persistent process, Rust round-trip time was 15,390,827 ns and Ruby round-trip
time was 330,402,383 ns. These local measurements are evidence for profiling,
not a public aggregate ranking.

## Remaining Gap

The Rust substrate identifies structural conflicts and their paths but does not
yet expose owned source regions for conflict rendering. Strict Git-driver mode
therefore leaves `ours` unchanged instead of guessing localized ranges. Porting
Ruby's shared owned-region and conflict-localization mechanics remains a Phase 6
substrate task.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate seven-case correctness report.
- `dev-report.json`: affected JSON-family report with unsupported neighbors.
- `rust-performance.json`: five iterations per micro case through one Rust process.
- `ruby-gm-report.json`: same-corpus Ruby correctness report.
- `ruby-gm-performance.json`: five iterations per micro case through one Ruby process.
- `manifest.json`: revisions, hashes, commands, outcomes, and timing comparison.
