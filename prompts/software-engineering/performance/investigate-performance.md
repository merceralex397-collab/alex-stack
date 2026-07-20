# Investigate Performance

Use this to diagnose slow, resource-heavy, or poorly scaling behavior.

## Prompt

Investigate this performance problem in `[system or repository]`:

`[problem description]`

Expected target: `[latency, throughput, memory, CPU, cost, or other goal]`

Observed measurements: `[data and conditions]`

Workload and environment: `[traffic, dataset, hardware, versions]`

Recent changes: `[details]`

Authorization: `[analysis only or optimization authorized]`

Define a reproducible baseline before optimizing. Identify likely bottlenecks,
then use measurements or profiling to test them. Separate client, network,
application, dependency, and storage costs where relevant. If changes are
authorized, prefer the smallest measured improvement and check for correctness
or resource trade-offs. Report before-and-after evidence and limitations.
