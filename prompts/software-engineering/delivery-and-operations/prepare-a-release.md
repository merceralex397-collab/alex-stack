# Prepare a Release

Use this to assess whether a change is ready to ship.

## Prompt

Prepare release `[version or change]` for `[product or service]`.

Included changes: `[commits, pull requests, or features]`

Target environments: `[environments]`

Release requirements: `[checks, approvals, documentation, or timing]`

Compatibility or migration concerns: `[details]`

Rollback capabilities: `[details]`

Inspect the actual release state and produce a readiness checklist covering
builds, tests, configuration, data migrations, security, observability,
documentation, stakeholder communication, rollout, validation, and rollback.
Identify blocking versus non-blocking risks and the evidence for each. Do not
deploy, publish, tag, or merge unless explicitly authorized.
