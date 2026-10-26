# Slice 1048 — temporal, dedupe and precondition fixtures

Designed contract examples for the temporal/dedupe/precondition rules of the ingest-observation contract (spec slice 1048, [plans #8](https://github.com/structuredmerge/plans/issues/8)): source time intervals (inverted and half-present rejections, accepted interval), unknown source time staying explicitly unknown, unchanged-content re-observation without head advancement, projection-evidence revision-reuse rejection, and the same observation identity verifying independently in another scope.

Loaded by `tools/test_validate_ingest_observations.py` alongside the 1045–1047 corpora. Regenerate with `tmp/generate-slice-1048.py` (workspace-local, not committed).
