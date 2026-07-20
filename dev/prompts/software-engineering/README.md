# Software Engineering Prompts

Prompts for work across the software-development lifecycle. Start with the
activity that matches the current task rather than automatically running every
stage.

## Areas

- `requirements` — define the problem, users, scope, and acceptance criteria.
- `planning` — inspect a codebase and plan a bounded implementation.
- `architecture` — design systems and record important technical decisions.
- `implementation` — make a feature change or improve existing code.
- `debugging` — establish a defect's cause before fixing it.
- `testing` — choose and implement meaningful quality checks.
- `code-review` — find consequential defects in changes.
- `documentation` — explain how software is used, operated, or continued.
- `security` — assess trust boundaries, abuse cases, and mitigations.
- `performance` — measure, explain, and improve slow or costly behavior.
- `maintenance` — make technical debt visible and actionable.
- `delivery-and-operations` — prepare releases and manage incidents.

## Working safely

When using these prompts with an agent that can edit files, explicitly state
whether the task is **analysis only**, **plan only**, or **implementation
authorized**. Provide the repository path, relevant local instructions, and the
validation commands when known. Keep credentials and private data out of the
prompt.
