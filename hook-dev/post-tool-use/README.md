# PostToolUse hook

`PostToolUse` runs after a supported local tool produces output. It can inspect the original input and result, add context, or replace the model-visible result with feedback.

The tool has already run. This hook cannot undo filesystem changes, commands, network calls, or other side effects.

## Tool coverage and matchers

The `matcher` is a regular expression applied to the tool name and supported aliases:

| Tool path | Matcher value |
| --- | --- |
| Shell commands and `exec_command` | `Bash` |
| `apply_patch` | `apply_patch`, `Edit`, or `Write` |
| MCP tools | Full name, such as `mcp__filesystem__read_file` |
| Other local function tools | Function name, such as `update_plan` |

For a long-running unified-exec command, the eventual `write_stdin` poll may deliver the original command's `PostToolUse` event when the command finishes. Non-zero Bash exits still produce this event.

Hosted tools such as `WebSearch` do not use this hook path, and specialized tools can opt out.

## Good uses

- Detect failed validation and tell Codex what to inspect next.
- Check an edited file or generated artifact after a write.
- Attach concise interpretation to noisy tool output.
- Record tool outcomes and identifiers for local observability.
- Prevent an unsafe or malformed result from reaching code-mode JavaScript.
- Ask the model to review side effects that have already occurred.

Avoid expensive full-repository checks after every tool call. Match only the relevant tool and keep the handler focused.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `PostToolUse` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `turn_id` | string | Active turn identifier |
| `tool_name` | string | Canonical tool name |
| `tool_use_id` | string | Identifier for the completed invocation |
| `tool_input` | JSON value | Arguments sent to the tool |
| `tool_response` | JSON value | Tool-specific result |

MCP calls provide the MCP call result. Other local function tools normally provide their model-facing output.

## Output behavior

Plain text on `stdout` is ignored. Emit JSON when feedback is needed.

```json
{
  "decision": "block",
  "reason": "The validation output contains failures that need review.",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Inspect the first failing test before editing more files."
  }
}
```

For this event, `decision: "block"` does not reverse the completed tool call. Codex records the feedback, replaces the original model-visible tool result with the hook feedback, and continues the model from that message.

Alternatives:

- Exit with code `2` and write feedback to `stderr`.
- Return `continue: false` to stop normal processing of the original result and replace it with hook feedback or stop text.
- Return `systemMessage` to show a warning in the UI or event stream.
- Exit `0` with no output to preserve normal processing.

`updatedMCPToolOutput` and `suppressOutput` are parsed but unsupported. Returning them causes the hook run to fail and normal result processing to continue.

### Code-mode behavior

| Hook result | What nested code mode sees |
| --- | --- |
| `decision: "block"` or exit code `2` | The tool runs, then the nested tool promise rejects with the hook reason |
| `continue: false` | Codex uses the hook feedback as model-visible output, but the nested promise is not rejected |

## Configuration example

```json
{
  "description": "Review shell output after each completed command.",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/post-tool-use/post_tool_use.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/post-tool-use/post_tool_use.py')\"",
            "timeout": 20,
            "statusMessage": "Reviewing command result"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This illustrative handler asks Codex to focus on output that contains a familiar failure marker:

```python
import json
import sys

event = json.load(sys.stdin)
response_text = json.dumps(event.get("tool_response"), ensure_ascii=False)

failure_markers = ("FAILED", "Test Suites: 1 failed", "npm ERR!")

if any(marker.lower() in response_text.lower() for marker in failure_markers):
    print(json.dumps({
        "decision": "block",
        "reason": (
            "The completed command reported a failure. "
            "Inspect the first root-cause error before continuing."
        ),
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "The original command has already run; do not assume "
                "its side effects were rolled back."
            ),
        },
    }))
```

Tool-response shapes differ, so production hooks should branch on `tool_name` and validate the expected result structure.

## Operational notes

- Multiple matching handlers launch concurrently and their feedback may be combined.
- Combined feedback visible to the model is limited to roughly 2,500 tokens.
- Commands run with the session `cwd`.
- Set focused matchers to avoid running validation after unrelated tools.
- Project hooks require trust, and changed definitions require review again.
- Use `PreToolUse` when an action must be prevented before it happens.

See the [official `PostToolUse` documentation](https://learn.chatgpt.com/docs/hooks#posttooluse).
