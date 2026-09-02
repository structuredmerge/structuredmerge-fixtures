# StructuredMerge Fixtures

Shared conformance fixtures for StructuredMerge.

This repository contains shared language-neutral fixture families along with implementation-specific fixture slices for the Go, TypeScript, Rust, and Ruby implementations. The mature Ruby implementation is the behavioral golden master. Shared fixtures extract that behavior into portable contracts so independent implementations can be compared without coupling them to Ruby classes or process-local parser objects. Language directories hold implementation-specific cases and metadata where needed.

Project links:

- Website: <https://structuredmerge.org>
- Fixture model: <https://structuredmerge.org/fixtures.html>
- Conformance model: <https://structuredmerge.org/conformance.html>
- Specification: <https://github.com/structuredmerge/structuredmerge-spec>
- Peer implementations: [Go](https://github.com/structuredmerge/structuredmerge-go), [TypeScript](https://github.com/structuredmerge/structuredmerge-typescript), [Rust](https://github.com/structuredmerge/structuredmerge-rust), [Ruby](https://github.com/structuredmerge/structuredmerge-ruby)

## Fixture families

The corpus is organized around document families and conformance slices, including:

- `conformance/`
- `text/`
- `json/`
- `jsonc/`
- `toml/`
- `yaml/`
- `markdown/`
- `diagnostics/`

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
- Treating Ruby's internal object model as the portable contract. Ruby behavior
  is authoritative, but portable fixtures define the cross-runtime transport.

## Adding fixtures

A good fixture is small, named for the behavior it exercises, and clear about whether it expects a successful merge, an unresolved review state, or a diagnostic. Prefer adding or updating manifest metadata when a fixture becomes part of a portable conformance subset.
