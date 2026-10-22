# Shared merge-driver v1: two-sided disjoint edits and designed conflicts

A portable **partial** conformance suite exercising the `merge-driver` command
of any installed full `smorg*` CLI against the regression class that bit the
JSON family in 7.1.15: both sides edit the same document at disjoint
locations, and the engine must merge both edits instead of failing or
conflicting.

Fourteen positive cases cover JSON (pretty and compact), JSONC, YAML block
mappings, TOML, dotenv, Markdown sections, Ruby, Go, Rust, TypeScript, Bash,
RBS, and ID-tagged HTML. Two negative cases pin designed fail-closed behavior
that must not be "fixed" into silent merges: YAML flow-style collections
(exact one-sided merges only) and HTML text edits in elements without IDs
(unmanaged source changes).

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_merge_driver_conformance.py --executable /absolute/path/to/smorg-rb
```

Each case runs in a fresh sandbox directory containing exactly the files in
its `files` map, invokes the executable with the case's `argv`, and checks:

- `exit_code` — exact process exit status
- `report_ok` — the `ok` field of the `--report` JSON
- `conflict_count` — number of entries in the report's `conflicts` array
- `output_source` — exact merged document (Ruby golden-master rendering)
- `output_json_value` — parsed-JSON equality, for runners that prefer
  semantic over byte-exact assertions (present on JSON-family cases)
- `diagnostics_contain` / `conflicts_category_contain` — substring/category
  presence for the designed-conflict cases

Render strategies are implementation-specific and intentionally not asserted.
The runner reports `full_cli_conformance: false`; it returns 1 if any case
fails.

The dotenv case ships its own `.gitattributes` because dotenv language
routing flows through gitattributes (`smorg.language=dotenv`); without that
mapping an `.env` path falls back to the plain-text provider.
