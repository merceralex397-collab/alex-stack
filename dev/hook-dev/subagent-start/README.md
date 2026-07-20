# SubagentStart hook

`SubagentStart` runs as a delegated subagent begins. It lets a workspace supply role-specific context directly to the child agent without adding that detail to every parent prompt.

## When it runs

The event fires at subagent-start scope. Its `matcher` is a regular expression applied to `agent_type`. Agent type values depend on the profile that starts, so inspect real event payloads before relying on a narrowly named profile.

Examples:

- `reviewer|tester` matches either named profile.
- `^reviewer$` matches only the exact reviewer type.
- Omitting `matcher`, or using `*` or an empty string, matches all subagents.

## Good uses

- Give reviewers a defect-first checklist and repository test commands.
- Give testing agents the locations of fixtures, logs, and validation scripts.
- Supply generated context that differs by subagent role.
- Record subagent identifiers and profiles for local audit or performance analysis.
- Warn a subagent that a required dependency is unavailable.

Use parent prompts or agent profile instructions for stable role definitions. Use this hook for dynamic workspace state or centrally enforced startup context.

## Input

The command receives one JSON object on `stdin`:

| Field | Type | Meaning |
| --- | --- | --- |
| `session_id` | string | Parent Codex session identifier |
| `transcript_path` | string or null | Parent session transcript path, when available |
| `cwd` | string | Session working directory |
| `hook_event_name` | string | `SubagentStart` |
| `model` | string | Active model slug |
| `turn_id` | string | Active parent turn identifier |
| `agent_id` | string | Identifier assigned to the subagent |
| `agent_type` | string | Subagent type or profile |
| `permission_mode` | string | Current permission mode |

## Output

Plain text on `stdout` becomes extra developer context for the new subagent. Structured output can provide the same context:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Review tests/README.md before changing test fixtures."
  }
}
```

`systemMessage` is also supported and appears as a warning in the UI or event stream.

Important limitation: `continue: false` is parsed for compatibility but does not prevent the subagent from starting. This event can guide or warn a subagent; it is not a start veto.

## Configuration example

```json
{
  "description": "Give selected subagents role-specific workspace context.",
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "reviewer|tester",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/hook-dev/subagent-start/subagent_start.py\"",
            "commandWindows": "powershell -NoProfile -Command \"py -3 (Join-Path (git rev-parse --show-toplevel) 'hook-dev/subagent-start/subagent_start.py')\"",
            "timeout": 30,
            "statusMessage": "Preparing subagent context"
          }
        ]
      }
    ]
  }
}
```

## Minimal Python handler

```python
import json
import sys

event = json.load(sys.stdin)
agent_type = event["agent_type"]

context_by_type = {
    "reviewer": (
        "Review the complete diff, report defects before summaries, "
        "and cite the exact validation evidence."
    ),
    "tester": (
        "Read the repository test instructions first and preserve "
        "existing fixtures unless the task explicitly changes them."
    ),
}

context = context_by_type.get(
    agent_type,
    "Confirm the delegated scope before making changes.",
)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SubagentStart",
        "additionalContext": context,
    }
}))
```

Keep the context role-specific and short. If every subagent needs a long static policy, put that policy in the agent profile or repository guidance and use the hook only to point to it.

## Operational notes

- Commands run with the parent session's `cwd`.
- Multiple matching handlers launch concurrently.
- A handler cannot prevent another matching handler from starting.
- Model-visible additional context is limited to roughly 2,500 tokens per message.
- Avoid returning secrets; oversized output can be written to a temporary file.
- Review new or changed non-managed hooks with `/hooks` before expecting them to run.

See the [official `SubagentStart` documentation](https://learn.chatgpt.com/docs/hooks#subagentstart).
