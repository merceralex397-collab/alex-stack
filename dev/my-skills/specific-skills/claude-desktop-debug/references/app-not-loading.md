# App Not Loading / Crashes

Use this reference for:
- White or blank screen when Claude Desktop opens
- App crashes immediately on launch
- App crashes when Windows starts (autostart), but works if opened manually
- Black flicker or unresponsive window

---

## White / Blank Screen

The most common cause is a GPU rendering issue — the Electron renderer process fails to initialize
the GPU context, typically after waking from hibernate, after a display configuration change (new
monitor, resolution change), or after a driver update.

### Fix 1: Launch with GPU compositing disabled

This resolves the majority of white screen and flicker cases:

1. Find the Claude Desktop shortcut (Start Menu or Desktop)
2. Right-click → Properties → Shortcut tab
3. In "Target", append ` --disable-gpu-compositing` after the executable path:
   ```
   "C:\Users\Alex\AppData\Local\AnthropicClaude\claude.exe" --disable-gpu-compositing
   ```
4. Click OK and relaunch using this shortcut

If `--disable-gpu-compositing` doesn't help, try `--disable-gpu` (heavier — disables all GPU
acceleration, may cause slower rendering but will load):

```
"C:\Users\Alex\AppData\Local\AnthropicClaude\claude.exe" --disable-gpu
```

### Fix 2: Kill all Claude processes then relaunch

Sometimes the Electron renderer process gets stuck. Kill everything:

```powershell
Get-Process -Name "claude" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "Claude" -ErrorAction SilentlyContinue | Stop-Process -Force
```

Wait 5 seconds, then relaunch normally.

### Fix 3: Check Windows Event Viewer

If the GPU flags don't help, check for a logged crash:

1. Open Start → **Event Viewer**
2. Navigate to: Windows Logs → Application
3. Filter by Source: look for `Claude` or `Application Error`
4. Check the timestamp against when the crash occurred

A typical entry looks like:
```
Faulting application name: claude.exe
Exception code: 0xc0000005
Faulting module: <native-module>.node
```

The faulting module name points to the component that crashed.

### Fix 4: Enable Electron logging

Set this environment variable before launching to capture verbose output:

```powershell
# In PowerShell — set for this session, then launch Claude Desktop
$env:ELECTRON_ENABLE_LOGGING = "1"
$env:ELECTRON_LOG_FILE = "$env:TEMP\claude-debug.log"
& "$env:LOCALAPPDATA\AnthropicClaude\claude.exe"
```

After the white screen appears, read the log:

```powershell
Get-Content "$env:TEMP\claude-debug.log" -Tail 50
```

---

## App Crashes on Windows Startup (Autostart)

This is a known issue where Windows enumerates startup apps in a way that triggers a crash in
`SettingsHandlers_Startup.dll`, distinct from a normal Claude Desktop crash.

**Distinguishing symptom:** The app crashes when Windows starts automatically, but launching it
manually from the Start Menu works fine.

### Fix: Disable autostart and use a manual shortcut

1. Open **Task Manager** → Startup Apps tab
2. Find Claude Desktop and set it to **Disabled**
3. Create a shortcut in the Windows startup folder instead:
   ```powershell
   # Open the startup folder
   Start-Process shell:startup
   ```
4. Copy a shortcut to Claude Desktop into this folder
5. Restart Windows to verify

The startup folder shortcut bypasses the Windows startup enumeration that triggers the crash.

### Alternative: Check for conflicting autostart entries

```powershell
# List all Claude-related startup entries
Get-CimInstance -ClassName Win32_StartupCommand | Where-Object { $_.Name -like "*Claude*" }
```

Remove duplicate entries if any are listed.

---

## Crash at Launch (not startup-related)

If Claude Desktop crashes every time you launch it (not just at Windows startup):

### Check crashpad for a report

```powershell
Get-ChildItem "$env:AppData\Claude\crashpad\reports\" -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 3
```

If crash reports exist, note the filenames (timestamps encoded) — this confirms a native crash
rather than a JavaScript error.

### Version-specific crash: delete the bad version

If the crash started after an update, the new version may have a bug. The old version is kept on
disk and can be restored:

```powershell
# List installed versions
Get-ChildItem "$env:LOCALAPPDATA\AnthropicClaude\" -Filter "app-*" | Select-Object Name
```

Delete the most recently added `app-*` folder. When you relaunch, the updater will fall back to
the previous version.

### Full clean reinstall

As a last resort:

```powershell
# 1. Uninstall via Add/Remove Programs or Settings → Apps
# 2. After uninstall, delete leftover data:
Remove-Item -Recurse "$env:APPDATA\Claude" -Force
Remove-Item -Recurse "$env:LOCALAPPDATA\AnthropicClaude" -Force
# 3. Reinstall from https://claude.ai/download
```

> This deletes your config, logs, and cached extensions. Back up
> `claude_desktop_config.json` first if you have custom MCP server configs.
