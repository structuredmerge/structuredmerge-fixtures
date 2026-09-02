# Slice 1025: Versioned merge operation envelopes

This fixture instantiates the serialized provider contract for `analyze`,
`diff2`, directional `merge2`, and base-aware `merge3`.

The source catalog is fixture-local and content-addressed. Each request repeats
the semantic role, byte length, and digest that an adapter must verify before
dispatch. Results use the existing Ruby provider-result schema identifier.

`invalid_cases` records role, selection, base-participation, output,
fallback, conflict, and preservation contradictions that consumers must reject.
