# Ruby Nested Suite Promotion Checklist

Suite:
`ruby_nested_portable` (working name for the delegated nested Ruby suite
defined by slices 249 to 251)

Target canonical set:
Not ready, but no longer blocked on base-family promotion. The next plausible
target is the canonical widened suite set.

Canonical review-request identity surface:
Unresolved. A promotion slice would need to define whether canonical review
requests identify this suite as:

- a new canonical nested Ruby member distinct from `ruby_portable`, or
- an extension of the existing Ruby canonical family surface

Reviewed-default context behavior:
Unresolved. A promotion slice would need to define whether delegated nested
Ruby behavior extends the existing `ruby_portable` default surface or requires
its own canonical defaultable family context.

Replay-compatibility behavior:
Unresolved. Replay is structurally portable, but canonical replay would need an
identity surface that distinguishes nested delegated Ruby review decisions from
ordinary `ruby_portable` review decisions.

Manifest or fixture membership changes:
Unresolved. Promotion would require:

- adding the promoted suite to the canonical suite definitions,
- adding canonical review/default/replay fixture coverage for the promoted
  nested Ruby surface,
- clarifying whether `ruby_portable` remains unchanged or is widened to absorb
  the nested delegated roles

Notes:

- Portable delegated-child shapes are already available.
- The base-family prerequisite is now satisfied by canonical promotion of
  `ruby_portable`.
- Current policy is to keep this suite family-scoped until canonical
  review/default/replay semantics are shared explicitly.
