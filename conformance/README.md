# Conformance Fixtures

Shared manifests and other fixture-index material used by multiple language
implementations to discover the same portable fixture subsets.

The conformance manifest is intentionally selective. It indexes representative
roles that multiple language implementations should exercise in common, rather
than attempting to enumerate every fixture in the corpus.

The manifest has two top-level sections:

- `family_feature_profiles` for per-family profile fixtures
- `families` for family-indexed fixture role entries

`diagnostics` is represented as a family inside `families`, not as a special
out-of-band fixture bucket.
