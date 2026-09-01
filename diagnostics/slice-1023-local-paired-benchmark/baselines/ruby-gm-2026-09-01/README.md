# Ruby Golden-Master Micro Baseline: 2026-09-01

This directory records the first pre-Alef Ruby golden-master execution of the
Slice 1023 `micro` profile. `manifest.json` pins the Ruby implementation, fixture
corpus, vendored TSLP runtime, loaded artifacts, and host environment.

The run loaded `ast-merge-git`, `ast-merge`, `json-merge`, and `tree_haver`
directly from the pinned StructuredMerge Ruby checkout. It loaded TSLP from the
pinned vendored checkout. It did not use released StructuredMerge gems.

## Result

| Case | Git | Ruby GM |
| --- | --- | --- |
| Independent JSON fields | `false_conflict` | `correct_clean` |
| Same-owner JSON edit | `true_conflict` | `true_conflict` |
| Malformed `ours` JSON | `false_conflict` | `error` |

The malformed-input error is the case's reviewed expected outcome and includes
the required `ours` attribution. It is not a runner crash. The benchmark report
currently presents all `error` outcomes under reliability, so later contract
work must distinguish expected diagnostic rejection from adapter or runner
failure.

No false auto-merge occurred. The non-compensable safety gate passed.

## Artifacts

- `micro-run.json` contains raw Git and candidate evidence for the same run.
- `micro-report.json` is the non-scalar paired aggregate built from that raw
  run without rerunning the adapters.
- `manifest.json` supplies source and runtime provenance that the v1 run
  envelope does not yet carry.
