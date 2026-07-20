# Security Engineering

This is a core development team from the source workflow.

Primary A-level artifact: a security pack covering assets, trust boundaries, threats, abuse cases, application and infrastructure controls, testing evidence, risk ranking, and remediation verification.

## Topology

- A: [Security Manager](./security-manager.toml) - `security-manager`
  - B: [Threat Modelling Lead](./security-threat-modelling-lead.toml) - `security-threat-modelling-lead`
    - C: [Asset and Trust Boundary Analyst](./security-asset-and-trust-boundary-analyst.toml) - `security-asset-and-trust-boundary-analyst`
    - C: [Attack Surface Analyst](./security-attack-surface-analyst.toml) - `security-attack-surface-analyst`
    - C: [Abuse Case Analyst](./security-abuse-case-analyst.toml) - `security-abuse-case-analyst`
    - C: [Threat Prioritisation Analyst](./security-threat-prioritisation-analyst.toml) - `security-threat-prioritisation-analyst`
  - B: [Application Security Lead](./security-application-security-lead.toml) - `security-application-security-lead`
    - C: [Authentication Reviewer](./security-authentication-reviewer.toml) - `security-authentication-reviewer`
    - C: [Authorisation Reviewer](./security-authorisation-reviewer.toml) - `security-authorisation-reviewer`
    - C: [Input Validation Reviewer](./security-input-validation-reviewer.toml) - `security-input-validation-reviewer`
    - C: [Dependency Security Reviewer](./security-dependency-security-reviewer.toml) - `security-dependency-security-reviewer`
  - B: [Infrastructure Security Lead](./security-infrastructure-security-lead.toml) - `security-infrastructure-security-lead`
    - C: [Cloud Permission Reviewer](./security-cloud-permission-reviewer.toml) - `security-cloud-permission-reviewer`
    - C: [Network Security Reviewer](./security-network-security-reviewer.toml) - `security-network-security-reviewer`
    - C: [Secrets Management Reviewer](./security-secrets-management-reviewer.toml) - `security-secrets-management-reviewer`
    - C: [Container Security Reviewer](./security-container-security-reviewer.toml) - `security-container-security-reviewer`
  - B: [Security Testing Lead](./security-testing-lead.toml) - `security-testing-lead`
    - C: [Static Analysis Specialist](./security-static-analysis-specialist.toml) - `security-static-analysis-specialist`
    - C: [Dynamic Analysis Specialist](./security-dynamic-analysis-specialist.toml) - `security-dynamic-analysis-specialist`
    - C: [Penetration Test Planner](./security-penetration-test-planner.toml) - `security-penetration-test-planner`
    - C: [Remediation Verifier](./security-remediation-verifier.toml) - `security-remediation-verifier`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
