# Session Log Signals

Codex session JSONL is useful operational evidence, not a stable public API. Treat unknown records as coverage warnings and continue conservatively.

## Project scope

- Use the requested project root as the boundary.
- Match `session_meta.payload.cwd` and later `turn_context.payload.cwd` values at or below that boundary.
- Compare canonical paths case-insensitively on Windows.
- Filter events by their own timestamps, not only file modification time.
- Do not count sessions launched from a parent workspace unless the active turn working directory is inside the target project.

## Positive usage signals

### Skills

Count:

- An explicit `$skill-name` in a user message.
- A tool call that reads the exact known `SKILL.md` path.
- Both current `function_call` and older `custom_tool_call` records when they carry that read.

Do not count:

- Skill catalogs in developer instructions.
- A skill name appearing in documentation or generated output.
- A plugin being installed or enabled.

### MCP servers and apps

Count:

- `response_item` function calls whose namespace begins with `mcp__`.
- `mcp_tool_call_end` events, paired by call ID when available.
- Namespaces beginning with `mcp__codex_apps__` as app calls.

Pair start and end records so one call is counted once. Preserve success, failure, and incomplete status without retaining arguments or results.

### Plugins

Plugins are bundles, not normal invocation endpoints. Attribute plugin use transitively when an owned skill, MCP server, app, or hook is used. Do not count marketplace discovery or installation as use.

## Negative and ambiguous signals

- `tool_search_output` means a tool was exposed or discovered, not invoked.
- A call without a completion record is an attempt with unknown outcome.
- A failed call is still use and should produce a setup warning.
- Hosted tools and specialized paths may not appear in local function-tool records.
- Session forks can duplicate records; deduplicate by call or turn identity.
- No matching logs means “no history available,” not “unused.”
- Matching logs with zero attributable events means “usage not established,” not “zero use.”

## Privacy boundary

The scanner may inspect message text only long enough to extract an explicit `$skill-name`. It must never emit or cache the message.

Never emit or cache:

- Prompts or assistant text.
- Command or tool arguments.
- Command or tool output.
- MCP results.
- Tokens, environment values, HTTP headers, or credentials.

The optional cache may retain only transcript-relative file identity, byte offsets, normalized capability identifiers, timestamps, call status, and deduplication hashes.
