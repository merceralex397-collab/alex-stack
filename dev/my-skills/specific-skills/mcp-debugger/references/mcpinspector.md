# MCP Inspector

Use this reference to isolate a server with the MCP Inspector before debugging the target
host. The Inspector is the first stop for "is it the server or the client?". This is a
hand-written summary (the modelcontextprotocol.io page documents the UI only and lags the
project). The GitHub README is authoritative; the tool moves fast, so confirm specifics
with `npx @modelcontextprotocol/inspector --version`. Written against the ~0.22.x line;
reconciled 2026-06-24.

## Contents

- Authentication and the proxy session token (mandatory)
- Launch recipes (stdio, node, uv/python, npm/PyPI, remote)
- CLI mode (--cli) for automation/CI
- Transports
- Ports and environment variables
- Config files and export
- Security model
- Common pitfalls

## Authentication and the proxy session token (mandatory)

Since v0.14.1 (the CVE-2025-49596 fix), the Inspector proxy requires auth by default. On
startup it prints a tokenized URL such as `http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<token>`
and opens it. **Open that exact URL** — a bare `http://localhost:6274` will fail with
"Connection Error" / "Invalid origin". The token is regenerated each run; paste it into
Configuration → "Proxy Session Token" if needed.

```bash
# Pin a stable token for scripting/CI
MCP_PROXY_AUTH_TOKEN=$(openssl rand -hex 32) npx @modelcontextprotocol/inspector node build/index.js
# Trusted, isolated dev box only — disables auth (re-enables the RCE risk the token prevents)
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector node build/index.js
```

If the UI is served from a non-default host/port (reverse proxy, container, Codespaces),
the proxy's Origin check may reject it — set `ALLOWED_ORIGINS` to the exact UI URL(s).

## Launch recipes

The command after the inspector invocation **is** the server command. Pass server env with
`-e KEY=VALUE` **before** the command and server args **after** it.

```bash
# local node build
npx @modelcontextprotocol/inspector node /abs/build/index.js
# with env + args
npx @modelcontextprotocol/inspector -e API_KEY=xyz node /abs/build/index.js --flag
# uv-managed Python project
npx @modelcontextprotocol/inspector uv --directory /abs/server run package-name args...
# npm-distributed server
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /abs/dir
# PyPI-distributed server
npx @modelcontextprotocol/inspector uvx mcp-server-git --repository /abs/repo.git
# remote Streamable HTTP (CLI form shown below)
npx @modelcontextprotocol/inspector --cli https://host/mcp --transport http --method tools/list
```

Runtime requirement: Node.js ^22.7.5 — older Node fails to launch the Inspector.

## CLI mode (--cli) for automation/CI

`--cli` runs non-interactively (no browser), prints JSON to stdout, and is the way to gate
CI. UI mode in CI will hang waiting for a browser.

```bash
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/call \
  --tool-name mytool --tool-arg key=value --tool-arg 'options={"format":"json"}'
npx @modelcontextprotocol/inspector --cli https://host/mcp --transport http \
  --header "Authorization: Bearer $TOKEN" --method tools/list
```

Grammar: `--cli <command-or-url> --method <m> [--tool-name n --tool-arg k=v ...]
[--transport http] [--header "H: v"] [--config <f> --server <name>]`. Methods include
`tools/list`, `tools/call`, `resources/list`, `prompts/list`. Pipe to `jq` to assert. The
proxy auth token still applies — pin `MCP_PROXY_AUTH_TOKEN` in CI for reproducibility.

## Transports

| Transport | Typical path | How to select | Status |
| --- | --- | --- | --- |
| stdio | (local command) | default for a command | local default |
| Streamable HTTP | `/mcp` | CLI `--transport http`; UI `?transport=streamable-http&serverUrl=...` | modern |
| SSE | `/sse` | bare URL; UI `?transport=sse&serverUrl=...` | legacy/deprecated |

A bare URL defaults toward SSE — HTTP servers need `--transport http`. Send remote auth via
`--header` (CLI) or the Authentication section (UI).

## Ports and environment variables

| Variable | Purpose / default |
| --- | --- |
| `CLIENT_PORT` | UI port (default 6274) |
| `SERVER_PORT` | proxy port (default 6277) |
| `HOST` | bind address (default 127.0.0.1; `0.0.0.0` exposes RCE risk) |
| `MCP_PROXY_AUTH_TOKEN` | set/pin the proxy session token |
| `DANGEROUSLY_OMIT_AUTH` | disable auth (trusted isolated dev only) |
| `ALLOWED_ORIGINS` | comma-separated allowed Origins |
| `MCP_AUTO_OPEN_ENABLED` | set `false` for headless/CI/Docker |
| `MCP_PROXY_FULL_ADDRESS` | point the UI at a non-default proxy |

`MCP_SERVER_REQUEST_TIMEOUT` (default 300000 ms) is client-side only — independent of the
server's own timeouts; a common source of "it timed out" confusion on long tool calls.

## Config files and export

Launch from a saved config instead of long CLI args:

```bash
npx @modelcontextprotocol/inspector --config ./mcp.json --server everything
npx @modelcontextprotocol/inspector --cli --config ./mcp.json --server my-server --method tools/list
```

The config uses an `mcpServers` map: stdio entries use `command`/`args`/`env`; remote
entries use `type: "sse" | "streamable-http"` plus `url`. Omit `--server` with a single
server or a `default-server` entry. The UI's "Server Entry" / "Servers File" buttons export
these.

## Security model

CVE-2025-49596 (CVSS 9.4 RCE, fixed in 0.14.1): before the fix the proxy had no auth, so a
browser could drive it to spawn arbitrary commands via DNS rebinding even when bound to
127.0.0.1. The current model: a per-run session token, Origin/Host validation, and a
default 127.0.0.1 bind. Keep auth on; only set `HOST=0.0.0.0` or `DANGEROUSLY_OMIT_AUTH` on
a trusted, isolated network, and prefer SSH port-forwarding for remote access.

## Common pitfalls

- Opening a bare `localhost:6274` without the token → "Connection Error".
- Server logging to stdout → corrupts the stdio stream (see `protocol-and-transport.md`).
- Wrong `--transport` for an HTTP server, or wrong endpoint path (`/mcp` vs `/sse`).
- `-e`/args ordering (env before the command, args after).
- Port 6274/6277 already in use → set `CLIENT_PORT`/`SERVER_PORT`.
- Browser auto-open in CI/Docker → set `MCP_AUTO_OPEN_ENABLED=false`.
