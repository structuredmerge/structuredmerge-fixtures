# Rust Kernel Provider Traits

This architecture fixture records the repositories audited for Slice 1030 and
the intended trait, ownership, provider-mode, and call-path constraints.

It is intentionally non-executable: the current Rust crates do not yet
implement these traits, and TSLP's current Alef IR exports no host-implemented
traits. Consumers validate that a future implementation follows the existing
portable envelopes, keeps TreeHaver as the only parser selector, batches host
calls, preserves native extensions, and fails closed.
