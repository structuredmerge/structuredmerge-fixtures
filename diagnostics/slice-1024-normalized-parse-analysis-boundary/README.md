# Slice 1024: Normalized parse and analysis boundary

This fixture instantiates the first transport contract from Spec Slice 1024.
It proves an explicitly selected TSLP JSON parse, normalized byte-oriented node
edges, and exact ownership of a retained interstitial blank-line gap.

The fixture intentionally starts with the Tree-sitter path. Native Prism and
Psych snapshots must be captured from a pinned Ruby golden-master release so
the fixture records observed behavior rather than a hand-authored approximation.

`invalid_cases` records fail-closed conditions every consumer must reject.
