# Performance Engineering

This is a core development team from the source workflow.

Primary A-level artifact: a performance pack with reproducible baselines, profiles, benchmarks, bottlenecks, improvements, regressions, capacity limits, and cost-performance trade-offs.

## Topology

- A: [Performance Manager](./performance-manager.toml) - `performance-manager`
  - B: [Measurement Lead](./performance-measurement-lead.toml) - `performance-measurement-lead`
    - C: [Profiling Specialist](./performance-profiling-specialist.toml) - `performance-profiling-specialist`
    - C: [Benchmark Designer](./performance-benchmark-designer.toml) - `performance-benchmark-designer`
    - C: [Load Test Developer](./performance-load-test-developer.toml) - `performance-load-test-developer`
    - C: [Baseline Analyst](./performance-baseline-analyst.toml) - `performance-baseline-analyst`
  - B: [Application Performance Lead](./performance-application-performance-lead.toml) - `performance-application-performance-lead`
    - C: [CPU Optimisation Specialist](./performance-cpu-optimisation-specialist.toml) - `performance-cpu-optimisation-specialist`
    - C: [Memory Optimisation Specialist](./performance-memory-optimisation-specialist.toml) - `performance-memory-optimisation-specialist`
    - C: [Concurrency Specialist](./performance-concurrency-specialist.toml) - `performance-concurrency-specialist`
    - C: [Algorithmic Complexity Reviewer](./performance-algorithmic-complexity-reviewer.toml) - `performance-algorithmic-complexity-reviewer`
  - B: [Data and Network Performance Lead](./performance-data-and-network-performance-lead.toml) - `performance-data-and-network-performance-lead`
    - C: [Database Query Optimiser](./performance-database-query-optimiser.toml) - `performance-database-query-optimiser`
    - C: [Cache Specialist](./performance-cache-specialist.toml) - `performance-cache-specialist`
    - C: [Network Latency Specialist](./performance-network-latency-specialist.toml) - `performance-network-latency-specialist`
    - C: [Serialization Specialist](./performance-serialization-specialist.toml) - `performance-serialization-specialist`
  - B: [Capacity and Scalability Lead](./performance-capacity-and-scalability-lead.toml) - `performance-capacity-and-scalability-lead`
    - C: [Capacity Planner](./performance-capacity-planner.toml) - `performance-capacity-planner`
    - C: [Horizontal Scaling Specialist](./performance-horizontal-scaling-specialist.toml) - `performance-horizontal-scaling-specialist`
    - C: [Bottleneck Analyst](./performance-bottleneck-analyst.toml) - `performance-bottleneck-analyst`
    - C: [Cost-Performance Analyst](./performance-cost-performance-analyst.toml) - `performance-cost-performance-analyst`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
