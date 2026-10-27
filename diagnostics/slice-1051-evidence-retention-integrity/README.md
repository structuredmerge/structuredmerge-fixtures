# Slice 1051 — evidence retention and integrity fixtures

Designed contract examples for the "Evidence retention and reference integrity" section of the ingest-observation contract (spec slice 1051, [plans #11](https://github.com/structuredmerge/plans/issues/11)): retained-evidence manifests on verified decisions (inline and ref transports), and evidence lifetime shorter than referring history rejecting as `unavailable_bytes` when the reference expires between observations.

Loaded by `tools/test_validate_ingest_observations.py` alongside the 1045–1050 corpora. Regenerate with `tmp/generate-slice-1051.py` (workspace-local, not committed).
