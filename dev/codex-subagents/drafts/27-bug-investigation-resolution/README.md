# Bug Investigation and Resolution

This is a core development team from the source workflow.

Primary A-level artifact: a bug-resolution pack covering severity, reproduction, impact, regression range, root cause, fix choice, repair needs, verification, side effects, and release risk.

## Topology

- A: [Bug Resolution Manager](./bug-resolution-manager.toml) - `bug-resolution-manager`
  - B: [Triage Lead](./bug-resolution-triage-lead.toml) - `bug-resolution-triage-lead`
    - C: [Severity Analyst](./bug-resolution-severity-analyst.toml) - `bug-resolution-severity-analyst`
    - C: [Reproduction Specialist](./bug-resolution-reproduction-specialist.toml) - `bug-resolution-reproduction-specialist`
    - C: [Regression Range Analyst](./bug-resolution-regression-range-analyst.toml) - `bug-resolution-regression-range-analyst`
    - C: [User Impact Analyst](./bug-resolution-user-impact-analyst.toml) - `bug-resolution-user-impact-analyst`
  - B: [Investigation Lead](./bug-resolution-investigation-lead.toml) - `bug-resolution-investigation-lead`
    - C: [Code Path Investigator](./bug-resolution-code-path-investigator.toml) - `bug-resolution-code-path-investigator`
    - C: [Data Investigator](./bug-resolution-data-investigator.toml) - `bug-resolution-data-investigator`
    - C: [Environment Investigator](./bug-resolution-environment-investigator.toml) - `bug-resolution-environment-investigator`
    - C: [Dependency Investigator](./bug-resolution-dependency-investigator.toml) - `bug-resolution-dependency-investigator`
  - B: [Fix Lead](./bug-resolution-fix-lead.toml) - `bug-resolution-fix-lead`
    - C: [Minimal Fix Developer](./bug-resolution-minimal-fix-developer.toml) - `bug-resolution-minimal-fix-developer`
    - C: [Root-Cause Fix Developer](./bug-resolution-root-cause-fix-developer.toml) - `bug-resolution-root-cause-fix-developer`
    - C: [Defensive Handling Developer](./bug-resolution-defensive-handling-developer.toml) - `bug-resolution-defensive-handling-developer`
    - C: [Migration or Repair Developer](./bug-resolution-migration-or-repair-developer.toml) - `bug-resolution-migration-or-repair-developer`
  - B: [Verification Lead](./bug-resolution-verification-lead.toml) - `bug-resolution-verification-lead`
    - C: [Reproduction Test Developer](./bug-resolution-reproduction-test-developer.toml) - `bug-resolution-reproduction-test-developer`
    - C: [Regression Test Developer](./bug-resolution-regression-test-developer.toml) - `bug-resolution-regression-test-developer`
    - C: [Side-Effect Reviewer](./bug-resolution-side-effect-reviewer.toml) - `bug-resolution-side-effect-reviewer`
    - C: [Release Risk Reviewer](./bug-resolution-release-risk-reviewer.toml) - `bug-resolution-release-risk-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
