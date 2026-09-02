# Rust Markdown Vertical Slice: 2026-09-02

This directory records the conservative Markdown heading-section substrate in
the cross-runtime TreeHaver-only benchmark gate. The exact oracle preserves
destination-customized sections and their spacing, inserts an incoming-only
section with its HTML comment, and retains the destination's missing final
newline.

## Correctness

The twelve-case `micro` profile executes every selected Rust candidate case.
Safety, preservation, and reliability pass with no false auto-merges,
unverified preservation requirements, errors, or unsupported micro cases. The
Ruby golden master passes the same profile.

The production `merge2` operation accepts only complete documents partitioned
by unique, same-level top-level ATX headings. It derives headings and source
ranges from the selected parser, retains current fragments for shared heading
identities, inserts incoming-only fragments, combines both documents' ordering
constraints through the shared `ast-merge` sequence kernel, and reparses the
exact composite. Preambles, setext headings, nested heading levels, duplicate
identities, incompatible order, and non-exact parser projections fail closed.

## Provider Comparison

Ruby TSLP, Markly, CommonMarker, and Kramdown plus Rust TSLP and Pulldown-cmark
produce the exact sentinel output with SHA-256
`0d73032ebccef65c3377d870c08f3861b947c8c3a1423649dab2c920f1c1e9bd`.
Parser-specific packages supply AST projections; heading-section ownership,
ordering, source rendering, and verification remain in the generic Markdown
substrate and shared kernel.

## Scope

This evidence claims source-preserving Markdown heading-section `merge2` for
the stated subset. It does not promote the legacy ordinal block/fence merger
as production behavior and does not claim Rust Markdown `merge3`. The affected
`dev` profile selects fifteen cases; Rust executes twelve and records YAML,
TOML, and Markdown `merge3` cases as unsupported coverage.

## Artifacts

- `micro-run.json`: raw paired process and output evidence.
- `micro-report.json`: aggregate twelve-case Rust correctness report.
- `dev-report.json`: affected Markdown report with explicit unsupported coverage.
- `ruby-gm-report.json`: matching micro report from the Ruby golden master.
- `provider-comparison.json`: exact output across six parser providers.
- `manifest.json`: revisions, hashes, commands, outcomes, and scope.
