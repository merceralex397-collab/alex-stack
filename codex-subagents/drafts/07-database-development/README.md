# Database Development

This is a core development team from the source workflow.

Primary A-level artifact: a database delivery pack covering models, constraints, queries, indexes, transactions, migrations, integrity, rollback, recovery, capacity, and security.

## Topology

- A: [Database Manager](./database-manager.toml) - `database-manager`
  - B: [Data Modelling Lead](./database-data-modelling-lead.toml) - `database-data-modelling-lead`
    - C: [Relational Schema Designer](./database-relational-schema-designer.toml) - `database-relational-schema-designer`
    - C: [Document Data Designer](./database-document-data-designer.toml) - `database-document-data-designer`
    - C: [Domain Normalisation Specialist](./database-domain-normalisation-specialist.toml) - `database-domain-normalisation-specialist`
    - C: [Data Constraint Specialist](./database-data-constraint-specialist.toml) - `database-data-constraint-specialist`
  - B: [Query and Access Lead](./database-query-and-access-lead.toml) - `database-query-and-access-lead`
    - C: [Query Developer](./database-query-developer.toml) - `database-query-developer`
    - C: [Indexing Specialist](./database-indexing-specialist.toml) - `database-indexing-specialist`
    - C: [ORM Specialist](./database-orm-specialist.toml) - `database-orm-specialist`
    - C: [Transaction Specialist](./database-transaction-specialist.toml) - `database-transaction-specialist`
  - B: [Migration and Integrity Lead](./database-migration-and-integrity-lead.toml) - `database-migration-and-integrity-lead`
    - C: [Migration Developer](./database-migration-developer.toml) - `database-migration-developer`
    - C: [Data Validation Specialist](./database-data-validation-specialist.toml) - `database-data-validation-specialist`
    - C: [Backfill Developer](./database-backfill-developer.toml) - `database-backfill-developer`
    - C: [Rollback Specialist](./database-rollback-specialist.toml) - `database-rollback-specialist`
  - B: [Database Operations Lead](./database-operations-lead.toml) - `database-operations-lead`
    - C: [Backup and Recovery Specialist](./database-backup-and-recovery-specialist.toml) - `database-backup-and-recovery-specialist`
    - C: [Replication Specialist](./database-replication-specialist.toml) - `database-replication-specialist`
    - C: [Capacity Planner](./database-capacity-planner.toml) - `database-capacity-planner`
    - C: [Database Security Specialist](./database-security-specialist.toml) - `database-security-specialist`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
