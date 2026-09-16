# Typed polyglot conformance fixtures

`typed-core/` contains Alef fixture inputs shared by the generated Ruby and
Python suites in the kernel repository. The kernel's `alef.toml` points directly
at this directory; do not maintain target-specific fixture copies.

The initial profile fixture checks the explicit scope and experimental status
of the Rust-native merge entry points without registering a parser provider.
It is an introspection contract, **not** native merge corpus coverage or proof
that a provider is available. Native parser setup, merge outcomes, preservation,
and failure fixtures must be added before the full conformance gate is met.

The Python native-merge family now covers independent assignments, conflicting
assignments, native syntax failure, unsupported import owners, and exact UTF-8
BOM/CRLF/comment/final-newline preservation. These expectations exercise the
bounded LibCST-backed Rust declarations profile, not general Python semantics or
Ruby oracle parity. Ruby intentionally does not run this Python-only family;
its Psych/YAML family remains to be mapped.
