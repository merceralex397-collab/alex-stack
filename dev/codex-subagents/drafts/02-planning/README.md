# Planning

This is a core development team from the source workflow.

Primary A-level artifact: an evidence-backed implementation plan covering current state, chosen approach, alternatives, affected components, phases, dependencies, tests, migration, rollout, rollback, and risks.

## Topology

- A: [Planning Manager](./planning-manager.toml) - `planning-manager`
  - B: [Discovery Lead](./planning-discovery-lead.toml) - `planning-discovery-lead`
    - C: [Repository Explorer](./planning-repository-explorer.toml) - `planning-repository-explorer`
    - C: [Requirements Analyst](./planning-requirements-analyst.toml) - `planning-requirements-analyst`
    - C: [Domain Specialist](./planning-domain-specialist.toml) - `planning-domain-specialist`
    - C: [Constraints Analyst](./planning-constraints-analyst.toml) - `planning-constraints-analyst`
  - B: [Ideation Lead](./planning-ideation-lead.toml) - `planning-ideation-lead`
    - C: [Practical Solution Designer](./planning-practical-solution-designer.toml) - `planning-practical-solution-designer`
    - C: [Alternative Solution Designer](./planning-alternative-solution-designer.toml) - `planning-alternative-solution-designer`
    - C: [Ambitious Solution Designer](./planning-ambitious-solution-designer.toml) - `planning-ambitious-solution-designer`
    - C: [Adversarial Brainstormer](./planning-adversarial-brainstormer.toml) - `planning-adversarial-brainstormer`
  - B: [Plan Author](./planning-plan-author.toml) - `planning-plan-author`
    - C: [Work Breakdown Specialist](./planning-work-breakdown-specialist.toml) - `planning-work-breakdown-specialist`
    - C: [Dependency and Sequencing Specialist](./planning-dependency-and-sequencing-specialist.toml) - `planning-dependency-and-sequencing-specialist`
    - C: [Testing Planner](./planning-testing-planner.toml) - `planning-testing-planner`
    - C: [Rollout Planner](./planning-rollout-planner.toml) - `planning-rollout-planner`
  - B: [Plan Reviewer](./planning-plan-reviewer.toml) - `planning-plan-reviewer`
    - C: [Feasibility Reviewer](./planning-feasibility-reviewer.toml) - `planning-feasibility-reviewer`
    - C: [Completeness Reviewer](./planning-completeness-reviewer.toml) - `planning-completeness-reviewer`
    - C: [Risk Reviewer](./planning-risk-reviewer.toml) - `planning-risk-reviewer`
    - C: [Evidence Reviewer](./planning-evidence-reviewer.toml) - `planning-evidence-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
