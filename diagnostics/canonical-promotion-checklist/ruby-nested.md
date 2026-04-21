# Ruby Nested Suite Promotion Checklist

Suite:
`ruby_nested_portable` (working name for the delegated nested Ruby suite
defined by slices 249 to 251)

Target canonical set:
Not ready, but no longer blocked on base-family promotion. The next plausible
target is the canonical widened suite set.

Canonical review-request identity surface:
Recommended shape: keep a distinct canonical nested Ruby suite while reusing
the existing `family_context:ruby` review-request surface.

Reviewed-default context behavior:
Recommended shape: reuse the existing canonical Ruby defaultable family
context rather than introducing a second Ruby-specific default surface.

Replay-compatibility behavior:
Recommended shape: reuse the existing canonical Ruby replay identity surface
while keeping nested Ruby as a distinct suite member in manifest/report
entries.

Manifest or fixture membership changes:
Still required:

- adding the promoted suite to the canonical suite definitions,
- adding canonical review/default/replay fixture coverage for the promoted
  nested Ruby surface,
- clarifying whether `ruby_portable` remains unchanged or is widened to absorb
  the nested delegated roles

Notes:

- Portable delegated-child shapes are already available.
- The base-family prerequisite is now satisfied by canonical promotion of
  `ruby_portable`.
- Recommended next design: keep nested Ruby as a separate canonical suite while
  reusing `family_context:ruby`.
- Current policy is to keep this suite family-scoped until canonical
  review/default/replay semantics are shared explicitly.
