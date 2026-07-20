# Investigate a Bug

Use this to establish a defect's cause and, when authorized, fix it.

## Prompt

Investigate this bug in `[repository or system]`:

`[bug report]`

Expected behavior: `[expected result]`

Observed behavior: `[actual result and exact errors]`

Reproduction steps: `[steps or unknown]`

Environment: `[version, platform, configuration]`

Recent changes or attempted fixes: `[details]`

Authorization: `[diagnosis only or diagnosis and fix]`

Inspect the relevant code and evidence. Reproduce the issue when practical,
separate observations from hypotheses, and narrow the cause with targeted
checks. If fixing is authorized, add a regression test where useful, make the
smallest cause-level fix, and run focused validation. Report the root cause,
evidence, change, and anything not verified.
