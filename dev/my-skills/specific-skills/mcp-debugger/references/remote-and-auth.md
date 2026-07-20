# Remote MCP and OAuth Debugging

Use this reference for remote (HTTP) MCP servers: probing an endpoint, network-layer
failures, the OAuth 2.1 discovery chain, and the `mcp-remote` bridge and hosted
connectors. For transport mechanics (sessions, protocol-version header, SSE,
backwards-compat detection) see `protocol-and-transport.md`. For per-client setup see
`clients.md`.

Authorization applies to HTTP transports only. stdio servers should read credentials
from their environment, not OAuth. Reconciled with the MCP spec (stable revision
2025-11-25) on 2026-06-24; re-verify against modelcontextprotocol.io.

## Contents

- Probe a remote endpoint first
- Network-layer failures (DNS, TLS, proxy, CORS)
- OAuth discovery chain (the causal path)
- WWW-Authenticate: 401 vs 403 and step-up
- Resource / audience binding (RFC 8707)
- Client registration: pre-registered, CIMD, DCR
- PKCE and redirect/callback
- Token vs session, refresh, and expiry
- Security anti-patterns
- The mcp-remote bridge (stdio client → remote URL)
- Hosted connectors (Claude.ai / Claude Desktop)
- Quick symptom → cause → fix

## Probe a remote endpoint first

Gather evidence before editing code. Run the bundled probe (no OAuth exchange, no
mutation; redacts secrets):

```bash
python scripts/mcp_http_probe.py https://mcp.example.com/mcp
python scripts/mcp_http_probe.py https://mcp.example.com/mcp --header "Authorization: Bearer $TOKEN"
```

It reports HTTP status, `Content-Type`, captured `Mcp-Session-Id`, negotiated
`protocolVersion`, tool names, and — on a 401 — the `WWW-Authenticate` challenge plus
the Protected Resource Metadata it points to. Exit code 2 means auth is required.

The equivalent raw curl handshake, when a tool other than the script is preferred:

```bash
# 1) initialize — capture status + headers with -D -
curl -s -D - -X POST "$MCP" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'

# 2) extract the session id (header name is case-insensitive)
SESSION_ID=$(curl -s -D - -X POST "$MCP" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" -d '{...initialize...}' \
  | grep -i 'mcp-session-id' | cut -d' ' -f2 | tr -d '\r')

# 3) notifications/initialized (expect HTTP 202, no body)
curl -s -X POST "$MCP" -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 4) tools/list — reuse the session id and protocol-version header
curl -s -X POST "$MCP" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" -H "MCP-Protocol-Version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

A bare `curl -v "$MCP"` (or `openssl s_client`) isolates failures below the HTTP layer.

## Network-layer failures (DNS, TLS, proxy, CORS)

Map the error before suspecting MCP:

| Error | Layer | Cause and fix |
| --- | --- | --- |
| `ENOTFOUND` / getaddrinfo | DNS | Host does not resolve. Check spelling; check split-horizon/VPN DNS. `nslookup host`. |
| `ECONNREFUSED` | TCP | Nothing listening, wrong port, or firewall RST. `curl -v https://host/mcp`. |
| `ETIMEDOUT` | TCP/proxy | Packets dropped by a firewall, or a corporate proxy is not configured. |
| `self-signed` / `unable to verify leaf signature` | TLS | Corporate/MITM CA not trusted. For Node bridges set `NODE_EXTRA_CA_CERTS=/path/ca.pem`. Use `NODE_TLS_REJECT_UNAUTHORIZED=0` (or the probe's `--no-verify`) only as a last-resort diagnostic, never in production. |
| 403 only from a browser client | CORS / Origin | Server validates `Origin` (DNS-rebinding mitigation) and rejects it, or CORS headers are missing. |

Inspect the certificate chain:

```bash
openssl s_client -connect host:443 -servername host </dev/null \
  | openssl x509 -noout -issuer -subject -dates
```

Behind a corporate proxy, set `HTTPS_PROXY` but always add
`NO_PROXY=localhost,127.0.0.1` so local MCP traffic is not proxied. CORS only affects
browser-based clients — a desktop/CLI client failing is not a CORS problem. Servers
must expose `Mcp-Session-Id` through any CDN/proxy or the session breaks.

## OAuth discovery chain (the causal path)

A remote server that needs auth returns `401` with a `WWW-Authenticate` header that
points to its metadata. Walk the chain:

1. **Unauthenticated request → 401.** Read `WWW-Authenticate`; it should contain
   `resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"`.
   A 401 with **no** `WWW-Authenticate` header is the single most common cause of a 401
   loop — the client cannot learn where to authenticate.

2. **GET the Protected Resource Metadata (RFC 9728).** Use the URL from the challenge,
   or probe the well-known paths (path-suffixed form first for sub-path servers):

   ```bash
   curl -i https://mcp.example.com/.well-known/oauth-protected-resource/mcp
   curl -i https://mcp.example.com/.well-known/oauth-protected-resource
   ```

   It must return `authorization_servers` (array, ≥1) and `resource`. If this document
   itself returns 401, it was wrongly placed behind the auth middleware — serve it
   unauthenticated.

3. **GET the Authorization Server metadata.** Take the issuer from
   `authorization_servers` and try, in priority order. Issuer with **no path**:

   ```bash
   curl -i https://auth.example.com/.well-known/oauth-authorization-server
   curl -i https://auth.example.com/.well-known/openid-configuration
   ```

   Issuer **with a path** (e.g. `https://auth.example.com/tenant1`), try in order:
   `/.well-known/oauth-authorization-server/tenant1`, then
   `/.well-known/openid-configuration/tenant1`, then
   `/tenant1/.well-known/openid-configuration`. Clients must support both OAuth (RFC
   8414) and OpenID Connect discovery.

4. **Validate the metadata.** The `issuer` value inside the returned document must
   exactly equal the issuer URL used to fetch it (RFC 8414 §3.3) — a top cause of
   strict-client discovery failures with path-based issuers (Okta/Keycloak/Clerk custom
   domains). Confirm `authorization_endpoint`, `token_endpoint`, `jwks_uri`,
   `registration_endpoint` (if DCR), and `code_challenge_methods_supported` (PKCE) are
   present.

## WWW-Authenticate: 401 vs 403 and step-up

The status code tells the client what to do:

- **401 Unauthorized** = no token or an invalid/expired token → (re)authenticate.
  `WWW-Authenticate: Bearer resource_metadata="...", scope="files:read"`
- **403 Forbidden** = a valid token that lacks required scope → step-up authorization.
  `WWW-Authenticate: Bearer error="insufficient_scope", scope="files:read files:write", resource_metadata="..."`

On a 403, parse the `scope=` hint (it is authoritative — do not assume it is a subset of
`scopes_supported`), re-authorize requesting the challenged scopes **plus** the scopes
already granted, then retry the original request a bounded number of times. An unbounded
retry is itself the bug. A 403 that omits the `scope=` hint leaves the client unable to
recover — fix the server to include it.

## Resource / audience binding (RFC 8707)

A token issued for the wrong audience validates structurally but the server rejects it.

- The client must send `resource=<canonical-server-URI>` in **both** the authorization
  and token requests (and on refresh), even if the AS appears not to support it.
- Canonical URI rules: lowercase scheme/host, no fragment, prefer no trailing slash.
  `https://mcp.example.com`, `https://mcp.example.com/`, and `https://mcp.example.com/mcp`
  are three different audiences.
- Decode the access token's `aud` claim (base64url the middle JWT segment) and compare
  it byte-for-byte to the server's expected URI and to the `resource` field in the
  Protected Resource Metadata — all three must agree.
- If the AS ignores the `resource` parameter and mints `aud = <the AS itself>`, the
  server correctly refuses the token; switch to an AS that honours audience binding.

## Client registration: pre-registered, CIMD, DCR

Priority order in the 2025-11-25 spec: pre-registered `client_id` > Client ID Metadata
Documents (when `client_id_metadata_document_supported: true`) > Dynamic Client
Registration (when `registration_endpoint` is present) > prompt the user. DCR was
demoted from SHOULD (2025-06-18) to MAY.

Test DCR (RFC 7591) manually:

```bash
curl -X POST https://auth.example.com/register \
  -H "Content-Type: application/json" \
  -d '{"client_name":"probe","redirect_uris":["http://localhost:9877/callback"],
       "grant_types":["authorization_code","refresh_token"],
       "response_types":["code"],"token_endpoint_auth_method":"none"}'
```

Common failures:

- `does not support dynamic client registration` / no `registration_endpoint` → fall
  back to a configured static `client_id` or Client ID Metadata Documents.
- `invalid_redirect_uri` → the registered URI must exactly match the callback used at
  authorize time (scheme/host/port/path); register both `localhost` and `127.0.0.1`
  variants if either may be used.
- `invalid_client_metadata` → inconsistent `grant_types`/`response_types`; public/native
  clients use `token_endpoint_auth_method: "none"`.
- `invalid_scope` after reusing a cached registration → re-register with the superset of
  scopes you will request; clear stale client credentials.

## PKCE and redirect/callback

- PKCE is mandatory; use `S256`. The client must confirm
  `code_challenge_methods_supported` is present in the AS/OIDC metadata and refuse to
  proceed if it is absent.
- Redirect URIs must be loopback or HTTPS (OAuth 2.1), pre-registered, and validated by
  exact match. Bind the callback listener to the registered port **before** opening the
  browser.
- Generate a cryptographically random `state` per request and reject callbacks whose
  `state` does not match (single-use, short TTL). A missing/mismatched `state` aborts the
  flow.

## Token vs session, refresh, and expiry

Separate the two failure axes — they are routinely confused:

- **HTTP 404 carrying an old `Mcp-Session-Id`** → the transport session expired or the
  request hit a replica that never saw it. Reinitialize the session (new
  `InitializeRequest`, no session header). This is **not** an auth problem.
- **HTTP 401 after idle** → the access token expired. Check `exp`; refresh and retry once.

Refresh manually to confirm the AS behaviour (include `resource` so the refreshed token
keeps the right audience):

```bash
curl -X POST <token_endpoint> \
  -d 'grant_type=refresh_token&refresh_token=...&resource=https%3A%2F%2Fmcp.example.com&client_id=...'
```

Public clients must rotate refresh tokens (store the new one each time). Confirm the
client persists tokens across restarts; some silently fail to reload and re-trigger a
full auth or appear to fail on reconnect.

## Security anti-patterns

These are spec violations and frequent security-review findings — flag them when seen:

- **Token passthrough is forbidden.** A server must reject any token whose `aud` is not
  itself and must never forward the client's token to a downstream API. It must obtain a
  separate upstream token as its own OAuth client.
- **Confused deputy.** A proxy with a static upstream `client_id` + client DCR + a
  third-party consent cookie lets a malicious dynamically-registered client skip consent
  and steal the auth code. Mitigate with per-client server-side consent before
  forwarding, exact `redirect_uri` match, and single-use `state`.
- **SSRF during discovery.** When the client runs server-side, a malicious server can
  point `resource_metadata`/`authorization_servers`/`token_endpoint` at internal IPs.
  Require HTTPS (loopback exempt in dev), block private/link-local ranges
  (10/8, 172.16/12, 192.168/16, 127/8, 169.254/16, fc00::/7, fe80::/10), and beware DNS
  rebinding (TOCTOU) and redirect chains.

## The mcp-remote bridge (stdio client → remote URL)

stdio-only desktop clients (Claude Desktop, Cursor, Windsurf) cannot speak Streamable
HTTP/SSE directly. `mcp-remote` bridges a stdio subprocess to a remote URL and handles
the OAuth flow:

```json
{ "mcpServers": { "remote": { "command": "npx", "args": ["mcp-remote", "https://server/mcp"] } } }
```

(On Windows wrap as `"command": "cmd", "args": ["/c", "npx", "mcp-remote", "https://server/mcp"]` — see `claude-desktop.md`.)

- Tokens and logs live in `~/.mcp-auth` (override with `MCP_REMOTE_CONFIG_DIR`). Reset a
  stuck OAuth state with `rm -rf ~/.mcp-auth`, then fully restart the client.
- `--debug` writes `~/.mcp-auth/{server_hash}_debug.log`.
- Test the bridge + auth standalone: `npx -p mcp-remote@latest mcp-remote-client https://server/mcp`.
- Flags: `--header "Authorization: Bearer <token>"` (API-key servers),
  `--transport http-only|sse-only|http-first|sse-first`, `--allow-http` (non-HTTPS on
  trusted networks), `--static-oauth-client-metadata`/`--static-oauth-client-info`
  (servers without DCR). Default OAuth callback port is 3334; override with a positional
  port after the URL if it is taken. Requires Node 18+ (the GUI app uses system Node).
- On Windows/Cursor an arg-spacing bug can split a `--header` value; put the value in an
  env var and reference it (`--header "Authorization:${AUTH}"` with `AUTH="Bearer ..."`).

## Hosted connectors (Claude.ai / Claude Desktop)

These connect from Anthropic's cloud, not the local device — the server must be reachable
over the public internet over HTTPS.

- If the server is on a private network/VPN/firewall, allowlist Anthropic's IP ranges
  (platform.claude.com IP-addresses doc). Validate end-to-end with the probe and the MCP
  Inspector before adding the connector.
- Prefer Streamable HTTP; legacy HTTP+SSE is being phased out.
- OAuth callback is `https://claude.ai/api/mcp/auth_callback` (Claude Code uses a loopback
  redirect instead). Use DCR or set a static OAuth Client ID/Secret under the connector's
  Advanced settings; `resource`/audience must equal the server URL, and the Protected
  Resource Metadata must list at least one `authorization_servers` entry.
- Hosted surfaces cap tool results at ~150,000 characters with a ~300-second timeout.
- On Team/Enterprise, an Owner must add the connector at the organisation level before
  members can connect. If OAuth broke right after a desktop update, treat it as a client
  version issue and check the app version.

## Quick symptom → cause → fix

| Symptom | Likely cause | First move |
| --- | --- | --- |
| 401, then retries forever | No `WWW-Authenticate` / no `resource_metadata` pointer; or PRM behind auth | Add the header; serve PRM unauthenticated |
| 401 with a token attached | Expired, wrong `aud`, bad signature, or foreign issuer | Decode `aud`/`exp`/`iss`; refresh; check jwks |
| 403 `insufficient_scope` | Valid token, missing scope | Step-up with challenged + existing scopes |
| `could not discover authorization server` | Missing/sub-path PRM, or issuer mismatch | Probe well-known paths; check RFC 8414 §3.3 |
| `does not support dynamic client registration` | No `registration_endpoint` | Use static `client_id` or CIMD |
| 404 after idle | Transport session expired | Reinitialize without the old `Mcp-Session-Id` |
| Connects with curl, not from Claude.ai | Server not publicly reachable | Expose over HTTPS; allowlist Anthropic IPs |
