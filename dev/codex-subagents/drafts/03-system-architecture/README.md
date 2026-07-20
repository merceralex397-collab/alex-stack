# System Architecture

This is a core development team from the source workflow.

Primary A-level artifact: an architecture pack containing system context, component boundaries, data flows, interfaces, quality attributes, failure and recovery behavior, and architecture decision records.

## Topology

- A: [Architecture Manager](./architecture-manager.toml) - `architecture-manager`
  - B: [Current-System Analysis Lead](./architecture-current-system-analysis-lead.toml) - `architecture-current-system-analysis-lead`
    - C: [Codebase Architect](./architecture-codebase-architect.toml) - `architecture-codebase-architect`
    - C: [Dependency Mapper](./architecture-dependency-mapper.toml) - `architecture-dependency-mapper`
    - C: [Data Flow Analyst](./architecture-data-flow-analyst.toml) - `architecture-data-flow-analyst`
    - C: [Integration Mapper](./architecture-integration-mapper.toml) - `architecture-integration-mapper`
  - B: [Solution Architecture Lead](./architecture-solution-architecture-lead.toml) - `architecture-solution-architecture-lead`
    - C: [Application Architect](./architecture-application-architect.toml) - `architecture-application-architect`
    - C: [Data Architect](./architecture-data-architect.toml) - `architecture-data-architect`
    - C: [Cloud Architect](./architecture-cloud-architect.toml) - `architecture-cloud-architect`
    - C: [Integration Architect](./architecture-integration-architect.toml) - `architecture-integration-architect`
  - B: [Quality Attributes Lead](./architecture-quality-attributes-lead.toml) - `architecture-quality-attributes-lead`
    - C: [Scalability Specialist](./architecture-scalability-specialist.toml) - `architecture-scalability-specialist`
    - C: [Reliability Specialist](./architecture-reliability-specialist.toml) - `architecture-reliability-specialist`
    - C: [Security Architect](./architecture-security-architect.toml) - `architecture-security-architect`
    - C: [Maintainability Specialist](./architecture-maintainability-specialist.toml) - `architecture-maintainability-specialist`
  - B: [Architecture Review Lead](./architecture-review-lead.toml) - `architecture-review-lead`
    - C: [Feasibility Reviewer](./architecture-feasibility-reviewer.toml) - `architecture-feasibility-reviewer`
    - C: [Complexity Reviewer](./architecture-complexity-reviewer.toml) - `architecture-complexity-reviewer`
    - C: [Vendor Lock-In Reviewer](./architecture-vendor-lock-in-reviewer.toml) - `architecture-vendor-lock-in-reviewer`
    - C: [Architecture Decision Record Writer](./architecture-decision-record-writer.toml) - `architecture-decision-record-writer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
