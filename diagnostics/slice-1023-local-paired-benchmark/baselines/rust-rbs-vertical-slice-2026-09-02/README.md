# Rust RBS Vertical Slice: 2026-09-02

This directory records the RBS substrate in the cross-runtime TreeHaver-only
benchmark gate. The exact oracle is promoted from shared Slice 1036. Ruby uses
both the native `rbs` backend and TSLP through the same `rbs-merge` workflow;
Rust uses normalized tree-sitter-language-pack nodes.

## Correctness

The eleven-case `micro` profile executes every selected Rust candidate case.
Safety, preservation, and reliability pass with no false auto-merges,
unverified preservation requirements, errors, or unsupported micro cases. The
Ruby golden master passes the same profile.

The RBS sentinel exposed a prior Ruby provider defect: `merge2` was modeled as
an exact one-sided `merge3`, so it selected the complete incoming file and lost
destination member customizations. The provider now delegates two-way work to
the shared RBS `SmartMerger` substrate and reparses the result through the
requested TreeHaver backend.

## Provider Comparison

Ruby native RBS, Ruby TSLP, and Rust TSLP produce the exact Slice 1036 output
with SHA-256
`cd89781501b1d8ca9b79a3420d18014ba4376626cd260ac322b4611d73e020db`.
Both runtimes reject TSLP's embedded inline-RBS grammar mode when parsing RBS
documents.

## Scope

This evidence claims source-preserving top-level declaration and recursive
member RBS `merge2`. It does not claim Rust RBS `merge3`. The affected `dev`
profile selects thirteen cases; Rust executes eleven and records the unrelated
YAML and TOML `merge3` cases as unsupported coverage.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate eleven-case Rust correctness report.
- `dev-report.json`: affected RBS report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `provider-comparison.json`: exact Slice 1036 results across three providers.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
