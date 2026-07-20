# Game Development

This is an optional specialist development team from the source workflow.

Primary A-level artifact: a game delivery pack covering mechanics, behavior, progression, rendering, assets, content systems, gameplay quality, performance, and platform compatibility.

## Topology

- A: [Game Development Manager](./game-development-manager.toml) - `game-development-manager`
  - B: [Gameplay Lead](./game-development-gameplay-lead.toml) - `game-development-gameplay-lead`
    - C: [Mechanics Developer](./game-development-mechanics-developer.toml) - `game-development-mechanics-developer`
    - C: [AI Behaviour Developer](./game-development-ai-behaviour-developer.toml) - `game-development-ai-behaviour-developer`
    - C: [Progression Systems Developer](./game-development-progression-systems-developer.toml) - `game-development-progression-systems-developer`
  - B: [Rendering and Visuals Lead](./game-development-rendering-and-visuals-lead.toml) - `game-development-rendering-and-visuals-lead`
    - C: [Graphics Developer](./game-development-graphics-developer.toml) - `game-development-graphics-developer`
    - C: [Shader Developer](./game-development-shader-developer.toml) - `game-development-shader-developer`
    - C: [Technical Artist](./game-development-technical-artist.toml) - `game-development-technical-artist`
  - B: [Content Systems Lead](./game-development-content-systems-lead.toml) - `game-development-content-systems-lead`
    - C: [Level Systems Developer](./game-development-level-systems-developer.toml) - `game-development-level-systems-developer`
    - C: [Asset Pipeline Developer](./game-development-asset-pipeline-developer.toml) - `game-development-asset-pipeline-developer`
    - C: [Dialogue and Narrative Developer](./game-development-dialogue-and-narrative-developer.toml) - `game-development-dialogue-and-narrative-developer`
  - B: [Game Quality Lead](./game-development-game-quality-lead.toml) - `game-development-game-quality-lead`
    - C: [Gameplay Tester](./game-development-gameplay-tester.toml) - `game-development-gameplay-tester`
    - C: [Performance Tester](./game-development-performance-tester.toml) - `game-development-performance-tester`
    - C: [Platform Compatibility Tester](./game-development-platform-compatibility-tester.toml) - `game-development-platform-compatibility-tester`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
