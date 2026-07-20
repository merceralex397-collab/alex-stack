# AI Agent and Multi-Agent Development

This is a core development team from the source workflow.

Primary A-level artifact: an agent-system delivery pack covering roles, delegation, state, termination, tools, permissions, memory, provenance, evaluation, deadlock prevention, and safety.

## Topology

- A: [Agentic Systems Manager](./agentic-systems-manager.toml) - `agentic-systems-manager`
  - B: [Agent Architecture Lead](./agentic-systems-agent-architecture-lead.toml) - `agentic-systems-agent-architecture-lead`
    - C: [Role and Responsibility Designer](./agentic-systems-role-and-responsibility-designer.toml) - `agentic-systems-role-and-responsibility-designer`
    - C: [Delegation Designer](./agentic-systems-delegation-designer.toml) - `agentic-systems-delegation-designer`
    - C: [State Machine Designer](./agentic-systems-state-machine-designer.toml) - `agentic-systems-state-machine-designer`
    - C: [Termination and Escalation Designer](./agentic-systems-termination-and-escalation-designer.toml) - `agentic-systems-termination-and-escalation-designer`
  - B: [Tooling Lead](./agentic-systems-tooling-lead.toml) - `agentic-systems-tooling-lead`
    - C: [MCP Tool Developer](./agentic-systems-mcp-tool-developer.toml) - `agentic-systems-mcp-tool-developer`
    - C: [Agent Skill Developer](./agentic-systems-agent-skill-developer.toml) - `agentic-systems-agent-skill-developer`
    - C: [Tool Permission Specialist](./agentic-systems-tool-permission-specialist.toml) - `agentic-systems-tool-permission-specialist`
    - C: [Tool Error-Recovery Specialist](./agentic-systems-tool-error-recovery-specialist.toml) - `agentic-systems-tool-error-recovery-specialist`
  - B: [Context and Memory Lead](./agentic-systems-context-and-memory-lead.toml) - `agentic-systems-context-and-memory-lead`
    - C: [Working Memory Designer](./agentic-systems-working-memory-designer.toml) - `agentic-systems-working-memory-designer`
    - C: [Long-Term Memory Designer](./agentic-systems-long-term-memory-designer.toml) - `agentic-systems-long-term-memory-designer`
    - C: [Context Compression Specialist](./agentic-systems-context-compression-specialist.toml) - `agentic-systems-context-compression-specialist`
    - C: [Provenance Specialist](./agentic-systems-provenance-specialist.toml) - `agentic-systems-provenance-specialist`
  - B: [Agent Evaluation Lead](./agentic-systems-agent-evaluation-lead.toml) - `agentic-systems-agent-evaluation-lead`
    - C: [Task Completion Evaluator](./agentic-systems-task-completion-evaluator.toml) - `agentic-systems-task-completion-evaluator`
    - C: [Delegation Quality Evaluator](./agentic-systems-delegation-quality-evaluator.toml) - `agentic-systems-delegation-quality-evaluator`
    - C: [Tool-Use Evaluator](./agentic-systems-tool-use-evaluator.toml) - `agentic-systems-tool-use-evaluator`
    - C: [Loop and Deadlock Tester](./agentic-systems-loop-and-deadlock-tester.toml) - `agentic-systems-loop-and-deadlock-tester`
    - C: [Safety and Permission Tester](./agentic-systems-safety-and-permission-tester.toml) - `agentic-systems-safety-and-permission-tester`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
