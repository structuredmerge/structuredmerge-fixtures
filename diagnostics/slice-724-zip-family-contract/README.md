# Slice 724: ZIP family contract

This fixture defines the first ZIP-family contract on top of the binary core
vocabulary. It models path-keyed archive entries, byte ranges for ZIP structures,
member merge decisions, and nested dispatch for a text-like member without
requiring a renderer yet.

The unsafe entries section seeds slice 729 with path traversal, duplicate
normalized path, encrypted member, and signing-sensitive member cases that must
fail closed before writable ZIP behavior is added.
