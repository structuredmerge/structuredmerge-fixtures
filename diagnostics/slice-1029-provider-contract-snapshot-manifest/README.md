# Provider Contract Snapshot Manifest

This manifest inventories the seven representative Phase 3 capture targets.
It intentionally admits no observed golden-master snapshots yet.

The existing TSLP JSON contract and Prism normalized-tree fixtures are marked
`provisional`: their bytes and repository provenance are useful, but they were
not produced by a pinned, clean Ruby GM capture with deterministic replay. The
remaining rows are `pending` and name exact provider/backend, input, normalized
contract, extension, and provenance requirements.

After the Ruby release is pinned, the capture pass replaces or supersedes these
rows with immutable `observed` rows. Validators must never infer matrix
completion from provisional expectations.
