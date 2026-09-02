# Source Preservation and Byte Evidence

This fixture makes Slice 1027 executable without choosing a parser or merge
implementation. Consumers validate exact descriptors, ranges, digests, output
partitions, source mappings, synthesis authorization, and property results.

`compose-current-layout-with-incoming-value` retains the current document's
CRLF bytes, comment, blank-line gap, local field, lexical style, and final
newline while selecting one exact value byte from incoming.

`authorized-synthesized-member` retains every original source byte and records
the inserted separator/member bytes as authorized synthesis. Synthesized bytes
are valid output, but they are never counted as source-preserved.

The invalid examples are contract rejections. In particular, semantic
equivalence and matching blank-line counts do not excuse changed source bytes.
