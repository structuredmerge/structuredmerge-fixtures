# Typed polyglot conformance fixtures

`typed-core/` contains Alef fixture inputs shared by the generated Ruby and
Python suites in the kernel repository. The kernel's `alef.toml` points directly
at this directory; do not maintain target-specific fixture copies.

The initial profile fixture checks the explicit scope and experimental status
of the Rust-native merge entry points without registering a parser provider.
It is an introspection contract, **not** native merge corpus coverage or proof
that a provider is available. Native parser setup, merge outcomes, preservation,
and failure fixtures must be added before the full conformance gate is met.
