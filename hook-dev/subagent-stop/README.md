# SubagentStop hook

`SubagentStop` runs when a delegated subagent is ready to stop. It can inspect the subagent's latest answer and request one more focused pass before control returns to the parent flow.

## Matchers

The hook group's `matcher` is a regular expression applied to `agent_type`.

Examples:

- `^reviewer$` applies only to a reviewer profile.
- `reviewer|tester` applies to either profile.
- Omitting `matcher`, or using `*` or an empty string, applies to all subagent types.

Agent type values depend on the subagent profiles in use. Log or inspect event metadata before assuming a profile name.

## Good uses

- Require a review agent to include exact findings or explicitly say none were found.
- Ask a testing agent to report commands, exit codes, and failures.
- Verify that a required artifact exists before the subagent finishes.
- Capture identifiers and completion metadata for local observability.
- Request one bounded follow-up pass when the latest answer is incomplete.

Use this as a quality gate, not as a way to keep a subagent working indefinitely.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Parent Codex session identifier |
| `transcript_path` | string or null | Parent session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `SubagentStop` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `turn_id` | string | Active parent turn identifier |
| `agent_id` | string | Subagent identifier |
| `agent_type` | string | Subagent type or profile |
| `agent_transcript_path` | string or null | Subagent transcript path, when available |
| `stop_hook_active` | boolean | Whether this subagent was already continued by a stop hook |
| `last_assistant_message` | string or null | Latest subagent answer, when available |

Treat transcript paths as convenience pointers, not stable data schemas.

## Output behavior

When the handler exits with code `0`, `stdout` must contain valid JSON. Plain text is invalid for this event.

Return an empty object to allow the subagent to stop:

```json
{}
```

Request another subagent pass with:

```json
{
  "decision": "block",
  "reason": "Run one more focused pass and include the exact verification command."
}
```

Exit code `2` with the continuation reason on `stderr` has the same continuation purpose.

The common fields `systemMessage`, `continue`, and `stopReason` are supported. If any matching `SubagentStop` hook returns `continue: false`, that takes precedence over continuation decisions from other matching hooks.

Always inspect `stop_hook_active` before requesting another pass. This is the primary loop guard.

## Configuration example

```json
{
  "description": "Require reviewer subagents to report verification evidence.",
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "^reviewer$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/subagent-stop/subagent_stop.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/subagent-stop/subagent_stop.py')\"",
            "timeout": 20,
            "statusMessage": "Checking subagent result"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This example requests at most one follow-up when a reviewer omits a verification section:

```python
import json
import sys

event = json.load(sys.stdin)
message = event.get("last_assistant_message") or ""
already_continued = event.get("stop_hook_active", False)

if not already_continued and "verification" not in message.lower():
    print(json.dumps({
        "decision": "block",
        "reason": (
            "Add a Verification section with the commands run and "
            "their results, then finish."
        ),
    }))
else:
    print("{}")
```

The follow-up reason becomes model-visible continuation context. Keep it narrow and actionable.

## Operational notes

- A successful handler must emit JSON, even when it has no decision.
- Continuation prompts are limited to roughly 2,500 model-visible tokens.
- Several matching handlers can run concurrently.
- One hook cannot stop another matching handler from starting.
- Commands run with the parent session's `cwd`.
- Review new or changed non-managed hooks with `/hooks`.

See the [official `SubagentStop` documentation](https://learn.chatgpt.com/docs/hooks#subagentstop).
