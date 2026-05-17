# Slice 952: Go Merge3

This fixture defines the first source-language git merge scenarios for Go.
They are intentionally small and parser-neutral so the tree-sitter, `go/parser`,
and `github.com/dave/dst` backends can all be compared against the same cases.

The expected outputs are semantic targets, not formatting guarantees. Backend
tests may record formatting-preservation scores separately.
