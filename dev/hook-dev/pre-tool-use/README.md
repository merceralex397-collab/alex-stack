# PreToolUse hook

`PreToolUse` runs immediately before a supported local tool call. It is the main lifecycle point for inspecting, blocking, or rewriting a tool invocation before side effects occur.

## Tool coverage and matchers

The `matcher` is a regular expression applied to the tool name and supported aliases:

| Tool path | Matcher value |
| --- | --- |
| Shell commands and `exec_command` | `Bash` |
| `apply_patch` | `apply_patch`, `Edit`, or `Write` |
| MCP tools | Full name, such as `mcp__filesystem__read_file` |
| Other local function tools | Function name, such as `update_plan` |
| Agent spawning | Its function name or the `Agent` alias |

Hosted tools such as `WebSearch` do not use this local function-tool hook path. Some specialized tool paths can also opt out. Treat this hook as a strong workflow guardrail, not as a complete security boundary.

`write_stdin` does not trigger `PreToolUse` again when it sends input to or polls an existing unified-exec session.

## Good uses

- Block destructive shell commands or writes to protected paths.
- Enforce a deployment freeze or repository-specific release policy.
- Require a tool call to stay inside an approved directory.
- Add model-visible context before a sensitive action.
- Rewrite a supported argument into a safer equivalent.
- Log tool intent and identifiers before execution.

Keep policies deterministic and quick. Use Codex sandboxing, permission profiles, managed configuration, and OS controls for security boundaries that must not be bypassable.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `PreToolUse` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `turn_id` | string | Active turn identifier |
| `tool_name` | string | Canonical name such as `Bash`, `apply_patch`, or an MCP tool name |
| `tool_use_id` | string | Identifier for this invocation |
| `tool_input` | JSON value | Arguments that Codex intends to send |

For `Bash` and `apply_patch`, the command or patch text is in `tool_input.command`. MCP and other function tools provide their normal argument object.

## Output decisions

Plain text on `stdout` is ignored. Emit JSON for decisions.

### Deny the call

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by workspace policy."
  }
}
```

Codex also accepts the older `{"decision":"block","reason":"..."}` shape. Exit code `2` with the reason on `stderr` blocks the call as well.

### Add context without blocking

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "This command touches generated files."
  }
}
```

### Rewrite the input

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {
      "command": "git status --short"
    }
  }
}
```

For `Bash` and `apply_patch`, `updatedInput` must contain a string `command`. For MCP and other local function tools, it must be the complete replacement arguments object. Return `updatedInput` only with `permissionDecision: "allow"`.

Do not use `permissionDecision: "ask"`, legacy `decision: "approve"`, `continue: false`, `stopReason`, or `suppressOutput`. These are parsed but unsupported; Codex reports the hook as failed and continues the original tool call.

## Configuration example

```json
{
  "description": "Check every shell command before it runs.",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/pre-tool-use/pre_tool_use.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/pre-tool-use/pre_tool_use.py')\"",
            "timeout": 15,
            "statusMessage": "Checking command policy"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This is an illustrative guardrail, not a production-grade command parser:

```python
import json
import sys

event = json.load(sys.stdin)
command = str(event.get("tool_input", {}).get("command", ""))

blocked_fragments = (
    "git reset --hard",
    "Remove-Item -Recurse -Force",
    "rm -rf",
)

if any(fragment.lower() in command.lower() for fragment in blocked_fragments):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "This command matches a destructive-operation guardrail."
            ),
        }
    }))
```

An exit code of `0` with no output allows the original tool call to proceed.

## Operational notes

- Matching command hooks launch concurrently; one handler cannot stop another handler from starting.
- Commands run with the session `cwd`.
- Model-visible context is limited to roughly 2,500 tokens per message.
- Only `type: "command"` handlers run currently.
- Set a short timeout so policy checks do not stall every tool call.
- Project hooks require a trusted project, and changed hooks require renewed review in `/hooks`.

See the [official `PreToolUse` documentation](https://learn.chatgpt.com/docs/hooks#pretooluse).
