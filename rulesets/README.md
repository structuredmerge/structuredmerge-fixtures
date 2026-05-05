# Compact ruleset fixtures

This tree contains compact ruleset contracts for fixture cases that exercise a
template, destination, and expected merge output.

The files intentionally live outside the JSON fixtures. A fixture records the
inputs and expected result; the matching `.smr` file records the merge contract
that a ruleset-aware implementation is expected to parse and interpret.

Ruleset paths mirror fixture paths:

```text
json/slice-09-merge/object-merge.json
rulesets/json/slice-09-merge/object-merge.smr
```

The compact syntax is the line-oriented ruleset syntax from
`MERGE_RULESET_INFORMATIONAL_DRAFT_01.md`, Appendix A.

Validate coverage and syntax with:

```sh
python3 tools/validate_rulesets.py
```
