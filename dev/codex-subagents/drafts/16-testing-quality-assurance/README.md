# Testing and Quality Assurance

This is a core development team from the source workflow.

Primary A-level artifact: a quality pack covering risk-based strategy, environments, automated and non-functional coverage, regressions, flakiness, gaps, and release readiness.

## Topology

- A: [QA Manager](./qa-manager.toml) - `qa-manager`
  - B: [Test Strategy Lead](./qa-test-strategy-lead.toml) - `qa-test-strategy-lead`
    - C: [Risk-Based Test Analyst](./qa-risk-based-test-analyst.toml) - `qa-risk-based-test-analyst`
    - C: [Test Coverage Analyst](./qa-test-coverage-analyst.toml) - `qa-test-coverage-analyst`
    - C: [Acceptance Test Designer](./qa-acceptance-test-designer.toml) - `qa-acceptance-test-designer`
    - C: [Test Environment Planner](./qa-test-environment-planner.toml) - `qa-test-environment-planner`
  - B: [Automated Testing Lead](./qa-automated-testing-lead.toml) - `qa-automated-testing-lead`
    - C: [Unit Test Developer](./qa-unit-test-developer.toml) - `qa-unit-test-developer`
    - C: [Integration Test Developer](./qa-integration-test-developer.toml) - `qa-integration-test-developer`
    - C: [End-to-End Test Developer](./qa-end-to-end-test-developer.toml) - `qa-end-to-end-test-developer`
    - C: [Contract Test Developer](./qa-contract-test-developer.toml) - `qa-contract-test-developer`
  - B: [Non-Functional Testing Lead](./qa-non-functional-testing-lead.toml) - `qa-non-functional-testing-lead`
    - C: [Performance Tester](./qa-performance-tester.toml) - `qa-performance-tester`
    - C: [Security Tester](./qa-security-tester.toml) - `qa-security-tester`
    - C: [Accessibility Tester](./qa-accessibility-tester.toml) - `qa-accessibility-tester`
    - C: [Resilience Tester](./qa-resilience-tester.toml) - `qa-resilience-tester`
  - B: [Quality Review Lead](./qa-quality-review-lead.toml) - `qa-quality-review-lead`
    - C: [Regression Analyst](./qa-regression-analyst.toml) - `qa-regression-analyst`
    - C: [Test Flakiness Analyst](./qa-test-flakiness-analyst.toml) - `qa-test-flakiness-analyst`
    - C: [Coverage Gap Analyst](./qa-coverage-gap-analyst.toml) - `qa-coverage-gap-analyst`
    - C: [Release Readiness Reviewer](./qa-release-readiness-reviewer.toml) - `qa-release-readiness-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
