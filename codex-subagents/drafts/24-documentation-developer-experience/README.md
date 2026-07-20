# Documentation and Developer Experience

This is a core development team from the source workflow.

Primary A-level artifact: a documentation and developer-experience pack covering user and developer guidance, setup, APIs, architecture, contribution, tooling, diagnostics, accuracy, usability, and staleness.

## Topology

- A: [Documentation and DX Manager](./documentation-dx-documentation-and-dx-manager.toml) - `documentation-dx-documentation-and-dx-manager`
  - B: [User Documentation Lead](./documentation-dx-user-documentation-lead.toml) - `documentation-dx-user-documentation-lead`
    - C: [Tutorial Writer](./documentation-dx-tutorial-writer.toml) - `documentation-dx-tutorial-writer`
    - C: [How-To Guide Writer](./documentation-dx-how-to-guide-writer.toml) - `documentation-dx-how-to-guide-writer`
    - C: [Reference Documentation Writer](./documentation-dx-reference-documentation-writer.toml) - `documentation-dx-reference-documentation-writer`
    - C: [Troubleshooting Writer](./documentation-dx-troubleshooting-writer.toml) - `documentation-dx-troubleshooting-writer`
  - B: [Developer Documentation Lead](./documentation-dx-developer-documentation-lead.toml) - `documentation-dx-developer-documentation-lead`
    - C: [API Documentation Writer](./documentation-dx-api-documentation-writer.toml) - `documentation-dx-api-documentation-writer`
    - C: [Architecture Documentation Writer](./documentation-dx-architecture-documentation-writer.toml) - `documentation-dx-architecture-documentation-writer`
    - C: [Setup Guide Writer](./documentation-dx-setup-guide-writer.toml) - `documentation-dx-setup-guide-writer`
    - C: [Contribution Guide Writer](./documentation-dx-contribution-guide-writer.toml) - `documentation-dx-contribution-guide-writer`
  - B: [Developer Experience Lead](./documentation-dx-developer-experience-lead.toml) - `documentation-dx-developer-experience-lead`
    - C: [Local Environment Specialist](./documentation-dx-local-environment-specialist.toml) - `documentation-dx-local-environment-specialist`
    - C: [CLI and Tooling Developer](./documentation-dx-cli-and-tooling-developer.toml) - `documentation-dx-cli-and-tooling-developer`
    - C: [Project Template Developer](./documentation-dx-project-template-developer.toml) - `documentation-dx-project-template-developer`
    - C: [Error Message and Diagnostics Specialist](./documentation-dx-error-message-and-diagnostics-specialist.toml) - `documentation-dx-error-message-and-diagnostics-specialist`
  - B: [Documentation Review Lead](./documentation-dx-documentation-review-lead.toml) - `documentation-dx-documentation-review-lead`
    - C: [Technical Accuracy Reviewer](./documentation-dx-technical-accuracy-reviewer.toml) - `documentation-dx-technical-accuracy-reviewer`
    - C: [Completeness Reviewer](./documentation-dx-completeness-reviewer.toml) - `documentation-dx-completeness-reviewer`
    - C: [Usability Reviewer](./documentation-dx-usability-reviewer.toml) - `documentation-dx-usability-reviewer`
    - C: [Staleness Reviewer](./documentation-dx-staleness-reviewer.toml) - `documentation-dx-staleness-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
