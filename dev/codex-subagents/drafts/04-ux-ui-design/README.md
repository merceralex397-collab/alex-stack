# UX and UI Design

This is a core development team from the source workflow.

Primary A-level artifact: an implementation-ready design specification covering journeys, information architecture, flows, screen states, responsive behavior, accessibility, components, and interaction rules.

## Topology

- A: [UX/UI Manager](./ux-ui-manager.toml) - `ux-ui-manager`
  - B: [UX Research Lead](./ux-ui-ux-research-lead.toml) - `ux-ui-ux-research-lead`
    - C: [User Journey Analyst](./ux-ui-user-journey-analyst.toml) - `ux-ui-user-journey-analyst`
    - C: [Workflow Analyst](./ux-ui-workflow-analyst.toml) - `ux-ui-workflow-analyst`
    - C: [Usability Researcher](./ux-ui-usability-researcher.toml) - `ux-ui-usability-researcher`
    - C: [Accessibility Researcher](./ux-ui-accessibility-researcher.toml) - `ux-ui-accessibility-researcher`
  - B: [Interaction Design Lead](./ux-ui-interaction-design-lead.toml) - `ux-ui-interaction-design-lead`
    - C: [Information Architecture Designer](./ux-ui-information-architecture-designer.toml) - `ux-ui-information-architecture-designer`
    - C: [User Flow Designer](./ux-ui-user-flow-designer.toml) - `ux-ui-user-flow-designer`
    - C: [Wireframe Designer](./ux-ui-wireframe-designer.toml) - `ux-ui-wireframe-designer`
    - C: [Error and Empty-State Designer](./ux-ui-error-and-empty-state-designer.toml) - `ux-ui-error-and-empty-state-designer`
  - B: [Visual Design Lead](./ux-ui-visual-design-lead.toml) - `ux-ui-visual-design-lead`
    - C: [Design System Specialist](./ux-ui-design-system-specialist.toml) - `ux-ui-design-system-specialist`
    - C: [Responsive Design Specialist](./ux-ui-responsive-design-specialist.toml) - `ux-ui-responsive-design-specialist`
    - C: [Typography and Layout Specialist](./ux-ui-typography-and-layout-specialist.toml) - `ux-ui-typography-and-layout-specialist`
    - C: [Motion and Feedback Specialist](./ux-ui-motion-and-feedback-specialist.toml) - `ux-ui-motion-and-feedback-specialist`
  - B: [Design Review Lead](./ux-ui-design-review-lead.toml) - `ux-ui-design-review-lead`
    - C: [Accessibility Reviewer](./ux-ui-accessibility-reviewer.toml) - `ux-ui-accessibility-reviewer`
    - C: [Usability Reviewer](./ux-ui-usability-reviewer.toml) - `ux-ui-usability-reviewer`
    - C: [Consistency Reviewer](./ux-ui-consistency-reviewer.toml) - `ux-ui-consistency-reviewer`
    - C: [Implementation Feasibility Reviewer](./ux-ui-implementation-feasibility-reviewer.toml) - `ux-ui-implementation-feasibility-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
