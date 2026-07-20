---
name: codex-stack-selection
description: Inventory the Codex skills, plugins, apps/connectors, and MCP servers available to a project; explain what each capability provides; analyze project-scoped use from local Codex session logs over the previous 14 days; recommend what to keep, disable, or repair; and safely update a trusted project's .codex/config.toml. Use for Codex stack audits, integration cleanup, reducing unused tools, diagnosing enabled-but-failing capabilities, or creating project-specific Codex configuration. Do not use to uninstall global capabilities or install telemetry hooks.
---

# Codex Stack Selection

Build a project-specific Codex stack from current inventory, recent local use, and repository evidence. Keep all collection local and make project configuration changes only after showing the proposed delta.

## Workflow

1. Resolve the target project.
   - Prefer the user-supplied path.
   - Otherwise use the current Git root, falling back to the current directory.
   - Treat Windows paths case-insensitively.

2. Run the bundled inventory:

   ```powershell
   python "<skill-dir>\scripts\codex_stack_inventory.py" --project "<project>" --days 14 --pretty
   ```

   Use `--no-cache` when the user wants no derived local index. Use `--refresh` when the cached transcript offsets may be stale.

3. Inspect repository evidence.
   - Read applicable `AGENTS.md` files and the existing `.codex/config.toml`.
   - Inspect only relevant manifests, infrastructure, CI, documentation, and source entry points.
   - Do not infer a provider need from a name alone when the repository can establish it.

4. Classify every inventoried capability.
   - **Keep**: recently used, required by project instructions, or strongly supported by repository evidence.
   - **Disable**: unused in the observation window and unsupported by project evidence.
   - **Needs attention**: recently attempted but failing, unresolved ownership, partial inventory, or insufficient history.
   - Count an attempted failure as use. Recommend repairing it or replacing it; do not call it unused.
   - Do not treat a tool-search result, injected catalog, installed plugin, or enabled setting as use.
   - Infer plugin use only through a used bundled skill, app, MCP server, or hook.
   - If no matching sessions exist, say that history is unavailable and rely on repository evidence. Never equate missing logs with zero need.

5. Explain the result.
   - List skills, plugins, apps, and MCP servers separately.
   - For each item, state its purpose, current state, recent-use evidence, project evidence, recommendation, and reason.
   - For large inventories, group by owner or category and use compact per-item tables. Do not omit items merely to shorten the report.
   - Identify failures without exposing command arguments, prompts, tool output, credentials, or session text.
   - Treat `auth_status = "unsupported"` as “the CLI could not assess authentication,” not as an authentication failure.
   - Read [references/selection-policy.md](references/selection-policy.md) for tie-breakers and control precedence.
   - Read [references/session-log-signals.md](references/session-log-signals.md) when log coverage is partial or a usage attribution is disputed.

6. Preview the project configuration.
   - Produce the exact `.codex/config.toml` delta.
   - Prefer a single owner-level plugin switch over redundant switches for all bundled components.
   - Preserve unrelated settings and comments.
   - Never add `otel`, notification telemetry, or a usage hook.
   - Never change global config, uninstall a plugin, delete a skill, or revoke external authorization.
   - Warn when a global skill override requires an absolute workstation-specific path.

7. Apply only after explicit user approval.
   - Create or edit `<project>\.codex\config.toml` with `apply_patch`.
   - Stop before editing if the project is untrusted; project config would be ignored.
   - Validate the resulting TOML with Python `tomllib`.
   - Rerun the inventory with `--no-cache` and confirm the effective state.
   - Report any recommendation that could not be represented project-locally.

## Configuration Controls

Use the smallest applicable project-scoped control:

```toml
[[skills.config]]
path = "C:/absolute/path/to/SKILL.md"
enabled = false

[mcp_servers.example]
enabled = false

[plugins."example@marketplace"]
enabled = false

[plugins."example@marketplace".mcp_servers.server_name]
enabled = false

[apps.connector_id]
enabled = false
```

Do not write redundant `enabled = true` entries when inherited state already matches the recommendation.

## Inventory Contract

The script is read-only except for its optional local cache. It:

- Uses `codex plugin list --json` and `codex mcp list --json` as current-state sources.
- Reads skill frontmatter and active plugin manifests.
- Uses cached plugin manifests only to name or attribute an already-configured opaque app; it does not count dormant cache entries as installed.
- Reads only the minimum transcript fields needed for attribution.
- Never outputs message content, arguments, results, tokens, environment values, or authentication headers.
- Stores only normalized capability events, counts, timestamps, statuses, transcript-relative paths, and byte offsets in its cache.
- Emits degraded-discovery warnings instead of inventing missing descriptions or ownership.
