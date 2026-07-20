# Claude Desktop Diagnostics
# Run in PowerShell: & "path\to\diagnose.ps1"
# Collects a snapshot of Claude Desktop environment for troubleshooting.

Write-Host "`n=== Claude Desktop Diagnostics ===" -ForegroundColor Cyan
Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"

# --- 1. Install type detection ---
Write-Host "--- Install Type ---" -ForegroundColor Yellow
$msixPkg = Get-AppxPackage -Name "*Claude*" -ErrorAction SilentlyContinue
if ($msixPkg) {
    Write-Host "MSIX install detected"
    Write-Host "  Package: $($msixPkg.Name)"
    Write-Host "  PackageFamilyName: $($msixPkg.PackageFamilyName)"
    $configBase = "$env:LOCALAPPDATA\Packages\$($msixPkg.PackageFamilyName)\LocalCache\Roaming\Claude"
    Write-Host "  Active config path: $configBase\claude_desktop_config.json"
} else {
    Write-Host "Standard (Win32) install"
    $configBase = "$env:APPDATA\Claude"
    Write-Host "  Active config path: $configBase\claude_desktop_config.json"
}

$configPath = "$configBase\claude_desktop_config.json"
$logsPath = "$configBase\logs"

# --- 2. App version ---
Write-Host "`n--- App Version ---" -ForegroundColor Yellow
$appExe = Get-ChildItem "$env:LOCALAPPDATA\AnthropicClaude" -Filter "claude.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if ($appExe) {
    $ver = (Get-Item $appExe.FullName).VersionInfo.FileVersion
    Write-Host "  claude.exe: $ver at $($appExe.FullName)"
} elseif ($msixPkg) {
    Write-Host "  MSIX version: $($msixPkg.Version)"
} else {
    Write-Host "  claude.exe not found in AnthropicClaude"
}

# --- 3. Config validation ---
Write-Host "`n--- Config File ---" -ForegroundColor Yellow
if (Test-Path $configPath) {
    $raw = Get-Content $configPath -Raw
    try {
        $cfg = $raw | ConvertFrom-Json
        Write-Host "  JSON: VALID"
        $servers = $cfg.mcpServers.PSObject.Properties.Name
        if ($servers) {
            Write-Host "  mcpServers ($($servers.Count)): $($servers -join ', ')"
        } else {
            Write-Host "  mcpServers: (empty)"
        }
    } catch {
        Write-Host "  JSON: INVALID - $($_.Exception.Message)" -ForegroundColor Red
    }
    # BOM check
    $bytes = [System.IO.File]::ReadAllBytes($configPath)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "  WARNING: File has UTF-8 BOM — this can break JSON parsing" -ForegroundColor Red
    }
} else {
    Write-Host "  NOT FOUND at $configPath" -ForegroundColor Red
}

# --- 4. Developer settings ---
Write-Host "`n--- Developer Settings ---" -ForegroundColor Yellow
$devPath = "$env:APPDATA\Claude\developer_settings.json"
if (Test-Path $devPath) {
    $devContent = Get-Content $devPath -Raw
    Write-Host "  $devContent"
} else {
    Write-Host "  Not present (DevTools not enabled)"
}

# --- 5. Log files ---
Write-Host "`n--- Log Files ---" -ForegroundColor Yellow
if (Test-Path $logsPath) {
    Get-ChildItem $logsPath -Filter "*.log" |
        Sort-Object LastWriteTime -Descending |
        ForEach-Object {
            Write-Host ("  {0,-55} {1,8} KB  {2}" -f $_.Name, [math]::Round($_.Length/1KB,1), $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm"))
        }
} else {
    Write-Host "  Logs directory not found at $logsPath" -ForegroundColor Red
}

# --- 6. MCP log tail ---
$mcpLog = "$logsPath\mcp.log"
if (Test-Path $mcpLog) {
    Write-Host "`n--- Last 20 lines of mcp.log ---" -ForegroundColor Yellow
    Get-Content $mcpLog -Tail 20
}

# --- 7. Installed extensions ---
Write-Host "`n--- Installed Extensions (dxt-install directories) ---" -ForegroundColor Yellow
$dxtDirs = Get-ChildItem "$env:APPDATA\Claude" -Filter "dxt-install-*" -ErrorAction SilentlyContinue
if ($msixPkg) {
    $msixBase = "$env:LOCALAPPDATA\Packages\$($msixPkg.PackageFamilyName)\LocalCache\Roaming\Claude"
    $dxtDirs += Get-ChildItem $msixBase -Filter "dxt-install-*" -ErrorAction SilentlyContinue
}
if ($dxtDirs) {
    $dxtDirs | ForEach-Object {
        $manifest = Get-ChildItem $_.FullName -Filter "manifest.json" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        $name = if ($manifest) { ($manifest | Get-Content -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue).name } else { "?" }
        Write-Host ("  {0,-40} name={1}" -f $_.Name, $name)
    }
} else {
    Write-Host "  None found"
}

# --- 8. Locally-unpacked mcpb bundles ---
$localMcpb = Get-ChildItem "$env:APPDATA\Claude" -Filter "local.unpacked.*.mcpb" -ErrorAction SilentlyContinue
if ($localMcpb) {
    Write-Host "`n--- Local .mcpb Files ---" -ForegroundColor Yellow
    $localMcpb | ForEach-Object {
        Write-Host ("  {0}  ({1:N0} KB)" -f $_.Name, ($_.Length/1KB))
    }
}

# --- 9. ANTHROPIC_API_KEY check ---
Write-Host "`n--- Environment Variable Check ---" -ForegroundColor Yellow
$apiKeyUser    = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
$apiKeyMachine = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "Machine")
$apiKeySession = $env:ANTHROPIC_API_KEY
if ($apiKeyUser -or $apiKeyMachine -or $apiKeySession) {
    Write-Host "  WARNING: ANTHROPIC_API_KEY is set — this may override OAuth auth" -ForegroundColor Red
    if ($apiKeyUser)    { Write-Host "    User scope:    sk-ant-***" }
    if ($apiKeyMachine) { Write-Host "    Machine scope: sk-ant-***" }
    if ($apiKeySession) { Write-Host "    Session scope: sk-ant-***" }
} else {
    Write-Host "  ANTHROPIC_API_KEY: not set (good)"
}

# --- 10. Crash reports ---
Write-Host "`n--- Crash Reports ---" -ForegroundColor Yellow
$crashDir = "$env:APPDATA\Claude\crashpad\reports"
if (Test-Path $crashDir) {
    $crashes = Get-ChildItem $crashDir -ErrorAction SilentlyContinue
    if ($crashes) {
        Write-Host "  $($crashes.Count) crash report(s) found:"
        $crashes | Sort-Object LastWriteTime -Descending | Select-Object -First 3 |
            ForEach-Object { Write-Host "    $($_.Name)  $($_.LastWriteTime)" }
    } else {
        Write-Host "  No crash reports"
    }
} else {
    Write-Host "  Crashpad directory not found"
}

Write-Host "`n=== End of diagnostics ===`n" -ForegroundColor Cyan
