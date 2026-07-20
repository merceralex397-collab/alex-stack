# Frontend Development

This is a core development team from the source workflow.

Primary A-level artifact: a verified frontend delivery pack covering components, behavior, integration, accessibility, compatibility, performance, tests, and remaining risks.

## Topology

- A: [Frontend Manager](./frontend-manager.toml) - `frontend-manager`
  - B: [UI Implementation Lead](./frontend-ui-implementation-lead.toml) - `frontend-ui-implementation-lead`
    - C: [Component Developer](./frontend-component-developer.toml) - `frontend-component-developer`
    - C: [Layout and Responsive Developer](./frontend-layout-and-responsive-developer.toml) - `frontend-layout-and-responsive-developer`
    - C: [Forms and Validation Developer](./frontend-forms-and-validation-developer.toml) - `frontend-forms-and-validation-developer`
    - C: [Design System Developer](./frontend-design-system-developer.toml) - `frontend-design-system-developer`
  - B: [Application Behaviour Lead](./frontend-application-behaviour-lead.toml) - `frontend-application-behaviour-lead`
    - C: [State Management Specialist](./frontend-state-management-specialist.toml) - `frontend-state-management-specialist`
    - C: [Routing Specialist](./frontend-routing-specialist.toml) - `frontend-routing-specialist`
    - C: [Client-Side Data Specialist](./frontend-client-side-data-specialist.toml) - `frontend-client-side-data-specialist`
    - C: [Error Handling Specialist](./frontend-error-handling-specialist.toml) - `frontend-error-handling-specialist`
  - B: [Platform Integration Lead](./frontend-platform-integration-lead.toml) - `frontend-platform-integration-lead`
    - C: [API Integration Developer](./frontend-api-integration-developer.toml) - `frontend-api-integration-developer`
    - C: [Authentication Developer](./frontend-authentication-developer.toml) - `frontend-authentication-developer`
    - C: [Caching Specialist](./frontend-caching-specialist.toml) - `frontend-caching-specialist`
    - C: [Real-Time Communication Developer](./frontend-real-time-communication-developer.toml) - `frontend-real-time-communication-developer`
  - B: [Frontend Quality Lead](./frontend-quality-lead.toml) - `frontend-quality-lead`
    - C: [Accessibility Tester](./frontend-accessibility-tester.toml) - `frontend-accessibility-tester`
    - C: [Browser Compatibility Tester](./frontend-browser-compatibility-tester.toml) - `frontend-browser-compatibility-tester`
    - C: [Frontend Performance Specialist](./frontend-performance-specialist.toml) - `frontend-performance-specialist`
    - C: [Component Test Developer](./frontend-component-test-developer.toml) - `frontend-component-test-developer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
