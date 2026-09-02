# Rust Generic Python Vertical Slice: 2026-09-02

This directory records Python as the first reviewed grammar in the
experimental generic TreeHaver/TSLP provider tier. It validates the tier's
conservative top-level named-owner `merge3` contract; it does not claim that
every grammar supplied by TSLP is merge-ready.

## Correctness

The unchanged sixteen-case `micro` profile passes every Rust and Ruby GM hard
gate. The affected `dev` profile selects nineteen cases, including the Python
case directly. Rust executes seventeen cases and records unrelated YAML and
TOML `merge3` cases as unsupported coverage. The Python result matches the
exact byte oracle and passes every preservation check.

There is no Ruby Python merge provider. Python is therefore not a Ruby-GM
differential claim and remains experimental. The Ruby artifact records only
that the existing mandatory GM profile remains green.

## Scope

The generic provider requires every non-comment top-level node to expose one
direct TreeHaver-normalized `name` field. Owner identities must be unique and
retain the same order in all revisions, and source between owners must remain
byte-identical. Output is reparsed through the same TSLP provider. Unnamed or
ambiguous nodes, imports, assignments, decorators, membership changes, layout
changes, parser errors, and unavailable grammars fail closed.

Only `merge3` is advertised. Dedicated language substrates supersede this
provider whenever language-specific ownership or a higher-fidelity native AST
is available.

## Artifacts

- `micro-run.json`: raw mandatory-profile evidence for the Rust candidate.
- `micro-report.json`: aggregate sixteen-case Rust correctness report.
- `dev-run.json`: raw affected-profile evidence containing the Python result.
- `dev-report.json`: affected generic-provider report.
- `ruby-gm-report.json`: unchanged mandatory-profile Ruby GM report.
- `provider-comparison.json`: explicit provider availability and exact result.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
