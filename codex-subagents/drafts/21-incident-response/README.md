# Incident Response

This is a core development team from the source workflow.

Primary A-level artifact: an incident pack covering impact, timeline, evidence, mitigation, recovery, root cause, corrective actions, monitoring improvements, and regression prevention.

## Topology

- A: [Incident Manager](./incident-response-incident-manager.toml) - `incident-response-incident-manager`
  - B: [Triage Lead](./incident-response-triage-lead.toml) - `incident-response-triage-lead`
    - C: [Impact Analyst](./incident-response-impact-analyst.toml) - `incident-response-impact-analyst`
    - C: [Timeline Analyst](./incident-response-timeline-analyst.toml) - `incident-response-timeline-analyst`
    - C: [Log and Trace Investigator](./incident-response-log-and-trace-investigator.toml) - `incident-response-log-and-trace-investigator`
    - C: [Reproduction Specialist](./incident-response-reproduction-specialist.toml) - `incident-response-reproduction-specialist`
  - B: [Mitigation Lead](./incident-response-mitigation-lead.toml) - `incident-response-mitigation-lead`
    - C: [Rollback Specialist](./incident-response-rollback-specialist.toml) - `incident-response-rollback-specialist`
    - C: [Configuration Mitigation Specialist](./incident-response-configuration-mitigation-specialist.toml) - `incident-response-configuration-mitigation-specialist`
    - C: [Traffic Management Specialist](./incident-response-traffic-management-specialist.toml) - `incident-response-traffic-management-specialist`
    - C: [Data Recovery Specialist](./incident-response-data-recovery-specialist.toml) - `incident-response-data-recovery-specialist`
  - B: [Root Cause Lead](./incident-response-root-cause-lead.toml) - `incident-response-root-cause-lead`
    - C: [Code Investigator](./incident-response-code-investigator.toml) - `incident-response-code-investigator`
    - C: [Infrastructure Investigator](./incident-response-infrastructure-investigator.toml) - `incident-response-infrastructure-investigator`
    - C: [Dependency Investigator](./incident-response-dependency-investigator.toml) - `incident-response-dependency-investigator`
    - C: [Process Failure Investigator](./incident-response-process-failure-investigator.toml) - `incident-response-process-failure-investigator`
  - B: [Post-Incident Lead](./incident-response-post-incident-lead.toml) - `incident-response-post-incident-lead`
    - C: [Postmortem Writer](./incident-response-postmortem-writer.toml) - `incident-response-postmortem-writer`
    - C: [Corrective Action Planner](./incident-response-corrective-action-planner.toml) - `incident-response-corrective-action-planner`
    - C: [Monitoring Improvement Specialist](./incident-response-monitoring-improvement-specialist.toml) - `incident-response-monitoring-improvement-specialist`
    - C: [Regression Prevention Reviewer](./incident-response-regression-prevention-reviewer.toml) - `incident-response-regression-prevention-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
