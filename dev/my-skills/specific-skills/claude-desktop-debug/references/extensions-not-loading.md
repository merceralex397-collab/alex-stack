# Extensions / Connectors Not Loading

Use this reference when a `.mcpb` extension or Desktop Connector installed via the Claude
Desktop directory is not working — shows a spinner, error badge, or simply never appears.

---

## Background: What mcpb files are

`.mcpb` (MCP Bundle) is Claude Desktop's packaged extension format. Each bundle is a ZIP archive
containing a server executable and a `manifest.json`. When you install an extension from the
in-app directory:

1. Claude Desktop unpacks the bundle into `%APPDATA%\Claude\dxt-install-<random>\`
2. It registers the server in `mcpServers` in `claude_desktop_config.json` automatically
3. Sensitive fields (API keys entered during install) go to **Windows Credential Manager**, not
   the JSON file

Locally-unpacked `.mcpb` files (e.g. `local.unpacked.*.mcpb`) follow the same structure but are
installed from the filesystem rather than the cloud directory.

---

## Checklist

### 1. Confirm the extension bundle is present

```powershell
Get-ChildItem "$env:AppData\Claude\" -Filter "dxt-install-*" | Select-Object Name, LastWriteTime
```

If the extension's `dxt-install-*` directory is missing:
- The installation didn't complete (network error, permission issue, or MSIX path bug — see below)
- Try reinstalling from the in-app directory

### 2. Check if the server was registered in config

```powershell
(Get-Content "$env:AppData\Claude\claude_desktop_config.json" -Raw | ConvertFrom-Json).mcpServers
```

You should see an entry whose `command` path points into a `dxt-install-*` directory. If the key
is absent, the extension didn't register — reinstall it.

### 3. Check the extension server log

```powershell
# List all extension server logs
Get-ChildItem "$env:AppData\Claude\logs\" -Filter "mcp-server-*" | Select-Object Name, Length, LastWriteTime

# Read the specific log
Get-Content "$env:AppData\Claude\logs\mcp-server-collision-engineers-dvsa-mot.log" -Tail 50
```

Common errors in extension logs:

| Error | Cause |
|---|---|
| `Cannot find module` | Node.js module not bundled correctly; reinstall the extension |
| `Missing required config: <key>` | API key or required field not filled in during install |
| `ENOENT` on `dist/index.js` | Unpacked bundle is corrupt or incomplete |
| `Error: CREDENTIAL_NOT_FOUND` | API key was not saved to Windows Credential Manager; reinstall and re-enter the key |

### 4. MSIX install path bug

On MSIX installs, extensions may be installed to the virtualized path but `claude_desktop_config.json`
in the Standard path is what Claude reads. This causes a silent mismatch.

Detection: the `dxt-install-*` directory exists but is under the MSIX path:

```powershell
$pfn = (Get-AppxPackage -Name "*Claude*").PackageFamilyName
Get-ChildItem "$env:LOCALAPPDATA\Packages\$pfn\LocalCache\Roaming\Claude\" -Filter "dxt-install-*"
```

If bundles are here but not under `%APPDATA%\Claude\`, you have the MSIX path mismatch.
The config that Claude Desktop actually reads is the MSIX one. Make sure the `mcpServers` entry in
the MSIX config points to the MSIX `dxt-install-*` path.

### 5. Chrome extension conflict

If you use both Claude Desktop and the Claude Chrome extension (for browser automation), they
register competing Chrome Native Messaging hosts. Chrome picks one, which can block the other.

Symptom: Claude Desktop's browser-connected features stop working after installing the Claude
Chrome extension, or vice versa.

Fix: disable the Chrome extension bridge in Claude Desktop settings, or uninstall the Chrome
extension if you don't use it.

---

## Clean reinstall of an extension

If the extension is stuck in a broken state:

1. **Remove the bundle directory:**
   ```powershell
   # Find the right dxt-install directory (look for your extension name in the contents)
   Get-ChildItem "$env:AppData\Claude\" -Filter "dxt-install-*" |
     ForEach-Object { Get-ChildItem $_.FullName -Recurse -Filter "manifest.json" | Select-Object FullName }
   ```
   Then delete the matching `dxt-install-*` folder.

2. **Remove the mcpServers entry:** Edit `claude_desktop_config.json` and delete the server key
   for the extension.

3. **Clear the Credential Manager entry** (optional, only if you need to re-enter API keys):
   - Open Start → Credential Manager → Windows Credentials
   - Look for entries starting with `Claude/` or the extension name
   - Delete them

4. **Fully quit Claude Desktop** (system tray → Quit) and relaunch.

5. **Reinstall** from the in-app extensions directory.

---

## Locally-unpacked extensions

For `.mcpb` files installed from disk (not the cloud directory), check:

```powershell
# Find locally unpacked bundles
Get-ChildItem "$env:AppData\Claude\" -Filter "local.unpacked.*.mcpb" | Select-Object Name, Length
```

If the file exists but the extension doesn't work, open the `.mcpb` as a ZIP archive (rename to
`.zip`) and inspect the `manifest.json` — verify `server.entry_point` exists inside the archive.
