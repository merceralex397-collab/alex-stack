# Desktop Development

This is a core development team from the source workflow.

Primary A-level artifact: a verified desktop delivery pack covering architecture, operating-system integration, local data, packaging, signing, updates, distribution, compatibility, and installation.

## Topology

- A: [Desktop Development Manager](./desktop-development-manager.toml) - `desktop-development-manager`
  - B: [Desktop Architecture Lead](./desktop-architecture-lead.toml) - `desktop-architecture-lead`
    - C: [Native Desktop Specialist](./desktop-native-desktop-specialist.toml) - `desktop-native-desktop-specialist`
    - C: [Electron or Webview Specialist](./desktop-electron-or-webview-specialist.toml) - `desktop-electron-or-webview-specialist`
    - C: [Local Data Specialist](./desktop-local-data-specialist.toml) - `desktop-local-data-specialist`
    - C: [Inter-Process Communication Specialist](./desktop-inter-process-communication-specialist.toml) - `desktop-inter-process-communication-specialist`
  - B: [Operating-System Integration Lead](./desktop-operating-system-integration-lead.toml) - `desktop-operating-system-integration-lead`
    - C: [File System Developer](./desktop-file-system-developer.toml) - `desktop-file-system-developer`
    - C: [System Tray and Notification Developer](./desktop-system-tray-and-notification-developer.toml) - `desktop-system-tray-and-notification-developer`
    - C: [Protocol and File Association Developer](./desktop-protocol-and-file-association-developer.toml) - `desktop-protocol-and-file-association-developer`
    - C: [Native Permission Specialist](./desktop-native-permission-specialist.toml) - `desktop-native-permission-specialist`
  - B: [Packaging Lead](./desktop-packaging-lead.toml) - `desktop-packaging-lead`
    - C: [Installer Developer](./desktop-installer-developer.toml) - `desktop-installer-developer`
    - C: [Auto-Update Developer](./desktop-auto-update-developer.toml) - `desktop-auto-update-developer`
    - C: [Code Signing Specialist](./desktop-code-signing-specialist.toml) - `desktop-code-signing-specialist`
    - C: [Distribution Specialist](./desktop-distribution-specialist.toml) - `desktop-distribution-specialist`
  - B: [Desktop Quality Lead](./desktop-quality-lead.toml) - `desktop-quality-lead`
    - C: [OS Compatibility Tester](./desktop-os-compatibility-tester.toml) - `desktop-os-compatibility-tester`
    - C: [Upgrade Tester](./desktop-upgrade-tester.toml) - `desktop-upgrade-tester`
    - C: [Resource Usage Tester](./desktop-resource-usage-tester.toml) - `desktop-resource-usage-tester`
    - C: [Installation Tester](./desktop-installation-tester.toml) - `desktop-installation-tester`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
