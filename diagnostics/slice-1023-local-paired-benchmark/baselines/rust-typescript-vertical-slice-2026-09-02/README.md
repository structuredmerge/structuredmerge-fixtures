# Rust TypeScript Vertical Slice: 2026-09-02

This directory records the conservative TypeScript top-level declaration
`merge3` substrate in the cross-runtime TreeHaver-only benchmark gate. The
exact oracle combines independent edits to two named functions while retaining
all source bytes outside the changed declaration owner.

## Correctness

The thirteen-case `micro` profile executes every selected Rust candidate case.
Safety, preservation, and reliability pass with no false auto-merges,
unverified preservation requirements, errors, or unsupported micro cases. The
Ruby golden master passes the same profile and produces the same exact
TypeScript output.

The affected `dev` profile selects fifteen cases. Rust executes thirteen and
records unrelated YAML and TOML `merge3` cases as unsupported coverage. The
TypeScript case is selected directly for changes below
`crates/typescript-merge/`.

## Scope

The production operation accepts TypeScript or TSX documents whose base, ours,
and theirs revisions contain the same ordered set of uniquely named supported
top-level declarations and identical inter-owner layout. It projects ownership
from TreeHaver's normalized TSLP AST, applies exact source replacements through
the shared declaration kernel, and reparses the composite through the same
provider. Parser errors, unsupported top-level syntax, ownership changes,
duplicate identities, layout changes, or verification mismatches fail closed.

This evidence does not claim source-preserving TypeScript `merge2`, declaration
insertion/deletion, import merging, or arbitrary nested declaration merging.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate thirteen-case Rust correctness report.
- `dev-report.json`: affected TypeScript report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `provider-comparison.json`: exact Ruby and Rust provider output comparison.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
