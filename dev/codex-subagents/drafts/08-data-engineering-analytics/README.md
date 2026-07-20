# Data Engineering and Analytics

This is a core development team from the source workflow.

Primary A-level artifact: a data delivery pack covering sources, contracts, ingestion, transformation, quality, storage, models, lineage, metrics, reports, and validation.

## Topology

- A: [Data Engineering Manager](./data-engineering-manager.toml) - `data-engineering-manager`
  - B: [Data Acquisition Lead](./data-engineering-data-acquisition-lead.toml) - `data-engineering-data-acquisition-lead`
    - C: [Source Connector Developer](./data-engineering-source-connector-developer.toml) - `data-engineering-source-connector-developer`
    - C: [Ingestion Pipeline Developer](./data-engineering-ingestion-pipeline-developer.toml) - `data-engineering-ingestion-pipeline-developer`
    - C: [Streaming Data Developer](./data-engineering-streaming-data-developer.toml) - `data-engineering-streaming-data-developer`
    - C: [Data Contract Specialist](./data-engineering-data-contract-specialist.toml) - `data-engineering-data-contract-specialist`
  - B: [Transformation Lead](./data-engineering-transformation-lead.toml) - `data-engineering-transformation-lead`
    - C: [ETL/ELT Developer](./data-engineering-etl-elt-developer.toml) - `data-engineering-etl-elt-developer`
    - C: [Data Cleaning Specialist](./data-engineering-data-cleaning-specialist.toml) - `data-engineering-data-cleaning-specialist`
    - C: [Schema Evolution Specialist](./data-engineering-schema-evolution-specialist.toml) - `data-engineering-schema-evolution-specialist`
    - C: [Data Quality Engineer](./data-engineering-data-quality-engineer.toml) - `data-engineering-data-quality-engineer`
  - B: [Storage and Modelling Lead](./data-engineering-storage-and-modelling-lead.toml) - `data-engineering-storage-and-modelling-lead`
    - C: [Warehouse Designer](./data-engineering-warehouse-designer.toml) - `data-engineering-warehouse-designer`
    - C: [Lakehouse Designer](./data-engineering-lakehouse-designer.toml) - `data-engineering-lakehouse-designer`
    - C: [Analytics Model Developer](./data-engineering-analytics-model-developer.toml) - `data-engineering-analytics-model-developer`
    - C: [Metadata and Lineage Specialist](./data-engineering-metadata-and-lineage-specialist.toml) - `data-engineering-metadata-and-lineage-specialist`
  - B: [Analytics Delivery Lead](./data-engineering-analytics-delivery-lead.toml) - `data-engineering-analytics-delivery-lead`
    - C: [Metrics Developer](./data-engineering-metrics-developer.toml) - `data-engineering-metrics-developer`
    - C: [Dashboard Developer](./data-engineering-dashboard-developer.toml) - `data-engineering-dashboard-developer`
    - C: [Reporting Developer](./data-engineering-reporting-developer.toml) - `data-engineering-reporting-developer`
    - C: [Analytics Validation Specialist](./data-engineering-analytics-validation-specialist.toml) - `data-engineering-analytics-validation-specialist`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
