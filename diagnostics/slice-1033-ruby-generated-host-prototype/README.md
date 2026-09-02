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

The `prototype_evidence` section in `contract.json` separates completed gates
from open work. In particular, repeated calls initiated by Ruby threads do not
prove that an arbitrary Rust worker can resolve an opaque Ruby value or reenter
Ruby under a supported runtime/GVL path.

The pinned run under `observed/2026-09-02-host-transport` measures a validated
in-process Rust identity operation, an Alef-generated typed Ruby callback, and
a canonical-JSON detached-file Ruby callback across 36 batch/payload scenarios.
Each scenario retains 30 raw monotonic-clock samples and verifies exact source
length and SHA-256 after every call. The reviewed decision is to use generated
typed values with inline binary source by default. Detached bytes remain an
explicitly negotiated option for isolation or out-of-process providers; this
single-host run does not justify an automatic payload-size threshold.

The generated typed callback receives DTOs from Rust and must return an exact
Ruby byte string. Its exercised return path performs no arbitrary `to_json`
conversion. Alef's general DTO input conversion still contains such a fallback,
but that reverse conversion is not part of this host callback transport and is
not evidence that arbitrary Ruby objects may cross the provider boundary.

The completed generated-host prototype also exercises native Rust worker
callbacks, async Rust-to-Ruby re-entry with the GVL released, cancellation at
all four dispatch boundaries, in-flight unregister and atomic replacement,
bounded graceful/forced shutdown, and loss of a real child-process sidecar.
Sidecar loss remains an error on the explicitly selected provider even when a
healthy alternative is registered; there is no substitution path.

The Phase 4 exit gate additionally registers the Rust TreeHaver adapter over a
real TSLP JSON parser beside an Alef-hosted Ruby parser in the same registry.
Both preserve a valid JSON source's exact CRLF and spacing bytes. Malformed JSON
fails on the explicitly selected Rust TSLP provider, and the Ruby provider's
recorded calls prove that it was not used as a fallback.
