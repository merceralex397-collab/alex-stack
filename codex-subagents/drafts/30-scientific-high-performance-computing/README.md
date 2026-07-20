# Scientific and High-Performance Computing

This is an optional specialist development team from the source workflow.

Primary A-level artifact: a scientific-computing pack covering numerical methods, stability, validation, parallelism, simulations, reproducibility, accuracy, performance, and resource efficiency.

## Topology

- A: [Scientific Computing Manager](./scientific-computing-manager.toml) - `scientific-computing-manager`
  - B: [Numerical Methods Lead](./scientific-computing-numerical-methods-lead.toml) - `scientific-computing-numerical-methods-lead`
    - C: [Algorithm Researcher](./scientific-computing-algorithm-researcher.toml) - `scientific-computing-algorithm-researcher`
    - C: [Numerical Stability Specialist](./scientific-computing-numerical-stability-specialist.toml) - `scientific-computing-numerical-stability-specialist`
    - C: [Validation Specialist](./scientific-computing-validation-specialist.toml) - `scientific-computing-validation-specialist`
  - B: [Parallel Computing Lead](./scientific-computing-parallel-computing-lead.toml) - `scientific-computing-parallel-computing-lead`
    - C: [CPU Parallelism Specialist](./scientific-computing-cpu-parallelism-specialist.toml) - `scientific-computing-cpu-parallelism-specialist`
    - C: [GPU Computing Specialist](./scientific-computing-gpu-computing-specialist.toml) - `scientific-computing-gpu-computing-specialist`
    - C: [Distributed Computing Specialist](./scientific-computing-distributed-computing-specialist.toml) - `scientific-computing-distributed-computing-specialist`
  - B: [Data and Simulation Lead](./scientific-computing-data-and-simulation-lead.toml) - `scientific-computing-data-and-simulation-lead`
    - C: [Simulation Developer](./scientific-computing-simulation-developer.toml) - `scientific-computing-simulation-developer`
    - C: [Scientific Data Specialist](./scientific-computing-scientific-data-specialist.toml) - `scientific-computing-scientific-data-specialist`
    - C: [Reproducibility Specialist](./scientific-computing-reproducibility-specialist.toml) - `scientific-computing-reproducibility-specialist`
  - B: [Performance Validation Lead](./scientific-computing-performance-validation-lead.toml) - `scientific-computing-performance-validation-lead`
    - C: [Benchmark Specialist](./scientific-computing-benchmark-specialist.toml) - `scientific-computing-benchmark-specialist`
    - C: [Accuracy Comparison Specialist](./scientific-computing-accuracy-comparison-specialist.toml) - `scientific-computing-accuracy-comparison-specialist`
    - C: [Resource Efficiency Specialist](./scientific-computing-resource-efficiency-specialist.toml) - `scientific-computing-resource-efficiency-specialist`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
