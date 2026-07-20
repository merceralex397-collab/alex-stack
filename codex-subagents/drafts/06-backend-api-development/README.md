# Backend and API Development

This is a core development team from the source workflow.

Primary A-level artifact: a verified backend delivery pack covering domain behavior, API contracts, persistence, asynchronous processing, error recovery, security, tests, and performance.

## Topology

- A: [Backend Manager](./backend-api-backend-manager.toml) - `backend-api-backend-manager`
  - B: [Domain Logic Lead](./backend-api-domain-logic-lead.toml) - `backend-api-domain-logic-lead`
    - C: [Domain Model Developer](./backend-api-domain-model-developer.toml) - `backend-api-domain-model-developer`
    - C: [Business Rules Developer](./backend-api-business-rules-developer.toml) - `backend-api-business-rules-developer`
    - C: [Workflow Developer](./backend-api-workflow-developer.toml) - `backend-api-workflow-developer`
    - C: [Validation Specialist](./backend-api-validation-specialist.toml) - `backend-api-validation-specialist`
  - B: [API Lead](./backend-api-api-lead.toml) - `backend-api-api-lead`
    - C: [REST API Developer](./backend-api-rest-api-developer.toml) - `backend-api-rest-api-developer`
    - C: [GraphQL or RPC Specialist](./backend-api-graphql-or-rpc-specialist.toml) - `backend-api-graphql-or-rpc-specialist`
    - C: [API Contract Specialist](./backend-api-api-contract-specialist.toml) - `backend-api-api-contract-specialist`
    - C: [API Versioning Specialist](./backend-api-api-versioning-specialist.toml) - `backend-api-api-versioning-specialist`
  - B: [Processing and Persistence Lead](./backend-api-processing-and-persistence-lead.toml) - `backend-api-processing-and-persistence-lead`
    - C: [Repository and ORM Developer](./backend-api-repository-and-orm-developer.toml) - `backend-api-repository-and-orm-developer`
    - C: [Background Job Developer](./backend-api-background-job-developer.toml) - `backend-api-background-job-developer`
    - C: [Queue and Event Developer](./backend-api-queue-and-event-developer.toml) - `backend-api-queue-and-event-developer`
    - C: [Cache Developer](./backend-api-cache-developer.toml) - `backend-api-cache-developer`
  - B: [Backend Quality Lead](./backend-api-backend-quality-lead.toml) - `backend-api-backend-quality-lead`
    - C: [Integration Test Developer](./backend-api-integration-test-developer.toml) - `backend-api-integration-test-developer`
    - C: [Error and Recovery Specialist](./backend-api-error-and-recovery-specialist.toml) - `backend-api-error-and-recovery-specialist`
    - C: [Security Reviewer](./backend-api-security-reviewer.toml) - `backend-api-security-reviewer`
    - C: [Backend Performance Specialist](./backend-api-backend-performance-specialist.toml) - `backend-api-backend-performance-specialist`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
