# Create a Test Plan

Use this to choose the most valuable checks for a change or system.

## Prompt

Create a test plan for `[feature, change, or system]`.

Expected behavior: `[requirements]`

Architecture and interfaces: `[relevant context]`

Main risks: `[known concerns]`

Supported environments: `[platforms, versions, or configurations]`

Existing test coverage: `[details, if known]`

Prioritize tests by user impact and likelihood of failure. Cover the happy path,
boundaries, invalid input, permissions, state transitions, failures,
compatibility, and recovery where relevant. Recommend the right level for each
test—unit, integration, end-to-end, or manual—and identify fixtures, mocks,
environments, and clear pass criteria. Avoid low-value duplication.
