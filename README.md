# StructuredMerge Fixtures

Shared conformance fixtures for StructuredMerge.

This repository contains language-neutral fixture data used by the Go, TypeScript, Rust, and Ruby implementations. The fixtures are part of the public contract: they keep independent implementations aligned without making any one runtime canonical.

Project links:

- Website: <https://structuredmerge.org>
- Fixture model: <https://structuredmerge.org/fixtures.html>
- Conformance model: <https://structuredmerge.org/conformance.html>
- Specification: <https://github.com/structuredmerge/structuredmerge-spec>
- Launch implementations: [Go](https://github.com/structuredmerge/structuredmerge-go), [TypeScript](https://github.com/structuredmerge/structuredmerge-typescript), [Rust](https://github.com/structuredmerge/structuredmerge-rust), [Ruby](https://github.com/structuredmerge/structuredmerge-ruby)

## Fixture families

The corpus is organized around document families and conformance slices, including:

- `conformance/`
- `text/`
- `json/`
- `jsonc/`
- `toml/`
- `yaml/`
- `markdown/`
- `rulesets/`

Each fixture set should include the smallest useful combination of:

- template input
- destination input
- optional ruleset/config input
- expected rendered output
- expected diagnostics when relevant
- manifest metadata for portable discovery

## Goals

- Keep behavior reproducible across Go, TypeScript, Rust, and Ruby.
- Make implementation differences visible through explicit capabilities and diagnostics.
- Support manifest-driven discovery for selected portable conformance subsets.
- Avoid copying fixture data into language repos.
- Separate shared merge behavior from package-manager or scaffold concerns.

## Non-goals

- Generated reports.
- Language-specific snapshots.
- Package scaffold examples.
- Privileging one implementation's internal model over the shared contract.

## Adding fixtures

A good fixture is small, named for the behavior it exercises, and clear about whether it expects a successful merge, an unresolved review state, or a diagnostic. Prefer adding or updating manifest metadata when a fixture becomes part of a portable conformance subset.
