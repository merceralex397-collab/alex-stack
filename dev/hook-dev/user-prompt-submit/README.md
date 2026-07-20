# UserPromptSubmit hook

`UserPromptSubmit` runs after the user submits a prompt but before Codex sends it to the model. It can add developer context, block the submission, or observe safe metadata about the request.

The event runs for every submitted prompt. `matcher` is not supported and is ignored if configured.

## Good uses

- Detect likely API keys, private keys, or regulated identifiers before model submission.
- Add dynamic repository context relevant to the incoming task.
- Require a local workflow precondition, such as selecting an active ticket.
- Record privacy-preserving metrics such as prompt length or task category.
- Block a prompt and explain how the user can resubmit it safely.

Avoid logging raw prompt text unless the user and organization have explicitly chosen that data policy. A hook intended to prevent secret disclosure should not leak the same secret into its own logs or output.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `UserPromptSubmit` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `turn_id` | string | Active turn identifier |
| `prompt` | string | Prompt that is about to be sent |

## Output behavior

### Add developer context

Plain text on `stdout` becomes extra developer context. Structured output can do the same:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "The active ticket is ALEX-142; preserve its acceptance criteria."
  }
}
```

This adds context around the prompt; it does not rewrite the user's prompt.

### Block submission

```json
{
  "decision": "block",
  "reason": "The prompt appears to contain a private key. Remove it and resubmit."
}
```

Exit code `2` with the reason written to `stderr` also blocks submission.

The common JSON fields `continue`, `stopReason`, and `systemMessage` are supported. Use the explicit `decision: "block"` shape when the intent is to reject the prompt. `suppressOutput` is parsed but is not implemented.

Exit code `0` with no output submits the prompt unchanged and adds no context.

## Configuration example

Because matchers are ignored, omit `matcher`:

```json
{
  "description": "Scan every user prompt before model submission.",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/user-prompt-submit/user_prompt_submit.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/user-prompt-submit/user_prompt_submit.py')\"",
            "timeout": 10,
            "statusMessage": "Checking prompt safety"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This example blocks two obvious secret formats without printing the matching value:

```python
import json
import re
import sys

event = json.load(sys.stdin)
prompt = event["prompt"]

secret_patterns = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)

if any(pattern.search(prompt) for pattern in secret_patterns):
    print(json.dumps({
        "decision": "block",
        "reason": (
            "The prompt appears to contain a secret. "
            "Remove or redact it, rotate it if exposed, and resubmit."
        ),
    }))
```

Production secret detection should cover the formats your organization actually uses and should be tested for false positives. Do not include the matched secret in `reason`, `systemMessage`, telemetry, or exception output.

## Operational notes

- The hook is in the prompt-submission path, so keep it fast.
- Matching command hooks from active sources launch concurrently.
- Additional context is limited to roughly 2,500 model-visible tokens.
- Commands run with the session `cwd`.
- Only `type: "command"` handlers run currently.
- Project hooks and changed hook definitions must be trusted through `/hooks`.

See the [official `UserPromptSubmit` documentation](https://learn.chatgpt.com/docs/hooks#userpromptsubmit).
