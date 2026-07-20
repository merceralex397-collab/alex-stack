# Product and Requirements

This is a core development team from the source workflow.

Primary A-level artifact: a decision-ready product brief with users, outcomes, functional and non-functional requirements, acceptance criteria, exclusions, constraints, assumptions, and unresolved questions.

## Topology

- A: [Product and Requirements Manager](./product-requirements-product-and-requirements-manager.toml) - `product-requirements-product-and-requirements-manager`
  - B: [Problem Discovery Lead](./product-requirements-problem-discovery-lead.toml) - `product-requirements-problem-discovery-lead`
    - C: [User Needs Analyst](./product-requirements-user-needs-analyst.toml) - `product-requirements-user-needs-analyst`
    - C: [Business Process Analyst](./product-requirements-business-process-analyst.toml) - `product-requirements-business-process-analyst`
    - C: [Stakeholder Analyst](./product-requirements-stakeholder-analyst.toml) - `product-requirements-stakeholder-analyst`
    - C: [Domain Researcher](./product-requirements-domain-researcher.toml) - `product-requirements-domain-researcher`
  - B: [Requirements Lead](./product-requirements-requirements-lead.toml) - `product-requirements-requirements-lead`
    - C: [Functional Requirements Analyst](./product-requirements-functional-requirements-analyst.toml) - `product-requirements-functional-requirements-analyst`
    - C: [Non-Functional Requirements Analyst](./product-requirements-non-functional-requirements-analyst.toml) - `product-requirements-non-functional-requirements-analyst`
    - C: [Acceptance Criteria Writer](./product-requirements-acceptance-criteria-writer.toml) - `product-requirements-acceptance-criteria-writer`
    - C: [Edge Case Analyst](./product-requirements-edge-case-analyst.toml) - `product-requirements-edge-case-analyst`
  - B: [Scope and Priority Lead](./product-requirements-scope-and-priority-lead.toml) - `product-requirements-scope-and-priority-lead`
    - C: [Dependency Analyst](./product-requirements-dependency-analyst.toml) - `product-requirements-dependency-analyst`
    - C: [Value and Impact Analyst](./product-requirements-value-and-impact-analyst.toml) - `product-requirements-value-and-impact-analyst`
    - C: [Effort Analyst](./product-requirements-effort-analyst.toml) - `product-requirements-effort-analyst`
    - C: [Scope Boundary Reviewer](./product-requirements-scope-boundary-reviewer.toml) - `product-requirements-scope-boundary-reviewer`
  - B: [Requirements Reviewer](./product-requirements-requirements-reviewer.toml) - `product-requirements-requirements-reviewer`
    - C: [Completeness Reviewer](./product-requirements-completeness-reviewer.toml) - `product-requirements-completeness-reviewer`
    - C: [Ambiguity Reviewer](./product-requirements-ambiguity-reviewer.toml) - `product-requirements-ambiguity-reviewer`
    - C: [Contradiction Reviewer](./product-requirements-contradiction-reviewer.toml) - `product-requirements-contradiction-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
