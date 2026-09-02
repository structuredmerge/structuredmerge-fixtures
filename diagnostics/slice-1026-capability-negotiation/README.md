# Slice 1026: Capability negotiation

This fixture separates `ast-merge` workflow/backend provider selection from
TreeHaver parser-backend selection. It covers multi-backend RBS, Ruby substrate
isolation from Prism, an explicit Prism provider, cold TSLP loading,
deterministic ties, and fail-closed backend unavailability.

The fixture records the Ruby golden master's remaining legacy TreeHaver
ordering as an implementation gap, not as portable selection behavior.
