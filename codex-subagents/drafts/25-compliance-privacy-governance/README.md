# Compliance, Privacy and Governance

This is a core development team from the source workflow.

Primary A-level artifact: a compliance and privacy pack covering applicable obligations, data inventory and minimization, retention, consent, governance, auditability, controls, evidence, and remediation.

## Topology

- A: [Compliance and Privacy Manager](./compliance-privacy-compliance-and-privacy-manager.toml) - `compliance-privacy-compliance-and-privacy-manager`
  - B: [Regulatory Analysis Lead](./compliance-privacy-regulatory-analysis-lead.toml) - `compliance-privacy-regulatory-analysis-lead`
    - C: [Applicable Law Researcher](./compliance-privacy-applicable-law-researcher.toml) - `compliance-privacy-applicable-law-researcher`
    - C: [Industry Standards Researcher](./compliance-privacy-industry-standards-researcher.toml) - `compliance-privacy-industry-standards-researcher`
    - C: [Contractual Requirements Analyst](./compliance-privacy-contractual-requirements-analyst.toml) - `compliance-privacy-contractual-requirements-analyst`
    - C: [Evidence Requirements Analyst](./compliance-privacy-evidence-requirements-analyst.toml) - `compliance-privacy-evidence-requirements-analyst`
  - B: [Privacy Engineering Lead](./compliance-privacy-privacy-engineering-lead.toml) - `compliance-privacy-privacy-engineering-lead`
    - C: [Data Inventory Specialist](./compliance-privacy-data-inventory-specialist.toml) - `compliance-privacy-data-inventory-specialist`
    - C: [Data Minimisation Specialist](./compliance-privacy-data-minimisation-specialist.toml) - `compliance-privacy-data-minimisation-specialist`
    - C: [Retention Policy Specialist](./compliance-privacy-retention-policy-specialist.toml) - `compliance-privacy-retention-policy-specialist`
    - C: [Consent and User Rights Specialist](./compliance-privacy-consent-and-user-rights-specialist.toml) - `compliance-privacy-consent-and-user-rights-specialist`
  - B: [Governance Lead](./compliance-privacy-governance-lead.toml) - `compliance-privacy-governance-lead`
    - C: [Access Governance Specialist](./compliance-privacy-access-governance-specialist.toml) - `compliance-privacy-access-governance-specialist`
    - C: [Auditability Specialist](./compliance-privacy-auditability-specialist.toml) - `compliance-privacy-auditability-specialist`
    - C: [Change Control Specialist](./compliance-privacy-change-control-specialist.toml) - `compliance-privacy-change-control-specialist`
    - C: [Model Governance Specialist](./compliance-privacy-model-governance-specialist.toml) - `compliance-privacy-model-governance-specialist`
  - B: [Compliance Validation Lead](./compliance-privacy-compliance-validation-lead.toml) - `compliance-privacy-compliance-validation-lead`
    - C: [Control Tester](./compliance-privacy-control-tester.toml) - `compliance-privacy-control-tester`
    - C: [Evidence Reviewer](./compliance-privacy-evidence-reviewer.toml) - `compliance-privacy-evidence-reviewer`
    - C: [Policy-to-Implementation Reviewer](./compliance-privacy-policy-to-implementation-reviewer.toml) - `compliance-privacy-policy-to-implementation-reviewer`
    - C: [Remediation Planner](./compliance-privacy-remediation-planner.toml) - `compliance-privacy-remediation-planner`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
