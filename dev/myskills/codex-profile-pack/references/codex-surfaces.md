# Codex customisation surfaces

Use this reference to choose paths and formats. These details were checked
against the official Codex manual on 20 July 2026. Refresh the linked official
documentation before relying on drift-prone schemas.

## Scope map

| Surface | Project | Global |
| --- | --- | --- |
| Skills | `<repo>/.agents/skills/<name>/SKILL.md` | `<user-home>/.agents/skills/<name>/SKILL.md` |
| Custom agents | `<repo>/.codex/agents/<name>.toml` | `<CODEX_HOME>/agents/<name>.toml` |
| Rules | `<repo>/.codex/rules/<name>.rules` | `<CODEX_HOME>/rules/<name>.rules` |
| Guidance | `<repo>/AGENTS.md` | `<CODEX_HOME>/AGENTS.md` |
| Hooks | `<repo>/.codex/hooks.json` or inline config | `<CODEX_HOME>/hooks.json` or inline config |
| MCP and base config | `<repo>/.codex/config.toml` | `<CODEX_HOME>/config.toml` |
| Named profile | Not supported as a project layer | `<CODEX_HOME>/<profile>.config.toml` |

`CODEX_HOME` defaults to `~/.codex`. Global skills use
`$HOME/.agents/skills`, not `CODEX_HOME/skills`.

Project `.codex/config.toml`, hooks, and rules load only when the project is
trusted. Codex scans repo skills from the current directory up to the
repository root.

## Skills

A skill is a directory containing `SKILL.md` with YAML frontmatter keys
`name` and `description`. Optional resources include `scripts/`, `references/`,
`assets/`, and `agents/openai.yaml`.

Use clear trigger language in `description`. Keep detailed instructions out of
frontmatter and use progressive disclosure.

Official source: [Build skills](https://learn.chatgpt.com/docs/build-skills)

## Custom agents

Put one standalone TOML file per agent under `agents/`. Require:

```toml
name = "reviewer"
description = "Review changes for correctness and missing tests."
developer_instructions = """
Review only. Return evidence with file references.
"""
```

Optional normal config keys include `nickname_candidates`, `model`,
`model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`.
Omitted values inherit from the parent. Prefer inheritance over unnecessary
pinning.

Official source: [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## Rules

Rules are experimental Starlark `.rules` files containing `prefix_rule(...)`
calls. Use `pattern`, `decision`, `justification`, and inline `match` /
`not_match` examples. The most restrictive matching decision wins.

Test each file with:

```text
codex execpolicy check --pretty --rules <file> -- <command> <args>
```

Official source: [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)

## AGENTS.md

Global discovery reads `AGENTS.override.md` first, otherwise `AGENTS.md`.
Project discovery walks from the repo root towards the current directory,
loading at most one applicable guidance file per directory. Closer guidance
wins.

Put personal communication defaults in the global file and repo conventions in
the project file. Keep the file concise and practical.

Official source: [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## Hooks

Use `hooks.json` or inline `[hooks]` in the active config layer, not both.
Pack layout uses `hooks/hooks.json` plus optional support files. The installer
maps the JSON file to the config-layer root and support files to its `hooks/`
directory.

Non-managed hooks require trust review. Matching hooks from multiple sources
all run, and multiple matching command hooks may run concurrently. Resolve
repo-local support scripts from the Git root rather than assuming the launch
directory.

Official source: [Hooks](https://learn.chatgpt.com/docs/hooks)

## MCP servers

Put MCP tables in `mcp.toml`:

```toml
[mcp_servers.docs]
url = "https://example.test/mcp"
bearer_token_env_var = "DOCS_MCP_TOKEN"
enabled = true
```

For stdio servers use `command`, optional `args`, `env`, `env_vars`, and `cwd`.
For Streamable HTTP use `url`, optional `auth`, `bearer_token_env_var`,
`http_headers`, and `env_http_headers`.

Never store secret values. Use environment-variable names, then perform OAuth
or other authentication separately after installation.

Official source: [Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp)

## Config and profiles

Put base configuration keys in `config.toml`. Put profile-only overrides in
`profile.toml`; the installer maps it to
`<CODEX_HOME>/<profile>.config.toml`.

Profiles are separate files selected with `codex --profile <name>`. Modern
Codex does not read `[profiles.<name>]` or a top-level `profile = "<name>"`
selector.

Project config cannot override provider/auth redirection, notifications,
telemetry, or profile selection. Keep those settings global.

Official sources:

- [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
