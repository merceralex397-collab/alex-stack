# MCP Tools Not Appearing

Use this reference when MCP server tools are not showing up in the Claude Desktop chat interface.

---

## Step 1: Confirm the symptom

"Tools not appearing" means different things — narrow it down:

- **No plus/tools icon at all** in the chat input → MCP never loaded, probably a config or launch error
- **Plus icon present but server not listed** → server registered but failed to start
- **Server listed but tools missing from the list** → server started but the tools endpoint failed

---

## Step 2: Check mcp.log for the load error

```powershell
Get-Content "$env:AppData\Claude\logs\mcp.log" -Tail 50
```

Common log patterns and what they mean:

| Log message | Cause |
|---|---|
| `SyntaxError` / `JSON parse error` | `claude_desktop_config.json` has invalid JSON |
| `ENOENT` on the command path | The `command` value doesn't exist at that path |
| `ENOENT npx` | `npx` called without `cmd /c` wrapper (see below) |
| `spawn ... EACCES` | The file exists but is not executable |
| `Process exited with code 1` | Server crashed at startup; read `mcp-server-<name>.log` |
| `Config loaded, 0 servers` | Config file is valid but `mcpServers` is empty or the path is wrong |
| No entries at all | Either using MSIX path but reading Standard logs, or Claude Desktop wasn't restarted after config change |

---

## Step 3: Validate config JSON

```powershell
Get-Content "$env:AppData\Claude\claude_desktop_config.json" -Raw | ConvertFrom-Json
```

If this throws: the JSON is broken. Open the file and look for:
- Trailing commas (last item in an array or object followed by a comma)
- Missing or mismatched `{` `}` `[` `]`
- Smart quotes (`"` `"`) instead of straight quotes (`"`) — can happen when config is typed in Word or email

**BOM trap:** If the file was saved by Windows Notepad, it may have an invisible UTF-8 BOM at the
start. This breaks JSON parsing. Fix: open in VS Code → bottom-right click on "UTF-8 with BOM" →
"Save with Encoding" → "UTF-8".

---

## Step 4: Fix `npx` on Windows

Claude Desktop spawns server processes without a shell. On Windows, `npx` is a `.cmd` batch file
shim — it only works when launched through a shell. Without the wrapper you get `ENOENT` and the
server silently fails to start.

**Broken:**
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\Alex\\Desktop"]
}
```

**Fixed:**
```json
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\Alex\\Desktop"]
}
```

The same applies to `uv`, `uvx`, and any other tool installed as a `.cmd` shim. Test whether a
command is a shim:

```powershell
(Get-Command npx).Source
# If output ends in .cmd → it needs the cmd /c wrapper
```

---

## Step 5: PATH not inherited

Claude Desktop (as a GUI app launched from the Start Menu) does not inherit the user's shell PATH.
If the server's executable is only on PATH in a terminal, it will fail when Claude Desktop tries
to launch it.

Workaround: use the full absolute path in `command`, or add the missing directory to `env.PATH`:

```json
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "my-mcp-server"],
  "env": {
    "PATH": "C:\\Program Files\\nodejs;C:\\Users\\Alex\\AppData\\Roaming\\npm;C:\\Windows\\system32"
  }
}
```

To find where a command lives:

```powershell
(Get-Command node).Source        # e.g. C:\Program Files\nodejs\node.exe
(Get-Command python).Source      # e.g. C:\Python312\python.exe
```

---

## Step 6: Read the per-server log

If the server started but crashed:

```powershell
Get-Content "$env:AppData\Claude\logs\mcp-server-<name>.log" -Tail 50
```

Replace `<name>` with the key name from your `mcpServers` config (not the display name).
This log captures the server's stderr — runtime errors, missing API keys, module not found, etc.

Common exit codes:

| Exit code | Likely cause |
|---|---|
| 1 | Application-level error (read the log for the message) |
| 2 | Syntax error in the server's own code |
| 127 | Command not found (bad path or missing shell) |
| 3221225477 (`0xC0000005`) | Windows access violation — usually a native module issue |

---

## Step 7: MSIX config path mismatch

If you confirmed you're on an MSIX install (see main SKILL.md Section 1) and edits to the config
file via the in-app "Edit Config" button didn't take effect, you were editing the wrong file.

The MSIX install reads config from:
```
%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

The in-app button opens:
```
%APPDATA%\Claude\claude_desktop_config.json
```

These are two separate files. Copy your server config from the Standard path to the MSIX path,
then fully quit and relaunch Claude Desktop.

---

## Step 8: Must restart fully

Config is read **only at startup**. Closing the Claude Desktop window does not exit the app — it
stays in the system tray. To fully restart:

1. Right-click the Claude icon in the system tray
2. Click **Quit Claude**
3. Wait for the process to fully exit (check Task Manager if uncertain)
4. Relaunch Claude Desktop

Changes to `claude_desktop_config.json` only take effect after this.

---

## Verify it worked

After restarting, look for the **tools / plus icon** in the chat input bar. Open a new chat and
click it — your server's tools should appear in the list.

If still not working after following all steps, run the full diagnostics script:

```powershell
& "$env:APPDATA\..\..\..\Documents\GitHub\collisionsuite\connectors\claude-desktop-debug\scripts\diagnose.ps1"
```
