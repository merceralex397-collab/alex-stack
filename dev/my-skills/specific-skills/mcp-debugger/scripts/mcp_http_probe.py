#!/usr/bin/env python3
"""Probe a remote (Streamable HTTP) MCP endpoint and report evidence.

This gathers evidence only. It performs the MCP initialize handshake, captures
the session id and negotiated protocol version, surfaces a 401 auth challenge
(and the OAuth Protected Resource Metadata it points to), and lists tools. It
performs NO OAuth token exchange and NO state mutation beyond the standard
initialize -> notifications/initialized -> tools/list read sequence.

Stdlib only (urllib + ssl); runs anywhere Python 3.8+ is present. Secrets in
echoed headers (bearer tokens, session ids) are redacted.

Examples:
  python scripts/mcp_http_probe.py https://mcp.example.com/mcp
  python scripts/mcp_http_probe.py https://mcp.example.com/mcp --header "Authorization: Bearer $TOKEN"
  python scripts/mcp_http_probe.py https://mcp.example.com/mcp --protocol-version 2025-11-25

Exit codes: 0 = handshake succeeded; 2 = auth required (401); 1 = any other failure.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_PROTOCOL_VERSION = "2025-11-25"

# Header names that carry secrets and must be redacted before printing.
SECRET_HEADERS = ("authorization", "mcp-session-id", "x-api-key", "cookie", "set-cookie")


def redact_header(name: str, value: str) -> str:
    if name.lower() in SECRET_HEADERS:
        return "<redacted>"
    return value


def redact_text(text: str) -> str:
    text = re.sub(r"(?i)(Bearer)\s+[A-Za-z0-9._~+/=-]+", r"\1 <redacted>", text)
    text = re.sub(r"sk-[A-Za-z0-9_-]{12,}", "sk-<redacted>", text)
    text = re.sub(r"\b(gh[posru]_|github_pat_)[A-Za-z0-9_]+", r"\1<redacted>", text)
    text = re.sub(r"\bxox[baprs]-[A-Za-z0-9-]+", "xox-<redacted>", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "<jwt-redacted>", text)
    text = re.sub(r"(?i)(mcp-session-id\s*[:=]\s*)\S+", r"\1<redacted>", text)
    text = re.sub(
        r"(?i)(api[_-]?key|token|secret|password|authorization)([\"'\s:=]+)([^,\s\"']+)",
        r"\1\2<redacted>",
        text,
    )
    return text


def build_ssl_context(no_verify: bool) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if no_verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def headers_to_dict(msg: Any) -> dict[str, str]:
    """Lower-cased header dict, preserving multi-valued auth/cookie headers."""
    out = {k.lower(): v for k, v in msg.items()}
    for multi in ("www-authenticate", "set-cookie"):
        values = msg.get_all(multi)
        if values and len(values) > 1:
            out[multi] = " , ".join(values)
    return out


def do_request(
    method: str,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any] | None,
    ctx: ssl.SSLContext,
    timeout: float,
) -> tuple[int, dict[str, str], bytes]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.status, headers_to_dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:  # 4xx/5xx still carry headers + body
        return exc.code, headers_to_dict(exc.headers), exc.read()


def parse_jsonrpc_body(content_type: str, raw: bytes) -> dict[str, Any] | None:
    """Return the JSON-RPC object from a JSON or SSE (text/event-stream) body."""
    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        return None
    if "text/event-stream" in content_type.lower():
        # Group into SSE events on blank lines; an event's `data:` lines join with \n.
        for event in re.split(r"\r?\n\r?\n", text):
            data_lines = []
            for line in event.splitlines():
                if line.startswith("data:"):
                    value = line[5:]
                    data_lines.append(value[1:] if value.startswith(" ") else value)
            if not data_lines:
                continue
            try:
                return json.loads("\n".join(data_lines))
            except json.JSONDecodeError:
                continue
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def session_id_from(headers: dict[str, str]) -> str | None:
    return headers.get("mcp-session-id")


def print_headers(headers: dict[str, str], keys: tuple[str, ...]) -> None:
    for key in keys:
        if key in headers:
            print(f"  {key}: {redact_header(key, headers[key])}")


def classify_network_error(exc: Exception) -> str:
    if isinstance(exc, ssl.SSLCertVerificationError):
        return (
            "TLS certificate not trusted. Likely a corporate/MITM CA. Point Node-based "
            "bridges at the CA bundle with NODE_EXTRA_CA_CERTS=/path/ca.pem; for this "
            "probe re-run with --no-verify (diagnostic only, never in production)."
        )
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, socket.gaierror):
            return "DNS resolution failed (ENOTFOUND/getaddrinfo). Check the hostname and split-horizon/VPN DNS."
        if isinstance(reason, ConnectionRefusedError):
            return "Connection refused (ECONNREFUSED). Nothing is listening on that host/port, or a firewall sent RST."
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return "Timed out (ETIMEDOUT). Packets dropped by a firewall, or a proxy is not configured. Set HTTPS_PROXY and NO_PROXY=localhost,127.0.0.1 if behind a corporate proxy."
        return f"Network error: {reason}"
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "Timed out (ETIMEDOUT). Packets dropped by a firewall, or a proxy is not configured."
    return f"Error: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe a remote Streamable HTTP MCP endpoint (evidence only).")
    parser.add_argument("url", help="MCP endpoint URL, e.g. https://mcp.example.com/mcp")
    parser.add_argument("--header", action="append", default=[], metavar="'Name: value'",
                        help="Extra request header (repeatable), e.g. --header 'Authorization: Bearer ...'")
    parser.add_argument("--protocol-version", default=DEFAULT_PROTOCOL_VERSION,
                        help=f"protocolVersion to offer (default {DEFAULT_PROTOCOL_VERSION})")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-request timeout in seconds")
    parser.add_argument("--no-verify", action="store_true",
                        help="Disable TLS verification (diagnostic only; never in production)")
    args = parser.parse_args()

    extra_headers: dict[str, str] = {}
    for item in args.header:
        if ":" not in item:
            print(f"ISSUE: --header '{item}' is not in 'Name: value' form.")
            return 1
        name, value = item.split(":", 1)
        if not name.strip():
            print(f"ISSUE: --header '{item}' has an empty header name.")
            return 1
        extra_headers[name.strip()] = value.strip()

    ctx = build_ssl_context(args.no_verify)
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    base_headers.update(extra_headers)

    init_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": args.protocol_version,
            "capabilities": {},
            "clientInfo": {"name": "mcp-http-probe", "version": "1.0.0"},
        },
    }

    print(f"MCP HTTP probe -> {args.url}")
    print(f"Offered protocolVersion: {args.protocol_version}")
    print("\n[1] initialize (POST)")
    try:
        status, headers, raw = do_request("POST", args.url, base_headers, init_body, ctx, args.timeout)
    except Exception as exc:  # noqa: BLE001 - surface network layer clearly
        print(f"  FAILED before HTTP response.\n  {classify_network_error(exc)}")
        return 1

    print(f"  HTTP {status}")
    print_headers(headers, ("content-type", "mcp-session-id", "mcp-protocol-version"))

    if status == 401:
        print("\n  401 Unauthorized -> the server requires OAuth.")
        www = headers.get("www-authenticate")
        if www:
            print(f"  WWW-Authenticate: {www}")
            match = re.search(r'resource_metadata="?([^",\s]+)"?', www)
            if match:
                prm_url = match.group(1)
                host = urllib.parse.urlparse(prm_url).hostname or ""
                if not (prm_url.lower().startswith("https://") or host in ("localhost", "127.0.0.1", "::1")):
                    print(f"\n  Refusing to fetch non-HTTPS metadata URL (SSRF/downgrade guard): {prm_url}")
                    return 2
                print(f"\n[2] Protected Resource Metadata (GET {prm_url})")
                try:
                    pstatus, _, praw = do_request("GET", prm_url, {"Accept": "application/json"}, None, ctx, args.timeout)
                    print(f"  HTTP {pstatus}")
                    meta = parse_jsonrpc_body("application/json", praw)
                    if isinstance(meta, dict):
                        print(f"  authorization_servers: {meta.get('authorization_servers')}")
                        print(f"  resource: {meta.get('resource')}")
                        print(f"  scopes_supported: {meta.get('scopes_supported')}")
                    print("\n  Next: fetch <issuer>/.well-known/oauth-authorization-server (or .../openid-configuration)")
                    print("  See references/remote-and-auth.md for the full discovery chain.")
                except Exception as exc:  # noqa: BLE001
                    print(f"  Could not fetch PRM: {classify_network_error(exc)}")
            else:
                print("  No resource_metadata= pointer in the challenge. The client cannot discover the")
                print("  authorization server. See references/remote-and-auth.md (401-loop section).")
        else:
            print("  No WWW-Authenticate header on the 401 -> the #1 cause of an OAuth 401 loop.")
            print("  See references/remote-and-auth.md.")
        return 2

    body = parse_jsonrpc_body(headers.get("content-type", ""), raw)
    if status >= 400 or not isinstance(body, dict) or "result" not in body:
        print("  initialize did not return a result.")
        snippet = redact_text(raw.decode("utf-8", errors="replace"))[:600]
        print(f"  Body (truncated, redacted): {snippet}")
        if status == 406:
            print("  406 Not Acceptable -> confirm Accept includes BOTH application/json and text/event-stream.")
        return 1

    result = body["result"]
    print(f"  negotiated protocolVersion: {result.get('protocolVersion')}")
    server_info = result.get("serverInfo", {})
    print(f"  serverInfo: {server_info.get('name')} {server_info.get('version', '')}".rstrip())
    print(f"  server capabilities: {sorted(result.get('capabilities', {}).keys())}")

    session_id = session_id_from(headers)
    # The version is server-controlled and is reflected into a request header, so
    # reject anything that is not a clean date-like token (no CR/LF injection).
    raw_version = result.get("protocolVersion", args.protocol_version)
    negotiated_version = raw_version if (isinstance(raw_version, str) and re.fullmatch(r"[0-9A-Za-z._-]{1,40}", raw_version)) else args.protocol_version

    follow_headers = dict(base_headers)
    if session_id:
        follow_headers["Mcp-Session-Id"] = session_id
        print("  (captured Mcp-Session-Id for subsequent requests)")
    follow_headers["MCP-Protocol-Version"] = negotiated_version

    print("\n[2] notifications/initialized (POST, expect 202)")
    try:
        nstatus, _, _ = do_request(
            "POST", args.url, follow_headers,
            {"jsonrpc": "2.0", "method": "notifications/initialized"}, ctx, args.timeout,
        )
        print(f"  HTTP {nstatus}" + ("  (accepted)" if nstatus == 202 else ""))
    except Exception as exc:  # noqa: BLE001
        print(f"  {classify_network_error(exc)}")

    print("\n[3] tools/list (POST)")
    try:
        tstatus, theaders, traw = do_request(
            "POST", args.url, follow_headers,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, ctx, args.timeout,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  {classify_network_error(exc)}")
        return 1

    print(f"  HTTP {tstatus}")
    if tstatus == 404:
        print("  404 with a session id -> the session expired/terminated. Reinitialize WITHOUT the old")
        print("  Mcp-Session-Id (this is a transport-session problem, not auth).")
        return 1
    tools_body = parse_jsonrpc_body(theaders.get("content-type", ""), traw)
    if isinstance(tools_body, dict) and isinstance(tools_body.get("result"), dict):
        tools = tools_body["result"].get("tools", [])
        names = [(t.get("name", "?") if isinstance(t, dict) else "?") for t in tools[:40]]
        print(f"  {len(tools)} tool(s): " + ", ".join(names))
    else:
        print(f"  Unexpected tools/list body (redacted): {redact_text(traw.decode('utf-8', errors='replace'))[:400]}")
        return 1

    print("\nHandshake OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
