# Slice 723: Binary core contract

This fixture defines portable binary merge vocabulary that format families can
reuse before implementing a real renderer. It intentionally stays format-neutral:
the sample uses PNG-like schema paths only to make byte ranges and checksum
updates concrete.

The raw payload section seeds slice 727 with a small hex-encoded byte corpus and
named header, length, body, and checksum regions for portable range checks.
