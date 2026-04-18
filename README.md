# Shared Fixtures

This directory is reserved for language-neutral merge fixtures.

Intended structure:

- `text/`
- `json/`
- `jsonc/`
- `toml/`
- `yaml/`
- `markdown/`
- `rulesets/`

Each fixture set should eventually include:

- template input
- destination input
- optional ruleset/config input
- expected rendered output
- expected diagnostics when relevant

Fixture goals:

- parity across Ruby, TypeScript, Rust, and Go
- reproducible behavior for MVP merge engines
- isolation from package-manager or templating concerns

Non-goals:

- storing generated reports
- language-specific snapshots
- package scaffold examples

