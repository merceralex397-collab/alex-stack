---
name: mcp-debugger
description: Deep, evidence-first debugging for Model Context Protocol (MCP) servers and client integrations across Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, and Claude.ai remote connectors. Use when diagnosing why an MCP server fails to appear, connect, or stay connected: stdio launch failures (spawn ENOENT/EINVAL, npx/uvx on Windows, stdout JSON-RPC contamination, missing env/PATH, stale build, exit codes); Streamable HTTP or legacy SSE transport, session-id and protocol-version errors; remote server and OAuth 2.1 problems (401/403 loops, WWW-Authenticate discovery, audience/resource binding, DCR, PKCE, mcp-remote); MCP Inspector testing; tool/resource/prompt schema and capability-negotiation failures; or config/log issues in any client. Use this whenever MCP tools or a server misbehave, even if the user only names a symptom (server disconnected, no tools showing, spawn ENOENT, connection failed) and does not say "MCP".
---

# MCP Debugger

## Operating Rules

Debug MCP issues as a layered system: client host, launch configuration, server process,
transport, protocol lifecycle, capability negotiation, MCP features, and upstream services.
Do not diagnose from UI symptoms alone. Gather evidence, isolate one failing layer, change
one thing, and retest through the same path.

Anchor protocol facts to the current stable MCP revision (2025-11-25), but confirm the
version actually negotiated in the `initialize` exchange rather than assuming one. For HTTP,
the `MCP-Protocol-Version` header is required on post-initialize requests.

Protect secrets in every artifact. Redact API keys, bearer tokens, session IDs, private
data, and env values before showing logs or config. Keep path details when they are
relevant to startup or filesystem permission failures.

## Dependencies

The bundled scripts need Python 3.8+ (invoke as `python` on Windows, `python3` on
macOS/Linux). Reproduction commands assume `node`/`npx` (Inspector and npm servers),
`uv`/`uvx` (Python servers), and `curl`/`openssl` (network triage). Do not assume these are
installed — check, and adapt to what the host has.

## Resource Routing

Load deeper resources only when the layer points there:

- `references/clients.md`: Identify the client host, then get its config path, top-level JSON
  key, server-entry shape, add-server command, logs, and reload action. Read this first when
  the host is not Claude Desktop.
- `references/claude-desktop.md`: Claude Desktop config paths (incl. MSIX/LocalCache),
  Windows launcher fixes (`cmd /c`), PATH/env inheritance, logs, exit codes, DevTools.
- `references/claude-code.md`: Claude Code CLI — `claude mcp` commands, scopes/precedence,
  project approval, `/mcp`, `claude --debug mcp`, OAuth.
- `references/protocol-and-transport.md`: lifecycle, version negotiation, stdio purity,
  Streamable HTTP, session IDs, SSE, transport detection, capability mismatch.
- `references/remote-and-auth.md`: remote endpoints — curl/probe handshake, network/TLS/proxy
  failures, the OAuth 2.1 discovery chain, DCR/PKCE/audience binding, `mcp-remote`, hosted
  connectors.
- `references/tool-resource-prompt-checks.md`: a server that starts but whose tools,
  resources, prompts, schemas, or results fail.
- `references/debugging.md`: local stdio deep-dive — launchers, exit codes, stdout
  contamination, env/cwd, build staleness, permissions.
- `references/mcpinspector.md`: MCP Inspector (current) — session-token auth, `--cli` mode,
  ports, transports, security model.

Scripts (execute, do not read into context):

- `scripts/claude_desktop_diagnostics.py`: validate a Claude Desktop config — JSON, env
  redaction, command resolution, Windows shim-spawn (`cmd /c`) detection, BOM, and MSIX
  path divergence, plus a recent-log preview.
- `scripts/mcp_http_probe.py <url>`: probe a remote endpoint — initialize handshake, session
  id, protocol version, tool list, and any 401 + `WWW-Authenticate` challenge. Evidence only.

## Initial Triage

Collect the smallest complete case:

- Client host and version: Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, a custom
  client, or a Claude.ai remote connector.
- OS, shell, and runtime managers: Windows/macOS/Linux, PowerShell/bash/zsh, `nvm`, `pyenv`,
  `uv`, Docker, etc.
- Transport: `stdio`, Streamable HTTP, older HTTP+SSE, or unknown.
- Server implementation: language, SDK, package manager, repo path, build output path.
- Launch source: client config, terminal command, Docker, `npx`, `uvx`, `uv`, `node`,
  `python`, `mcp-remote`, or a binary.
- Config excerpt: server name, `command`, `args`, `env`, HTTP URL, auth settings.
- Exact symptom: absent server, connection error, initialization error, missing tools, failed
  tool call, timeout, auth failure, or client UI error.
- Fresh logs from both server and client.
- Reproduction surface: Inspector, target client, both, or only one.

## Client Router

Identify the client host before validating config or reloading — the config path, top-level
key, log location, and reload action all differ. Open `references/clients.md` to get them.
One trap worth checking immediately: the top-level key is `mcpServers` for Claude Desktop,
Cursor, Windsurf, and Claude Code, but `servers` (with a required `type`) for VS Code.

## Failure Map

Classify before editing:

| Symptom | Likely failed layer | Load / run |
| --- | --- | --- |
| Server absent from the client | Client config / launch config | `clients.md`, `claude-desktop.md`; run `claude_desktop_diagnostics.py` |
| `spawn ENOENT`/`EINVAL` on Windows (npx/uvx) | Launcher shim | `claude-desktop.md` (use `cmd /c`) |
| Connects then drops / "disconnected" | Server process / stdout framing | `debugging.md` (read `mcp-server-<NAME>.log`) |
| Silent failure after a Desktop update, no logs | MSIX config-path divergence | `claude-desktop.md` |
| Tools/resources/prompts missing | Features / stale build | `tool-resource-prompt-checks.md`, `debugging.md` |
| Tool call fails or times out | Schema / handler / upstream | `tool-resource-prompt-checks.md` |
| HTTP 400/404 session, or version error | Transport session lifecycle | `protocol-and-transport.md` |
| HTTP 401/403 or OAuth loop | Remote auth | `remote-and-auth.md`; run `mcp_http_probe.py` |
| Remote URL in a stdio-only client does nothing | Missing HTTP bridge | `remote-and-auth.md` (`mcp-remote`) |
| Unsure whether it's the server or the client | Need isolation | `mcpinspector.md` (test the server alone) |
| Host is Claude Code CLI (zero tools, scope/approval) | Client-specific config | `claude-code.md` |

## Workflow

1. Identify the client and validate its config (`references/clients.md`). For Claude Desktop,
   run from the skill directory:

   ```bash
   python scripts/claude_desktop_diagnostics.py
   ```

   (If packaged as a plugin, use `${CLAUDE_PLUGIN_ROOT}/scripts/claude_desktop_diagnostics.py`.)

2. Prove the server starts outside the client, using the exact command, args, env, and
   absolute paths from the config. A healthy stdio server blocks on stdin and appears to
   hang — that is normal, not a failure.

3. Isolate with MCP Inspector before debugging the target host (open the tokenized URL it
   prints):

   ```bash
   npx -y @modelcontextprotocol/inspector node /absolute/path/server/build/index.js
   npx -y @modelcontextprotocol/inspector uv --directory /absolute/path/server run package-name
   ```

   Use `--cli ... --method tools/list` for a scriptable check.

4. For remote/HTTP servers, probe the endpoint before editing code, then follow the
   discovery chain in `references/remote-and-auth.md`:

   ```bash
   python scripts/mcp_http_probe.py https://host/mcp
   ```

5. Inspect lifecycle before feature behaviour: `initialize`, server capabilities, the
   `initialized` notification, then list/call tools/resources/prompts.

6. Debug the failing feature using the matching reference. Keep stdio stdout protocol-only;
   send logs to stderr, files, or MCP log notifications.

7. For HTTP servers, capture status, response body, headers, session ID, protocol version,
   SSE behaviour, and auth metadata before changing code.

8. After each fix, rebuild if needed, rerun the direct command, reconnect in Inspector,
   reload the target client the right way for that host (`references/clients.md`), and confirm
   the original user-visible symptom is gone.

## Reporting

Return a concise debugging report:

- Root cause and failed layer.
- Evidence used: config validation, log excerpt, Inspector result, probe output, protocol
  exchange, or code path.
- Files/settings changed.
- Validation commands and results.
- Remaining risks: version compatibility, auth expiry, permissions, host-specific behaviour,
  or unresolved logs.
