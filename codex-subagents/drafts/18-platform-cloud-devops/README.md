# Platform, Cloud and DevOps

This is a core development team from the source workflow.

Primary A-level artifact: a platform delivery pack covering infrastructure, identity, networking, build and test pipelines, artifacts, runtime configuration, recovery, consistency, and security.

## Topology

- A: [Platform and DevOps Manager](./platform-devops-platform-and-devops-manager.toml) - `platform-devops-platform-and-devops-manager`
  - B: [Infrastructure Lead](./platform-devops-infrastructure-lead.toml) - `platform-devops-infrastructure-lead`
    - C: [Cloud Resource Developer](./platform-devops-cloud-resource-developer.toml) - `platform-devops-cloud-resource-developer`
    - C: [Infrastructure-as-Code Developer](./platform-devops-infrastructure-as-code-developer.toml) - `platform-devops-infrastructure-as-code-developer`
    - C: [Network Infrastructure Specialist](./platform-devops-network-infrastructure-specialist.toml) - `platform-devops-network-infrastructure-specialist`
    - C: [Identity and Access Specialist](./platform-devops-identity-and-access-specialist.toml) - `platform-devops-identity-and-access-specialist`
  - B: [Build and CI Lead](./platform-devops-build-and-ci-lead.toml) - `platform-devops-build-and-ci-lead`
    - C: [Build Pipeline Developer](./platform-devops-build-pipeline-developer.toml) - `platform-devops-build-pipeline-developer`
    - C: [Test Pipeline Developer](./platform-devops-test-pipeline-developer.toml) - `platform-devops-test-pipeline-developer`
    - C: [Artifact Management Specialist](./platform-devops-artifact-management-specialist.toml) - `platform-devops-artifact-management-specialist`
    - C: [Dependency Cache Specialist](./platform-devops-dependency-cache-specialist.toml) - `platform-devops-dependency-cache-specialist`
  - B: [Runtime Platform Lead](./platform-devops-runtime-platform-lead.toml) - `platform-devops-runtime-platform-lead`
    - C: [Container Specialist](./platform-devops-container-specialist.toml) - `platform-devops-container-specialist`
    - C: [Kubernetes or Orchestration Specialist](./platform-devops-kubernetes-or-orchestration-specialist.toml) - `platform-devops-kubernetes-or-orchestration-specialist`
    - C: [Serverless Specialist](./platform-devops-serverless-specialist.toml) - `platform-devops-serverless-specialist`
    - C: [Configuration Management Specialist](./platform-devops-configuration-management-specialist.toml) - `platform-devops-configuration-management-specialist`
  - B: [Platform Reliability Lead](./platform-devops-platform-reliability-lead.toml) - `platform-devops-platform-reliability-lead`
    - C: [Backup Specialist](./platform-devops-backup-specialist.toml) - `platform-devops-backup-specialist`
    - C: [Disaster Recovery Specialist](./platform-devops-disaster-recovery-specialist.toml) - `platform-devops-disaster-recovery-specialist`
    - C: [Environment Consistency Reviewer](./platform-devops-environment-consistency-reviewer.toml) - `platform-devops-environment-consistency-reviewer`
    - C: [Platform Security Reviewer](./platform-devops-platform-security-reviewer.toml) - `platform-devops-platform-security-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
