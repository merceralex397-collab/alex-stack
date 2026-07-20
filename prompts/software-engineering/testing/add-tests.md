# Add Tests

Use this when an agent is authorized to add or improve automated tests.

## Prompt

Add tests for `[behavior, feature, or defect]` in `[repository or project]`.

Behavior to protect: `[requirements or regression]`

Relevant code: `[files or modules]`

Known risks and edge cases: `[details]`

Constraints: `[test framework, runtime, or scope]`

Inspect existing tests and project instructions first. Choose the lowest test
level that reliably proves the behavior, follow local patterns, and test
observable outcomes rather than implementation details. Ensure the test would
fail for the relevant broken behavior. Run the focused test command and report
coverage added, results, and gaps that remain.
