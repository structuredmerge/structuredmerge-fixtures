# Provider Contract Snapshot Manifest

This manifest inventories and admits the seven representative Phase 3 Ruby
golden-master capture targets.

Every observed artifact was captured twice in a fresh Ruby process from the
same clean revision. Admission compares complete artifact bytes and separately
records a differential `merge2` replay after canonical JSON request transport.
No output or semantic field is excluded from comparison.

Capture one target from the Ruby repository with:

```console
bundle exec ruby tools/capture_provider_snapshot.rb snapshot.tslp.json
```

Run `python3 tools/validate_provider_snapshots.py` from this repository to
verify target coverage, artifact integrity, producer provenance, normalized and
native extension evidence, exact replay, and manifest summary counts.
