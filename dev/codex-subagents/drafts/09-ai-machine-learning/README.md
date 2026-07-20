# AI and Machine Learning

This is a core development team from the source workflow.

Primary A-level artifact: an AI/ML delivery pack covering dataset provenance, training, evaluation, bias and robustness, deployment, versioning, optimization, and monitoring.

## Topology

- A: [AI/ML Manager](./ai-ml-manager.toml) - `ai-ml-manager`
  - B: [Data and Dataset Lead](./ai-ml-data-and-dataset-lead.toml) - `ai-ml-data-and-dataset-lead`
    - C: [Dataset Curator](./ai-ml-dataset-curator.toml) - `ai-ml-dataset-curator`
    - C: [Labelling Specialist](./ai-ml-labelling-specialist.toml) - `ai-ml-labelling-specialist`
    - C: [Data Quality Analyst](./ai-ml-data-quality-analyst.toml) - `ai-ml-data-quality-analyst`
    - C: [Dataset Bias Analyst](./ai-ml-dataset-bias-analyst.toml) - `ai-ml-dataset-bias-analyst`
  - B: [Model Development Lead](./ai-ml-model-development-lead.toml) - `ai-ml-model-development-lead`
    - C: [Model Researcher](./ai-ml-model-researcher.toml) - `ai-ml-model-researcher`
    - C: [Training Engineer](./ai-ml-training-engineer.toml) - `ai-ml-training-engineer`
    - C: [Fine-Tuning Specialist](./ai-ml-fine-tuning-specialist.toml) - `ai-ml-fine-tuning-specialist`
    - C: [Feature Engineering Specialist](./ai-ml-feature-engineering-specialist.toml) - `ai-ml-feature-engineering-specialist`
  - B: [Evaluation Lead](./ai-ml-evaluation-lead.toml) - `ai-ml-evaluation-lead`
    - C: [Benchmark Designer](./ai-ml-benchmark-designer.toml) - `ai-ml-benchmark-designer`
    - C: [Error Analysis Specialist](./ai-ml-error-analysis-specialist.toml) - `ai-ml-error-analysis-specialist`
    - C: [Robustness Tester](./ai-ml-robustness-tester.toml) - `ai-ml-robustness-tester`
    - C: [Human Evaluation Coordinator](./ai-ml-human-evaluation-coordinator.toml) - `ai-ml-human-evaluation-coordinator`
  - B: [Model Deployment Lead](./ai-ml-model-deployment-lead.toml) - `ai-ml-model-deployment-lead`
    - C: [Inference Engineer](./ai-ml-inference-engineer.toml) - `ai-ml-inference-engineer`
    - C: [Model Optimisation Specialist](./ai-ml-model-optimisation-specialist.toml) - `ai-ml-model-optimisation-specialist`
    - C: [Model Monitoring Specialist](./ai-ml-model-monitoring-specialist.toml) - `ai-ml-model-monitoring-specialist`
    - C: [Model Versioning Specialist](./ai-ml-model-versioning-specialist.toml) - `ai-ml-model-versioning-specialist`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
