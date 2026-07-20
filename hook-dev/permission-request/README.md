# PermissionRequest hook

`PermissionRequest` runs only when Codex is about to ask for approval. It can allow a narrowly understood request, deny it, or decline to decide so the normal user approval prompt remains in control.

It does not run for tool calls that do not require approval.

## When it is useful

- Automatically deny deployments, destructive operations, or protected-environment access.
- Auto-approve a very small, deterministic class of requests that policy already permits.
- Keep routine decisions consistent across a team.
- Record approval-request metadata for an audit trail.
- Surface a policy warning while leaving the final decision to the user.

Be conservative with automatic `allow`. A broad matcher or weak string test can remove a safety checkpoint that would otherwise be shown to the user.

## Matchers

The `matcher` is a regular expression applied to `tool_name` and supported aliases:

| Tool path | Matcher value |
| --- | --- |
| Shell or unified exec request | `Bash` |
| Patch request | `apply_patch`, `Edit`, or `Write` |
| MCP request | Full MCP name, such as `mcp__server__tool` |

Omit `matcher`, or use `*` or an empty string, to inspect every supported permission request.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Current Codex session identifier |
| `transcript_path` | string or null | Session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `PermissionRequest` |
| `model` | string | Active model slug |
| `permission_mode` | string | Current permission mode |
| `turn_id` | string | Active turn identifier |
| `tool_name` | string | Canonical tool name |
| `tool_input` | JSON value | Tool-specific arguments |
| `tool_input.description` | string or null | Human-readable approval reason, when provided |

For `Bash` and `apply_patch`, `tool_input.command` contains the command or patch text. Do not assume every tool includes `tool_input.description`.

## Output decisions

Plain text on `stdout` is ignored. Use one of these structured outcomes.

### Allow without prompting

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow"
    }
  }
}
```

### Deny

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "deny",
      "message": "Production deployment is blocked by repository policy."
    }
  }
}
```

### Leave the decision to the normal flow

Exit `0` without writing anything to `stdout`. Codex then displays its normal approval prompt.

When several matching hooks return decisions, any `deny` wins. Otherwise, an `allow` lets the request proceed without surfacing the approval prompt.

`systemMessage` is supported for a UI or event-stream warning. Do not return `updatedInput`, `updatedPermissions`, or `interrupt`; these fields are reserved for future behavior and fail closed currently. The common fields `continue`, `stopReason`, and `suppressOutput` are not supported for this event.

## Configuration example

```json
{
  "description": "Apply repository policy to shell approval requests.",
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/permission-request/permission_request.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/permission-request/permission_request.py')\"",
            "timeout": 15,
            "statusMessage": "Checking approval policy"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

This example denies obvious production deployment requests and leaves everything else to the normal approval prompt:

```python
import json
import sys

event = json.load(sys.stdin)
command = str(event.get("tool_input", {}).get("command", ""))

production_markers = (
    "--environment production",
    "--env production",
    "kubectl apply",
)

if any(marker.lower() in command.lower() for marker in production_markers):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": "deny",
                "message": (
                    "Production operations require the separate release workflow."
                ),
            },
        }
    }))
```

In a real policy hook, parse structured tool arguments where possible and use an explicit allowlist. Treat simple substring checks as illustrative only.

## Operational notes

- The hook runs after a tool has been classified as requiring approval, not before every tool call.
- Matching handlers launch concurrently, so one handler cannot stop another from starting.
- Keep handlers fast; they sit directly in the approval path.
- Only `type: "command"` handlers run currently.
- Commands run with the session `cwd`.
- Review new or changed non-managed hooks with `/hooks`.

See the [official `PermissionRequest` documentation](https://learn.chatgpt.com/docs/hooks#permissionrequest).
