# Ruby Generated Host-Provider Prototype

This architecture fixture defines the executable acceptance and measurement
harness for the first Alef-generated Ruby host provider. It keeps the prototype
outside canonical SM Ruby, compares generated typed values with canonical JSON
plus exact bytes, and treats thread/GVL, lifecycle, preservation, and error
fidelity as hard gates.

`identity-corpus.json` is the executable, runtime-neutral byte corpus. Each
case defines a compact payload recipe plus an independently recorded byte
length and SHA-256 digest. Implementations must materialize the recipe and
verify those fields before using the payload, then prove the same fields after
every boundary crossing. The above-threshold case does not prove detached
transport unless the tested adapter actually selects that transport.
