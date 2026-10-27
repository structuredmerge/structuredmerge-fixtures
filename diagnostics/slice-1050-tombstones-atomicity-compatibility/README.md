# Slice 1050 — tombstone, atomicity and compatibility fixtures

Designed contract examples for the "Tombstone records, application atomicity and compatibility" section of the ingest-observation contract (spec slice 1050, [plans #9](https://github.com/structuredmerge/plans/issues/9)): derived tombstone records asserted for authoritative-empty and explicit-source deletions, and an overlapping upsert/delete rejection.

Loaded by `tools/test_validate_ingest_observations.py` alongside the 1045–1049 corpora. Regenerate with `tmp/generate-slice-1050.py` (workspace-local, not committed).
