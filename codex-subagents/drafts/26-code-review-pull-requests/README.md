# Code Review and Pull Requests

This is a core development team from the source workflow.

Primary A-level artifact: a deduplicated review report prioritized by blocking, high-priority, recommended, optional, and validation-required findings, each with concrete evidence and impact.

## Topology

- A: [Code Review Manager](./code-review-manager.toml) - `code-review-manager`
  - B: [Correctness Review Lead](./code-review-correctness-review-lead.toml) - `code-review-correctness-review-lead`
    - C: [Logic Reviewer](./code-review-logic-reviewer.toml) - `code-review-logic-reviewer`
    - C: [Edge Case Reviewer](./code-review-edge-case-reviewer.toml) - `code-review-edge-case-reviewer`
    - C: [Error Handling Reviewer](./code-review-error-handling-reviewer.toml) - `code-review-error-handling-reviewer`
    - C: [Concurrency Reviewer](./code-review-concurrency-reviewer.toml) - `code-review-concurrency-reviewer`
  - B: [Architecture Review Lead](./code-review-architecture-review-lead.toml) - `code-review-architecture-review-lead`
    - C: [Boundary and Coupling Reviewer](./code-review-boundary-and-coupling-reviewer.toml) - `code-review-boundary-and-coupling-reviewer`
    - C: [Pattern Consistency Reviewer](./code-review-pattern-consistency-reviewer.toml) - `code-review-pattern-consistency-reviewer`
    - C: [API Contract Reviewer](./code-review-api-contract-reviewer.toml) - `code-review-api-contract-reviewer`
    - C: [Data Flow Reviewer](./code-review-data-flow-reviewer.toml) - `code-review-data-flow-reviewer`
  - B: [Quality Review Lead](./code-review-quality-review-lead.toml) - `code-review-quality-review-lead`
    - C: [Test Coverage Reviewer](./code-review-test-coverage-reviewer.toml) - `code-review-test-coverage-reviewer`
    - C: [Maintainability Reviewer](./code-review-maintainability-reviewer.toml) - `code-review-maintainability-reviewer`
    - C: [Performance Reviewer](./code-review-performance-reviewer.toml) - `code-review-performance-reviewer`
    - C: [Documentation Reviewer](./code-review-documentation-reviewer.toml) - `code-review-documentation-reviewer`
  - B: [Risk Review Lead](./code-review-risk-review-lead.toml) - `code-review-risk-review-lead`
    - C: [Security Reviewer](./code-review-security-reviewer.toml) - `code-review-security-reviewer`
    - C: [Compatibility Reviewer](./code-review-compatibility-reviewer.toml) - `code-review-compatibility-reviewer`
    - C: [Deployment Risk Reviewer](./code-review-deployment-risk-reviewer.toml) - `code-review-deployment-risk-reviewer`
    - C: [Migration Risk Reviewer](./code-review-migration-risk-reviewer.toml) - `code-review-migration-risk-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
