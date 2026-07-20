# SessionStart hook

`SessionStart` runs at the beginning of a Codex session lifecycle. It is the best hook for loading concise, dynamic workspace context before the agent starts normal work.

## When it runs

The event's `source` field identifies why it fired:

| `source` | Timing |
| --- | --- |
| `startup` | A new session starts |
| `resume` | A saved session resumes |
| `clear` | The session is cleared and begins with fresh context |
| `compact` | The session continues after context compaction |

The hook group's `matcher` is a regular expression applied to `source`. For example, `startup|resume` handles ordinary entry points, while `^compact$` handles only post-compaction restoration.

## Good uses

- Add the current branch, build status, or active ticket as developer context.
- Load short workspace conventions that are generated dynamically.
- Warn when a required runtime or local service is unavailable.
- Restore a durable checkpoint after compaction by matching `compact`.
- Record session-start telemetry without exposing prompt or transcript content.

Prefer `AGENTS.md` for stable repository instructions. Use `SessionStart` when the information is generated, environment-dependent, or changes more often than repository guidance.

## Input

Every command hook receives one JSON object on `stdin`. `SessionStart` receives:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `SessionStart` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `source` | string | `startup`, `resume`, `clear`, or `compact` |

The transcript path is convenient but its file format is not a stable hook API. Avoid tightly coupling a hook to that format.

## Output

Two output forms can add developer context:

1. Plain text written to `stdout`.
2. JSON containing `hookSpecificOutput.additionalContext`.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "The active release branch is release/2026-07."
  }
}
```

The common JSON fields `continue`, `stopReason`, and `systemMessage` are also accepted. `systemMessage` appears as a warning in the UI or event stream. `suppressOutput` is parsed but is not implemented.

Exit code `0` with no output means success with no added context.

## Configuration example

Put the event under the top-level `hooks` object in `.codex/hooks.json`:

```json
{
  "description": "Load dynamic workspace context when a session starts.",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|compact",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/session-start/session_start.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/session-start/session_start.py')\"",
            "timeout": 30,
            "statusMessage": "Loading workspace context"
          }
        ]
      }
    ]
  }
}
```

The git-root lookup keeps the script path stable when Codex starts in a repository subdirectory.

## Minimal Python handler

Save this beside the README as `session_start.py` if you want to try the example:

```python
import json
import subprocess
import sys

event = json.load(sys.stdin)
source = event["source"]

branch = subprocess.run(
    ["git", "branch", "--show-current"],
    cwd=event["cwd"],
    capture_output=True,
    text=True,
    check=False,
).stdout.strip()

context = f"Session source: {source}. Active Git branch: {branch or 'unknown'}."
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}))
```

Keep model-visible output brief. Codex limits each model-visible hook message to roughly 2,500 tokens and may save oversized output to a temporary file. Never return secrets.

## Operational notes

- Commands run with the session `cwd`.
- Only `type: "command"` handlers execute currently.
- The default timeout is 600 seconds; set a shorter explicit timeout for startup checks.
- Matching hooks from every active source run, and matching command hooks launch concurrently.
- Project hooks run only when the project `.codex` layer is trusted.
- New or changed non-managed hooks are skipped until reviewed with `/hooks`.

See the [official `SessionStart` documentation](https://learn.chatgpt.com/docs/hooks#sessionstart).
