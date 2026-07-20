#!/usr/bin/env python3
"""Inspect Claude Desktop MCP config and logs without exposing env secrets."""

from __future__ import annotations

import argparse
import glob
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


SECRET_MARKERS = (
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASS",
    "AUTH",
    "BEARER",
    "CREDENTIAL",
    "PAT",
    "DSN",
    "CONNECTION",
    "WEBHOOK",
    "COOKIE",
    "SESSION",
)

# Value shapes that are secret regardless of the variable name (e.g. DATABASE_URL,
# GITHUB_PAT). Redacting by key marker alone leaks these.
SECRET_VALUE_PATTERNS = (
    re.compile(r"://[^/@\s:]+:[^/@\s]+@"),                 # user:password@ in a URL/DSN
    re.compile(r"\b(?:gh[posru]_|github_pat_)[A-Za-z0-9_]+"),  # GitHub tokens/PATs
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]+"),            # Slack tokens
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                  # AWS access key id
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}"),               # OpenAI-style keys
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),  # JWT
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{8,}"),   # bearer tokens
)

# npm-family launchers that ship as .cmd shims on Windows (npx.cmd, npm.cmd, ...).
# Node's child_process.spawn cannot run a .cmd/.bat without a shell, so a bare
# command of one fails with spawn ENOENT/EINVAL; the fix is command="cmd",
# args=["/c", <launcher>, ...]. uv/uvx/bun/deno are usually native .exe (no shim),
# so they are caught only when the resolved file is actually a .cmd/.bat.
NPM_FAMILY_SHIMS = {"npx", "npm", "pnpm", "yarn", "pnpx"}


def value_looks_secret(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_VALUE_PATTERNS)


def msix_localcache_roots() -> list[Path]:
    """MSIX/Store Claude Desktop virtualizes its config under LocalCache.

    The 'Edit Config' button opens the legacy %APPDATA% file via Electron, which
    bypasses MSIX redirection, so the two can diverge and edits land in a file the
    app never reads -- the classic 'silently broke after an update, no logs' case.
    """
    localappdata = os.environ.get("LOCALAPPDATA")
    if not localappdata:
        return []
    pattern = str(Path(localappdata) / "Packages" / "Claude_*" / "LocalCache" / "Roaming" / "Claude")
    return [Path(p) for p in glob.glob(pattern)]


def config_candidates() -> list[Path]:
    """All plausible Claude Desktop config paths, most-likely-read first."""
    system = platform.system()
    candidates: list[Path] = []
    if system == "Windows":
        for root in msix_localcache_roots():
            candidates.append(root / "claude_desktop_config.json")
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(Path(appdata) / "Claude" / "claude_desktop_config.json")
    elif system == "Darwin":
        candidates.append(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
    else:
        candidates.append(Path.home() / ".config" / "Claude" / "claude_desktop_config.json")
    return candidates


def logs_candidates() -> list[Path]:
    system = platform.system()
    candidates: list[Path] = []
    if system == "Windows":
        for root in msix_localcache_roots():
            candidates.append(root / "logs")
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(Path(appdata) / "Claude" / "logs")
    elif system == "Darwin":
        candidates.append(Path.home() / "Library" / "Logs" / "Claude")
    else:
        candidates.append(Path.home() / ".config" / "Claude" / "logs")
    return candidates


def default_config_path() -> Path:
    for candidate in config_candidates():
        if candidate.exists():
            return candidate
    candidates = config_candidates()
    return candidates[0] if candidates else Path("claude_desktop_config.json")


def default_logs_dir() -> Path:
    for candidate in logs_candidates():
        if candidate.exists():
            return candidate
    candidates = logs_candidates()
    return candidates[0] if candidates else Path("logs")


def redact_env(env: Any) -> dict[str, str]:
    if not isinstance(env, dict):
        return {}
    redacted: dict[str, str] = {}
    for key, value in env.items():
        text_key = str(key)
        value_text = str(value)
        if any(marker in text_key.upper() for marker in SECRET_MARKERS) or value_looks_secret(value_text):
            redacted[text_key] = "<redacted>"
        else:
            redacted[text_key] = value_text if len(value_text) <= 80 else value_text[:77] + "..."
    return redacted


def looks_like_local_path(value: str) -> bool:
    if value.startswith(("http://", "https://")):
        return False
    if value.startswith(("-", "--")):
        return False
    if value.startswith("@"):  # npm scoped package spec (e.g. @scope/server), not a path
        return False
    if re.fullmatch(r"/[a-zA-Z]", value):  # cmd flag such as /c or /k, not a path
        return False
    if value in {"-y", "run", "exec"}:
        return False
    return (
        "/" in value
        or "\\" in value
        or value.startswith(".")
        or value.startswith("~")
        or (len(value) > 2 and value[1:3] == ":\\")
        or (len(value) > 2 and value[1:3] == ":/")
    )


def is_absolute_like(value: str) -> bool:
    if value.startswith("~"):
        return False
    # Decide absoluteness by the value's own path flavor, not the host's, so a
    # Windows config validated from macOS/Linux (or vice versa) is judged correctly.
    if re.match(r"^[A-Za-z]:[\\/]", value) or value.startswith("\\\\"):
        return PureWindowsPath(value).is_absolute()
    if value.startswith("/"):
        return PurePosixPath(value).is_absolute()
    return Path(value).is_absolute()


def load_config(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    issues: list[str] = []
    if not path.exists():
        return None, [f"Config file not found: {path}"]
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return None, [f"Could not read config: {exc}"]
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        issues.append(
            "UTF-8 BOM detected. Some clients reject a config with a leading BOM. "
            "Re-save as UTF-8 without BOM (PowerShell 7: Set-Content -Encoding utf8NoBOM)."
        )
    try:
        # utf-8-sig tolerates a BOM so the parse below still works for diagnosis.
        data = json.loads(raw_bytes.decode("utf-8-sig"))
    except json.JSONDecodeError as exc:
        return None, issues + [f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"]
    except UnicodeDecodeError as exc:
        return None, issues + [f"Config is not valid UTF-8: {exc}. Re-save as UTF-8 (without BOM)."]
    if not isinstance(data, dict):
        issues.append("Config root should be a JSON object.")
        return None, issues
    if "mcpServers" not in data:
        issues.append("Missing top-level 'mcpServers'.")
    elif not isinstance(data["mcpServers"], dict):
        issues.append("'mcpServers' should be an object.")
    return data, issues


def inspect_servers(data: dict[str, Any], windows: bool) -> tuple[list[str], int]:
    lines: list[str] = []
    issue_count = 0
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return lines, issue_count
    if not servers:
        lines.append("No MCP servers configured.")
        return lines, issue_count

    for name, raw_server in servers.items():
        lines.append(f"\nServer: {name}")
        if not isinstance(raw_server, dict):
            lines.append("  ISSUE: server entry should be an object.")
            issue_count += 1
            continue

        command = raw_server.get("command")
        args = raw_server.get("args", [])
        env = raw_server.get("env", {})
        args_list = args if isinstance(args, list) else []

        lines.append(f"  command: {command!r}")
        wrapped_cmd_c = (
            isinstance(command, str)
            and command.strip().lower() in {"cmd", "cmd.exe"}
            and len(args_list) >= 1
            and isinstance(args_list[0], str)
            and args_list[0].lower() == "/c"
        )
        if not isinstance(command, str) or not command:
            lines.append("  ISSUE: missing or invalid command.")
            issue_count += 1
        else:
            base = command.strip().lower()
            resolved = shutil.which(command)
            resolves_to_shim = bool(resolved and resolved.lower().endswith((".cmd", ".bat")))
            # Only the npm family is always a .cmd shim by bare name; uv/uvx/bun/deno
            # are native .exe and are flagged only when the resolved file is a shim.
            is_bare_shim = base in NPM_FAMILY_SHIMS
            inner = args_list[1] if (wrapped_cmd_c and len(args_list) >= 2 and isinstance(args_list[1], str)) else None
            if wrapped_cmd_c:
                lines.append("  OK: wrapped with cmd /c (Windows-safe)" + (f" -> {inner}" if inner else "") + ".")
            elif resolved and not resolves_to_shim:
                lines.append(f"  command resolves to: {resolved}")
            elif resolves_to_shim or is_bare_shim:
                where = f" ({resolved})" if resolved else ""
                if windows:
                    lines.append(
                        f"  ISSUE: '{command}' is a .cmd/.bat launcher shim{where}. Node spawn (used by "
                        "the client) cannot run it without a shell, so it fails with spawn ENOENT/EINVAL "
                        f'on Windows. Wrap it: command="cmd", args=["/c", "{base}", ...], or point command '
                        "at the absolute node.exe/python.exe plus the entry script."
                    )
                    issue_count += 1
                else:
                    lines.append(
                        f"  NOTE: '{command}' is a shim{where}; on Windows it needs cmd /c (bare command "
                        "works on macOS/Linux). Re-run with --assume-windows to validate a Windows config."
                    )
            elif is_absolute_like(command) and Path(command).exists():
                lines.append("  command is an existing absolute path.")
            else:
                lines.append("  ISSUE: command was not found on PATH from this process.")
                issue_count += 1

        if not isinstance(args, list):
            lines.append("  ISSUE: args should be an array.")
            issue_count += 1
            args = []
        else:
            lines.append(f"  args: {args!r}")

        for arg in args:
            if not isinstance(arg, str):
                lines.append(f"  ISSUE: non-string arg: {arg!r}")
                issue_count += 1
                continue
            if looks_like_local_path(arg) and not is_absolute_like(arg):
                lines.append(f"  ISSUE: local path should be absolute: {arg!r}")
                issue_count += 1
            if any(ch in arg for ch in "\t\n\r\f\b\v"):
                lines.append(
                    f"  NOTE: arg contains a control character: {arg!r}. A Windows path with a single "
                    "backslash (e.g. C:\\temp -> the \\t becomes a TAB) corrupts on parse. Use forward "
                    "slashes (C:/temp) or doubled backslashes (C:\\\\temp)."
                )

        if isinstance(env, dict):
            if env:
                lines.append(f"  env: {json.dumps(redact_env(env), sort_keys=True)}")
        elif env is not None:
            lines.append("  ISSUE: env should be an object when present.")
            issue_count += 1

    return lines, issue_count


def redact_log_line(line: str) -> str:
    line = re.sub(r"(?i)(Bearer)\s+[A-Za-z0-9._~+/=-]+", r"\1 <redacted>", line)
    line = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-<redacted>", line)
    line = re.sub(r"(?i)(MCP-Session-Id\s*[:=]\s*)\S+", r"\1<redacted>", line)
    line = re.sub(
        r"(?i)(api[_-]?key|token|secret|password|authorization)([\"'\s:=]+)([^,\s\"']+)",
        r"\1\2<redacted>",
        line,
    )
    return line


def recent_log_files(logs_dir: Path) -> list[Path]:
    patterns = [str(logs_dir / "mcp*.log"), str(logs_dir / "*mcp*.log")]
    paths = {Path(path) for pattern in patterns for path in glob.glob(pattern)}

    def mtime(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:  # log rotated away mid-scan
            return 0.0

    return sorted(paths, key=mtime, reverse=True)


def tail_file(path: Path, lines: int) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [f"Could not read {path}: {exc}"]
    return content[-lines:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Claude Desktop MCP config and logs.")
    parser.add_argument("--config", type=Path, default=default_config_path(), help="Path to claude_desktop_config.json")
    parser.add_argument("--logs", type=Path, default=default_logs_dir(), help="Path to Claude logs directory")
    parser.add_argument("--tail", type=int, default=40, help="Recent log lines to show per file")
    parser.add_argument("--no-logs", action="store_true", help="Skip log preview")
    parser.add_argument("--assume-windows", action="store_true",
                        help="Apply Windows shim-spawn checks even when running on another OS")
    args = parser.parse_args()

    windows = platform.system() == "Windows" or args.assume_windows

    print("Claude Desktop MCP diagnostics")
    print(f"Platform: {platform.platform()}")

    # Surface the MSIX/LocalCache vs %APPDATA% divergence: the 'Edit Config'
    # button and the running app can read different files after an update.
    existing_configs = [c for c in config_candidates() if c.exists()]
    if platform.system() == "Windows" and len(existing_configs) > 1:
        print("\nWARNING: multiple Claude Desktop config files exist on this machine:")
        for c in existing_configs:
            print(f"  - {c}")
        print("  The MSIX/Store build reads the LocalCache copy; the 'Edit Config' button often opens")
        print("  the legacy %APPDATA% copy. Edit the one the app actually reads, then fully quit.")

    print(f"Config: {args.config}")

    data, issues = load_config(args.config)
    issue_count = len(issues)
    for issue in issues:
        print(f"ISSUE: {issue}")

    if data:
        print("Config JSON: valid")
        server_lines, server_issue_count = inspect_servers(data, windows)
        issue_count += server_issue_count
        for line in server_lines:
            print(line)

    if not args.no_logs:
        print(f"\nLogs: {args.logs}")
        if not args.logs.exists():
            # Benign before any server has started; not counted toward issue_count.
            print("NOTE: logs directory not found (normal if no MCP server has started yet).")
        else:
            logs = recent_log_files(args.logs)
            if not logs:
                print("No mcp*.log files found.")
            for log_path in logs[:3]:
                print(f"\n--- {log_path.name} ---")
                for line in tail_file(log_path, max(args.tail, 0)):
                    print(redact_log_line(line))

    return 1 if issue_count else 0


if __name__ == "__main__":
    sys.exit(main())
