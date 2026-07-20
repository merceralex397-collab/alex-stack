# Review Code

Use this for a defect-focused review of code or a change set.

## Prompt

Review `[code, commit, diff, or file set]` in `[repository or project]`.

Intended behavior: `[requirements]`

Review scope: `[correctness, security, reliability, performance, maintainability]`

Relevant constraints: `[compatibility, architecture, or operating environment]`

Inspect the surrounding code, callers, tests, and local instructions needed to
understand the change. Lead with actionable findings ordered by severity. For
each finding, cite the precise location, describe the failing scenario and
impact, and explain why existing checks do not prevent it. Distinguish defects
from preferences. If no findings remain, say so and list residual testing or
context gaps.
