# Local stdio Server Deep-Dive

Use this reference when a local (stdio) server is absent, drops after connecting, or starts
but misbehaves. It consolidates launcher, exit-code, stdout-contamination, env/cwd,
build-staleness, and permission facts. For Claude Desktop paths/logs see
`claude-desktop.md`; for transport/protocol mechanics see `protocol-and-transport.md`; for
remote servers see `remote-and-auth.md`.

Hand-written summary reconciled with modelcontextprotocol.io (legacy/tools/debugging and
docs/develop/connect-local-servers) on 2026-06-24; re-verify upstream.

## Contents

- Launcher matrix and failure modes
- Prove the server starts
- Exit-code triage
- stdout contamination (the #1 connects-then-drops cause)
- env / PATH / cwd divergence
- Build-output staleness
- Permissions (EACCES)
- Tool-call timeout / hang
- Reading client logs
- Old patterns

## Launcher matrix and failure modes

| Launcher | Direct-launch command | Typical pitfall |
| --- | --- | --- |
| node | `node /abs/build/index.js` | wrong/stale build path; not on the client's PATH |
| python | `python /abs/server.py` | venv not active; `PYTHONPATH`/site-packages differ |
| uv | `uv run --directory /abs/project <entry>` | missing `--directory` runs the wrong project; PATH-sensitive |
| uvx | `uvx <package> [args]` | run-without-install needs network the first time; usually a native `.exe` |
| npx | `npx -y <package> [args]` | Windows `.cmd` shim → `spawn ENOENT/EINVAL` (use `cmd /c`) |

The Windows `.cmd`-shim spawn failure is specific to the npm family (`npx`/`npm`/`pnpm`/
`yarn`); `uv`/`uvx` ship a native `.exe` and need `cmd /c` only if installed as a Scripts
shim. For the `cmd /c` wrapper and PATH-inheritance details see `claude-desktop.md`.

## Prove the server starts

Run the exact `command`/`args`/`env` from the client config, with absolute paths, in a
terminal:

```bash
node /abs/build/index.js 2>&1 | tee server.log
```

A healthy stdio server then appears to hang — it is blocking on stdin waiting for
newline-delimited JSON-RPC. That is normal. If it exits, capture why:

```bash
node /abs/build/index.js >/dev/null 2>&1 ; echo "exit=$?"
```

Then reproduce the full lifecycle in MCP Inspector:

```bash
npx -y @modelcontextprotocol/inspector node /abs/build/index.js
```

## Exit-code triage

When the client spawns the server, a missing/unlaunchable command appears as a
`spawn ENOENT`/`EINVAL` error event in the client log (no child exit code). When you run the
command yourself, read the exit code:

| Signal | Meaning | Next step |
| --- | --- | --- |
| 0 / never exits | Healthy (blocks on stdin) | Debug features, not startup |
| `spawn ENOENT`/`EINVAL` (client log) | Could not find/launch the command | Windows: `cmd /c` or absolute `node.exe`/`python.exe` |
| Exit 1 (or 9009 on cmd.exe) | Unhandled exception, or "command not recognized" | Read stderr / `mcp-server-<NAME>.log` |
| Exit 127 (bash / macOS / Linux only) | Command not found | Fix launcher or PATH |
| Exits immediately after start | Missing `await server.connect(transport)`, or threw in init | Connect the transport; add missing env |

## stdout contamination (the #1 connects-then-drops cause)

stdout must carry only JSON-RPC. Any banner, log, or progress line breaks framing. The
definitive test pipes stdout only and looks for non-JSON:

```bash
node server.js 2>/dev/null | head        # any non-JSON line is contamination
node server.js 2>/dev/null | od -c | head # to see hidden/leading bytes
```

PowerShell equivalent (the dominant Windows shell):

```powershell
node server.js 2>$null | Select-Object -First 20      # any non-JSON line is contamination
node server.js 2>$null | Format-Hex | Select-Object -First 4   # see leading/hidden bytes
```

Move all diagnostics to stderr: Node `console.error`; Python `logging` with
`stream=sys.stderr` (or `print(..., file=sys.stderr)`); Java/Spring disable the banner and
the stdout console appender. Ensure any child process's stdout does not leak into the
server's stdout.

## env / PATH / cwd divergence

If the command works in your shell but fails inside the client, the environment differs:

- stdio servers inherit only a limited, platform-dependent env subset — the interactive
  shell PATH and rc-file exports are not inherited. Add every required variable under the
  server's `env` key.
- The working directory may be undefined (often `/` on macOS). Replace all relative paths
  (script, data dirs, `.env`) with absolute paths.
- For a Python venv, invoke the venv interpreter by absolute path, or use
  `uv run --directory /abs/project <entry>` instead of relying on an activated shell.

## Build-output staleness

A new tool not appearing, or a fixed bug still reproducing, usually means the config runs
old build output:

```bash
ls -la dist/server.js src/server.ts        # compare timestamps (mac/Linux)
npm run build                              # or npm run watch during development
find . -type d -name __pycache__ -exec rm -r {} +   # clear stale .pyc (or run python -B)
```

Confirm `args` points at the freshly built output, then full-restart the client and
re-list tools in Inspector.

## Permissions (EACCES)

`spawn EACCES` / "permission denied" means a non-executable launcher or script, or an
unwritable output directory:

```bash
ls -l server.js ; ls -l "$(which node)"
chmod +x server.js                         # for shebang-launched entrypoints
```

Or invoke via an explicit interpreter (`node script.js` / `python script.py`) to sidestep
the exec bit, and fix ownership/permissions for any path the server writes to.

## Tool-call timeout / hang

The connection stays up but a tool call spins and times out:

- Add stderr timing logs (start/end + request id) around the handler to find where it blocks.
- Reproduce the single call in MCP Inspector to isolate it from the host.
- Wrap async work in a timeout (`Promise.race` with a timer) and return a tool error on
  expiry; add explicit timeouts to upstream HTTP calls. For legitimately long work, stream
  progress notifications instead of one long blocking call.

## Reading client logs

For Claude Desktop, `mcp.log` holds general connection events and `mcp-server-<NAME>.log`
holds that server's stderr — read the per-server file for crashes. For Claude Code,
`claude --debug mcp` prints the spawn line and the immediate cause, and `claude mcp get
<name>` shows the exact command/args. Redact API keys, tokens, and session ids before
sharing any excerpt.

## Old patterns

- The deprecated 2024-11-05 HTTP+SSE transport (two endpoints) is remote-only; see
  `protocol-and-transport.md` for detecting it. Not relevant to local stdio.
- Older guidance "use an absolute path to `npx.cmd`" no longer works on patched Node — use
  `cmd /c` instead (`claude-desktop.md`).
