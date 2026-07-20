# Mobile Development

This is a core development team from the source workflow.

Primary A-level artifact: a verified mobile delivery pack covering architecture, UI, device features, offline behavior, synchronization, compatibility, accessibility, performance, and store requirements.

## Topology

- A: [Mobile Development Manager](./mobile-development-manager.toml) - `mobile-development-manager`
  - B: [Mobile Architecture Lead](./mobile-architecture-lead.toml) - `mobile-architecture-lead`
    - C: [Native Platform Specialist](./mobile-native-platform-specialist.toml) - `mobile-native-platform-specialist`
    - C: [Cross-Platform Specialist](./mobile-cross-platform-specialist.toml) - `mobile-cross-platform-specialist`
    - C: [Offline Data Specialist](./mobile-offline-data-specialist.toml) - `mobile-offline-data-specialist`
    - C: [Mobile Navigation Specialist](./mobile-navigation-specialist.toml) - `mobile-navigation-specialist`
  - B: [Mobile Feature Lead](./mobile-feature-lead.toml) - `mobile-feature-lead`
    - C: [UI Developer](./mobile-ui-developer.toml) - `mobile-ui-developer`
    - C: [Device Capability Developer](./mobile-device-capability-developer.toml) - `mobile-device-capability-developer`
    - C: [Notifications Developer](./mobile-notifications-developer.toml) - `mobile-notifications-developer`
    - C: [Background Processing Developer](./mobile-background-processing-developer.toml) - `mobile-background-processing-developer`
  - B: [Mobile Integration Lead](./mobile-integration-lead.toml) - `mobile-integration-lead`
    - C: [API Integration Developer](./mobile-api-integration-developer.toml) - `mobile-api-integration-developer`
    - C: [Authentication Specialist](./mobile-authentication-specialist.toml) - `mobile-authentication-specialist`
    - C: [Local Storage Developer](./mobile-local-storage-developer.toml) - `mobile-local-storage-developer`
    - C: [Synchronisation Specialist](./mobile-synchronisation-specialist.toml) - `mobile-synchronisation-specialist`
  - B: [Mobile Quality Lead](./mobile-quality-lead.toml) - `mobile-quality-lead`
    - C: [Device Compatibility Tester](./mobile-device-compatibility-tester.toml) - `mobile-device-compatibility-tester`
    - C: [Battery and Performance Tester](./mobile-battery-and-performance-tester.toml) - `mobile-battery-and-performance-tester`
    - C: [Accessibility Tester](./mobile-accessibility-tester.toml) - `mobile-accessibility-tester`
    - C: [Store Compliance Reviewer](./mobile-store-compliance-reviewer.toml) - `mobile-store-compliance-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
