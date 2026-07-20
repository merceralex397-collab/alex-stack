# Maintenance and Refactoring

This is a core development team from the source workflow.

Primary A-level artifact: a maintenance pack covering debt evidence, refactoring boundaries, behavior preservation, compatibility, deprecation, regression tests, performance comparison, and maintainability.

## Topology

- A: [Maintenance Manager](./maintenance-manager.toml) - `maintenance-manager`
  - B: [Technical Debt Assessment Lead](./maintenance-technical-debt-assessment-lead.toml) - `maintenance-technical-debt-assessment-lead`
    - C: [Code Smell Analyst](./maintenance-code-smell-analyst.toml) - `maintenance-code-smell-analyst`
    - C: [Dependency Health Analyst](./maintenance-dependency-health-analyst.toml) - `maintenance-dependency-health-analyst`
    - C: [Complexity Analyst](./maintenance-complexity-analyst.toml) - `maintenance-complexity-analyst`
    - C: [Duplication Analyst](./maintenance-duplication-analyst.toml) - `maintenance-duplication-analyst`
  - B: [Refactoring Lead](./maintenance-refactoring-lead.toml) - `maintenance-refactoring-lead`
    - C: [Module Boundary Specialist](./maintenance-module-boundary-specialist.toml) - `maintenance-module-boundary-specialist`
    - C: [API Refactoring Specialist](./maintenance-api-refactoring-specialist.toml) - `maintenance-api-refactoring-specialist`
    - C: [Data Model Refactoring Specialist](./maintenance-data-model-refactoring-specialist.toml) - `maintenance-data-model-refactoring-specialist`
    - C: [Legacy Code Specialist](./maintenance-legacy-code-specialist.toml) - `maintenance-legacy-code-specialist`
  - B: [Compatibility Lead](./maintenance-compatibility-lead.toml) - `maintenance-compatibility-lead`
    - C: [Behaviour Preservation Analyst](./maintenance-behaviour-preservation-analyst.toml) - `maintenance-behaviour-preservation-analyst`
    - C: [Backward Compatibility Specialist](./maintenance-backward-compatibility-specialist.toml) - `maintenance-backward-compatibility-specialist`
    - C: [Migration Compatibility Specialist](./maintenance-migration-compatibility-specialist.toml) - `maintenance-migration-compatibility-specialist`
    - C: [Deprecation Specialist](./maintenance-deprecation-specialist.toml) - `maintenance-deprecation-specialist`
  - B: [Refactoring Validation Lead](./maintenance-refactoring-validation-lead.toml) - `maintenance-refactoring-validation-lead`
    - C: [Regression Test Developer](./maintenance-regression-test-developer.toml) - `maintenance-regression-test-developer`
    - C: [Performance Comparison Specialist](./maintenance-performance-comparison-specialist.toml) - `maintenance-performance-comparison-specialist`
    - C: [Public Contract Reviewer](./maintenance-public-contract-reviewer.toml) - `maintenance-public-contract-reviewer`
    - C: [Maintainability Reviewer](./maintenance-maintainability-reviewer.toml) - `maintenance-maintainability-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
