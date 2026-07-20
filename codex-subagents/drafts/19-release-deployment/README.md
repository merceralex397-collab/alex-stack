# Release and Deployment

This is a core development team from the source workflow.

Primary A-level artifact: a release pack covering versioning, artifacts, notes, migrations, configuration, rollout, validation, rollback, evidence, and go or no-go criteria.

## Topology

- A: [Release Manager](./release-manager.toml) - `release-manager`
  - B: [Release Preparation Lead](./release-preparation-lead.toml) - `release-preparation-lead`
    - C: [Versioning Specialist](./release-versioning-specialist.toml) - `release-versioning-specialist`
    - C: [Changelog Developer](./release-changelog-developer.toml) - `release-changelog-developer`
    - C: [Dependency and Artifact Verifier](./release-dependency-and-artifact-verifier.toml) - `release-dependency-and-artifact-verifier`
    - C: [Release Notes Writer](./release-notes-writer.toml) - `release-notes-writer`
  - B: [Deployment Lead](./release-deployment-lead.toml) - `release-deployment-lead`
    - C: [Deployment Pipeline Developer](./release-deployment-pipeline-developer.toml) - `release-deployment-pipeline-developer`
    - C: [Database Migration Coordinator](./release-database-migration-coordinator.toml) - `release-database-migration-coordinator`
    - C: [Configuration Coordinator](./release-configuration-coordinator.toml) - `release-configuration-coordinator`
    - C: [Environment Validation Specialist](./release-environment-validation-specialist.toml) - `release-environment-validation-specialist`
  - B: [Rollout Lead](./release-rollout-lead.toml) - `release-rollout-lead`
    - C: [Feature Flag Specialist](./release-feature-flag-specialist.toml) - `release-feature-flag-specialist`
    - C: [Canary Release Specialist](./release-canary-release-specialist.toml) - `release-canary-release-specialist`
    - C: [Blue-Green Deployment Specialist](./release-blue-green-deployment-specialist.toml) - `release-blue-green-deployment-specialist`
    - C: [User Migration Specialist](./release-user-migration-specialist.toml) - `release-user-migration-specialist`
  - B: [Release Validation Lead](./release-validation-lead.toml) - `release-validation-lead`
    - C: [Smoke Test Developer](./release-smoke-test-developer.toml) - `release-smoke-test-developer`
    - C: [Post-Deployment Validator](./release-post-deployment-validator.toml) - `release-post-deployment-validator`
    - C: [Rollback Tester](./release-rollback-tester.toml) - `release-rollback-tester`
    - C: [Release Readiness Reviewer](./release-readiness-reviewer.toml) - `release-readiness-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
