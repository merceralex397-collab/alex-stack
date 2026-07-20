# Work-ready Codex subagent drafts

This directory implements the complete A/B/C subagent organization from the referenced **Subagent Workflow Design** conversation. It is a reviewable role library, not an automatically loaded agent directory.

## Design

- Root orchestrator routes work to the smallest sufficient set of A-level teams.
- A managers own decisions and consolidate one team artifact.
- B leads own a stage, delegate bounded work, and fan specialist results back into one stage artifact.
- C specialists investigate, design, implement, test, or review one bounded concern and do not delegate further.
- All agent names are globally unique and match their filenames.
- Managers, leads, and analytical/review specialists default to `read-only`.
- Implementation-capable specialists inherit the parent model, reasoning effort, sandbox, tools, and approvals. Their prompts still require explicit edit authority and exclusive file ownership.
- No model is pinned. This lets Codex choose from the models actually available to the parent session and avoids stale catalog assumptions.
- Every prompt defines mission, authority, boundaries, method, evidence, return contract, and completion criteria.

## Inventory

| # | Team | Type | A | B | C |
| ---: | --- | --- | ---: | ---: | ---: |
| 01 | [Product and Requirements](./01-product-requirements/README.md) | Core | 1 | 4 | 15 |
| 02 | [Planning](./02-planning/README.md) | Core | 1 | 4 | 16 |
| 03 | [System Architecture](./03-system-architecture/README.md) | Core | 1 | 4 | 16 |
| 04 | [UX and UI Design](./04-ux-ui-design/README.md) | Core | 1 | 4 | 16 |
| 05 | [Frontend Development](./05-frontend-development/README.md) | Core | 1 | 4 | 16 |
| 06 | [Backend and API Development](./06-backend-api-development/README.md) | Core | 1 | 4 | 16 |
| 07 | [Database Development](./07-database-development/README.md) | Core | 1 | 4 | 16 |
| 08 | [Data Engineering and Analytics](./08-data-engineering-analytics/README.md) | Core | 1 | 4 | 16 |
| 09 | [AI and Machine Learning](./09-ai-machine-learning/README.md) | Core | 1 | 4 | 16 |
| 10 | [LLM and RAG Development](./10-llm-rag-development/README.md) | Core | 1 | 4 | 17 |
| 11 | [AI Agent and Multi-Agent Development](./11-agentic-multi-agent-systems/README.md) | Core | 1 | 4 | 17 |
| 12 | [MCP and External Integrations](./12-mcp-external-integrations/README.md) | Core | 1 | 4 | 16 |
| 13 | [Mobile Development](./13-mobile-development/README.md) | Core | 1 | 4 | 16 |
| 14 | [Desktop Development](./14-desktop-development/README.md) | Core | 1 | 4 | 16 |
| 15 | [Security Engineering](./15-security-engineering/README.md) | Core | 1 | 4 | 16 |
| 16 | [Testing and Quality Assurance](./16-testing-quality-assurance/README.md) | Core | 1 | 4 | 16 |
| 17 | [Performance Engineering](./17-performance-engineering/README.md) | Core | 1 | 4 | 16 |
| 18 | [Platform, Cloud and DevOps](./18-platform-cloud-devops/README.md) | Core | 1 | 4 | 16 |
| 19 | [Release and Deployment](./19-release-deployment/README.md) | Core | 1 | 4 | 16 |
| 20 | [Observability and SRE](./20-observability-sre/README.md) | Core | 1 | 4 | 16 |
| 21 | [Incident Response](./21-incident-response/README.md) | Core | 1 | 4 | 16 |
| 22 | [Maintenance and Refactoring](./22-maintenance-refactoring/README.md) | Core | 1 | 4 | 16 |
| 23 | [Migration and Modernisation](./23-migration-modernisation/README.md) | Core | 1 | 4 | 16 |
| 24 | [Documentation and Developer Experience](./24-documentation-developer-experience/README.md) | Core | 1 | 4 | 16 |
| 25 | [Compliance, Privacy and Governance](./25-compliance-privacy-governance/README.md) | Core | 1 | 4 | 16 |
| 26 | [Code Review and Pull Requests](./26-code-review-pull-requests/README.md) | Core | 1 | 4 | 16 |
| 27 | [Bug Investigation and Resolution](./27-bug-investigation-resolution/README.md) | Core | 1 | 4 | 16 |
| 28 | [Embedded Systems and IoT](./28-embedded-systems-iot/README.md) | Optional | 1 | 4 | 12 |
| 29 | [Game Development](./29-game-development/README.md) | Optional | 1 | 4 | 12 |
| 30 | [Scientific and High-Performance Computing](./30-scientific-high-performance-computing/README.md) | Optional | 1 | 4 | 12 |

Total: **620 agent TOML files** across **30 development team folders**, plus the root orchestrator folder.

Machine-readable hierarchy and sandbox metadata are in [`manifest.json`](./manifest.json).

## Activation

Files under `drafts/` are not discovered automatically. Review and copy only the roles needed for a workflow:

```text
Project:  .codex/agents/<agent-name>.toml
Personal: ~/.codex/agents/<agent-name>.toml
```

Use the filename unchanged so it continues to match the TOML `name`. Project-scoped configuration is loaded only for trusted projects.

The live parent sandbox and approval choices still govern spawned agents. A role-level `sandbox_mode` is a conservative default, not a permission bypass.

## Hierarchy compatibility

The full design expects root -> A -> B -> C delegation. Some Codex orchestration backends or configurations limit recursive depth. On configurations where nested delegation is unavailable, use the manifest to flatten only the necessary roles under the root while preserving the same ownership and fan-in contracts.

Do not raise concurrency or nesting limits casually. Prefer the compact route for normal work and the expanded hierarchy only when the task's size, independence, and risk justify its token and coordination cost.

## Source and prompt-engineering basis

The files follow the local [`../template/subagent-template.toml`](../template/subagent-template.toml) and current official Codex guidance:

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Best practices](https://learn.chatgpt.com/guides/best-practices)
- [Prompting](https://learn.chatgpt.com/docs/prompting)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

The generator is [`../scripts/generate-drafts.mjs`](../scripts/generate-drafts.mjs). It writes deterministically except for the `generated_at` timestamp in the manifest and refuses to target a path outside `codex-subagents/`.

Run [`../scripts/validate-drafts.py`](../scripts/validate-drafts.py) with Python 3.11 or newer to parse every TOML and check names, hierarchy, sandbox declarations, required prompt sections, counts, placeholders, and local Markdown links.
