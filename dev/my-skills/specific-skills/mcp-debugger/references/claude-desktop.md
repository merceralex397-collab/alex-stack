# Claude Desktop MCP Debugging

Use this reference when a server fails in Claude Desktop or behaves differently there than
in MCP Inspector or a terminal. For other hosts see `clients.md`; for local launcher and
exit-code detail see `debugging.md`. Reconciled 2026-06-24.

## Contents

- Config locations (incl. MSIX/LocalCache divergence)
- Config checks
- Windows launchers (the dominant native-Windows failure)
- GUI PATH inheritance
- Encoding and backslashes (BOM)
- Restart rules
- Server status UI
- Logs (mcp.log vs mcp-server-<NAME>.log)
- Exit-code triage
- Build-output staleness
- DevTools
- Common fixes and a Windows quick-fix list

## Config locations

```text
macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json
Windows: %APPDATA%\Claude\claude_desktop_config.json
```

**Windows MSIX/Store builds read a different file.** The packaged app reads config and
writes logs under
`%LOCALAPPDATA%\Packages\<PackageFamilyName>\LocalCache\Roaming\Claude\` (commonly
`Claude_pzs8sxrjxfjjc`), while the in-app **Edit Config** button opens the legacy
`%APPDATA%` copy via Electron, bypassing MSIX redirection. The two diverge, so edits land
in a file the app never reads — the classic "MCP silently stopped working after an update,
no error, no logs" case. Detect and locate the real file:

```powershell
Get-AppxPackage -Name "*Claude*" | Select-Object Name, PackageFamilyName
$pkg = (Get-AppxPackage -Name "*Claude*").PackageFamilyName
"$env:LOCALAPPDATA\Packages\$pkg\LocalCache\Roaming\Claude\claude_desktop_config.json"
```

`scripts/claude_desktop_diagnostics.py` probes both locations and reports which the app
actually reads.

Validate JSON before reading logs:

```powershell
Get-Content "$env:AppData\Claude\claude_desktop_config.json" -Raw | ConvertFrom-Json | Out-Null
```

```bash
jq . "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

Expected shape:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["C:/absolute/path/server/build/index.js"],
      "env": { "MY_API_KEY": "redacted" }
    }
  }
}
```

## Config checks

- Top-level object contains `mcpServers`; each server has a stable key and a `command`.
- Local script paths in `args` are absolute (not `./`, `~`, shell aliases, or cwd-relative).
- Windows paths use forward slashes (`C:/path/server.js`) or escaped backslashes
  (`C:\\path\\server.js`).
- Required credentials are in `env`, or a config file referenced by absolute path.
- The configured command resolves from Claude's environment, not only from an interactive
  shell.

Find launcher paths:

```powershell
where.exe node ; where.exe npx ; where.exe uv ; where.exe uvx ; where.exe python
```

```bash
which node npx uv uvx python3
```

## Windows launchers (the dominant native-Windows failure)

On Windows, `npx`, `npm`, `pnpm`, and `yarn` are `.cmd` shims (e.g. `npx.cmd` in
`%APPDATA%\npm`); `uv`/`uvx` are usually native `.exe` (no shim) unless installed as
Scripts-dir shims. Node's `child_process.spawn` — which Claude Desktop uses — cannot launch
a `.cmd`/`.bat` without a shell, so a bare `"command": "npx"` fails with `spawn npx ENOENT`.
Since the April 2024 Node security releases (≥18.20.2/20.12.2/21.7.3, CVE-2024-27980 /
BatBadBut), spawning a `.cmd` without a shell throws `EINVAL` by design — so **an absolute
path to `npx.cmd` is not a fix either.**

Fixes:

```json
// Wrap a .cmd-shim launcher with cmd /c (cmd.exe is a real .exe; it resolves the shim)
{ "command": "cmd", "args": ["/c", "npx", "-y", "@scope/server"] }
// uvx is usually a native .exe and needs no wrapper; wrap it only if where.exe shows a .cmd
{ "command": "uvx", "args": ["server-name"] }

// Or bypass the shim entirely — point at the real binary plus the entry script
{ "command": "node", "args": ["C:/abs/path/server/build/index.js"] }
{ "command": "C:/Program Files/nodejs/node.exe", "args": ["C:/abs/server.js"] }
```

macOS/Linux do **not** need `cmd /c` (there `npx` is a real executable). A literal,
unexpanded `${APPDATA}` (or any `${VAR}`) reaching the launcher means the host did not
substitute the placeholder — replace it with a real absolute path. Separately, if `npx`
itself errors on a missing `APPDATA`, add
`"env": { "APPDATA": "C:\\Users\\<you>\\AppData\\Roaming\\" }` to that server. The same
`cmd /c` rule applies to `.cmd`-shim launchers in Claude Code, Cursor, VS Code, and Windsurf.

## GUI PATH inheritance

Claude Desktop inherits only the User+System environment present at launch. It does **not**
source PowerShell profiles, shell rc files, or version-manager shims (nvm-windows, fnm,
volta, asdf, mise). So a tool that works in your terminal can be invisible to the GUI. Fix
by pointing `command` at an absolute `node.exe`/`python.exe`, or set `env.PATH` explicitly
in the server entry to include the dirs holding `node`/`npx`/`uv`. Compare what the GUI
sees vs your shell:

```powershell
where.exe node ; where.exe python
[Environment]::GetEnvironmentVariable('Path','User'); [Environment]::GetEnvironmentVariable('Path','Machine')
```

## Encoding and backslashes (BOM)

JSON needs doubled backslashes (`C:\\path`); a single `\` either breaks parsing or creates
an escape (`C:\temp` → the `\t` becomes a TAB). Prefer forward slashes (`C:/path`), which
Node, Python, and Windows APIs all accept.

A UTF-8 BOM (bytes `EF BB BF`) at the file start can make a strict parser reject the config.
Windows Notepad "UTF-8", PowerShell 5.1 `Out-File`/`Set-Content -Encoding UTF8`, and some
IDEs add one by default. Detect and strip it:

```powershell
Format-Hex "$env:AppData\Claude\claude_desktop_config.json" | Select-Object -First 1   # leading EF BB BF = BOM
# PowerShell 7+ (the utf8NoBOM token does not exist in Windows PowerShell 5.1):
(Get-Content -Raw path.json) | Set-Content -Path path.json -Encoding utf8NoBOM
# Windows PowerShell 5.1 — the default shell, where the above errors:
[IO.File]::WriteAllText("path.json", (Get-Content -Raw path.json), (New-Object Text.UTF8Encoding($false)))
```

## Restart rules

After config or server-code changes, fully quit and reopen Claude Desktop — closing the
window is not enough. On Windows, also end lingering processes so the reload takes effect:

```powershell
# -Force avoids the confirmation prompt; Claude* also catches MSIX helper processes
Get-Process Claude* -ErrorAction SilentlyContinue | Stop-Process -Force
```

If compiled TypeScript changed, rebuild first (`npm run build`).

## Server status UI

In a chat, click the plus icon near the input, then hover the Connectors menu. Confirm the
server appears and its tools are listed. If no MCP UI appears, at least one server is
misconfigured or the config was not loaded.

## Logs

```text
macOS:   ~/Library/Logs/Claude
Windows: %APPDATA%\Claude\logs   (MSIX builds: under the LocalCache path above)
```

Two log files matter, and confusing them wastes time:

- **`mcp.log`** — general MCP connection events, config errors, and disconnects.
- **`mcp-server-<NAME>.log`** — that one server's captured **stderr**. This is the single
  most useful file for "connects then drops": it holds the crash/exception.

Follow the per-server log while reproducing:

```powershell
Get-Content "$env:AppData\Claude\logs\mcp-server-<NAME>.log" -Tail 100 -Wait
```

```bash
tail -n 100 -F "$HOME/Library/Logs/Claude/mcp-server-<NAME>.log"
```

## Exit-code triage

A launch failure shows up two different ways. When the **client** spawns the server, a
missing/unlaunchable command surfaces in `mcp.log` as a `spawn ... ENOENT`/`EINVAL` error
event — there is no child exit code. When you run the command **yourself** to reproduce,
read the exit code:

| Signal | Meaning | Next step |
| --- | --- | --- |
| 0 / never exits | Healthy — a stdio server blocks on stdin | Not a startup failure; debug features |
| `spawn ENOENT`/`EINVAL` (in `mcp.log`, no exit code) | Client could not find/launch the command | Windows: `cmd /c` or an absolute `node.exe`/`python.exe` |
| Exit 1 (or 9009 from cmd.exe) | Unhandled exception, or "command not recognized" | Read `mcp-server-<NAME>.log`; check the launcher/PATH |
| Exit 127 (bash / macOS / Linux only) | Command not found | Fix the launcher or PATH |
| Exits right after start | Missing `await server.connect(transport)`, or threw during init | Connect the transport; add missing env |

## Build-output staleness

If a new tool does not appear or a fixed bug still reproduces, the config likely runs stale
build output. Compare timestamps and rebuild, then full-restart:

```powershell
Get-Item dist\index.js, src\index.ts | Select-Object Name, LastWriteTime
```

```bash
npm run build            # or npm run watch during development
find . -type d -name __pycache__ -exec rm -r {} +   # Python: clear stale .pyc
```

Confirm the new tool appears in MCP Inspector before blaming the client.

## DevTools

Enable only when UI, client-side, or network behaviour matters.

```powershell
'{"allowDevTools": true}' | Set-Content "$env:AppData\Claude\developer_settings.json"
```

```bash
echo '{"allowDevTools": true}' > "$HOME/Library/Application Support/Claude/developer_settings.json"
```

Open with `Ctrl+Alt+I` (Windows) or `Cmd-Opt-I` (macOS). Two windows appear; use the main
content window's Console and Network panels.

## Common fixes and a Windows quick-fix list

- Server not listed: fix JSON, correct config path (check MSIX LocalCache), fully quit/reopen.
- `spawn ENOENT`/`EINVAL` on Windows for npx/uvx → wrap with `cmd /c` (not an absolute
  `.cmd` path).
- Works in terminal only → add missing env vars, remove cwd assumptions, use absolute paths
  and an absolute `node.exe`/`python.exe`.
- Starts then disconnects → check stdout contamination (the test is in `debugging.md`),
  build path, missing files, permissions, and read `mcp-server-<NAME>.log`.
- Tool missing → compare Inspector's list with Claude's; check registration, capabilities,
  and stale build.
- Tool fails only in Claude → compare Claude's arguments with Inspector's; refine the schema
  descriptions and required fields.

Windows symptom → cause shortcut: `ENOENT/EINVAL` → `.cmd` shim spawn (use `cmd /c`);
silent failure with no logs → MSIX/LocalCache path divergence; "invalid JSON" that looks
fine → UTF-8 BOM or a single backslash.
