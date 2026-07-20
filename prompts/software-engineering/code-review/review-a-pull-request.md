# Review a Pull Request

Use this for an end-to-end pull request review.

## Prompt

Review pull request `[number or URL]` in `[repository]`.

Stated goal: `[summary]`

Acceptance criteria or issue: `[details or link]`

Review priorities: `[correctness, security, tests, docs, deployment, or other]`

Read the full diff, relevant surrounding code, linked requirements, automated
checks, and unresolved discussion. Look for behavioral regressions, incomplete
paths, unsafe assumptions, compatibility issues, missing tests, and
documentation or rollout gaps. Return findings first, ordered by severity and
anchored to exact changed lines. Then summarize verification performed and
residual risks. Do not approve, merge, or post comments unless explicitly
authorized.
