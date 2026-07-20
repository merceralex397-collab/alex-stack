# Specific agents

Specific agents are justified by a distinctive playbook, not merely a domain
label. Use one in place of the nearest general agent when the specialist
checks are central to success.

| Agent | Default access | Why it is specific |
| --- | --- | --- |
| [`security-reviewer`](security-reviewer.toml) | Read-only | Requires authorised scope, trust-boundary analysis, and careful exploitability claims. |
| [`accessibility-reviewer`](accessibility-reviewer.toml) | Read-only | Requires assistive-technology, keyboard, focus, semantic, and visual-state checks. |
| [`performance-profiler`](performance-profiler.toml) | Read-only | Requires controlled baselines, comparable measurements, and attribution. |
| [`data-migration-reviewer`](data-migration-reviewer.toml) | Read-only | Requires integrity, compatibility, idempotency, reconciliation, and recovery analysis. |
| [`ai-evaluation-specialist`](ai-evaluation-specialist.toml) | Inherit parent | Requires versioned datasets, probes, metrics, leakage controls, cost controls, and independent evidence. |
| [`mcp-integration-specialist`](mcp-integration-specialist.toml) | Inherit parent | Requires MCP transport, lifecycle, capability, schema, authentication, and host-specific reasoning. |

## Selection boundaries

- Use `code-reviewer` for ordinary code review; select `security-reviewer` or
  `accessibility-reviewer` when that specialist lens is the primary task.
- Use `test-engineer` for ordinary regression coverage; select
  `performance-profiler` or `ai-evaluation-specialist` when measurement or
  evaluation validity is the core concern.
- Use `solution-planner` for an ordinary schema change; select
  `data-migration-reviewer` when live data transition and recovery properties
  matter.
- Use `implementation-worker` for ordinary integrations; select
  `mcp-integration-specialist` only when MCP semantics are central.

These agents are flat peers. They do not manage one another or automatically
invoke a general agent.
