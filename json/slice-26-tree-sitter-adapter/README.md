# Slice 26 Tree-sitter Adapter

Shared fixture covering the minimal tree-sitter-backed strict-json adapter
baseline:

- success preserves the existing observable `JsonAnalysis` shape
- backend syntax errors surface as `parse_error`
- unsupported dialect requests surface as `unsupported_feature`
