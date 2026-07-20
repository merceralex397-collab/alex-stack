# Pack contract and helper

## Source layout

```text
<pack>/
├── pack.toml
├── skills/<skill-name>/SKILL.md
├── agents/<agent-name>.toml
├── rules/<policy-name>.rules
├── AGENTS.md
├── hooks/
│   ├── hooks.json
│   └── <support files>
├── mcp.toml
├── config.toml
└── profile.toml
```

Only `pack.toml` is required by the schema, but validation rejects a pack with
no usable components.

## Manifest

```toml
schema_version = 1
name = "review-pack"
description = "Review workflow and supporting Codex configuration."

[install]
default_scope = "project"
profile = ""
```

Names use lowercase letters, digits, and hyphens. `default_scope` is advisory;
the explicit CLI `--scope` wins. Set `profile` only when `profile.toml` should
have a default global profile name.

## Commands

```text
python <skill-dir>/scripts/codex_profile_pack.py init --path <dir> --name <name> --components <csv>
python <skill-dir>/scripts/codex_profile_pack.py validate --pack <dir> [--check-rules]
python <skill-dir>/scripts/codex_profile_pack.py plan --pack <dir> --scope project|global [destination options]
python <skill-dir>/scripts/codex_profile_pack.py install --pack <dir> --scope project|global [destination options] --apply
```

Destination options:

- `--project-root`: repo root; defaults to the nearest parent containing `.git`.
- `--codex-home`: defaults to `CODEX_HOME`, then `<user-home>/.codex`.
- `--user-home`: defaults to the current user's home and controls global skills.
- `--profile`: overrides `install.profile`.
- `--replace`: permits backed-up replacement of different component files. It
  does not permit conflicting TOML keys.
- `--json`: emits a machine-readable plan.

## Installation behaviour

- Skills, agents, rules, and hook support files copy file by file.
- Identical files are unchanged.
- Different component files are collisions unless `--replace` is explicit.
- `AGENTS.md` is managed through a named comment block, preserving surrounding
  user content.
- Hook event arrays are merged and exact duplicate hook objects are skipped.
- `config.toml`, `mcp.toml`, and `profile.toml` are parsed before installation.
  Non-conflicting root keys and tables are merged while preserving existing
  text. Conflicting keys or repeated explicit tables stop the whole install
  before any write.
- Existing files changed by an install are copied to a timestamped backup.
- The helper writes an install record under
  `<config-layer>/profile-packs/<pack-name>.json`.
- A project install containing `profile.toml` is invalid.
- The helper rejects symlinks, unresolved `TODO` markers, malformed component
  files, and common credential patterns.

The helper deliberately does not authenticate MCP servers, start hook
services, trust projects or hooks, run deployments, or alter managed policy.
