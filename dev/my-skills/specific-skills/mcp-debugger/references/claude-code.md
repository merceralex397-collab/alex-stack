# Claude Code (CLI) MCP Debugging

Use this reference when the host is Claude Code: the `claude mcp` command surface, config
scopes and precedence, project approval, OAuth, debug flags, and Windows quirks. For
config-key differences across clients see `clients.md`; for remote/OAuth see
`remote-and-auth.md`. Command names and flags evolve fast — confirm with `claude mcp --help`
and `claude --help`. Reconciled 2026-06-24.

## Contents

- Command surface
- Transports
- Scopes and precedence
- Project approval model
- Connected-but-zero-tools / failing servers
- OAuth and authentication
- Environment variables
- Diagnostics
- Windows quirks

## Command surface

```bash
claude mcp add <name> -- <command> [args]      # stdio server (-- separates Claude flags)
claude mcp add --transport http <name> <url>   # remote Streamable HTTP
claude mcp add --transport sse  <name> <url>   # remote SSE (legacy)
claude mcp add-json <name> '<json>'            # full JSON entry (incl. type/headers/oauth)
claude mcp add-from-claude-desktop             # import Claude Desktop servers
claude mcp list                                 # all servers + status
claude mcp get <name>                           # exact command/args being spawned
claude mcp remove <name>
claude mcp reset-project-choices                # re-prompt for .mcp.json approvals
claude mcp serve                                # run Claude Code itself as an MCP server
```

## Transports

`--transport http|sse|stdio`. In JSON, `type` accepts `streamable-http` (alias for
`http`), `sse`, `stdio`, and `ws`. The `--` token separates Claude's own flags from the
server command:

```bash
claude mcp add fs -- npx -y @modelcontextprotocol/server-filesystem /abs/dir
claude mcp add api --transport http secure https://api.example.com/mcp \
  --header "Authorization: Bearer $TOKEN"
```

## Scopes and precedence

`--scope` selects where the entry is stored:

- `local` (default) — `~/.claude.json`, keyed by the current project path.
- `project` — repo-root `.mcp.json`, git-shareable.
- `user` — `~/.claude.json`, global across projects.

Precedence, highest first: **local > project > user > plugin-provided > Claude.ai
connectors**. The entire entry from the highest source wins; fields are not merged. So a
`local` server shadows a `project` server of the same name — a common "my edit to
`.mcp.json` did nothing" cause.

## Project approval model

Servers from a project `.mcp.json` require one-time approval and show as `⏸ Pending
approval` (or `✗ Rejected`) in `claude mcp list`/`get`. Approve them in `/mcp`. To
re-prompt, run `claude mcp reset-project-choices`. Place `.mcp.json` at the repository
root, not under `.claude/`. Note that `settings.json` does **not** read `mcpServers`.

## Connected-but-zero-tools / failing servers

1. `/mcp` → check status; choose Reconnect if connected with zero tools.
2. `claude --debug mcp` (current form; older guides show `--mcp-debug`) prints the server's
   stderr and the immediate failure cause. Add `--verbose` for protocol detail.
3. `claude mcp get <name>` shows the exact spawn command — reproduce it in a plain terminal
   to read stderr directly.

Common causes: relative `command`/`args` resolving against the launch directory (use
absolute paths); `spawn ENOENT` (executable not on Claude Code's PATH, or a Windows shim —
see `claude-desktop.md`); stdout contamination breaking JSON-RPC framing; startup slower
than the timeout. Note that env vars set in `settings.json` do **not** propagate to MCP
child processes — put per-server credentials in the server's `env` block.

## OAuth and authentication

- In-session: run `/mcp` and complete the browser OAuth flow (HTTP transport).
- CLI: `claude mcp login <name>` (`--no-browser` over SSH, paired with `ssh -t`);
  `claude mcp logout <name>`.
- Pre-configured creds: `--client-id`, `--client-secret` (masked prompt),
  `--callback-port <port>`; for CI set `MCP_CLIENT_SECRET`.
- A wrong static `headers.Authorization` makes Claude report the server as `failed` rather
  than falling back to OAuth — remove the bad header to allow the OAuth flow.
- "Clear authentication" in `/mcp` revokes stored tokens.

## Environment variables

- `MCP_TIMEOUT` — server startup timeout (e.g. `MCP_TIMEOUT=10000 claude`).
- per-server `timeout` (ms) in the entry, or `MCP_TOOL_TIMEOUT` — per-tool wall-clock.
- `MAX_MCP_OUTPUT_TOKENS` — tool output cap (default ~25000; a warning fires near 10000).
- `CLAUDE_PROJECT_DIR` — set in the spawned server's environment.

## Diagnostics

`/doctor` validates configuration, `/status` shows active settings sources and auth
method, `/context` shows loaded MCP tools, and `claude --safe-mode` disables
customizations to isolate a problem. HTTP/SSE servers auto-reconnect with exponential
backoff; stdio servers do not auto-reconnect.

## Windows quirks

`claude mcp add` can mangle a `/c` flag into a drive path (`C:/`), and Git-Bash/MSYS
rewrites `/c` via path conversion. Mitigate by hand-editing the JSON so `args[0]` is
exactly `"/c"`, quoting paths after `--`, prefixing the call with `MSYS_NO_PATHCONV=1`, or
running the add from `cmd`/PowerShell rather than bash:

```bash
claude mcp add fs -- cmd /c npx -y @modelcontextprotocol/server-filesystem "C:/Users/you/Desktop"
MSYS_NO_PATHCONV=1 claude mcp add fs -- cmd /c npx -y @scope/server
```
