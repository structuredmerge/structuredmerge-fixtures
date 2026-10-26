# Slice 1045: ingest observation and deletion authority

`contract.json` contains designed (not runtime-captured) cases for the proposed
`structuredmerge.ingest-observation/v1` companion. The companion preserves exact
legacy result bytes separately from source/processing/authority evidence.

Run from the fixtures root:

```sh
python3 tools/validate_ingest_observations.py
python3 -m unittest discover -s tools -p 'test_*.py'
```

Each isolated `cases` entry has an envelope, trusted local `context`, and either
an expected verification decision or a named rejection. `sequences` share model
state across deliveries to exercise exact retry versus conflicting payloads.
No expected success is proof of deployed adapter support or producer conformance.

Context provides the document scope, producer ID, trusted prior head/digest,
validated evidence references, authorized actions and retrievable local byte
resources. It is supplied by the harness, **never obtained from the envelope**.
A real adapter must authenticate/resolve these facts independently and enforce
atomic, document-scoped effects. The model has one head per invocation sequence,
uses fresh projection revisions, and does not implement unchanged-revision
observation persistence, cross-document event storage or real compare-and-set.

Positive cases preserve duplicate occurrences, ordinal churn, original CRLF and
whitespace, reprojection identity and both hosted JSONL-string and Ur Brain array
dialects. Negative cases exercise incomplete deletion authority, scope/prior
mismatch, unavailable or mismatching bytes, unknown parser proof, invalid times,
malformed exports and injected deletes. Tests assert failure has no modeled
state effects and never rewrites the envelope. Additional unit tests cover strict
JSON and retry tampering.

The validator checks compact inventories, delta membership and authorization;
it does not reproduce chunking, validate every legacy metric, implement vector
rebuilds, infer lineage or authenticate source events. Existing v1 producers and
consumers are untouched. See spec `INGEST_OBSERVATION_CONTRACT.md` and plans
issues #2, #3 and #12 for the remaining adapter/storage/rollout gates.
