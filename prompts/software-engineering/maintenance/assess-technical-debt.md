# Assess Technical Debt

Use this to decide which maintenance problems deserve attention.

## Prompt

Assess technical debt in `[repository, module, or system]`.

Business or product priorities: `[goals]`

Known pain points: `[incidents, slow delivery, fragile areas, or complaints]`

Constraints: `[capacity, deadlines, compatibility, or ownership]`

Available evidence: `[code, metrics, issues, or team observations]`

Identify concrete debt items and the recurring cost or risk each creates.
Distinguish cosmetic inconsistency from debt that impedes change, reliability,
security, performance, or operations. Rank items by impact, urgency, effort,
dependencies, and confidence. Recommend a small set to address now, with
incremental remediation and proof that the work improved the stated problem.
