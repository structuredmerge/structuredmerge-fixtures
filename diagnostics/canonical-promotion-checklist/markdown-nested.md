# Markdown Nested Suite Promotion Checklist

Suite:
`markdown_nested_portable` (working name for the delegated nested Markdown
suite defined by slices 246 to 248)

Target canonical set:
Blocked pending base-family promotion. `markdown_portable` should enter a
canonical suite set before this nested suite is reconsidered.

Canonical review-request identity surface:
Unresolved. A promotion slice would need to define whether canonical review
requests identify this suite as:

- a new canonical Markdown nested family member, or
- a variant of the existing Markdown family review surface

Reviewed-default context behavior:
Unresolved. A promotion slice would need to define whether delegated nested
Markdown review introduces a new defaultable family context or reuses the
existing Markdown family context.

Replay-compatibility behavior:
Unresolved. Replay is structurally portable, but canonical replay would need an
unambiguous identity surface for nested Markdown decisions so they cannot be
mistaken for ordinary Markdown family review decisions.

Manifest or fixture membership changes:
Unresolved. Promotion would require:

- adding the promoted suite to the canonical suite definitions,
- adding any canonical review/default/replay fixture coverage for that suite,
- clarifying whether the dedicated Markdown family manifest remains parallel or
  becomes partially canonicalized

Notes:

- Portable delegated-child shapes are already available.
- The next concrete prerequisite is canonical promotion of `markdown_portable`.
- Current policy is to keep this suite family-scoped until canonical
  review/default/replay semantics are shared explicitly.
