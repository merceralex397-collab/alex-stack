# Implement a Change

Use this when an agent is authorized to modify a codebase.

## Prompt

Implement `[feature, fix, or change]` in `[repository or project]`.

Expected behavior: `[requirements or acceptance criteria]`

In scope: `[included work]`

Out of scope: `[excluded work]`

Relevant starting points: `[files, modules, or documentation]`

Constraints: `[compatibility, style, dependencies, or safety limits]`

Required validation: `[tests, type checks, linters, builds, or manual checks]`

First inspect the repository, local instructions, current implementation, and
working-tree state. Make the smallest coherent change, follow existing patterns,
preserve unrelated work, and update nearby documentation when behavior or usage
changes. Run the narrowest meaningful validation. Report changed files, results,
and remaining uncertainty.
