# Slice 1047 — revision ancestry and merge-role fixtures

Designed contract examples for the "Revision ancestry and merge-role links" section of the ingest-observation contract (spec slice 1047, [plans #5](https://github.com/structuredmerge/plans/issues/5)). Six negative cases (missing chain parent, self-parent, declared root with prior, duplicate parents, non-string parent, late import with declared parents) and one four-step chain sequence (undeclared initial → linear parent → multi-parent merge with external parent → content-equal distinct revision).

Loaded by `tools/test_validate_ingest_observations.py` alongside the 1045/1046 corpora. Regenerate with `tmp/generate-slice-1047.py` (workspace-local, not committed).
