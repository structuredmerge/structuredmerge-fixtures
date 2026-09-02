# Rust-Language Vertical Slice: 2026-09-02

This directory records the conservative Rust-language top-level function
`merge3` substrate in the cross-runtime TreeHaver-only benchmark gate. The
exact oracle combines independent edits to two named functions while retaining
all inter-function source bytes.

## Correctness

The fifteen-case `micro` profile executes every selected Rust candidate case.
Safety, preservation, and reliability pass with no false auto-merges,
unverified preservation requirements, errors, or unsupported micro cases. The
Ruby golden master passes the same profile and produces the same exact
Rust-language output.

The affected `dev` profile selects seventeen cases. Rust executes fifteen and
records unrelated YAML and TOML `merge3` cases as unsupported coverage. The
Rust-language case is selected directly for changes below `crates/rust-merge/`.

## Scope

The production operation accepts Rust documents whose base, ours, and theirs
revisions contain the same ordered set of uniquely named top-level functions
and identical source outside those function owners. It projects ownership from
TreeHaver's normalized TSLP AST, applies exact source replacements through the
shared declaration kernel, and reparses through the same provider. Parser
errors, attributes, unsupported items, membership changes, duplicate
identities, layout changes, or verification mismatches fail closed.

The native `syn` parser remains explicitly unsupported for source-preserving
merging because it does not expose the required source spans. This evidence
does not claim Rust-language `merge2`, declaration insertion/deletion, macro or
compound-use merging, or nested declaration merging.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate fifteen-case Rust correctness report.
- `dev-report.json`: affected Rust-language report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `provider-comparison.json`: exact Ruby and Rust provider output comparison.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
