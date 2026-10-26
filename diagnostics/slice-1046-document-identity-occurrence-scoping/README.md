# Slice 1046 — document identity, namespace and occurrence scoping fixtures

Designed contract examples for the "Document identity, namespace and rename/alias semantics" section of the ingest-observation contract (spec slice 1046, [plans #4](https://github.com/structuredmerge/plans/issues/4)). Six cases covering rename-as-new-scope, cross-scope prior rejection, extension alias non-authorization, workspace namespace disjointness, equal text under distinct documents, and duplicate ordinals in a prior inventory.

Run via `tools/test_validate_ingest_observations.py` (loads this corpus and the slice-1045 corpus). Regenerate with `tmp/generate-slice-1046.py` (workspace-local, not committed).
