# Slice 951: Git Driver JSON Integration

This fixture defines JSON scenarios that implementation-specific `smorg-*`
executables must exercise through a real git-style merge-driver invocation.
The test harness should create a repository, materialize base/ours/theirs files,
run the implementation's merge-driver command with `%O %A %B %P` semantics, and
assert the exit code and working-tree output.
