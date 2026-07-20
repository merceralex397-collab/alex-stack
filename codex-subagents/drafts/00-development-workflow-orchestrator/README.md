# Development Workflow Orchestrator

- Root: [Development Workflow Orchestrator](./development-workflow-orchestrator.toml) - `development-workflow-orchestrator`

This routing role selects the smallest sufficient set of A-level teams, enforces dependency order and stage gates, and consolidates their canonical outputs. It is deliberately read-only.

The orchestrator prompt includes the full manager catalog and a flattening fallback for runtimes that do not support the A-to-B-to-C nesting depth.
