# Selection cases

[`selection-cases.json`](selection-cases.json) records expected routing
boundaries for the catalogue.

Each case contains:

- a user-style prompt;
- the single best catalogue agent for the primary responsibility;
- nearby agents that should not be selected for that responsibility;
- a short rationale.

These fixtures are not a keyword router and the validator does not claim to
measure model judgement. They provide reviewable acceptance examples and a
stable input set for a future live selection evaluation.

Every catalogue agent must be the expected result of at least one case. Add a
near-miss case whenever a new role could overlap an existing one.
