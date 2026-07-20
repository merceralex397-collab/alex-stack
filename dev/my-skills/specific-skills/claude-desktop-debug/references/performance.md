# Performance Issues — Slow / Laggy / Freezing

Use this reference when Claude Desktop feels sluggish, the UI freezes during typing or scrolling,
or responses are slow to appear.

---

## GPU compositing (most common cause)

The Electron GPU compositing layer can cause lag and stuttering on Windows, especially with
high-DPI displays, high-refresh-rate monitors, or certain NVIDIA drivers.

### Fix: Disable GPU compositing

1. Find the Claude Desktop shortcut
2. Right-click → Properties → Shortcut tab → Target field
3. Append ` --disable-gpu-compositing` to the path:
   ```
   "C:\Users\Alex\AppData\Local\AnthropicClaude\claude.exe" --disable-gpu-compositing
   ```
4. Launch via this shortcut

If this resolves the lag, add it permanently to your shortcut. The visual quality difference
is minimal on modern displays.

---

## Clear Electron cache

A large or corrupt HTTP cache can slow startup and response rendering.

```powershell
# Check cache size first
(Get-ChildItem "$env:AppData\Claude\Cache\" -Recurse -ErrorAction SilentlyContinue |
  Measure-Object -Property Length -Sum).Sum / 1MB

# Clear the cache (safe — it will be rebuilt on next launch)
Remove-Item "$env:AppData\Claude\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
```

Also clear the GPU shader cache if GPU issues are suspected:

```powershell
Remove-Item "$env:AppData\Claude\GPUCache\*" -Recurse -Force -ErrorAction SilentlyContinue
```

Relaunch after clearing.

---

## Check memory usage

If the app feels sluggish after a long session, it may be consuming excessive memory. Claude
Desktop runs as multiple Electron processes:

```powershell
Get-Process -Name "claude" |
  Select-Object ProcessName, Id,
    @{Name="RAM_MB"; Expression={[math]::Round($_.WorkingSet64/1MB,1)}} |
  Sort-Object RAM_MB -Descending
```

If any single renderer process is above ~1 GB, restarting the app will reclaim memory.

---

## Identify slow API calls with DevTools

If responses are slow to appear (rather than the UI being laggy), the bottleneck may be network
latency or a slow MCP server call.

1. Open DevTools with **Ctrl+Alt+I**
2. Go to the **Network** tab
3. Send a message in Claude Desktop
4. Look for slow requests — the Timing column shows time-to-first-byte and total duration

Requests to `api.anthropic.com` slower than ~2–3 seconds may indicate a regional routing issue
or rate limiting. Requests to a local MCP server process slower than expected suggest the server
itself is the bottleneck (check the server's own log for processing times).

---

## Node.js version

Some MCP server performance issues trace to an outdated Node.js version. Claude Desktop bundles
its own Node for extensions, but `npx`-based servers in `claude_desktop_config.json` use the
system Node.

```powershell
node --version
# Should be 18.0.0 or newer
```

Update from nodejs.org if below 18.

---

## Known slow versions

Version 1.1.3189 (released February 2026) introduced a UI rendering regression that caused severe
lag on many Windows configurations. If you are on that version, update to the latest release
via Settings → About → Check for Updates.
