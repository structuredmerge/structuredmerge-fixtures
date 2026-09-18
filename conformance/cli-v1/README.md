# Shared CLI v1: discovery and argument rejection

The normative contract is the specification repository's
`CLI_DISPATCH_CONTRACT.md`. This is a portable **partial** conformance suite, not
full CLI or provider authority. Twenty cases execute real processes against any
installed full `smorg*` CLI. Product-group extensions do not implement this suite.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --executable /absolute/path/to/smorg
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p test_check_cli_contract.py -v
```

Each case starts with fresh, tiny UTF-8 source/output/report sentinels in a
repository-local scratch directory. Every case in this initial subset must leave
all those files unchanged and create no extra files. Cases check exact exit codes,
stdout/stderr channel behavior, required help tokens, and basic version/language
JSON envelopes. A successful basic JSON check does **not** validate full provider
availability or the report's nested schemas; those remain separate gates.

The runner always reports `full_cli_conformance: false` and
`publication_gate: false`. It returns 1 if any case fails. Unsupported discovery
commands are failures, not skips. Reports retain executable and manifest hashes,
argument vectors, exit status, exact base64-captured output, diagnostic text views
and before/after file identities. Output exceeding 256 KiB fails and is truncated
in the retained report. Each child has a ten-second deadline; Unix process groups
are retired, including descendants, on completion or failure. Windows currently
terminates only the direct child and does not establish descendant cleanup.

Allow 1 GiB working space above the mandatory 20 GiB reserve. Runtime polling
checks free space and capture size; these are cooperative monitoring limits, not
an OS filesystem quota. Case directories are cleaned even when assertions fail;
small `tmp/cli-conformance-*/report.json` files remain. Do not point the runner at
untrusted executables: it is not a sandbox and inherits the operator's environment.

Remaining portable coverage includes positive typed operations, full report
validation, selectors and unavailable providers, exact-byte preservation on
success, conflicts/fallback policy, real Git, output/report aliases and write
faults, external dispatch, and the platform/runtime matrix. Existing kernel
integration suites retain some of that evidence but do not close this shared gate.
