# PreCompact hook

`PreCompact` runs immediately before Codex compacts the chat context. It is the last lifecycle point for checkpointing external state or vetoing compaction.

Compaction condenses older context so a long-running task can continue. A hook should not assume it can control the exact summary format.

## When it runs

The event's `trigger` field is:

| `trigger` | Meaning |
| --- | --- |
| `manual` | Compaction was explicitly requested |
| `auto` | Codex initiated compaction automatically |

The hook group's `matcher` is a regular expression applied to `trigger`. Use `^auto$`, `^manual$`, or `manual|auto`.

## Good uses

- Write a compact checkpoint to a durable project or external state store.
- Record the current turn and compaction trigger for diagnostics.
- Flush buffered telemetry before older context is condensed.
- Verify that a required task-state file exists.
- Stop compaction when losing uncaptured state would make the workflow unsafe.

Do not use the transcript as a long-term contract. `transcript_path` may be null, and the transcript format can change.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `PreCompact` |
| `model` | string | Active model slug |
| `turn_id` | string | Active turn identifier |
| `trigger` | string | `manual` or `auto` |

## Output

Plain text on `stdout` is ignored.

Exit `0` with no output to allow compaction. To stop before compaction, return:

```json
{
  "continue": false,
  "stopReason": "The external task checkpoint could not be saved.",
  "systemMessage": "Compaction was stopped because checkpointing failed."
}
```

`systemMessage` appears as a warning in the UI or event stream. `suppressOutput` is parsed but is not implemented.

Reserve `continue: false` for a genuine state-safety requirement. Repeatedly blocking automatic compaction can prevent a long-running session from making progress.

## Configuration example

```json
{
  "description": "Checkpoint lightweight task metadata before compaction.",
  "hooks": {
    "PreCompact": [
      {
        "matcher": "manual|auto",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/pre-compact/pre_compact.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/pre-compact/pre_compact.py')\"",
            "timeout": 20,
            "statusMessage": "Checkpointing task state"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This example saves event metadata without parsing the unstable transcript:

```python
import json
from pathlib import Path
import sys

event = json.load(sys.stdin)
checkpoint_dir = Path(event["cwd"]) / ".codex" / "hook-state"
checkpoint_dir.mkdir(parents=True, exist_ok=True)

checkpoint = {
    "session_id": event["session_id"],
    "turn_id": event["turn_id"],
    "trigger": event["trigger"],
    "model": event["model"],
}

(checkpoint_dir / "pre-compact.json").write_text(
    json.dumps(checkpoint, indent=2),
    encoding="utf-8",
)
```

The handler emits no `stdout`, so successful checkpointing allows compaction. If saving is mandatory, catch write errors and emit the `continue: false` shape before exiting successfully, or fail according to your operational policy.

## Operational notes

- Commands run with the session `cwd`.
- Multiple matching handlers launch concurrently.
- Keep checkpoint writes atomic if another process may read them immediately.
- Do not save secrets or raw prompts in an unprotected state file.
- Only `type: "command"` handlers run currently.
- Review the hook in `/hooks` after creating or changing it.

See the [official `PreCompact` documentation](https://learn.chatgpt.com/docs/hooks#precompact).
