# General agents

General agents describe reusable ways of working. They should remain useful
across languages, frameworks, and application domains.

| Agent | Default access | Select when |
| --- | --- | --- |
| [`repository-explorer`](repository-explorer.toml) | Read-only | Current repository structure and change surface must be mapped. |
| [`external-researcher`](external-researcher.toml) | Read-only | Current external facts or primary-source guidance are required. |
| [`requirements-analyst`](requirements-analyst.toml) | Read-only | Intent, scope, constraints, or acceptance remain unclear. |
| [`solution-planner`](solution-planner.toml) | Read-only | The objective is stable and needs a decision-complete implementation plan. |
| [`implementation-worker`](implementation-worker.toml) | Inherit parent | A bounded change is authorised and has clear ownership. |
| [`debug-investigator`](debug-investigator.toml) | Read-only | A symptom needs causal diagnosis before a fix is attempted. |
| [`code-reviewer`](code-reviewer.toml) | Read-only | Existing code or a change needs independent, findings-first review. |
| [`test-engineer`](test-engineer.toml) | Inherit parent | Test design, test implementation, or execution is the main task. |
| [`documentation-writer`](documentation-writer.toml) | Inherit parent | Verified behaviour must be reflected in bounded documentation. |

## Selection boundaries

- Use `requirements-analyst` before `solution-planner` when unresolved product
  choices would materially change the plan.
- Use `debug-investigator` before `implementation-worker` when the cause is not
  yet supported by evidence.
- Use `code-reviewer` to assess an existing change and `test-engineer` to own
  test design or test files.
- Use `external-researcher` for external facts and `repository-explorer` for
  local codebase truth.

The root Codex agent owns delegation and synthesis. Every agent in this folder
returns its bounded result directly and does not spawn other agents.
