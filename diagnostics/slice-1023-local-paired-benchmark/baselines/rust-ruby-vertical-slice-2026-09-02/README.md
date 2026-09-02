# Rust Ruby Vertical Slice: 2026-09-02

This directory records the generic Ruby substrate in the cross-runtime
TreeHaver-only benchmark gate. The Rust candidate uses normalized
tree-sitter-language-pack nodes; the Ruby golden master uses the same
`ruby-merge` behavior through its TreeHaver-selected tree-sitter backend. The
exact oracle is promoted from shared Slice 941.

## Correctness

The ten-case `micro` profile executes every selected candidate case. It
produces eight correct clean outcomes and two true conflicts. Safety,
preservation, and reliability gates pass with no false auto-merges, unverified
preservation requirements, errors, or unsupported micro cases. The Ruby golden
master passes the same profile.

The Ruby-focused `dev` profile selects thirteen cases. The generic Ruby
`merge2` case passes exact bytes. The distinct Prism `merge3` case and the YAML
and TOML `merge3` cases remain outside the Rust descriptor and are recorded as
unsupported coverage rather than quality failures.

## Provider Comparison

Ruby TSLP, Ruby Prism, and Rust TSLP now produce the exact Slice 941 output.
The comparison exposed a Prism whitespace-preservation defect: template-only
nodes without leading comments skipped their shared layout-owned leading gap.
That defect was fixed in the Ruby golden master before this baseline was
finalized.

## Scope

This evidence claims source-preserving class and method Ruby `merge2` for the
Rust TSLP provider. It does not claim Ruby `merge3`, constants, visibility
sections, DSL-specific signatures, comments, or native Prism AST parity. Prism
remains a distinct native provider and is not selected by generic `ruby-merge`.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate ten-case Rust correctness report.
- `dev-report.json`: affected Ruby report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `provider-comparison.json`: exact Slice 941 results across three providers.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
