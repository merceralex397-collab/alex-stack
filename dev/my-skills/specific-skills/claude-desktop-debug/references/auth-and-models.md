# Authentication Failures and Missing Models

Use this reference when:
- Claude Desktop keeps asking you to log in (login loop)
- You get "Invalid authorization" or "OAuth error" messages
- You are logged in but models are not appearing in the model picker
- A model you previously had access to is no longer available

---

## Authentication Loop

### Check for an ANTHROPIC_API_KEY environment variable conflict

This is the most common non-obvious auth failure. If `ANTHROPIC_API_KEY` is set in your Windows
user environment (or in a PowerShell profile), Claude Desktop may use it instead of your OAuth
session. If the key is invalid, expired, or from the wrong account, you'll see auth failures even
though you can log in normally at claude.ai.

```powershell
# Check if the variable is set
[System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
[System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "Machine")
$env:ANTHROPIC_API_KEY   # also check current session
```

If any of these return a value, that key is being used. To clear it:

```powershell
# Remove from user environment permanently
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $null, "User")
```

Then fully quit and relaunch Claude Desktop.

### Stale OAuth token

If the token cache is corrupted or expired:

1. Inside Claude Desktop, open **Settings** → sign out
2. Close and reopen the app
3. Sign back in — a browser window should open for OAuth

If the browser window does not open automatically, the OAuth URL is usually printed in the
Console (Ctrl+Alt+I → Console tab). Copy it and open it manually.

### Clear the token cache

If sign-out / sign-in doesn't resolve it:

```powershell
# Delete the auth cache file (you will need to sign in again)
Remove-Item "$env:AppData\Claude\config.json" -Force
```

The `config.json` file contains an encrypted OAuth token cache. Deleting it forces a fresh auth
flow on next launch.

---

## Models Not Appearing in Model Picker

### Check your subscription

1. Open claude.ai in a browser
2. Go to Account → Billing — confirm your plan and that it's active
3. Sign out of Claude Desktop and back in to refresh entitlements

### Check for regional restrictions

Some models are not available in all regions. If you use a VPN, try disabling it and relaunching.

### Gateway / proxy setup

If you route Claude Desktop through a local proxy or OpenAI-compatible gateway, newer versions
of Claude Desktop require the `/v1/models` endpoint response to include `capabilities` and
`context_length` fields. Gateways that don't provide these fields cause models to be hidden.

Check what your gateway returns:

```powershell
# Replace with your gateway base URL
Invoke-RestMethod "http://localhost:8080/v1/models" | ConvertTo-Json -Depth 5
```

Look for `capabilities` on each model object. If absent, update your gateway software.

### Developer / beta features

Some models require a beta features flag. Check `developer_settings.json`:

```powershell
Get-Content "$env:AppData\Claude\developer_settings.json" | ConvertFrom-Json
```

---

## Checking Auth Status Inside the App

Open a conversation and type `/status` — Claude Desktop returns your current auth method,
account tier, and region. This is the fastest way to confirm whether the issue is auth-related
or subscription-related.
