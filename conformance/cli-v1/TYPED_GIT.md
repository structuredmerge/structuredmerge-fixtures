# Typed kernel real-Git cases

`typed-git.json` is a separate positive/error execution corpus for the explicit
typed kernel Git profile. It does not replace the portable discovery manifest
or claim all native CLIs conform. The kernel's
`workspace-scripts/check_installed_cli_git.py --typed` consumes these cases.

Each case creates base/ours/theirs Git commits and executes one real Git merge
using `kernel.git.json`, `kernel.git.json.v1` and `kernel.tslp.json`. A caller
supplies an existing local JSON grammar; `cold: true` intentionally withholds it.
Conflict policy is leave-ours unless `conflict_policy: write` is explicit.

Expected `git_exit` and reported `driver_exit` are distinct: Git returns 1 for
both unresolved conflict and driver error, while the typed report distinguishes
conflict (1) from unavailable/parser failure (2). Never classify conflict from
the Git process exit alone. Preserve the typed result nested in the CLI report.

Clean merges verify stage-0 bytes and JSON content. Failed/conflicted merges
verify all three unresolved index stages and either exact ours preservation or
exact provider `conflicted_output` bytes. All cases preserve branch source blobs
and HEAD. The runner uses a logical `.txt` name with quoting/Unicode characters
to catch accidental extension dispatch and shell quoting errors.

The runner must clean disposable repositories/install copies on success and
failure, retaining small reports with fixture, executable and grammar digests.
These cases do not cover typed diff, default selection, pre-execution report
transport, asset provenance, other grammar families or cross-platform packaging.
