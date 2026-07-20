# Stop hook

`Stop` runs when Codex is about to finish the current turn. It is the final lifecycle gate for checking whether the turn's answer or external state meets a workspace-specific completion rule.

`matcher` is not supported for this event and is ignored if configured.

## Good uses

- Require a final answer to include verification evidence.
- Check a status file produced by tests, linting, or a release workflow.
- Ask Codex for one more bounded review pass when a concrete condition failed.
- Persist turn-completion metadata for an audit trail.
- Enforce a small, objective completion checklist.

Avoid vague gates such as "make the answer better." A continuation should name the missing evidence or failed condition so Codex can complete one focused pass.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `Stop` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `turn_id` | string | Active turn identifier |
| `stop_hook_active` | boolean | Whether this turn was already continued by `Stop` |
| `last_assistant_message` | string or null | Latest assistant message, when available |

The transcript format is not a stable hook interface. Prefer the explicit event fields or a durable status artifact owned by your workflow.

## Output behavior

When the handler exits with code `0`, `stdout` must contain valid JSON. Plain text is invalid for this event.

Return an empty object to let the turn finish:

```json
{}
```

To keep Codex working, return:

```json
{
  "decision": "block",
  "reason": "Run the targeted tests and report the command and result."
}
```

For `Stop`, `decision: "block"` does not reject the turn. Codex creates a continuation prompt that acts as a new user prompt, using `reason` as the prompt text.

Exit code `2` with the continuation reason on `stderr` also requests continuation.

The common fields `systemMessage`, `continue`, and `stopReason` are supported. If any matching `Stop` hook returns `continue: false`, it takes precedence over continuation decisions from other matching hooks.

Check `stop_hook_active` before returning another `decision: "block"` so the same rule does not create an endless continuation loop.

## Configuration example

```json
{
  "description": "Check the final answer before each turn finishes.",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/stop/stop.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/stop/stop.py')\"",
            "timeout": 30,
            "statusMessage": "Checking completion criteria"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This example asks for verification at most once:

```python
import json
import sys

event = json.load(sys.stdin)
message = event.get("last_assistant_message") or ""
already_continued = event.get("stop_hook_active", False)

has_verification = any(
    marker in message.lower()
    for marker in ("verification", "tests:", "validated")
)

if not already_continued and not has_verification:
    print(json.dumps({
        "decision": "block",
        "reason": (
            "Before finishing, run or identify the relevant verification "
            "and report the concrete result."
        ),
    }))
else:
    print("{}")
```

For stronger enforcement, inspect a machine-readable result file rather than relying on words in the assistant message.

## Design guidance

- Make the rule objective: a file exists, a command passed, or a required section is present.
- Make continuation bounded: request one specific action and honor `stop_hook_active`.
- Keep checks fast because the hook runs every time a turn is ready to finish.
- Do not run broad, destructive, or externally mutating operations from a completion check.
- Use `PostToolUse` for feedback immediately after a tool result; use `Stop` only for turn-level completion.

## Operational notes

- A successful handler must emit JSON, even when allowing the turn to finish.
- Continuation output is limited to roughly 2,500 model-visible tokens.
- Matching handlers from all active hook sources launch concurrently.
- Commands run with the session `cwd`.
- Only `type: "command"` handlers execute currently.
- Review new or changed non-managed hooks with `/hooks`.

See the [official `Stop` documentation](https://learn.chatgpt.com/docs/hooks#stop).
