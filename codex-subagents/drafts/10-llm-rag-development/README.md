# LLM and RAG Development

This is a core development team from the source workflow.

Primary A-level artifact: an LLM system delivery pack covering retrieval, context, prompts, structured outputs, evaluation, routing, cost, caching, traces, and operational safeguards.

## Topology

- A: [LLM Systems Manager](./llm-rag-llm-systems-manager.toml) - `llm-rag-llm-systems-manager`
  - B: [Knowledge and Retrieval Lead](./llm-rag-knowledge-and-retrieval-lead.toml) - `llm-rag-knowledge-and-retrieval-lead`
    - C: [Document Processing Specialist](./llm-rag-document-processing-specialist.toml) - `llm-rag-document-processing-specialist`
    - C: [Chunking Specialist](./llm-rag-chunking-specialist.toml) - `llm-rag-chunking-specialist`
    - C: [Embedding Specialist](./llm-rag-embedding-specialist.toml) - `llm-rag-embedding-specialist`
    - C: [Retrieval and Reranking Specialist](./llm-rag-retrieval-and-reranking-specialist.toml) - `llm-rag-retrieval-and-reranking-specialist`
    - C: [Knowledge Graph Specialist](./llm-rag-knowledge-graph-specialist.toml) - `llm-rag-knowledge-graph-specialist`
  - B: [Prompt and Context Lead](./llm-rag-prompt-and-context-lead.toml) - `llm-rag-prompt-and-context-lead`
    - C: [System Prompt Designer](./llm-rag-system-prompt-designer.toml) - `llm-rag-system-prompt-designer`
    - C: [Context Assembly Specialist](./llm-rag-context-assembly-specialist.toml) - `llm-rag-context-assembly-specialist`
    - C: [Structured Output Specialist](./llm-rag-structured-output-specialist.toml) - `llm-rag-structured-output-specialist`
    - C: [Conversation State Specialist](./llm-rag-conversation-state-specialist.toml) - `llm-rag-conversation-state-specialist`
  - B: [LLM Evaluation Lead](./llm-rag-llm-evaluation-lead.toml) - `llm-rag-llm-evaluation-lead`
    - C: [Accuracy Evaluator](./llm-rag-accuracy-evaluator.toml) - `llm-rag-accuracy-evaluator`
    - C: [Hallucination Evaluator](./llm-rag-hallucination-evaluator.toml) - `llm-rag-hallucination-evaluator`
    - C: [Retrieval Evaluator](./llm-rag-retrieval-evaluator.toml) - `llm-rag-retrieval-evaluator`
    - C: [Adversarial Evaluator](./llm-rag-adversarial-evaluator.toml) - `llm-rag-adversarial-evaluator`
  - B: [LLM Operations Lead](./llm-rag-llm-operations-lead.toml) - `llm-rag-llm-operations-lead`
    - C: [Model Router Developer](./llm-rag-model-router-developer.toml) - `llm-rag-model-router-developer`
    - C: [Token and Cost Optimiser](./llm-rag-token-and-cost-optimiser.toml) - `llm-rag-token-and-cost-optimiser`
    - C: [Cache Developer](./llm-rag-cache-developer.toml) - `llm-rag-cache-developer`
    - C: [Trace and Monitoring Specialist](./llm-rag-trace-and-monitoring-specialist.toml) - `llm-rag-trace-and-monitoring-specialist`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
