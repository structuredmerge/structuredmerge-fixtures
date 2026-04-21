# Conformance Fixtures

Shared manifests and other fixture-index material used by multiple language
implementations to discover the same portable fixture subsets.

The conformance manifest is intentionally selective. It indexes representative
roles that multiple language implementations should exercise in common, rather
than attempting to enumerate every fixture in the corpus.

Canonical suite membership is more selective still. Family-local nested or
delegated suites, including the current Markdown delegated suite and Ruby
delegated nested suite, remain outside the canonical stable and widened suite
sets until a later slice promotes their review/default/replay policy
explicitly.

The manifest has two top-level sections:

- `family_feature_profiles` for per-family profile fixtures
- `families` for family-indexed fixture role entries

`diagnostics` is represented as a family inside `families`, not as a special
out-of-band fixture bucket.
