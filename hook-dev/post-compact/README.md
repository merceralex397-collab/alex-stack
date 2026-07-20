# PostCompact hook

`PostCompact` runs after Codex has compacted the chat context. It is useful for auditing the event, validating external checkpoints, and deciding whether the turn should proceed after compaction.

Compaction has already happened when this hook runs; it cannot restore the original in-memory context or undo the compaction.

## When it runs

The event's `trigger` field is:

| `trigger` | Meaning |
| --- | --- |
| `manual` | Compaction was explicitly requested |
| `auto` | Codex initiated compaction automatically |

The hook group's `matcher` is a regular expression applied to `trigger`.

## Good uses

- Record that manual or automatic compaction completed.
- Verify that a pre-compaction checkpoint exists and is readable.
- Rotate or clean up temporary state associated with the old context.
- Emit a UI warning if external task state is now inconsistent.
- Stop the workflow after compaction when a required recovery check fails.

To add developer context after compaction, use a `SessionStart` hook with matcher `^compact$`. The documented `PostCompact` output supports common control fields, not `hookSpecificOutput.additionalContext`.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `PostCompact` |
| `model` | string | Active model slug |
| `turn_id` | string | Active turn identifier |
| `trigger` | string | `manual` or `auto` |

## Output

Plain text on `stdout` is ignored.

Exit `0` with no output to proceed normally. JSON can use the common output shape:

```json
{
  "continue": true,
  "systemMessage": "Automatic compaction completed and checkpoint validation passed."
}
```

If a matching hook returns `continue: false`, Codex stops after compacting:

```json
{
  "continue": false,
  "stopReason": "The pre-compaction checkpoint is missing.",
  "systemMessage": "Post-compaction validation failed."
}
```

`systemMessage` is a UI or event-stream warning; it is not a replacement for developer context. `suppressOutput` is parsed but is not implemented.

## Configuration example

```json
{
  "description": "Validate external task state after compaction.",
  "hooks": {
    "PostCompact": [
      {
        "matcher": "manual|auto",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/post-compact/post_compact.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/post-compact/post_compact.py')\"",
            "timeout": 20,
            "statusMessage": "Validating compacted session"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This example checks for the checkpoint created by the `PreCompact` example:

```python
import json
from pathlib import Path
import sys

event = json.load(sys.stdin)
checkpoint = Path(event["cwd"]) / ".codex" / "hook-state" / "pre-compact.json"

if not checkpoint.is_file():
    print(json.dumps({
        "continue": False,
        "stopReason": "Expected pre-compaction checkpoint was not found.",
        "systemMessage": "Compaction completed, but checkpoint validation failed.",
    }))
```

With no output, Codex continues. If the checkpoint is missing, the hook stops the flow after compaction and surfaces the reason.

## Operational notes

- Pair with `PreCompact` for before-and-after checkpoint validation.
- Pair with `SessionStart` matched on `compact` when the model needs restored context.
- Commands run with the session `cwd`.
- Matching handlers launch concurrently.
- Keep recovery checks quick and deterministic.
- Review new or changed non-managed hooks with `/hooks`.

See the [official `PostCompact` documentation](https://learn.chatgpt.com/docs/hooks#postcompact).
