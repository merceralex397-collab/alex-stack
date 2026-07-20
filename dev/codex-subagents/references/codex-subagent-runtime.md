# Codex custom-agent runtime notes

This is a distilled reference for the catalogue design. The underlying
documentation and `openai/codex` source were inspected on 19 July 2026, at
source commit `0fb559f0f6e231a88ac02ea002d3ecd248e2b515`. Recheck unstable
runtime details before relying on them in a pinned client or shared
configuration.

## Standalone agent files

A standalone custom-agent TOML file requires:

| Field | Purpose |
| --- | --- |
| `name` | Stable identity used when selecting and referring to the agent. |
| `description` | Selection guidance explaining when the role is appropriate. |
| `developer_instructions` | Durable behaviour, boundaries, method, and return contract. |
| `nickname_candidates` | Optional display-only names. |

Matching the filename to `name` is the clearest convention and is enforced by
this catalogue.

Agent files can also act as configuration layers and may support model,
reasoning, sandbox, MCP, skill, and other session settings. The catalogue
avoids those overrides initially so files remain portable and inherit the
active parent session.

## Discovery

Custom agents are discovered from supported agent directories:

```text
Project:  .codex/agents/<agent-name>.toml
Personal: ~/.codex/agents/<agent-name>.toml
```

Files elsewhere are reference material only. Project-scoped configuration
requires a trusted project.

## Permissions and inheritance

Subagents remain constrained by the active parent session, available tools,
and approval mode. An agent-level sandbox value is a conservative default, not
a permission bypass.

This catalogue therefore:

- pins `read-only` for agents that must never edit;
- omits the sandbox setting for agents that may edit;
- requires explicit task authority and non-overlapping ownership before any
  edit;
- does not place secrets or workstation-specific tool configuration in agent
  files.

## Orchestration

Codex clients and versions can expose different collaboration tool names and
nesting behaviour. Prompts should state the desired outcome—bounded delegation,
independent ownership, waiting, and consolidation—rather than hard-code a
particular backend's tool calls.

The root agent should select the smallest sufficient set of independent peers.
Parallel write-heavy tasks need exclusive file ownership. Read-heavy
exploration and independent reviews are safer candidates for parallel work.

The catalogue intentionally prevents its subagents from delegating. That keeps
selection and fan-in visible to the root and avoids depending on recursive
orchestration support.

## Model and tool settings

Model availability and supported reasoning levels vary by account, client, and
time. Inheriting the parent is the portable default. Pin a model or dedicated
tool surface only for a demonstrated capability, latency, cost, or isolation
requirement.

MCP credentials must come from environment variables or an authorised
authentication flow, never from a committed agent file. Skill paths can be
machine-specific and should not be embedded in this shared catalogue.

## Primary references

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Configuration basics](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Models](https://learn.chatgpt.com/docs/models)
- [`openai/codex` feature definitions](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/features/src/lib.rs)
