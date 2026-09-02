# Rust Bash Vertical Slice: 2026-09-02

This directory records the conservative Bash top-level function `merge3`
substrate in the cross-runtime TreeHaver-only benchmark gate. The exact oracle
combines independent edits to two named functions while retaining all source
bytes between function owners.

## Correctness

The sixteen-case `micro` profile executes every selected Rust candidate case.
Safety, preservation, and reliability pass with no false auto-merges,
unverified preservation requirements, errors, or unsupported micro cases. The
Ruby golden master passes the same profile and produces the same exact Bash
output.

The affected `dev` profile selects eighteen cases. Rust executes sixteen and
records unrelated YAML and TOML `merge3` cases as unsupported coverage. The
Bash case is selected directly for changes below `crates/bash-merge/`.

## Scope

The production operation accepts Bash documents whose base, ours, and theirs
revisions contain the same ordered set of uniquely named top-level functions
and identical source outside those function owners. It projects ownership from
TreeHaver's normalized TSLP AST, applies exact source replacements through the
shared declaration kernel, and reparses through the same provider. Parser
errors, unsupported top-level statements, membership changes, duplicate
identities, layout changes, or verification mismatches fail closed.

This evidence does not claim Bash `merge2`, function insertion or deletion,
command or assignment merging, heredoc merging, or nested declaration merging.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate sixteen-case Rust correctness report.
- `dev-report.json`: affected Bash report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `provider-comparison.json`: exact Ruby and Rust provider output comparison.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
