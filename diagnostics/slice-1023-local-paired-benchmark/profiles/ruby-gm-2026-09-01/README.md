# Ruby Golden-Master Startup Profile: 2026-09-01

This profile isolates process and parser-loading costs for the pre-Alef Ruby
golden master. It is an observation baseline, not a release gate.

Fresh-process samples use GNU `time` around seven independent Ruby processes
with a warm filesystem. In-process samples use `CLOCK_MONOTONIC` around seven
independent processes. Each process loads StructuredMerge directly from the
pinned checkout and TSLP directly from the pinned vendored checkout.

The host was otherwise idle when retained samples were collected. An earlier
sample set collected while the kettle-jem suite saturated the host was
discarded rather than mixed into this profile.

## Median Observations

| Boundary | Wall time | Peak RSS |
| --- | ---: | ---: |
| Bare Ruby process | 0.03 s | 15,684 KB |
| Load `ast/merge/git` | 0.10 s | 22,748 KB |
| Load `json/merge` and TSLP | 0.17 s | 28,104 KB |
| Load and perform first strict JSON parse | 0.17 s | 28,216 KB |
| Load and perform first JSONC merge2 | 0.19 s | 29,864 KB |

Within a loaded process, the median first strict JSON parse was 8.38 ms and
the second was 0.17 ms. The JSONC grammar was already available after that
first TSLP parse: its first and second parses were 0.17 ms and 0.14 ms. A first
merge2 with loaded grammars was 14.97 ms; 100 repeated merges had a median of
1.27 ms per operation.

The important architectural signal is that process and library loading dwarf
small-file parsing and merging. A batched or long-lived adapter can remove
roughly 0.17 seconds of repeated startup per invocation without changing the
correctness path. The profile does not imply that TSLP grammars are eagerly
cached: it records only these JSON/JSONC calls through the supported TSLP API.

`startup-profile.json` contains every retained sample, summary statistics,
source revisions, hashes, commands, and environment metadata.
