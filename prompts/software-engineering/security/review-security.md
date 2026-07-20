# Review Software Security

Use this to assess a change or design for realistic security risks.

## Prompt

Perform a security review of `[feature, design, code, or system]`.

Assets to protect: `[data, capabilities, availability, or reputation]`

Actors and trust boundaries: `[users, services, administrators, third parties]`

Entry points and data flows: `[interfaces]`

Environment and constraints: `[deployment context]`

Relevant code or design: `[files, links, or pasted material]`

Identify plausible abuse cases across authentication, authorization, input
handling, secrets, data exposure, dependency risk, logging, and availability as
applicable. For each finding, describe prerequisites, exploit path, impact,
evidence, and a proportionate mitigation. Rank risks by likelihood and impact.
Do not claim a vulnerability without supporting evidence, and distinguish code
findings from design concerns that still need validation.
