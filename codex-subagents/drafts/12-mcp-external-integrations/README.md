# MCP and External Integrations

This is a core development team from the source workflow.

Primary A-level artifact: an integration delivery pack covering capabilities, authentication, limits, connectors, events, idempotency, failure behavior, contracts, mocks, secrets, and permissions.

## Topology

- A: [Integration Manager](./integrations-integration-manager.toml) - `integrations-integration-manager`
  - B: [External System Discovery Lead](./integrations-external-system-discovery-lead.toml) - `integrations-external-system-discovery-lead`
    - C: [API Documentation Researcher](./integrations-api-documentation-researcher.toml) - `integrations-api-documentation-researcher`
    - C: [Authentication Researcher](./integrations-authentication-researcher.toml) - `integrations-authentication-researcher`
    - C: [Capability Mapper](./integrations-capability-mapper.toml) - `integrations-capability-mapper`
    - C: [Rate Limit and Constraint Analyst](./integrations-rate-limit-and-constraint-analyst.toml) - `integrations-rate-limit-and-constraint-analyst`
  - B: [Connector Development Lead](./integrations-connector-development-lead.toml) - `integrations-connector-development-lead`
    - C: [REST Connector Developer](./integrations-rest-connector-developer.toml) - `integrations-rest-connector-developer`
    - C: [GraphQL Connector Developer](./integrations-graphql-connector-developer.toml) - `integrations-graphql-connector-developer`
    - C: [SDK Integration Developer](./integrations-sdk-integration-developer.toml) - `integrations-sdk-integration-developer`
    - C: [MCP Server Developer](./integrations-mcp-server-developer.toml) - `integrations-mcp-server-developer`
  - B: [Event Integration Lead](./integrations-event-integration-lead.toml) - `integrations-event-integration-lead`
    - C: [Webhook Developer](./integrations-webhook-developer.toml) - `integrations-webhook-developer`
    - C: [Queue Integration Developer](./integrations-queue-integration-developer.toml) - `integrations-queue-integration-developer`
    - C: [Event Schema Specialist](./integrations-event-schema-specialist.toml) - `integrations-event-schema-specialist`
    - C: [Retry and Idempotency Specialist](./integrations-retry-and-idempotency-specialist.toml) - `integrations-retry-and-idempotency-specialist`
  - B: [Integration Quality Lead](./integrations-integration-quality-lead.toml) - `integrations-integration-quality-lead`
    - C: [Contract Test Developer](./integrations-contract-test-developer.toml) - `integrations-contract-test-developer`
    - C: [Mock Service Developer](./integrations-mock-service-developer.toml) - `integrations-mock-service-developer`
    - C: [Failure Simulation Specialist](./integrations-failure-simulation-specialist.toml) - `integrations-failure-simulation-specialist`
    - C: [Secrets and Permissions Reviewer](./integrations-secrets-and-permissions-reviewer.toml) - `integrations-secrets-and-permissions-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
