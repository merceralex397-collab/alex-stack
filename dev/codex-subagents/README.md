# Codex subagents guide

This folder is a reference and template library for Codex subagents. Files
inside `codex-subagents/` are not discovered automatically. To activate an
agent, copy its TOML file into one of Codex's supported agent directories:

- Project-scoped: `.codex/agents/<agent-name>.toml`
- Personal/global: `~/.codex/agents/<agent-name>.toml`

The current starter is
[`template/subagent-template.toml`](template/subagent-template.toml). The
complete reviewable role library derived from the Subagent Workflow Design is
in [`drafts/`](drafts/README.md); it contains a root orchestrator and all A, B,
and C roles organized by development team.

> The custom-agent format is still evolving. This guide reflects the official
> OpenAI documentation and the `openai/codex` `main` branch at commit
> `0fb559f0f6e231a88ac02ea002d3ecd248e2b515`, inspected on 19 July 2026.

## What subagents are

A subagent is a specialized child agent spawned by the main Codex agent to
handle a bounded part of a task. Each subagent gets its own thread, context,
model work, and tool calls. The main agent can run independent subagents in
parallel and consolidate their results.

This is useful for:

- Exploring separate areas of a codebase in parallel.
- Splitting a review into security, correctness, testing, and maintainability.
- Running tests or analyzing logs without filling the main thread with noise.
- Giving different roles different models, reasoning effort, tools, or
  permissions.
- Using a documentation-only agent with an MCP documentation server.
- Using a browser-debugging agent separately from the agent that edits code.
- Processing large, repeated batches from CSV with structured outputs.

Subagents consume more tokens than a comparable single-agent run because every
agent performs its own reasoning and tool work. Parallel write-heavy tasks can
also conflict when multiple agents edit the same files. Prefer subagents for
independent or read-heavy work, or give each writing agent exclusive ownership
of a distinct file set.

## Built-in agents

Codex includes these built-in agent types:

| Agent | Intended use |
| --- | --- |
| `default` | General-purpose fallback |
| `worker` | Implementation and fixes |
| `explorer` | Read-heavy codebase exploration |

A custom agent with the same `name` as a built-in agent takes precedence.

## Creating a custom agent

Each standalone custom-agent TOML file must define:

| Field | Required | Purpose |
| --- | :---: | --- |
| `name` | Yes | Identity Codex uses to spawn and refer to the agent |
| `description` | Yes | Guidance telling Codex when this role is appropriate |
| `developer_instructions` | Yes | The role's behavior, method, boundaries, and output contract |
| `nickname_candidates` | No | Unique display names for instances of the role |

Example:

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."

developer_instructions = """
Review code like an owner.
Prioritize correctness, security, regressions, and missing test coverage.
Lead with concrete findings and cite the relevant files and symbols.
Do not edit code.
"""

nickname_candidates = ["Atlas", "Delta", "Echo"]
```

The `name` field is the source of truth. Matching the filename to the name is
the clearest convention, for example `reviewer.toml` for `name = "reviewer"`.

Nickname candidates:

- Are display-only; they do not change the agent's identity.
- Must be a non-empty list when supplied.
- Must be unique within the list.
- May contain ASCII letters, digits, spaces, hyphens, and underscores.

## Agent-specific session settings

A custom-agent file is loaded as a Codex configuration layer. Omitted settings
inherit from the parent session. OpenAI explicitly documents these settings as
useful agent-level overrides:

| Setting | Purpose |
| --- | --- |
| `model` | Pin a model for this role |
| `model_reasoning_effort` | Set the reasoning depth for this role |
| `sandbox_mode` | Make the role read-only, workspace-writing, or full-access by default |
| `mcp_servers` | Give the role dedicated external tools or context |
| `skills.config` | Enable or disable individual skills for the role |

Other supported `config.toml` keys can also be placed in an agent file because
the file is a session configuration layer. Use that flexibility carefully:
keep role files narrow, avoid embedding secrets, and consult the configuration
reference before adding general session settings.

### Model selection

The current subagent documentation recommends:

| Model | Good fit |
| --- | --- |
| `gpt-5.6` | Demanding, ambiguous, multi-step work with planning and validation |
| `gpt-5.4` | Workflows intentionally pinned to GPT-5.4 |
| `gpt-5.6-terra` | Faster, lower-cost exploration, scans, large-file review, and supporting work |
| `gpt-5.3-codex-spark` | Near-instant text-only iteration for eligible ChatGPT Pro users; research preview |

If neither `model` nor `model_reasoning_effort` is pinned, Codex can choose a
combination based on the delegated task.

Model availability can depend on the user's plan, client, and current model
catalog. A reusable template should usually inherit the parent's model unless
the role has a clear speed, cost, or capability requirement.

### Reasoning effort

The subagent documentation describes these model-dependent effort levels:

- `ultra`
- `max`
- `xhigh`
- `high`
- `medium`
- `low`
- `minimal`
- `none`

Not every model supports every level. `medium` is a balanced default, `high` or
above suits complex review and security work, and `low` suits straightforward
scans where latency matters. Higher effort generally increases latency and
token use.

Example:

```toml
model = "gpt-5.6-terra"
model_reasoning_effort = "medium"
```

### Sandbox modes

```toml
sandbox_mode = "read-only"
```

The documented modes are:

| Mode | Intended boundary |
| --- | --- |
| `read-only` | Inspect and report without normal workspace writes |
| `workspace-write` | Permit writes within the configured workspace boundary |
| `danger-full-access` | Remove the normal sandbox boundary; use only in an already isolated environment |

Use `read-only` for explorers, reviewers, researchers, and diagnostics agents.
Reserve write access for roles that explicitly own implementation.

Important inheritance rules:

- Subagents inherit the parent turn's active sandbox and permission mode.
- Live runtime choices on the parent turn are reapplied when a child is
  spawned, even if an agent file contains different defaults.
- In interactive CLI sessions, an approval can surface from an inactive
  subagent thread.
- In non-interactive runs, an action that needs a new approval fails when the
  approval cannot be surfaced.
- Work mode uses the tools available to the parent chat; website and connector
  permissions remain tool-specific.

Choose the parent permission mode before asking Codex to delegate. Treat an
agent-level `sandbox_mode` as a role default, not a way to bypass the parent
session's active security boundary.

## Giving an agent an MCP server

An agent can have a dedicated MCP server configuration. This is useful when a
role needs a specific tool surface and other roles do not.

HTTP example:

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

Local STDIO example:

```toml
[mcp_servers.example]
command = "npx"
args = ["-y", "@example/mcp-server"]
env_vars = ["EXAMPLE_TOKEN"]
```

Relevant MCP settings include:

- STDIO transport: `command`, `args`, `cwd`, `env`, `env_vars`
- HTTP transport: `url`, `auth`, `bearer_token_env_var`, `scopes`,
  `oauth_resource`, `http_headers`, `env_http_headers`
- Availability: `enabled`, `required`
- Timing: `startup_timeout_sec`, `startup_timeout_ms`, `tool_timeout_sec`
- Tool exposure: `enabled_tools`, `disabled_tools`
- Approval defaults: `default_tools_approval_mode`
- Per-tool approvals: `tools.<tool>.approval_mode`

Do not store bearer tokens directly in an agent file. Use an environment
variable or the documented OAuth flow.

## Enabling or disabling skills per agent

Use `[[skills.config]]` entries to override whether a particular skill is
available to the role:

```toml
[[skills.config]]
path = "C:/Users/you/.agents/skills/example/SKILL.md"
enabled = false
```

Each entry supports:

| Setting | Purpose |
| --- | --- |
| `path` | Path to the skill folder or its `SKILL.md`, as supported by the active client |
| `enabled` | Enable or disable that skill for the agent |

This is useful for keeping an implementation agent from invoking a
documentation-editing workflow, or ensuring a specialist role has only the
skills relevant to its job.

## Global subagent settings

Global limits belong under `[agents]` in user-level `~/.codex/config.toml` or
project-level `.codex/config.toml`:

```toml
[features]
multi_agent = true

[agents]
enabled = true
max_concurrent_threads_per_session = 6
max_depth = 1
# Optional role-independent defaults:
# default_subagent_model = "gpt-5.6-terra"
# default_subagent_reasoning_effort = "medium"
job_max_runtime_seconds = 1800
interrupt_message = true
```

| Setting | Default | Meaning |
| --- | ---: | --- |
| `features.multi_agent` | `true` | Enables the stable multi-agent collaboration tools |
| `agents.enabled` | `true` | Enables local multi-agent tools; an enabled V2 feature takes precedence |
| `agents.max_concurrent_threads_per_session` | Backend-specific | Maximum number of spawned threads open per session |
| `agents.max_threads` | Legacy alias | Older public name normalized to `max_concurrent_threads_per_session` |
| `agents.max_depth` | `1` | Maximum V1 spawn nesting depth; the root is depth `0` |
| `agents.default_subagent_model` | Parent/backend choice | Default child model when spawn does not select one |
| `agents.default_subagent_reasoning_effort` | Parent/backend choice | Default child reasoning effort when spawn does not select one |
| `agents.job_max_runtime_seconds` | `1800` tool fallback | Default per-worker timeout for CSV fan-out jobs |
| `agents.interrupt_message` | `true` | Adds a model-visible message when an agent turn is interrupted |

The dedicated public Subagents page currently calls the concurrency setting
`agents.max_threads` and gives a default of `6`. Current source has renamed the
canonical key to `agents.max_concurrent_threads_per_session` and retains
`max_threads` as a compatibility alias. Prefer the canonical name when targeting
current builds; use the public name when maintaining configuration for an older
released client that does not recognize the new key.

`agents.max_depth` is enforced by the V1 backend. Current Codex source
explicitly marks it as ignored by V2. For V1, keep `max_depth = 1` unless
recursive delegation is genuinely required. A higher value can create repeated
fan-out, increasing token usage, latency, and resource consumption.
`max_threads` limits concurrent open threads but does not remove those costs.

Project-scoped configuration is loaded only for trusted projects.

### V2 source-level settings

The current `openai/codex` source exposes a separate structured feature table
for V2:

```toml
[features.multi_agent_v2]
enabled = true
max_concurrent_threads_per_session = 4
min_wait_timeout_ms = 10000
max_wait_timeout_ms = 3600000
default_wait_timeout_ms = 30000
tool_namespace = "collaboration"
hide_spawn_agent_metadata = true
expose_spawn_agent_model_overrides = true
non_code_mode_only = true
```

These V2 settings are source-level and under development, rather than stable
public configuration:

| Setting | Source default | Purpose |
| --- | ---: | --- |
| `enabled` | `false` | Select the V2 backend when explicitly enabled |
| `max_concurrent_threads_per_session` | `4` | Total simultaneous slots including the root |
| `min_wait_timeout_ms` | `10000` | Minimum V2 mailbox-wait timeout |
| `max_wait_timeout_ms` | `3600000` | Maximum V2 mailbox-wait timeout |
| `default_wait_timeout_ms` | `30000` | Default V2 mailbox-wait timeout |
| `usage_hint_text` | Unset | Shared custom usage guidance |
| `root_agent_usage_hint_text` | Built in | Root-specific orchestration guidance |
| `subagent_usage_hint_text` | Built in | Child-agent orchestration guidance |
| `multi_agent_mode_hint_text` | Effort-derived | Overrides the explicit-only or proactive delegation policy text |
| `tool_namespace` | `collaboration` | Namespace containing the V2 collaboration tools |
| `hide_spawn_agent_metadata` | `true` | Hides optional spawn-result metadata such as nicknames |
| `expose_spawn_agent_model_overrides` | `true` | Exposes `model` and `reasoning_effort` on V2 spawn calls |
| `non_code_mode_only` | `true` | Restricts where the V2 surface is exposed relative to code mode |
| `usage_hint_enabled` | Ignored | Deprecated compatibility field |

Wait timeouts must be between `0` and `3,600,000` milliseconds, and the
minimum, default, and maximum must be ordered consistently. The tool namespace
must be 1–64 ASCII letters, digits, underscores, or hyphens and cannot collide
with reserved tool namespaces.

Because `multi_agent_v2` is marked **under development** and defaults to
disabled in current source, do not put these settings into shared production
configuration without testing the exact Codex client and version in use.

### Alternative explicit role registration

The configuration reference also documents named role tables:

```toml
[agents.reviewer]
description = "Find correctness, security, and test risks in code."
config_file = "./agents/reviewer.toml"
nickname_candidates = ["Athena", "Ada"]
```

The available registration fields are:

| Setting | Purpose |
| --- | --- |
| `agents.<name>.description` | Role-selection guidance |
| `agents.<name>.config_file` | Path to a TOML configuration layer; relative to the declaring config file |
| `agents.<name>.nickname_candidates` | Optional display nickname pool |

For new setups, prefer the simpler standalone files in `.codex/agents/` or
`~/.codex/agents/`, as described by the dedicated subagents guide. Use explicit
registration when you intentionally want the role mapping to live in a
particular `config.toml` layer.

## V1 and V2 orchestration backends

V1 and V2 are not different models or custom-agent file formats. They are two
local Codex orchestration backends that expose different tools for identifying,
messaging, waiting for, and managing spawned agents.

The public Subagents guide describes subagents without presenting a formal
V1-to-V2 migration guide. The names and concrete differences below come from
the current open-source Codex implementation.

### Current status

At the inspected source commit:

- `features.multi_agent` selects the V1 collaboration backend. It is marked
  **stable** and defaults to enabled.
- `features.multi_agent_v2` selects the path-based V2 backend. It is marked
  **under development** and defaults to disabled.
- An enabled V2 setting takes precedence over V1.
- A model or client can select V2 even when the user has not forced it through
  configuration.
- This Codex task is using the V2 surface because its available collaboration
  tools use task paths, `fork_turns`, `send_message`, and `followup_task`.

Therefore, “always use V2 for new workflows” is not yet a safe general
recommendation. Use the backend exposed by the current client/model unless you
are deliberately testing V2 against a pinned Codex version.

### V1 versus V2

| Area | V1 | V2 |
| --- | --- | --- |
| Identity | Opaque thread/agent ID returned as `agent_id` | Human-readable canonical path such as `/root/security_review` |
| Spawn naming | No required task name | Requires a lowercase `task_name`; returns its canonical path |
| Context fork | `fork_context = true` or `false` | `fork_turns = "none"`, `"all"`, or a positive integer string |
| Role/model controls | Optional `agent_type`, `model`, `reasoning_effort`, and service tier | Same kinds of overrides can exist, but the selected client/model may hide them |
| Messaging | `send_input`, with text or structured items and optional interruption | `send_message` queues information; `followup_task` assigns work and starts/resumes a turn |
| Waiting | Wait for specified agent IDs to reach final status | Wait for any live-agent mailbox update; content arrives as agent messages |
| Discovery | Retain IDs returned by spawn | `list_agents` returns the named task tree and status |
| Interruption | `send_input` can redirect immediately | `interrupt_agent` stops the active turn but retains the agent context |
| Close/resume | Explicit `close_agent` and `resume_agent` | No equivalent close tool; use interrupt plus a later `followup_task` |
| Nesting | Enforced by `agents.max_depth` | Path hierarchy supports descendants; `agents.max_depth` is ignored |
| Collaboration style | Primarily controller-to-worker | Agents can address peers and descendants by canonical task path |

### Context behavior

V1 provides a binary history decision:

```text
fork_context = false  -> start from the delegated prompt
fork_context = true   -> copy the full parent history
```

V2 provides finer control:

```text
fork_turns = "none"   -> no surrounding parent turns
fork_turns = "all"    -> full available history; this is the default
fork_turns = "3"      -> only the three most recent turns
```

V2 rejects `fork_context` and directs callers to use `fork_turns`. Full-history
forks inherit the parent model and reasoning effort. When an explicit
agent-role, model, or reasoning override is needed, use `"none"` or a positive
turn count rather than `"all"`.

### V1 lifecycle

The V1 tool surface consists of:

- `spawn_agent`
- `send_input`
- `wait_agent`
- `resume_agent`
- `close_agent`

V1 is useful when a workflow specifically relies on structured input items,
interrupting through `send_input`, closing threads to release concurrency, or
resuming a previously closed agent by ID.

### V2 lifecycle

The V2 tool surface consists of:

- `spawn_agent`
- `send_message`
- `followup_task`
- `wait_agent`
- `interrupt_agent`
- `list_agents`

`send_message` delivers information without starting a new turn.
`followup_task` assigns work and starts or resumes a non-root agent turn.
`wait_agent` watches the caller's mailbox rather than a supplied list of IDs.
`interrupt_agent` leaves the target available for later messages and follow-up
tasks. `list_agents` exposes the live named tree.

### Important naming collision: Responses API `v1`

The Responses API also has a beta header named
`responses_multi_agent=v1`. That API feature uses `/root` paths and the six
V2-style hosted collaboration actions listed above. Its `v1` label is the
version of the public API beta, not proof that it uses Codex's legacy V1 local
backend.

Keep these concepts separate:

- **Codex V1/V2:** internal local orchestration backends and tool surfaces.
- **Responses Multi-agent beta `v1`:** the first public beta protocol version,
  currently using path-based collaboration semantics.

The Responses API also differs operationally: all agents share the request's
model and tool list, and `max_concurrent_subagents` limits active child turns.
Do not copy its API configuration directly into local Codex `config.toml`.

## How subagents are triggered

In local Codex clients, subagents are spawned when:

- The user asks directly for subagents, delegation, or parallel agents.
- Applicable `AGENTS.md` instructions require delegation.
- An invoked skill instructs Codex to delegate work.

Good delegation prompts specify:

1. How to divide the work.
2. Which role should own each part.
3. Whether Codex should wait for all agents.
4. The output or summary each agent must return.
5. Whether agents may edit, and their non-overlapping ownership boundaries.

Example:

```text
Review this branch with three parallel subagents. Use an explorer to map the
affected execution paths, a reviewer to find correctness and security risks,
and a test specialist to identify missing coverage. Keep all agents read-only,
wait for all three, then consolidate only evidence-backed findings with file
references.
```

## Orchestration and thread controls

Codex exposes the V1 or V2 tool set selected for the current client, model, and
configuration. Prompts should describe the desired orchestration outcome
instead of hard-coding backend tool calls unless the workflow is intentionally
version-specific.

The exact controls exposed in the UI vary by client:

- Desktop app: open subagent threads from their activity and ask Codex to
  steer, stop, or close them.
- CLI: use `/agent` to inspect and switch among agent threads.
- IDE extension: use the background-agent panel when available to inspect or
  stop subagents.

The main agent can wait for requested agents and consolidate their results. It
should return summaries rather than copying all intermediate logs into the main
thread.

## Experimental CSV fan-out

`spawn_agents_on_csv` is an experimental workflow for many similar tasks with
one work item per CSV row. Codex:

1. Reads the source CSV.
2. Spawns one worker per row, subject to concurrency limits.
3. Waits for the batch.
4. Exports the original row data and combined results to another CSV.

Good uses include reviewing one file, package, service, incident, PR, or
migration target per row.

The documented inputs are:

| Input | Purpose |
| --- | --- |
| `csv_path` | Source CSV |
| `instruction` | Worker prompt template using `{column_name}` placeholders |
| `id_column` | Optional column used for stable item IDs |
| `output_schema` | Optional JSON schema for every worker result |
| `output_csv_path` | Destination CSV |
| `max_concurrency` | Per-call concurrency control |
| `max_runtime_seconds` | Per-call worker timeout; overrides the global default |

Every CSV worker must call `report_agent_job_result` exactly once. A worker that
exits without reporting is recorded as an error. Exported results include the
original columns plus metadata such as `job_id`, `item_id`, `status`,
`last_error`, and `result_json`.

`sqlite_home` controls where Codex stores the SQLite-backed state used for
resumable agent jobs and exported results:

```toml
sqlite_home = "C:/path/to/codex-state"
```

Because this feature is experimental, verify the current documentation and
client support before building a durable workflow around it.

## Subagent lifecycle hooks

Codex hooks can observe subagent lifecycle events:

| Event | When it runs | Matcher |
| --- | --- | --- |
| `SubagentStart` | When a child agent starts | Subagent type |
| `SubagentStop` | When a child agent turn stops | Subagent type |

Hooks can be stored in `hooks.json` or inline under `[hooks]` in a config layer.
They can be used for logging, adding role-specific context, recording metrics,
or checking completion output.

Important hook behavior:

- `SubagentStart` can return a `systemMessage` as additional context.
- Returning `continue: false` from `SubagentStart` does not stop the subagent.
- `SubagentStop` can provide a continuation message or stop reason.
- Hook matchers are regular expressions; `*`, an empty string, or no matcher
  matches every supported occurrence.
- Hooks are useful guardrails, not a complete security boundary.
- Avoid secrets in hook output; large model-visible output may be written to a
  local hook-output file.

See the Hooks guide for the complete event payload and command-hook schema
before implementing lifecycle automation.

## Recommended role patterns

### Read-only explorer

Use:

- `sandbox_mode = "read-only"`
- A fast model with `medium` or `low` reasoning
- Instructions to cite files and symbols
- A clear prohibition on proposing or applying fixes unless asked

### Reviewer

Use:

- `sandbox_mode = "read-only"`
- A strong model with `high` reasoning
- Instructions to prioritize correctness, security, regressions, and tests
- An output contract requiring evidence, impact, and reproduction steps

### Documentation researcher

Use:

- `sandbox_mode = "read-only"`
- A dedicated documentation MCP server
- Instructions to use primary sources and return links
- No application-code edits

### Implementation worker

Use:

- Workspace write access only when necessary
- Exclusive ownership of specified files
- Instructions to make the smallest coherent change
- Required verification and a concise handoff summary

### Browser debugger

Use:

- A browser or DevTools MCP server
- Instructions to reproduce and collect console, network, or screenshot evidence
- No application-code edits unless the role is intentionally combined with a
  fixer

## Design guidance

The best custom agents are narrow and opinionated:

- Give each role one clear job.
- Make `description` specific enough for reliable selection.
- Put durable behavior and boundaries in `developer_instructions`.
- Match tools and permissions to the job.
- Require concise, structured results.
- Keep explorers and reviewers read-only.
- Avoid overlapping write ownership.
- Inherit parent settings unless a role has a clear reason to override them.
- On V1, start with direct children and the default depth of `1`.
- On V2, control fan-out with bounded task scopes and concurrency; the V1
  `max_depth` setting does not apply.
- Use CSV fan-out only for genuinely uniform row-level work.

## Official references

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Configuration basics and precedence](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Hooks](https://learn.chatgpt.com/docs/hooks)
- [Models](https://learn.chatgpt.com/docs/models)
- [Responses API Multi-agent beta](https://developers.openai.com/api/docs/guides/responses-multi-agent)
- [`openai/codex` feature definitions](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/features/src/lib.rs#L1042-L1055)
- [`openai/codex` V1/V2 selection and limits](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/core/src/config/mod.rs#L1438-L1481)
- [`openai/codex` V1/V2 tool specifications](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/core/src/tools/handlers/multi_agents_spec.rs#L148-L363)
- [`openai/codex` V2 configuration schema](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/features/src/feature_configs.rs#L34-L75)
