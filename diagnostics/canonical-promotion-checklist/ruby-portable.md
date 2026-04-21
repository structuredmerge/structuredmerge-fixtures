# Ruby Portable Promotion Checklist

Suite:
`{kind: "portable", subject: {grammar: "ruby"}}`

Target canonical set:
Completed: canonical widened suite set.

Canonical review-request identity surface:
Resolved for the base suite. Ruby now uses the ordinary canonical widened
family-context review-request surface.

Reviewed-default context behavior:
Resolved for the base suite. The base Ruby portable descriptor now behaves like
the other canonical widened source families when explicit Ruby family context
is absent.

Replay-compatibility behavior:
Resolved for the base suite through the ordinary widened canonical replay
surface.

Manifest or fixture membership changes:
Completed:

- add the base Ruby portable descriptor to the canonical widened suite
  definitions,
- add canonical widened plan/report/review/default/replay fixture coverage for
  Ruby,
- keep nested delegated Ruby roles outside canonical membership for now

Notes:

- This base-family promotion is now landed.
- Nested Ruby promotion may now be reconsidered, but only through a separate
  nested promotion slice.
