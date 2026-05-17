# Git Merge3 Contract

This slice defines the initial portable contract for `ast-merge-git`.

It deliberately uses JSON first because JSON has deterministic parsing and
owner-path matching in every implementation. The contract proves that git merge
requests carry three roles (`base`, `ours`, `theirs`) and that semantic results
are based on base-relative deltas, not a two-way template/destination merge.
