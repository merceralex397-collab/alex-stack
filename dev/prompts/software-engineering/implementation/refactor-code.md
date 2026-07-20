# Refactor Code

Use this to improve internal structure without intentionally changing behavior.

## Prompt

Refactor `[code, module, or subsystem]`.

Motivation: `[maintainability problem or desired improvement]`

Behavior that must remain unchanged: `[contracts and invariants]`

Allowed scope: `[boundaries]`

Constraints: `[compatibility, performance, dependencies, or style]`

Validation: `[existing tests and checks]`

Inspect callers and tests before editing. State the invariants, identify the
smallest useful refactor, and avoid mixing unrelated feature changes into the
work. Preserve public contracts unless explicitly authorized. Add or improve
characterization tests where behavior is not adequately protected, then run the
relevant checks and summarize any residual risk.
