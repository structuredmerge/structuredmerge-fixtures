# Markdown Portable Promotion Checklist

Suite:
`{kind: "portable", subject: {grammar: "markdown"}}`

Target canonical set:
Blocked pending provider-policy resolution. No canonical target set should be
selected until Markdown provider choice is explicit.

Canonical review-request identity surface:
Blocked on provider policy. A promotion slice must define whether canonical
Markdown review uses:

- a native provider identity,
- a substrate/tree-sitter identity, or
- a portable provider-selection rule

Reviewed-default context behavior:
Blocked on provider policy. Reviewed-default behavior cannot be fixed until the
canonical Markdown family context shape chooses a provider policy.

Replay-compatibility behavior:
Blocked on provider policy. Replay needs one stable canonical Markdown context
identity surface before imported decisions can be unambiguous.

Manifest or fixture membership changes:
Expected after provider policy is resolved:

- add the base Markdown portable descriptor to the chosen canonical suite set,
- add canonical plan/report/review/default/replay fixture coverage for
  Markdown,
- keep nested Markdown blocked until base-family promotion lands first

Notes:

- Markdown already has a portable family contract and suite-descriptor surface.
- The remaining blocker is canonical provider policy.
