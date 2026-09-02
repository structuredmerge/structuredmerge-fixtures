# Rust YAML Vertical Slice: 2026-09-02

This directory records the first YAML case in the cross-runtime TreeHaver-only
benchmark gate. The candidate uses `yaml-merge` for merge behavior and
TreeHaver's tree-sitter-language-pack provider for parsing. The exact oracle is
promoted from the shared Slice 720 fixture.

## Correctness

The eight-case `micro` profile executes every selected candidate case. It
produces six correct clean outcomes and two true conflicts. Safety,
preservation, and reliability gates pass with no false auto-merges, unverified
preservation requirements, errors, or unsupported micro cases. The Ruby golden
master passes the same expanded profile.

The YAML-focused `dev` profile selects both YAML cases plus the mandatory
sentinels and two deterministic neighbors. The YAML `merge2` case passes exact
bytes. YAML `merge3` remains explicitly unsupported by the Rust descriptor, as
does the sampled TOML neighbor; unsupported coverage does not enter quality
denominators.

## Scope

This evidence does not claim YAML `merge3`, aliases, anchors, flow collections,
or multi-document streams. It proves recursive block-mapping `merge2`, exact
source preservation for the reviewed case, family-specific provider identity,
and fail-closed capability reporting.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate eight-case Rust correctness report.
- `dev-report.json`: affected YAML report with explicit unsupported coverage.
- `ruby-gm-report.json`: expanded micro report from the Ruby golden master.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
