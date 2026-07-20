---
name: codex-profile-pack
description: Create, validate, preview, and optionally install a coordinated Codex customisation pack containing skills, custom subagents, command rules, AGENTS.md guidance, lifecycle hooks, MCP server configuration, and either a base config.toml fragment or a named profile. Use when a user wants to build, bundle, migrate, reproduce, or install a Codex setup at project or global scope, especially when several Codex customisation surfaces must work together. Do not use for installing a published plugin or for changing one isolated Codex setting that does not need a reusable pack.
---

# Codex Profile Pack

Build a source-controlled pack first, then install it only when the user explicitly requests installation. Treat project and global scope as separate products: do not silently promote project conventions into personal global defaults.

## Establish the brief

1. Inspect the repository, its applicable `AGENTS.md`, existing `.codex/` and `.agents/` content, Git status, and available validation commands.
2. Identify the requested components: skills, agents, rules, `AGENTS.md`, hooks, MCP servers, base config, and/or profile.
3. Confirm or infer the output pack directory. Keep authored pack files separate from their install destinations.
4. Establish the install scope:
   - Use `project` for repo-owned behaviour.
   - Use `global` only for personal behaviour intended across repositories.
5. Keep installation optional. Creating a pack does not authorise installing it.
6. Read [codex-surfaces.md](references/codex-surfaces.md) before authoring component files. Refresh against current official Codex documentation when a format or path may have changed.
7. Read [pack-contract.md](references/pack-contract.md) before using or modifying the helper.

## Design the pack

Use the smallest set of surfaces that expresses the requested behaviour:

- Put durable repo conventions and validation commands in `AGENTS.md`.
- Put reusable procedures, scripts, and references in skills.
- Put narrow delegated roles in custom agent TOML files.
- Put command approval policy in `.rules` files.
- Put lifecycle enforcement in hooks.
- Put live external tools in MCP server tables.
- Put shared runtime defaults in `config.toml`.
- Put an optional named CLI configuration layer in `profile.toml`; profiles are global-only.

Avoid duplicating the same instruction across surfaces. Keep secrets, tokens, credentials, personal data, and literal bearer values out of the pack. Refer to environment-variable names instead.

## Initialise the source pack

Resolve `<skill-dir>` to the directory containing this `SKILL.md`. Invoke the
helper by its absolute path; do not assume the current working directory is the
skill directory.

Run the helper with only the components needed:

```powershell
python <skill-dir>/scripts/codex_profile_pack.py init `
  --path <pack-directory> `
  --name <pack-name> `
  --components skill,agent,rule,agents-md,hook,mcp,config
```

Available component names are `skill`, `agent`, `rule`, `agents-md`, `hook`, `mcp`, `config`, and `profile`. Replace every `TODO` in generated artifacts. Delete unused placeholder components rather than leaving them inert.

For each generated skill, follow the local skill-creation workflow when available and include valid `agents/openai.yaml` metadata. Make custom agents narrow, with required `name`, `description`, and `developer_instructions`. Add rule `match` and `not_match` examples. Make hook commands portable for their intended scope. Define MCP credentials through environment references.

## Validate

Run:

```powershell
python <skill-dir>/scripts/codex_profile_pack.py validate --pack <pack-directory> --check-rules
```

Fix every error. Treat warnings as unresolved until reviewed. Also run the narrow validators belonging to nested skills, hook scripts, MCP servers, or other generated code.

The helper checks pack structure, manifests, skill frontmatter, custom-agent TOML, hook JSON, config TOML, obvious secrets, placeholders, and—when `codex` is available—rule loading through `codex execpolicy check`.

## Preview installation

Always preview the exact destination map:

```powershell
python <skill-dir>/scripts/codex_profile_pack.py plan `
  --pack <pack-directory> `
  --scope project `
  --project-root <repository-root>
```

For global scope:

```powershell
python <skill-dir>/scripts/codex_profile_pack.py plan `
  --pack <pack-directory> `
  --scope global `
  --codex-home <CODEX_HOME> `
  --user-home <user-home> `
  --profile <optional-profile-name>
```

Review collisions, config key overlaps, hook additions, the resolved `CODEX_HOME`, and the global skill destination. Do not use a legacy `[profiles.<name>]` table. A project installation cannot install `profile.toml`.

## Install only when authorised

After the user has explicitly requested installation and the plan is clean, run the corresponding command with `--apply`:

```powershell
python <skill-dir>/scripts/codex_profile_pack.py install <same-options> --apply
```

The helper creates an installation record and backups for changed existing files. It refuses different skill, agent, rule, and hook-support files unless `--replace` is supplied. Use `--replace` only after inspecting the destination diff. It never overwrites conflicting TOML keys; resolve those manually and preview again.

Do not authenticate MCP servers, start external services, enable billed resources, or weaken sandbox/approval policy unless the user separately requested those actions.

## Verify and report

1. Run `validate` again against the source pack.
2. Inspect the installation record reported by the helper.
3. Re-run `plan`; expect only `unchanged` or managed-block refresh actions.
4. Validate any installed rules with `codex execpolicy check`.
5. Explain that project `.codex` configuration, rules, and hooks require a trusted project.
6. State whether a new Codex session or restart is needed for discovery.
7. Report the pack path, scope, installed components, backups, checks run, and anything deliberately left uninstalled or unauthenticated.
