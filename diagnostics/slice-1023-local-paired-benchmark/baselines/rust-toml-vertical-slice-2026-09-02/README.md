# Rust TOML Vertical Slice: 2026-09-02

This directory records the first TOML case in the cross-runtime TreeHaver-only
benchmark gate. The Rust candidate uses the shared `toml-merge` substrate and
TreeHaver's tree-sitter-language-pack provider. The exact oracle is promoted
from the shared Slice 720 nested-table fixture.

## Correctness

The nine-case `micro` profile executes every selected candidate case. It
produces seven correct clean outcomes and two true conflicts. Safety,
preservation, and reliability gates pass with no false auto-merges, unverified
preservation requirements, errors, or unsupported micro cases. The Ruby golden
master passes the same profile.

The TOML-focused `dev` profile selects both TOML cases plus mandatory sentinels
and one YAML neighbor. TOML `merge2` passes exact bytes. TOML and YAML `merge3`
remain explicitly unsupported by the Rust descriptor and affect coverage only.

## Provider Comparison

Ruby TSLP and Citrus, plus Rust TSLP, produce exact output for both Slice 720
and the richer Slice 721 dotted-key/inline-table fixture. Ruby Parslet and Rust
Pest produce exact Slice 720 output but reject Slice 721 at the parser boundary.
Those parser limitations are covered as explicit fail-closed expectations.

## Scope

This evidence claims source-preserving nested-table TOML `merge2` for the Rust
TSLP provider. It does not claim TOML `merge3`, quoted-key identity, or repeated
array-of-table identity. Parser-specific packages retain their declared syntax
limits while sharing substrate merge behavior for supported projections.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate nine-case Rust correctness report.
- `dev-report.json`: affected TOML report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `manifest.json`: revisions, hashes, commands, outcomes, comparison, and scope.
