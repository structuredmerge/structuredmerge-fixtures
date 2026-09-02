# Expanded Ruby Golden-Master Comparison: 2026-09-01

This directory records the seven-case pre-Alef Ruby golden-master `micro`
profile against the textual baseline and pinned Mergiraf 0.18.0 competitor.
It extends the first three-case baseline with merge2 layout preservation,
JSONC comments, JSON5 order/formatting, and duplicate identity.

## Results

| Case | Git / overwrite baseline | Ruby GM | Mergiraf |
| --- | --- | --- | --- |
| Independent JSON fields | `false_conflict` | `correct_clean` | `correct_clean` |
| Same-owner JSON edit | `true_conflict` | `true_conflict` | `true_conflict` |
| Malformed `ours` JSON | `false_conflict` | `correct_clean` expected rejection | `false_conflict` |
| JSONC merge2 layout | `false_auto_merge` | `correct_clean` | `unsupported` |
| JSONC comment preservation | `false_conflict` | `correct_clean` | `unsupported` |
| JSON5 order and formatting | `false_conflict` | `correct_clean` | `unsupported` |
| Duplicate JSON identity | `true_conflict` | `true_conflict` | `false_auto_merge` |

Ruby has five correct clean results and two true conflicts. Its safety,
preservation, and reliability gates pass with no unverified preservation
requirements. The categorized parse rejection is expected by its oracle and
is not a runner error.

The Mergiraf comparison is intentionally coverage-aware. The pinned version
does not claim merge2, JSONC, or JSON5 support, so those three cases are
`unsupported`, not quality failures. Its duplicate-identity result is a
non-compensable competitor safety finding, but competitor outcomes never alter
the Ruby candidate gate. Seven cases are development sentinels, not enough for
a public aggregate ranking.

## Artifacts

- `micro-run.json` contains exact process, output, diagnostic, runtime,
  preservation, and competitor evidence.
- `micro-report.json` is generated from that exact run without rerunning any
  adapter.
- `external-time.txt` records end-to-end orchestration time and peak RSS; it is
  observational and does not affect correctness.
- `manifest.json` pins source revisions, hashes, environment, and the outcome
  interpretation.
