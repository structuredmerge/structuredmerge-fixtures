# Typed polyglot conformance fixtures

`typed-core/` contains Alef fixture inputs shared by the generated Ruby and
Python suites in the kernel repository. The kernel's `alef.toml` points directly
at this directory; do not maintain target-specific fixture copies.

The twelve `capability_*` fixtures cover explicit-profile manifest observations:
all eight profiles, missing-backend eligibility, undeclared operations/dialects,
and empty inventory queries. Helpers only construct typed requests; assertions
live here. These are not the full workflow-negotiation contract or merge corpus
coverage. See the spec repository's `TYPED_CAPABILITY_MANIFEST_CONTRACT.md`.

The initial profile fixture checks the explicit scope and experimental status
of the Rust-native merge entry points without registering a parser provider.
It is an introspection contract, **not** native merge corpus coverage or proof
that a provider is available. Native parser setup, merge outcomes, preservation,
and failure fixtures must be added before the full conformance gate is met.

The Python native-merge family now covers independent assignments, conflicting
assignments, native syntax failure, unsupported import owners, and exact UTF-8
BOM/CRLF/comment/final-newline preservation. These expectations exercise the
bounded LibCST-backed Rust declarations profile, not general Python semantics or
Ruby oracle parity. Ruby intentionally does not run this Python-only family.

The Ruby Psych/YAML family covers independent mapping edits, conflicts, native
syntax failures, unsupported top-level sequences, and exact BOM/CRLF/Unicode
preservation. Python intentionally excludes this Ruby-provider family. Each
family exercises its real native parser and the corresponding scoped Rust merge
entry point; neither claims full-language or cross-provider parity.

The JSON operation family runs the same eleven fixtures in both generated Ruby
and Python suites. It covers nested JSON5 analysis, unclaimed native comments,
JSONC dialect rejection, duplicate decoded keys, repeated-fragment and trivia
diffs, Unicode no-ops, directional current/array precedence, independent merge3,
canonical conflicts, and selected-source comment/CRLF/final-newline preservation.
Each adapter explicitly registers the Rust TreeHaver language-pack provider and
builds typed common requests. It contains no matching, expected-output or render
logic. These fixtures test the generated binding path, not Ruby golden-master
authority, all parser backends, full analysis-policy parity or publication gates.
