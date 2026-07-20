# AGENTS.md

## Repository purpose

This is Alex's personal workspace for exploring AI agent concepts.

The repository may contain anything that benefits from iteration: experiments,
prototypes, prompts, agent definitions, skills, tools, hooks, workflows,
evaluations, notes, and supporting code. Ideas may be incomplete, temporary, or
deliberately exploratory.

## How to work here

- Treat each top-level folder as a potentially independent project. Inspect its
  files and local instructions before assuming a shared language, toolchain, or
  architecture.
- Prefer small, reversible changes that make the next iteration easier.
- Preserve useful experiments and the reasoning behind non-obvious decisions.
  Do not replace exploratory work with production complexity unless the task
  calls for it.
- Make reasonable assumptions and test them quickly. Clearly label mock data,
  placeholders, unverified claims, and unfinished paths.
- Reuse existing patterns when they fit, but feel free to propose a better
  approach when an experiment is testing a different idea.
- Keep credentials, tokens, personal data, and other secrets out of the
  repository.

## Before changing files

1. Read the relevant folder's documentation and any more specific
   `AGENTS.md`.
2. Inspect the current implementation and available validation commands.
3. Keep the change within the requested experiment or concept.
4. Avoid modifying unrelated work; this workspace may contain several active
   lines of exploration at once.

## Validation

Use the narrowest meaningful checks available in the affected folder. For
example, run its tests, validator, formatter, type checker, or a focused manual
exercise. If no automated check exists, inspect the changed artifact directly
and explain what was verified and what remains uncertain.

## Documentation

Update nearby documentation when a change affects how an experiment is used,
understood, or continued. Favor concise notes that capture the current idea,
how to try it, what was learned, and the most useful next iteration.
