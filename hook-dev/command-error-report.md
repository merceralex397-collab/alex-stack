# Codex Session Command Error Inventory

Generated: 2026-07-19T00:56:28.181Z

## Scope and method

This is a streaming scan of Codex session JSONL under the global folder `C:\Users\PC\.codex`. It parses only terminal tool-call and tool-output records, identifies failed command outputs by an explicit nonzero exit code, and assigns exactly one normalized diagnostic signature to each failed command. It does not load entire session files into memory or copy prompts and responses into this report.

Indicator matching is reported as supporting context only. A failure is counted from its nonzero exit code, so failures without familiar PowerShell, Bash, or generic error wording are still included.

| Log root | Files | Size |
|---|---:|---:|
| `C:\Users\PC\.codex\sessions` | 454 | 7.40 GiB |
| `C:\Users\PC\.codex\archived_sessions` | 12 | 5.91 MiB |

The SQLite application log `C:\Users\PC\.codex\logs_2.sqlite` and non-session files were not scanned because this inventory is specifically for session command records.

## Totals

- Session files scanned: 466
- JSONL size streamed: 7.41 GiB
- JSONL records streamed: 921,205
- Terminal calls seen: 55,795
- Terminal outputs seen: 55,778
- Failed command outputs: 358
- Unique normalized error rows: 142
- Failures matching common error wording: 160
- Failures without common error wording: 198
- Malformed selected JSONL records encountered: 4
- Failed shell outputs recovered from malformed JSONL: 0
- Malformed shell-linked records without a nonzero exit marker: 3
- Unresolved malformed shell records: 0

## Failures by terminal tool

| Tool | Failed commands |
|---|---:|
| `shell_command` | 190 |
| `exec_command` | 131 |
| `write_stdin` | 36 |
| `wait` | 1 |

## Failures by exit code

| Exit code | Failed commands |
|---:|---:|
| 1 | 333 |
| 124 | 17 |
| -1 | 5 |
| 127 | 3 |

## Failures by category

| Category | Failed commands |
|---|---:|
| No diagnostic | 166 |
| PowerShell | 72 |
| Build/test | 36 |
| Other | 35 |
| ripgrep | 22 |
| Git | 10 |
| Bash/POSIX | 9 |
| Node/package | 8 |

## Source attribution and findings

### The largest row is mostly silent exit-code behavior

The most common normalized result is not one error message. It is a terminal command returning exit code `1` without familiar diagnostic wording. The attribution pass found 141 such occurrences in its fixed snapshot:

| Source | Count |
|---|---:|
| Legacy `shell_command` | 80 |
| Current `exec_command` | 54 |
| `write_stdin` continuation | 7 |

This bucket is distributed across many tasks rather than originating from one broken project. Its leading command families were:

| Command family | Count |
|---|---:|
| PowerShell compound command | 30 |
| `rg` | 22 |
| Inline `@'` block | 8 |
| `gh` | 7 |
| `npx` | 7 |
| `Write-Output` | 7 |

`rg` returns exit code `1` when it finds no matches, so its 22 occurrences are normally search outcomes rather than execution failures. Other silent exit-1 results include probes, checks, interrupted continuations, and commands whose diagnostics were suppressed. They should remain visible in the inventory, but they should not be interpreted as 141 instances of one defect.

The leading working directories for this bucket were:

| Working directory | Count |
|---|---:|
| `C:\Users\PC\Documents\GitHub\collisionsuite\active\collisionspike` | 18 |
| `C:\Users\PC` | 15 |
| `C:\Users\PC\Documents\GitHub\vscodex` | 15 |
| `C:\Users\PC\Documents\Codex\2026-06-06\locate-collisioncc-and-collision-plugin-you` | 14 |
| `C:\Users\PC\Documents\GitHub\agent-setup` | 14 |
| `C:\Users\PC\Documents\GitHub\alexrowanschedule` | 13 |
| `C:\Users\PC\Documents\GitHub\vehicledata` | 11 |
| `C:\Users\PC\.codex` | 10 |

### The most common identifiable failure family is PowerShell

PowerShell accounts for 72 failed commands in the categorized inventory. The directly attributable current-format `ParserError` records concentrate in:

| Working directory | Direct `ParserError` records |
|---|---:|
| `C:\Users\PC\Documents\GitHub\vehicledata` | 14 |
| `C:\Users\PC\Documents\GitHub\alex-stack` | 4 |
| `C:\Users\PC\Documents\GitHub\agent-setup` | 2 |
| `C:\Users\PC\Documents\GitHub\vscodex` | 2 |

Sixteen of those 22 direct parser errors came from long PowerShell compound commands. The recurring risk factors are dense one-line loops and object construction, nested quoting, pipelines placed directly after control-flow blocks, inline Python or Node payloads, and Bash-style redirection or heredoc syntax sent to PowerShell.

The four `alex-stack` parser errors are inspection-command noise created while producing and verifying this report, not product-runtime failures. Because the active Codex session is part of the scanned global archive, the report can observe its own diagnostic commands.

### Recommended interpretation

- Treat explicit diagnostics such as `ParserError`, missing paths, compiler failures, and command-not-found messages as actionable errors.
- Treat `rg` exit code `1` as an expected no-match result unless the surrounding workflow required a match.
- Review silent exit-code rows by command semantics before opening defects; absence of diagnostic text is not itself a root cause.
- Prefer short PowerShell commands or checked `.ps1` scripts over dense one-liners when arrays, loops, nested quoting, or inline-language payloads are involved.
- When a command intentionally probes for absence, capture that expectation explicitly so telemetry can distinguish a successful negative check from a failed operation.

The attribution logic is preserved in `attribute-top-errors.mjs` beside this report.

## Full normalized error list

Counts in this table sum to the failed-command total above.

| Count | Category | Exit code | Tool | Common indicator | Normalized error |
|---:|---|---:|---|:---:|---|
| 80 | No diagnostic | 1 | `shell_command` | no | [No common diagnostic text; exit code 1] |
| 55 | No diagnostic | 1 | `exec_command` | no | [No common diagnostic text; exit code 1] |
| 18 | PowerShell | 1 | `shell_command` | no | ParserError: |
| 17 | No diagnostic | 124 | `shell_command` | no | [No common diagnostic text; exit code 124] |
| 13 | PowerShell | 1 | `exec_command` | yes | ParserError: |
| 8 | Node/package | 1 | `write_stdin` | yes | npm error Maximum call stack size exceeded |
| 7 | No diagnostic | 1 | `write_stdin` | no | [No common diagnostic text; exit code 1] |
| 4 | No diagnostic | -1 | `write_stdin` | no | [No common diagnostic text; exit code -1] |
| 3 | Build/test | 1 | `shell_command` | yes | curl: (35) schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e) - No credentials are available in the security package |
| 3 | Git | 1 | `exec_command` | yes | fatal: not a git repository (or any of the parent directories): .git |
| 3 | Other | 1 | `shell_command` | no | \| Access denied |
| 3 | Other | 1 | `shell_command` | yes | ERROR: Bad Request({"error":{"code":"BadRequest","message":"Invalid query definition, Dataset is invalid or not supplied. (Request ID: <guid>)"}}) |
| 3 | PowerShell | 1 | `exec_command` | yes | ParserError: \| Missing file specification after redirection operator. |
| 2 | Build/test | 1 | `write_stdin` | yes | Test run failed with code 1 |
| 2 | Git | 1 | `shell_command` | yes | fatal: not a git repository (or any of the parent directories): .git |
| 2 | No diagnostic | 127 | `exec_command` | no | [No common diagnostic text; exit code 127] |
| 2 | Other | 1 | `shell_command` | yes | Error: Expected the bundled Codex runtime @oai/artifact-tool package to point to @oai/artifact-tool. |
| 2 | Other | 1 | `shell_command` | yes | ERROR: Unsupported Media Type({"error":{"code":"415","message":"The request contains an entity body but no Content-Type header. The inferred media type 'application/octet-stream' is not supported for this resource. (Request ID: <guid>)"}}) |
| 2 | Other | 1 | `write_stdin` | yes | Error: Timed out waiting 120000ms from config.webServer. |
| 2 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\references\evidence.md' because it does not exist. |
| 2 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\references\semantic-layer.md' because it does not exist. |
| 2 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\references\source-inventory.md' because it does not exist. |
| 2 | PowerShell | 1 | `shell_command` | no | ParserError: \| Missing argument in parameter list. |
| 2 | ripgrep | 1 | `exec_command` | yes | rg: regex parse error: |
| 2 | ripgrep | 1 | `shell_command` | yes | rg: workingspace/ai-realignment-plans/*.md: IO error for operation on workingspace/ai-realignment-plans/*.md: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | Bash/POSIX | 1 | `exec_command` | yes | bash: line 1: node: command not found |
| 1 | Bash/POSIX | 1 | `shell_command` | yes | ~\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe: can't open file '~\\.codex\\plugins\\cache\\openai-primary-runtime\\documents\\26.601.10930\\skills\\documents\\scripts\\render_docx.py': [Errno 2] No such file or directory |
| 1 | Bash/POSIX | 1 | `shell_command` | no | alex@100.104.196.66: Permission denied (publickey,password). |
| 1 | Bash/POSIX | 1 | `shell_command` | no | cealex-may25@100.80.66.84: Permission denied (publickey,password,keyboard-interactive). |
| 1 | Bash/POSIX | 1 | `shell_command` | no | cealex-may25@cealex-may25-1: Permission denied (publickey,password,keyboard-interactive). |
| 1 | Bash/POSIX | 1 | `shell_command` | yes | debug1: load_hostkeys: fopen ~/.ssh/known_hosts2: No such file or directory |
| 1 | Bash/POSIX | 1 | `shell_command` | no | pc@cealex-may25-1: Permission denied (publickey,password,keyboard-interactive). |
| 1 | Bash/POSIX | 1 | `shell_command` | yes | ssh-keygen: C:\\ProgramData\\ssh\\ssh_host_ed25519_key.pub: Permission denied |
| 1 | Bash/POSIX | 127 | `exec_command` | yes | /bin/bash: line 1: node: command not found |
| 1 | Build/test | 1 | `exec_command` | yes | .next/types/validator.ts(5,79): error TS2307: Cannot find module './routes.js' or its corresponding type declarations. |
| 1 | Build/test | 1 | `exec_command` | yes | .next/types/validator.ts(89,39): error TS2307: Cannot find module '../../src/app/api/auth/[...all]/route.js' or its corresponding type declarations. |
| 1 | Build/test | 1 | `exec_command` | yes | ❯ tests/unit/validation.test.ts (3 tests \| 1 failed) 90ms |
| 1 | Build/test | 1 | `exec_command` | yes | ~\Documents\GitHub\CollisionCC\src\app\api\ai-agents\vision\route.ts:84: details: { images: evidence.length, error: error instanceof Error ? error.message : "Vision agent failed" } |
| 1 | Build/test | 1 | `exec_command` | yes | 111:5 error Error: Calling setState synchronously within an effect can trigger cascading renders |
| 1 | Build/test | 1 | `exec_command` | yes | 1116:5 error Error: Calling setState synchronously within an effect can trigger cascading renders |
| 1 | Build/test | 1 | `exec_command` | yes | 861:5 error Error: Calling setState synchronously within an effect can trigger cascading renders |
| 1 | Build/test | 1 | `exec_command` | yes | Error: expect(locator).toBeVisible() failed |
| 1 | Build/test | 1 | `exec_command` | yes | Error: Transform failed with 4 errors: |
| 1 | Build/test | 1 | `exec_command` | yes | ExpectError: expect(locator).toBeVisible() failed |
| 1 | Build/test | 1 | `exec_command` | yes | src/components/AgentSetupApp.tsx(13,3): error TS2305: Module '"lucide-react"' has no exported member 'Github'. |
| 1 | Build/test | 1 | `exec_command` | yes | src/lib/profile.ts(155,23): error TS2339: Property 'model' does not exist on type '{}'. |
| 1 | Build/test | 1 | `exec_command` | yes | src/provider.ts(21,55): error TS2305: Module '"./config"' has no exported member 'ReasoningEffort'. |
| 1 | Build/test | 1 | `shell_command` | yes | - ctx.log(`[archiveMirrorMonitor] completion failed for ${row.evidenceId}: ${String(e)}`); |
| 1 | Build/test | 1 | `shell_command` | yes | \| Program 'rg.exe' failed to run: An error occurred trying to start process '~\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\codex-path\rg.exe' with working directory '~\.codex'. The filename or extension is too long.At line:2 char:334 |
| 1 | Build/test | 1 | `shell_command` | yes | docs/operations/cloud-inventory-2026-07-17.md:477:scale. The "last month" and "forecast" cost queries failed on a query-shape technicality, not a permission |
| 1 | Build/test | 1 | `shell_command` | yes | ERROR tests/test_cli.py |
| 1 | Build/test | 1 | `shell_command` | yes | ERROR: The command failed with an unexpected error. Here is the traceback: |
| 1 | Build/test | 1 | `shell_command` | yes | failed to connect to local tailscaled (which appears to be running as tailscaled.exe, pid 18236). Got error: Get "http://local-tailscaled.sock/localapi/v0/status": open \\.\pipe\ProtectedPrefix\Administrators\Tailscale\tailscaled: Access is denied. |
| 1 | Build/test | 1 | `shell_command` | yes | frontend\src\App.tsx:470: console.error("Live run failed:", err); |
| 1 | Build/test | 1 | `shell_command` | yes | plugins\cache\openai-bundled\browser\26.715.31925\scripts\node_modules\abstract-level\test\hooks\postopen.js:186: t.is(err.cause.message, 'error from hook; error from resource') |
| 1 | Build/test | 1 | `shell_command` | yes | scripts/checks/check-doc-links.mjs-12- * Exit code 0 = all selected checks passed; nonzero = at least one failed. |
| 1 | Build/test | 1 | `shell_command` | yes | scripts/hooks/pre-commit:39: echo "pre-commit: doc-links check FAILED — commit blocked." |
| 1 | Build/test | 1 | `shell_command` | yes | scripts/hooks\pre-commit:39: echo "pre-commit: doc-links check FAILED — commit blocked." |
| 1 | Build/test | 1 | `shell_command` | yes | services/data-api/src/features/inbound/outlook-queue.ts:99: * and records outlook_move_state='failed' so the SPA never shows a phantom "Filing…". |
| 1 | Build/test | 1 | `shell_command` | yes | services/orchestration/src/workflows/intake/eva-report-poll.ts-61- if (runtimeStatus && !['Failed', 'Terminated', 'Completed'].includes(runtimeStatus)) { |
| 1 | Build/test | 1 | `shell_command` | yes | services\data-api\src\features\assistant\suggestion-generation-routes.test.ts:169: it('callSuggestionModel throws → { generated: 0, reason: error }; NO ai_suggestion INSERT (no partial write); the failure is LOGGED', async () => { |
| 1 | Build/test | 1 | `shell_command` | yes | X Failed to log in to github.com account merceralex397-collab (default) |
| 1 | Build/test | 1 | `write_stdin` | yes | [browser] Uncaught Error: Hydration failed because the server rendered text didn't match the client. As a result this tree will be regenerated on the client. This can happen if a SSR-ed Client Component used:- A server/client branch `if (typeof window !== 'undefined')`. |
| 1 | Build/test | 1 | `write_stdin` | yes | Error: Package security acceptance failed: |
| 1 | Build/test | 1 | `write_stdin` | yes | ExpectError: expect(locator).toBeVisible() failed |
| 1 | Git | 1 | `exec_command` | yes | fatal: bad revision '575777f0c3258184fdb1bad1f153e1d5b26a08cb^' |
| 1 | Git | 1 | `exec_command` | yes | fatal: couldn't find remote ref fix/audit-provider-resolution |
| 1 | Git | 1 | `shell_command` | yes | fatal: unable to access 'https://github.com/collisionengineers/CollisionCC.git/': schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e) - No credentials are available in the security package |
| 1 | Git | 1 | `shell_command` | yes | fatal: unable to access 'https://github.com/merceralex397-collab/collisionautomation.git/': schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e) - No credentials are available in the security package |
| 1 | Git | 1 | `shell_command` | yes | fatal: unable to checkout working tree |
| 1 | No diagnostic | -1 | `exec_command` | no | [No common diagnostic text; exit code -1] |
| 1 | Other | 1 | `exec_command` | yes | 'tsc' is not recognized as an internal or external command, |
| 1 | Other | 1 | `exec_command` | yes | console.error(error instanceof Error ? error.message : String(error)); |
| 1 | Other | 1 | `exec_command` | yes | Error: browserType.launch: Executable doesn't exist at ~\AppData\Local\ms-playwright\chromium_headless_shell-1228\chrome-headless-shell-win64\chrome-headless-shell.exe |
| 1 | Other | 1 | `exec_command` | yes | Error: Can't find the deployment "dpl_alexrowanschedule" under the context "alexs-projects-916cfeed" |
| 1 | Other | 1 | `exec_command` | yes | Error: Cannot find module 'playwright-core' |
| 1 | Other | 1 | `exec_command` | yes | Error: Invalid arguments. Use an API path starting with /, or run `vercel api` interactively. |
| 1 | Other | 1 | `exec_command` | yes | Error: This module cannot be imported from a Client Component module. It should only be used from a Server Component. |
| 1 | Other | 1 | `exec_command` | yes | Exception: |
| 1 | Other | 1 | `exec_command` | yes | function mapProviderError(error: unknown): Error { |
| 1 | Other | 1 | `exec_command` | yes | locator.fill: Error: strict mode violation: getByLabel('Task') resolved to 2 elements: |
| 1 | Other | 1 | `exec_command` | yes | SyntaxError: Invalid or unexpected token |
| 1 | Other | 1 | `shell_command` | yes | \| Service 'Sense (Sense)' cannot be queried due to the following error: PermissionDenied |
| 1 | Other | 1 | `shell_command` | yes | a11y_audit.py: error: argument --fix_table_headers: expected one argument |
| 1 | Other | 1 | `shell_command` | yes | C:\Python314\python.exe: Error while finding module specification for 'cedocumentmapper_v2.cli' (ModuleNotFoundError: No module named 'cedocumentmapper_v2') |
| 1 | Other | 1 | `shell_command` | yes | docs\collision_releated\Sentry_API_Complete_Guide.md:54:Every Sentry API endpoint — **without exception** — requires a valid JSON Web Token (JWT) passed in the HTTP `Authorization` header. Requests without a token, or with an expired or invalid token, will receive a `401 Unauthorized` response. |
| 1 | Other | 1 | `shell_command` | no | Error code: Wsl/Service/WSL_E_DISTRO_NOT_FOUND |
| 1 | Other | 1 | `shell_command` | yes | ERROR: Access denied |
| 1 | Other | 1 | `shell_command` | yes | services/data-api/src/features/cases/capture-rate-limit.ts:211: jsonBody: { error: 'capture_retryable', message: 'Too many requests. Try again shortly.' }, |
| 1 | Other | 1 | `wait` | yes | [{"type":"input_text","text":"Script completed\nWall time 7.9 seconds\nOutput:\n"},{"type":"input_text","text":"{\"chunk_id\":\"a624f1\",\"wall_time_seconds\":12.5422481,\"exit_code\":1,\"original_token_count\":742,\"output\":\"\\n> codex-conduit@0.1.0 package:vsix\\n> node scripts/packageVsix.mjs --pre-release\\n\\nExecuting prepublish script 'npm run vscode:prepublish'...\\n\\n> codex-conduit@0.1.0 vscode:prepublish\\n> npm run compile && npm run check:security\\n\\n\\n> codex-conduit@0.1.0... |
| 1 | Other | 1 | `write_stdin` | yes | [main <timestamp>] Error: Code is currently being updated. Please wait for the update to complete before launching. |
| 1 | Other | 1 | `write_stdin` | yes | Error occurred prerendering page "/settings". Read more: https://nextjs.org/docs/messages/prerender-error |
| 1 | Other | 1 | `write_stdin` | yes | Error: Cannot find native binding. npm has a bug related to optional dependencies (https://github.com/npm/cli/issues/4828). Please try `npm i` again after removing both package-lock.json and node_modules directory. |
| 1 | Other | 1 | `write_stdin` | yes | Error: Could not load the "sharp" module using the win32-x64 runtime |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\.codex\plugins\cache\openai-curated-remote\product-design\0.1.46\get-context\SKILL.md' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\.codex\plugins\cache\openai-curated-remote\product-design\0.1.46\index\SKILL.md' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\AppData\Local\Programs\Microsoft VS Code\resources\app\extensions' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\agent-setup\init.md' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\collisionplugin\connectors\valuation-tool\app\server.py' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\ai-research-reports\UK Vehicle Datasets for Valuation, Total Loss, Salvage and Collision Analysis.md' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | \| Cannot find path '~\Documents\GitHub\vscodex\test\support\buildTsModules.mjs' because it does not exist. |
| 1 | PowerShell | 1 | `exec_command` | yes | 9 1 exec_command true ParserError: Original token count: 58 |
| 1 | PowerShell | 1 | `exec_command` | yes | ParserError: \| Missing property name after reference operator. |
| 1 | PowerShell | 1 | `exec_command` | yes | ParserError: \| Missing type name after '['. |
| 1 | PowerShell | 1 | `exec_command` | yes | ParserError: \| Unexpected token '"'][^"' in expression or statement. |
| 1 | PowerShell | 1 | `exec_command` | yes | ParserError: \| Unexpected token ')' in expression or statement. |
| 1 | PowerShell | 1 | `exec_command` | yes | ParserError: 10 \| … } else { [pscustomobject]@{Path=$p; Header='<missing>'} } } \| Format- … |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '\\wsl.localhost\Ubuntu-24.04\home\pc\projects' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '\\wsl$\Ubuntu-24.04\home\pc\projects' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '~\.codex\plugins\cache\openai-curated\google-drive\2cb26e7b\skills\google-drive\SKILL.md' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '~\.codex\plugins\cache\openai-primary-runtime\presentations\26.601.10930\skills\scripts' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '~\.codex\plugins\cache\openai-primary-runtime\ticket-implement\SKILL.md' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '~\Documents\GitHub\CollisionCC\docs\reference_information\case_corpus\readme.md' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path '~\Documents\GitHub\collisionsuite\AGENTS.md' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path 'workingspace/ai-realignment-plans/05-agent-run-traces-and-operator-notes.md' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | \| Cannot find path 'workingspace/architecture-simplification/04-scripts-checks-and-evaluation-consolidation.md' because it does not exist. |
| 1 | PowerShell | 1 | `shell_command` | no | ParserError: \| Missing '=' operator after key in hash literal. |
| 1 | PowerShell | 1 | `shell_command` | no | ParserError: \| Missing file specification after redirection operator. |
| 1 | PowerShell | 1 | `write_stdin` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\ai-research-reports\cereference\_investigation\00-EXECUTIVE-SUMMARY.md' because it does not exist. |
| 1 | PowerShell | 1 | `write_stdin` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\ai-research-reports\cereference\_investigation\01-data-dictionary.md' because it does not exist. |
| 1 | PowerShell | 1 | `write_stdin` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\ai-research-reports\cereference\_investigation\02-integrity-findings.md' because it does not exist. |
| 1 | PowerShell | 1 | `write_stdin` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\ai-research-reports\cereference\_investigation\11-business-applications.md' because it does not exist. |
| 1 | PowerShell | 1 | `write_stdin` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\ai-research-reports\README.md' because it does not exist. |
| 1 | PowerShell | 1 | `write_stdin` | yes | \| Cannot find path '~\Documents\GitHub\vehicledata\dft_test_result_2023\test_result.csv' because it does not exist. |
| 1 | ripgrep | 1 | `exec_command` | yes | rg: :: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `exec_command` | yes | rg: ~\Documents\GitHub\vehicledata\cereference\_investigation\*.md: IO error for operation on ~\Documents\GitHub\vehicledata\cereference\_investigation\*.md: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `exec_command` | yes | rg: app: The system cannot find the file specified. (os error 2) |
| 1 | ripgrep | 1 | `exec_command` | yes | rg: node_modules/vscode/vscode.d.ts: The system cannot find the path specified. (os error 3) |
| 1 | ripgrep | 1 | `exec_command` | yes | rg: src/parser/*.test.ts: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: *.spec: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: docs/adr/0019-case-correlation-dedup-and-intake-idempotency.md: The system cannot find the file specified. (os error 2) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: docs/adr/0019-hybrid-deterministic-ai-triage-policy.md: The system cannot find the file specified. (os error 2) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: docs/reviews/150726/*/review.md: IO error for operation on docs/reviews/150726/*/review.md: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: docs/tickets/backlog/TKT-23*: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: docs\testing\cli_audit_current\texts\*KERR*.txt: IO error for operation on docs\testing\cli_audit_current\texts\*KERR*.txt: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: docs\testing\cli_audit_current\texts\ALISON_*.txt: IO error for operation on docs\testing\cli_audit_current\texts\ALISON_*.txt: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: regex parse error: |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: scripts/evaluation/email/model-matrix*.json: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: scripts/maintenance/cloud-inventory/*.ps1: IO error for operation on scripts/maintenance/cloud-inventory/*.ps1: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: services/functions/*/infra/main.bicep: The filename, directory name, or volume label syntax is incorrect. (os error 123) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: SETUP.md: The system cannot find the file specified. (os error 2) |
| 1 | ripgrep | 1 | `shell_command` | yes | rg: src\CollisionIntake.Core\ExportWorkflowPolicy.cs: The system cannot find the file specified. (os error 2) |
