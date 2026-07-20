# Migration and Modernisation

This is a core development team from the source workflow.

Primary A-level artifact: a migration pack covering current and target states, contracts, transition architecture, code and data movement, parallel run, reconciliation, cutover, and rollback.

## Topology

- A: [Migration Manager](./migration-manager.toml) - `migration-manager`
  - B: [Current-State Assessment Lead](./migration-current-state-assessment-lead.toml) - `migration-current-state-assessment-lead`
    - C: [Legacy System Explorer](./migration-legacy-system-explorer.toml) - `migration-legacy-system-explorer`
    - C: [Dependency Mapper](./migration-dependency-mapper.toml) - `migration-dependency-mapper`
    - C: [Data Inventory Specialist](./migration-data-inventory-specialist.toml) - `migration-data-inventory-specialist`
    - C: [Behavioural Contract Analyst](./migration-behavioural-contract-analyst.toml) - `migration-behavioural-contract-analyst`
  - B: [Target-State Design Lead](./migration-target-state-design-lead.toml) - `migration-target-state-design-lead`
    - C: [Target Architecture Designer](./migration-target-architecture-designer.toml) - `migration-target-architecture-designer`
    - C: [Technology Selection Specialist](./migration-technology-selection-specialist.toml) - `migration-technology-selection-specialist`
    - C: [Compatibility Designer](./migration-compatibility-designer.toml) - `migration-compatibility-designer`
    - C: [Transition Architecture Specialist](./migration-transition-architecture-specialist.toml) - `migration-transition-architecture-specialist`
  - B: [Migration Execution Lead](./migration-execution-lead.toml) - `migration-execution-lead`
    - C: [Code Migration Developer](./migration-code-migration-developer.toml) - `migration-code-migration-developer`
    - C: [Data Migration Developer](./migration-data-migration-developer.toml) - `migration-data-migration-developer`
    - C: [Interface Migration Developer](./migration-interface-migration-developer.toml) - `migration-interface-migration-developer`
    - C: [Parallel-Run Specialist](./migration-parallel-run-specialist.toml) - `migration-parallel-run-specialist`
  - B: [Migration Validation Lead](./migration-validation-lead.toml) - `migration-validation-lead`
    - C: [Data Reconciliation Specialist](./migration-data-reconciliation-specialist.toml) - `migration-data-reconciliation-specialist`
    - C: [Behaviour Comparison Specialist](./migration-behaviour-comparison-specialist.toml) - `migration-behaviour-comparison-specialist`
    - C: [Cutover Tester](./migration-cutover-tester.toml) - `migration-cutover-tester`
    - C: [Rollback Reviewer](./migration-rollback-reviewer.toml) - `migration-rollback-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
