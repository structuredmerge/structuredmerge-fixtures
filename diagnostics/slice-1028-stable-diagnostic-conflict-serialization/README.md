# Stable Diagnostics and Conflicts

This fixture exercises Slice 1028 independently of parser implementation. It
contains an ordered parse-failure cause chain, one exact unresolved merge3
conflict without marker output, and the same conflict retained after explicit
policy resolution.

Consumers validate canonical categories/codes, deterministic sequence and
causal references, source roles and byte spans, native-code separation,
base/ours/theirs alternatives, exact localization digests, and resolution
authorization. The invalid examples pin failures that must not be inferred from
messages or conflict-marker text.
