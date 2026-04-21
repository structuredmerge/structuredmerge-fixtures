# Ruby Portable Promotion Checklist

Suite:
`ruby_portable`

Target canonical set:
Recommended next target: canonical widened suite set.

Canonical review-request identity surface:
Needed. Promotion should define the canonical review-request identity for the
Ruby family alongside the existing widened source-family request surfaces.

Reviewed-default context behavior:
Needed. Promotion should define whether `ruby_portable` behaves like the other
canonical widened source families when explicit Ruby family context is absent.

Replay-compatibility behavior:
Needed. Promotion should define replay compatibility for canonical Ruby review
decisions using the ordinary widened canonical replay surface.

Manifest or fixture membership changes:
Expected:

- add `ruby_portable` to the canonical widened suite definitions,
- add canonical widened plan/report/review/default/replay fixture coverage for
  Ruby,
- keep nested delegated Ruby roles outside canonical membership for now

Notes:

- This is the narrowest next canonical promotion candidate because Ruby already
  has a defined family manifest and a portable non-nested suite surface.
- Nested Ruby promotion should only be reconsidered after this base-family
  promotion lands.
