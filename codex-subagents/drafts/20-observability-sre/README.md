# Observability and SRE

This is a core development team from the source workflow.

Primary A-level artifact: an operational-readiness pack covering telemetry, service objectives, resilience, capacity, alerts, dashboards, runbooks, recovery tests, and operational risks.

## Topology

- A: [Observability and SRE Manager](./observability-sre-observability-and-sre-manager.toml) - `observability-sre-observability-and-sre-manager`
  - B: [Telemetry Lead](./observability-sre-telemetry-lead.toml) - `observability-sre-telemetry-lead`
    - C: [Logging Specialist](./observability-sre-logging-specialist.toml) - `observability-sre-logging-specialist`
    - C: [Metrics Specialist](./observability-sre-metrics-specialist.toml) - `observability-sre-metrics-specialist`
    - C: [Distributed Tracing Specialist](./observability-sre-distributed-tracing-specialist.toml) - `observability-sre-distributed-tracing-specialist`
    - C: [Audit Trail Specialist](./observability-sre-audit-trail-specialist.toml) - `observability-sre-audit-trail-specialist`
  - B: [Service Reliability Lead](./observability-sre-service-reliability-lead.toml) - `observability-sre-service-reliability-lead`
    - C: [Service-Level Objective Designer](./observability-sre-service-level-objective-designer.toml) - `observability-sre-service-level-objective-designer`
    - C: [Availability Specialist](./observability-sre-availability-specialist.toml) - `observability-sre-availability-specialist`
    - C: [Resilience Engineer](./observability-sre-resilience-engineer.toml) - `observability-sre-resilience-engineer`
    - C: [Capacity Specialist](./observability-sre-capacity-specialist.toml) - `observability-sre-capacity-specialist`
  - B: [Alerting Lead](./observability-sre-alerting-lead.toml) - `observability-sre-alerting-lead`
    - C: [Alert Rule Designer](./observability-sre-alert-rule-designer.toml) - `observability-sre-alert-rule-designer`
    - C: [Noise Reduction Specialist](./observability-sre-noise-reduction-specialist.toml) - `observability-sre-noise-reduction-specialist`
    - C: [Escalation Policy Designer](./observability-sre-escalation-policy-designer.toml) - `observability-sre-escalation-policy-designer`
    - C: [Dashboard Developer](./observability-sre-dashboard-developer.toml) - `observability-sre-dashboard-developer`
  - B: [Operational Readiness Lead](./observability-sre-operational-readiness-lead.toml) - `observability-sre-operational-readiness-lead`
    - C: [Runbook Writer](./observability-sre-runbook-writer.toml) - `observability-sre-runbook-writer`
    - C: [Failure Scenario Tester](./observability-sre-failure-scenario-tester.toml) - `observability-sre-failure-scenario-tester`
    - C: [Recovery Procedure Tester](./observability-sre-recovery-procedure-tester.toml) - `observability-sre-recovery-procedure-tester`
    - C: [Operational Risk Reviewer](./observability-sre-operational-risk-reviewer.toml) - `observability-sre-operational-risk-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
