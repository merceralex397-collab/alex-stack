# MCP Clients: Config, Logs, and Debug Commands

Use this reference to identify the client host first, then find its config path, its
top-level JSON key, how to add a server, where its logs live, and how to reload it. MCP
behaviour is mostly shared across clients, but config location and shape differ — getting
the wrong file or the wrong key is a frequent copy-paste failure.

For Claude Desktop deep-dives (Windows shims, MSIX paths, per-server logs) see
`claude-desktop.md`. For Claude Code specifics see `claude-code.md`. For remote/OAuth see
`remote-and-auth.md`. Reconciled 2026-06-24; re-verify vendor docs.

## Contents

- Config-key cheat-sheet (the #1 trap)
- Per-client matrix
- Reload / restart semantics
- Logs by client

## Config-key cheat-sheet (the #1 trap)

The top-level key and remote-server fields are not the same everywhere:

- `mcpServers` — Claude Desktop, Cursor, Windsurf, Claude Code (`.mcp.json`).
- `servers` (plus a required `type`) — **VS Code**. Using `mcpServers` in VS Code silently
  does nothing.
- Windsurf uses `serverUrl` (not `url`/`command`) for a remote server.
- VS Code requires `type`: `stdio` | `http` | `sse`.
- Claude Code accepts `streamable-http` as an alias for `http`, plus `ws`.

On Windows, stdio servers launched via `npx`/`uvx` need the `cmd /c` wrapper in **every**
one of these Node-based clients — see `claude-desktop.md`.

## Per-client matrix

### Claude Desktop
- Config: macOS `~/Library/Application Support/Claude/claude_desktop_config.json`;
  Windows `%APPDATA%\Claude\claude_desktop_config.json` (MSIX builds read a LocalCache
  copy — see `claude-desktop.md`).
- Key: `mcpServers`. Entry: `command`/`args`/`env` (stdio). No native remote field — use
  `mcp-remote` for remote URLs.
- Add: edit JSON (or use the in-app connectors UI). Verify via the plus icon → Connectors.
- Logs: `%APPDATA%\Claude\logs` / `~/Library/Logs/Claude` (`mcp.log` + `mcp-server-<NAME>.log`).
- Reload: fully quit and reopen (Windows: also end lingering `Claude.exe`).

### Claude Code (CLI)
- Config: user/local in `~/.claude.json` (keyed by project); project in repo-root
  `.mcp.json` (git-shareable). Key: `mcpServers`. See `claude-code.md`.
- Add: `claude mcp add`, `claude mcp add-json`, `claude mcp add --transport http <name> <url>`.
- Inspect: `claude mcp list`, `claude mcp get <name>`, `/mcp` in-session.
- Logs/debug: `claude --debug mcp` (shows server stderr), `--verbose`.
- Reload: `/mcp` → Reconnect, or relaunch.

### Cursor
- Config: global `~/.cursor/mcp.json` (Windows `%USERPROFILE%\.cursor\mcp.json`); project
  `<root>/.cursor/mcp.json` (project overrides global on a name conflict). Key: `mcpServers`.
- Add: edit JSON, or Settings → MCP/Tools, or one-click "Add to Cursor" from the marketplace.
- Logs: Output panel (Ctrl/Cmd+Shift+U) → "MCP Logs". stdio stderr historically is not
  forwarded — run the server command in a terminal to read it.
- Reload: restart Cursor, or toggle the server off/on.

### VS Code (native MCP / Copilot agent mode)
- Config: workspace `.vscode/mcp.json`, or user config via "MCP: Open User Configuration".
- Key: **`servers`** (not `mcpServers`); each entry needs `type` (`stdio`/`http`/`sse`).
  Optional top-level `inputs` for secrets (`${input:id}`).
- Add: "MCP: Add Server" (guided), or `code --add-mcp '{...}'`. Import others' servers via
  `chat.mcp.discovery.enabled`.
- Logs: "MCP: List Servers" → select → "Show Output". First-run trust prompt blocks
  startup; reset with "MCP: Reset Trust".
- Reload: "MCP: List Servers" → Restart.

### Windsurf (Cascade)
- Config: `~/.codeium/windsurf/mcp_config.json` (Windows
  `%USERPROFILE%\.codeium\windsurf\mcp_config.json`) — create it if absent. Key:
  `mcpServers`. stdio uses `command`/`args`/`env`; remote uses `serverUrl` with optional
  `headers`. Interpolation: `${env:VAR}`, `${file:/path}`.
- Add: Cascade → Plugins/Manage plugins → "Add custom server" / "View raw config".
- Limit: Cascade loads at most 100 active tools; extras are dropped silently — disable
  unused servers/tools.
- Logs: `~/.codeium/windsurf/logs`.
- Reload: click Refresh in the Plugins/MCP panel.

### Claude.ai web custom connectors (remote only)
- Add (Pro/Max): Settings → Connectors → "+" → "Add custom connector" (name + remote URL;
  OAuth Client ID/Secret under Advanced). Team/Enterprise: an Owner adds it at
  Organization settings → Connectors first.
- Reachability: Claude connects from Anthropic's cloud, so the server must be publicly
  reachable over HTTPS — not on a private network. See `remote-and-auth.md`.
- Reload: reconnect from the Connectors list.

## Reload / restart semantics

A config or server-code change needs a reload, and the action differs per client:

| Client | Reload action |
| --- | --- |
| Claude Desktop | Fully quit + reopen; Windows: end lingering `Claude.exe` |
| Claude Code | `/mcp` → Reconnect, or relaunch |
| Cursor | Restart, or toggle the server off/on |
| VS Code | "MCP: List Servers" → Restart |
| Windsurf | Refresh in the Plugins/MCP panel |
| Claude.ai connector | Reconnect from Connectors |

## Logs by client

| Client | Where |
| --- | --- |
| Claude Desktop | `%APPDATA%\Claude\logs` / `~/Library/Logs/Claude` (`mcp.log`, `mcp-server-<NAME>.log`) |
| Claude Code | `claude --debug mcp`, `--verbose` |
| Cursor | Output panel → "MCP Logs" |
| VS Code | "MCP: List Servers" → "Show Output" |
| Windsurf | `~/.codeium/windsurf/logs` |

Redact API keys, tokens, and session ids before sharing any log excerpt.
