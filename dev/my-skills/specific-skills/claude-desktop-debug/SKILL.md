---
name: claude-desktop-debug
description: >-
  Use this skill whenever a user reports any problem with the Claude Desktop application on
  Windows — including but not limited to: MCP tools or connectors not appearing in chat,
  extensions not loading (spinner, error badge, nothing shows), app showing a white or blank
  screen, app crashing on startup or at launch, Claude Desktop running slowly or freezing,
  models not available or missing from the model picker, authentication failing or looping,
  extensions such as collision-engineers-dvsa-mot or any DVSA / valuation connector not
  working, or any symptom described as "Claude Desktop broke", "my extension stopped working",
  "the app won't open", "I lost my tools", or "MCP isn't working". Trigger this skill even
  if the user does not mention MCP, extensions, or connectors by name — focus on the symptom.
version: 0.1.0
---

# Claude Desktop Diagnostics

You are helping a user diagnose a problem with the **Claude Desktop chat application** on Windows.
Work through the sections below in order. The decision tree in Section 2 routes to detailed
reference files — read them as needed.

---

## 1. Detect Install Type (Do This First)

Claude Desktop is distributed in two ways, and they use **different config and log paths**. Many
issues — especially "everything stopped working after an update" — trace directly to this. Always
identify the install type before reading any config or logs.

Run this in PowerShell:

```powershell
Get-AppxPackage -Name "*Claude*" | Select-Object Name, PackageFamilyName
```

| Result | Install type |
|---|---|
| Returns a package entry | **MSIX** (Store / new installer) |
| Returns nothing | **Standard** (Win32 / old installer) |

### Path quick-reference

| Resource | Standard path | MSIX path |
|---|---|---|
| Config | `%APPDATA%\Claude\claude_desktop_config.json` | `%LOCALAPPDATA%\Packages\<PFN>\LocalCache\Roaming\Claude\claude_desktop_config.json` |
| Logs dir | `%APPDATA%\Claude\logs\` | `%LOCALAPPDATA%\Packages\<PFN>\LocalCache\Roaming\Claude\logs\` |

Replace `<PFN>` with the `PackageFamilyName` from the command above (typically `Claude_pzs8sxrjxfjjc`).

> **MSIX gotcha:** The in-app "Edit Config" button opens the Standard path even on MSIX installs.
> Edits made there are silently ignored. Always use the MSIX path if detected.

To resolve the MSIX config path automatically:

```powershell
$pfn = (Get-AppxPackage -Name "*Claude*").PackageFamilyName
"$env:LOCALAPPDATA\Packages\$pfn\LocalCache\Roaming\Claude\claude_desktop_config.json"
```

---

## 2. Issue Decision Tree

| Symptom | Reference |
|---|---|
| MCP tools / connectors not appearing in the chat input area | [`references/mcp-tools-missing.md`](references/mcp-tools-missing.md) |
| Extension installed but not loading — spinner, error badge, nothing | [`references/extensions-not-loading.md`](references/extensions-not-loading.md) |
| App shows white / blank screen on launch | [`references/app-not-loading.md`](references/app-not-loading.md) |
| App crashes immediately at launch or on Windows startup | [`references/app-not-loading.md`](references/app-not-loading.md) |
| Keeps asking to log in / authentication loops | [`references/auth-and-models.md`](references/auth-and-models.md) |
| Models missing from model picker | [`references/auth-and-models.md`](references/auth-and-models.md) |
| App is slow, laggy, or freezes during use | [`references/performance.md`](references/performance.md) |

---

## 3. Quick Log Triage

Run these in PowerShell to pull the most relevant evidence immediately. Substitute the MSIX path
from Section 1 if needed.

```powershell
# MCP connection log — shows config errors, server disconnects, JSON parse failures
Get-Content "$env:AppData\Claude\logs\mcp.log" -Tail 30

# Per-server log — replace the name with your server or extension name
Get-Content "$env:AppData\Claude\logs\mcp-server-collision-engineers-dvsa-mot.log" -Tail 50

# See all log files and their sizes
Get-ChildItem "$env:AppData\Claude\logs\" |
  Sort-Object LastWriteTime -Descending |
  Select-Object Name, Length, LastWriteTime
```

If the logs directory is empty or missing, you are on an MSIX install — use the resolved path from
Section 1.

Relevant log files:

| Log file | What it records |
|---|---|
| `mcp.log` | All MCP connections, config load errors, JSON parse failures |
| `mcp-server-<name>.log` | stderr output from that specific server / extension process |
| `main.log` | Main Electron process events |
| `unknown-remote.log` | Cloud / remote session events |

---

## 4. Config Validation

A JSON syntax error in `claude_desktop_config.json` silently disables **all** MCP servers — no
error is shown in the UI, and `mcp.log` will be empty or terse. Always validate the config before
reading deeper.

```powershell
# Validate config JSON (Standard path — substitute MSIX path if needed)
Get-Content "$env:AppData\Claude\claude_desktop_config.json" -Raw | ConvertFrom-Json
```

If this throws an error, the JSON is broken. Common causes:

- **Trailing comma** — `"args": ["last-item",]` — not valid JSON
- **BOM (Byte Order Mark)** — Notepad on Windows adds an invisible BOM character at the start of
  UTF-8 files. It breaks JSON parsers. Re-save the file using VS Code or Notepad++ with encoding
  set to "UTF-8 without BOM".
- **Unmatched brackets** — missing `}` or `]` when adding a new server entry

A valid minimal config with one MCP server looks like:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["C:\\path\\to\\server.js"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

**Windows-specific:** `npx`-based servers must be wrapped in `cmd /c` — Claude Desktop spawns
processes without a shell, so bare `npx` fails with `ENOENT`:

```json
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\Alex\\Desktop"]
}
```

---

## 5. Extension Quick Check

For the `collision-engineers-dvsa-mot` extension (or any installed extension):

```powershell
# Check if extension bundle directories exist
Get-ChildItem "$env:AppData\Claude\" -Filter "dxt-install-*" | Select-Object Name

# Check if an extension server log was created (means the server at least started)
Get-ChildItem "$env:AppData\Claude\logs\" -Filter "mcp-server-*" | Select-Object Name
```

- If **no `dxt-install-*` directories** → the extension was never installed (or installed to the
  wrong path). See [`references/extensions-not-loading.md`](references/extensions-not-loading.md).
- If **no log file** for the extension → the server process never started. Read `mcp.log` for
  the load error, then see [`references/mcp-tools-missing.md`](references/mcp-tools-missing.md).

---

## 6. Developer Tools (DevTools)

DevTools is already enabled on this machine (`developer_settings.json` has `allowDevTools: true`).

Open with **Ctrl+Alt+I** inside Claude Desktop.

- **Console tab** — JavaScript errors from the app renderer; look for red `Error:` lines
- **Network tab** — API calls; look for 4xx/5xx responses that explain auth or model failures

To enable DevTools on a machine where it is not yet enabled:

```powershell
'{"allowDevTools": true}' | Set-Content "$env:AppData\Claude\developer_settings.json"
```

Then relaunch Claude Desktop and press Ctrl+Alt+I.

---

## Reference Files

| File | Use it when |
|---|---|
| [`references/mcp-tools-missing.md`](references/mcp-tools-missing.md) | Tools / server entries don't appear in chat |
| [`references/extensions-not-loading.md`](references/extensions-not-loading.md) | A `.mcpb` extension won't load |
| [`references/app-not-loading.md`](references/app-not-loading.md) | White screen, crash at launch, crash on Windows startup |
| [`references/auth-and-models.md`](references/auth-and-models.md) | Auth loops, missing models |
| [`references/performance.md`](references/performance.md) | Slow, laggy, or freezing app |

The script [`scripts/diagnose.ps1`](scripts/diagnose.ps1) runs a full environment snapshot in one
step — useful when the user just wants to paste something and get results.
