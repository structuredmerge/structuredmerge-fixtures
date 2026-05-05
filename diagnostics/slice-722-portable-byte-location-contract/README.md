# Slice 722: Portable byte location contract

This fixture defines portable byte-location semantics for tree-haver adapters and
binary substrates. Ranges are half-open byte ranges, source-point columns are
byte-oriented, and byte slicing must preserve UTF-8 source text without treating
characters as byte offsets.
