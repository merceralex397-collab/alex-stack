# Codex subagent catalogue

This folder contains a small, reviewable catalogue of custom Codex subagents.
It is organised by how broadly an agent can be reused, not as a simulated
software organisation.

- [`general-agents/`](general-agents/README.md) contains reusable ways of
  working such as exploration, planning, implementation, debugging, review,
  testing, and documentation.
- [`specific-agents/`](specific-agents/README.md) contains narrow roles whose
  domain changes the method, evidence standard, or safety boundary.

The catalogue is deliberately flat. The root Codex agent selects a bounded set
of peers, owns any parallelism, and consolidates their results. Catalogue
agents do not manage other agents or encode a fixed workflow.

## Choosing an agent

Start with a general agent. Choose a specific agent only when its specialist
checks materially change the work.

Examples:

- Map an unfamiliar repository with `repository-explorer`.
- Diagnose an unexplained failure with `debug-investigator`; use
  `implementation-worker` later if a fix is authorised.
- Review an ordinary code change with `code-reviewer`; use
  `security-reviewer` when trust boundaries, permissions, secrets, or abuse
  cases are the primary concern.
- Build ordinary application behaviour with `implementation-worker`; use
  `mcp-integration-specialist` when MCP transport and protocol behaviour are
  central to the task.
- Run ordinary regression checks with `test-engineer`; use
  `ai-evaluation-specialist` when datasets, model or prompt versions, leakage,
  metrics, cost, or evaluation independence determine whether the result is
  valid.

Do not invoke a general and specific agent for the same responsibility merely
to create more activity. Use both only when their outputs are independent, for
example an implementation followed by a separate security review.

## Activation

Files in this repository are not discovered automatically. Review and copy
only the agents needed for a workflow:

```text
Project:  .codex/agents/<agent-name>.toml
Personal: ~/.codex/agents/<agent-name>.toml
```

Keep the filename unchanged so it continues to match the TOML `name`. Project
configuration is loaded only for trusted projects.

Copying a new catalogue file does not remove older custom agents already
installed in either location. Retire those separately after reviewing the
active configuration.

## Agent contract

Every catalogue agent is a standalone TOML file with:

- `name`
- `description`
- `developer_instructions`
- optional `sandbox_mode = "read-only"`

Read-only agents pin their conservative default. An agent that may edit omits
the sandbox setting, inherits the parent session boundary, and still requires
explicit edit authority with non-overlapping file ownership.

The initial catalogue intentionally does not pin models, reasoning effort,
skills, MCP servers, or other workstation-specific configuration. See the
dated [runtime reference](references/codex-subagent-runtime.md) for the format
and inheritance notes behind this choice.

## Catalogue

### General agents

| Agent | Default | Use |
| --- | --- | --- |
| [`repository-explorer`](general-agents/repository-explorer.toml) | Read-only | Map repository structure and evidence. |
| [`external-researcher`](general-agents/external-researcher.toml) | Read-only | Research current primary sources. |
| [`requirements-analyst`](general-agents/requirements-analyst.toml) | Read-only | Resolve intent, scope, and acceptance. |
| [`solution-planner`](general-agents/solution-planner.toml) | Read-only | Produce a decision-complete implementation plan. |
| [`implementation-worker`](general-agents/implementation-worker.toml) | Inherit parent | Make a bounded, authorised change. |
| [`debug-investigator`](general-agents/debug-investigator.toml) | Read-only | Isolate root cause without fixing it. |
| [`code-reviewer`](general-agents/code-reviewer.toml) | Read-only | Report evidence-backed code findings. |
| [`test-engineer`](general-agents/test-engineer.toml) | Inherit parent | Design, add, and run tests. |
| [`documentation-writer`](general-agents/documentation-writer.toml) | Inherit parent | Update verified documentation. |

### Specific agents

| Agent | Default | Distinctive concern |
| --- | --- | --- |
| [`security-reviewer`](specific-agents/security-reviewer.toml) | Read-only | Trust, permissions, secrets, and abuse cases. |
| [`accessibility-reviewer`](specific-agents/accessibility-reviewer.toml) | Read-only | Inclusive interaction and assistive technology. |
| [`performance-profiler`](specific-agents/performance-profiler.toml) | Read-only | Reproducible baselines and measurement. |
| [`data-migration-reviewer`](specific-agents/data-migration-reviewer.toml) | Read-only | Integrity, compatibility, reconciliation, and recovery. |
| [`ai-evaluation-specialist`](specific-agents/ai-evaluation-specialist.toml) | Inherit parent | Valid model and agent evaluation evidence. |
| [`mcp-integration-specialist`](specific-agents/mcp-integration-specialist.toml) | Inherit parent | MCP lifecycle, transport, capabilities, and hosts. |

## Migration from the generated catalogue

The former role hierarchy has no compatibility layer:

- Coordination roles are removed; the root Codex agent already owns routing
  and synthesis.
- Repository-mapping roles become `repository-explorer`.
- Requirements and planning roles become `requirements-analyst` or
  `solution-planner`.
- General developer roles become `implementation-worker`.
- Investigation roles become `debug-investigator`.
- General review roles become `code-reviewer`.
- Test and documentation roles become `test-engineer` and
  `documentation-writer`.
- Domain roles survive only where one of the specific agents has a genuinely
  different playbook.

Git history preserves the generated experiment. Keeping aliases in the live
catalogue would preserve the ambiguity this redesign removes.

## Adding an agent

A proposed agent belongs in `specific-agents/` only if all of the following are
true:

1. Its trigger can be distinguished from the general catalogue.
2. Its working method contains checks absent from the nearest general agent.
3. Its evidence, tool, or safety requirements materially affect completion.
4. A selection fixture demonstrates both the positive trigger and a nearby
   case where it should not be selected.

Otherwise improve an existing general agent instead.

Start from the
[`general-agent-template.toml`](template/general-agent-template.toml) or
[`specific-agent-template.toml`](template/specific-agent-template.toml). Keep
prompts concise and grounded in observable behaviour.

## Validation

Run:

```powershell
python codex-subagents/scripts/validate-agents.py
python -m unittest discover -s codex-subagents/tests -p "test_*.py"
```

The validator checks TOML shape, names, prompt contracts, permissions,
catalogue indexes, local links, selection coverage, and the absence of the old
reporting hierarchy. Selection cases are expectations for human or future
model-based evaluation; the validator checks their integrity but does not
pretend to score model judgement.
