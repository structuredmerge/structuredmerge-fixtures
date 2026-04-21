# Conformance Fixtures

Shared manifests and other fixture-index material used by multiple language
implementations to discover the same portable fixture subsets.

The conformance manifest is intentionally selective. It indexes representative
roles that multiple language implementations should exercise in common, rather
than attempting to enumerate every fixture in the corpus.

Canonical suite membership is more selective still. The current Markdown
delegated nested suite remains outside the canonical stable and widened suite
sets. Ruby nested delegated coverage now participates in the widened canonical
suite set, but remains outside the canonical stable suite set.

The manifest has two top-level sections:

- `family_feature_profiles` for per-family profile fixtures
- `families` for family-indexed fixture role entries

`diagnostics` is represented as a family inside `families`, not as a special
out-of-band fixture bucket.
