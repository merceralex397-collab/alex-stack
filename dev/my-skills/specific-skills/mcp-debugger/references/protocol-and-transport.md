# Protocol and Transport Debugging

Use this reference for connection failures, lifecycle errors, capability mismatches,
stdio corruption, Streamable HTTP behaviour, session problems, or protocol version
issues. For OAuth/auth, the curl probe, and network-layer failures see
`remote-and-auth.md`. For local launcher/exit-code/log detail see `debugging.md`.

Current stable MCP revision: **2025-11-25** (supersedes 2025-06-18). Clients send the
version they negotiated at `initialize`; do not assume a fixed revision — confirm it in
the handshake. Reconciled 2026-06-24 with modelcontextprotocol.io; re-verify upstream.

## Contents

- Lifecycle check
- Capability negotiation traps
- stdio transport (stdout purity)
- Streamable HTTP basics
- Session lifecycle (400 / 404 / DELETE)
- Protocol-version header (silent-downgrade trap)
- SSE and resumability
- Backwards-compat transport detection
- 2025-11-25 behaviour deltas

## Lifecycle check

Verify the sequence before debugging feature handlers:

1. Client sends `initialize` with protocol version, client info, and client capabilities.
2. Server returns protocol version, server info, and server capabilities.
3. Client sends the `notifications/initialized` notification.
4. Client calls list/read/call methods according to the negotiated capabilities.

Look for:

- Unsupported or mismatched protocol versions.
- Stale SDKs using incompatible message shapes.
- A server advertising capabilities it does not implement.
- A server sending client requests the client did not declare.
- Missing `initialized` notification handling.
- JSON-RPC `-32602 Invalid params`, often caused by a schema or capability mismatch.

## Capability negotiation traps

`-32602` frequently comes from a server using a feature the client never declared:

- Server requests sampling, but the client did not declare sampling support.
- Server requests elicitation, but the client did not declare elicitation support.
- Server requests roots, but the client does not support or expose roots.
- Server assumes progress/logging behaviour the client does not honour.

Inspect the `initialize` exchange and confirm both sides declared what you expect.

## stdio transport (stdout purity)

For stdio servers, stdout is protocol-only. Any banner, normal log, progress print,
warning, or framework output on stdout corrupts JSON-RPC framing (newline-delimited,
UTF-8, no embedded newlines).

The definitive contamination test — pipe stdout only and look for any non-JSON line:

```bash
node server.js 2>/dev/null | head        # any line that is not one JSON-RPC object is contamination
```

Route diagnostics to stderr instead:

- Node: prefer `console.error`, not `console.log`.
- Python: configure logging with `stream=sys.stderr`; never bare `print`.
- Java/Spring: disable the banner and any console appender that writes to stdout.
- CLI wrappers / child processes: ensure their stdout does not leak into the server's.

A stdio server launched directly in a terminal appears to hang — it is blocking on stdin
waiting for JSON-RPC. That is healthy, not a failure. For exit-code triage see
`debugging.md`.

## Streamable HTTP basics

For HTTP servers, capture request and response headers before editing code (run
`scripts/mcp_http_probe.py <url>` or the curl handshake in `remote-and-auth.md`).

- JSON-RPC messages are sent with HTTP POST to the single MCP endpoint.
- `Accept` must include both `application/json` and `text/event-stream`. Omitting
  `text/event-stream` makes a spec-compliant server reject the POST (often 406/400).
- The POST body is a single JSON-RPC request, response, or notification.
- For a JSON-RPC **request**, the server returns either `application/json` (one object) or
  `text/event-stream` (SSE); the client must accept both.
- For a JSON-RPC **response or notification** the server accepts, it returns `202 Accepted`
  with no body; if it cannot accept it, it returns an HTTP error.
- A GET for server-to-client messages either returns SSE or `405 Method Not Allowed`. A
  405 means "no server-initiated stream" — it is legal; do not retry-loop on it.

## Session lifecycle (400 / 404 / DELETE)

If the server assigns `Mcp-Session-Id` in the `InitializeResult` headers, the client must
echo it on every subsequent request. The value is visible ASCII (0x21–0x7E); header names
are case-insensitive but standardize on `Mcp-Session-Id`.

| Condition | Meaning | Action |
| --- | --- | --- |
| Non-init request without `Mcp-Session-Id` | Server requires a session | Send the id from `initialize` (→ 400 if missing) |
| Request with a stale/terminated id → **404** | Session expired/terminated, or hit a replica that never saw it | Reinitialize: new `InitializeRequest` with **no** session header |
| Client wants to end the session | Clean teardown | HTTP `DELETE` with the id; server may answer `405` if it disallows client termination |

`404 → reinitialize-without-session-id` is a real bug class — several clients/SDKs fail to
do it and get permanently stuck. If a proxy/CDN strips `Mcp-Session-Id`, allowlist the
header. Server-side, a 404 after scale-in usually means no sticky sessions / no shared
session store.

## Protocol-version header (silent-downgrade trap)

Send `MCP-Protocol-Version: <negotiated version>` on every post-`initialize` HTTP request.

- If the header is **absent**, the server assumes `2025-03-26` — a silent downgrade that
  can change behaviour. Always set it explicitly.
- If the value is **invalid/unsupported**, the server returns `400 Bad Request`.

## SSE and resumability

Inspect SSE behaviour separately from cancellation:

- A disconnect is not a cancellation. To cancel, send the MCP cancellation notification.
- If resumability is implemented, each SSE event carries an `id` that is globally unique
  within the session and encodes its originating stream.
- Resume by reconnecting with an HTTP GET carrying `Last-Event-ID`; the server replays only
  messages from the **same** stream after that id and must not replay across streams.
- The server must send each JSON-RPC message on exactly one stream — never broadcast the
  same message across multiple streams.

## Backwards-compat transport detection

To tell a modern Streamable HTTP server from a deprecated (2024-11-05) HTTP+SSE server
when you only have a URL:

1. POST `initialize` with the dual `Accept` header. Success → Streamable HTTP (one
   endpoint for POST and GET).
2. On `400/404/405`, issue a GET and look for an SSE `endpoint` event as the first event →
   legacy HTTP+SSE (separate GET `/sse` stream + a POST message endpoint named by that
   event).

`mcp-remote --transport http-only|sse-only|http-first|sse-first` forces a mode when
auto-detection misbehaves (see `remote-and-auth.md`).

## 2025-11-25 behaviour deltas

Recent changes that affect diagnosis (do not treat older behaviour as current):

- An invalid `Origin` on Streamable HTTP returns **HTTP 403 Forbidden** (DNS-rebinding
  mitigation). Local servers should bind to `127.0.0.1`.
- Tool **input-validation** errors should be returned as Tool Execution Errors (`isError`
  result) so the model can self-correct — not as JSON-RPC protocol errors. See
  `tool-resource-prompt-checks.md`.
- **JSON Schema 2020-12** is the default dialect for tool schemas (relevant to schema
  mismatch / `-32602`).
- `stderr` may carry **all** log levels, not just errors — do not assume stderr means a
  failure.
