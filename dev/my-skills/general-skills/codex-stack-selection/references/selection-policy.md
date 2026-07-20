# Stack Selection Policy

## Evidence order

Use evidence in this order:

1. Explicit project instructions and required workflows.
2. Successful or failed project-scoped use during the selected window.
3. Repository manifests, source, infrastructure, CI, and documentation.
4. Capability metadata and ownership.
5. Name-based inference, clearly labelled as weak.

Do not let a single weak signal override stronger contrary evidence.

## Recommendation rules

### Keep

Keep a capability when any of these apply:

- It was actually invoked for the project within the observation window.
- Project instructions require it.
- Repository evidence establishes an active dependency or workflow.
- It is the selected owner for a capability needed by the project.

Recent use is evidence of need even when the call failed. Put the failure in **Needs attention** as an additional status.

### Disable

Recommend disabling only when all apply:

- No actual project-scoped use appears within the window.
- No explicit instruction requires it.
- No strong repository evidence supports it.
- Disabling it does not disable a needed bundled component.
- A project-local control can represent the change.

Do not recommend disabling solely because logs are unavailable or incomplete.

### Needs attention

Use this category when:

- Recent calls failed or authentication/setup is incomplete.
- A plugin owns both needed and unneeded components.
- App or MCP ownership cannot be resolved.
- Session logs are absent, malformed, truncated, or outside the current schema.
- Matching sessions contain no attributable capability events; absence remains inconclusive.
- Current state is available only from fallback config/cache inspection.
- A desired change is global-only or would require a machine-specific path.

## Redundancy

When capabilities overlap, keep the one demonstrated by project use or explicit project instructions. If evidence is equal, prefer:

1. A project-specific integration over a generic UI automation tool.
2. A read-only or narrowly scoped capability over a broad write-capable one.
3. One owning plugin switch over multiple child overrides.
4. A current, working capability over a recently failing duplicate.

Do not disable a broader fallback merely because a preferred integration exists when project history shows both are used for distinct workflows.

## Configuration precedence

- Project config is loaded only for trusted projects.
- A project `.codex/config.toml` can control skills, MCP servers, plugins, and apps.
- Disable an entire plugin when none of its components are needed.
- Keep the plugin enabled and disable a child MCP or app only when another bundled component remains needed.
- Use `[[skills.config]]` for standalone skills. Absolute global-skill paths are workstation-specific.
- Preserve unrelated project config and comments.
- Never use project config for provider credentials, profiles, notifications, or telemetry.

## Report requirements

For every item, include:

- Identifier and human-readable name.
- Owner and component type.
- Effective enabled state.
- Short purpose.
- Last-used timestamp and attempt/success/failure counts when available.
- Project evidence.
- Recommendation and concise rationale.

Clearly distinguish:

- Installed from enabled.
- Enabled from authorized.
- An unsupported authentication-status probe from a failed authentication state.
- Exposed from invoked.
- Attempted from successful.
- Project-local control from global installation state.
