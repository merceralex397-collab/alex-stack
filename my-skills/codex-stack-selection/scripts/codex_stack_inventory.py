#!/usr/bin/env python3
"""Inventory a project's Codex stack and recent local capability use."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


CACHE_VERSION = 2
OUTPUT_VERSION = 1
SKILL_NAME_RE = re.compile(r"\$([a-z0-9][a-z0-9-]{1,63})\b", re.IGNORECASE)
FRONTMATTER_FIELD_RE = re.compile(r"^(name|description):\s*(.*)$", re.MULTILINE)
RELEVANT_RECORD_MARKERS = (
    b'"type":"turn_context"',
    b'"type":"function_call"',
    b'"type":"custom_tool_call"',
    b'"type":"mcp_tool_call_end"',
    b'"role":"user"',
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(path: str | Path) -> str:
    expanded = os.path.expandvars(os.path.expanduser(str(path)))
    return os.path.normcase(os.path.abspath(expanded))


def _is_within(path: str | Path, root: str | Path) -> bool:
    try:
        return os.path.commonpath([_canonical(path), _canonical(root)]) == _canonical(root)
    except (ValueError, OSError):
        return False


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:24]


def _read_json(path: Path, warnings: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        warnings.append(f"Could not read JSON metadata at {path}: {type(exc).__name__}")
        return None


def _read_toml(path: Path, warnings: list[str]) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
        return value if isinstance(value, dict) else {}
    except (OSError, tomllib.TOMLDecodeError) as exc:
        warnings.append(f"Could not read TOML config at {path}: {type(exc).__name__}")
        return {}


def _clean_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _skill_metadata(path: Path, warnings: list[str]) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        warnings.append(f"Could not read skill metadata at {path}: {type(exc).__name__}")
        return path.parent.name, ""
    if not text.startswith("---"):
        return path.parent.name, ""
    end = text.find("\n---", 3)
    if end < 0:
        return path.parent.name, ""
    values = {match.group(1): _clean_yaml_scalar(match.group(2)) for match in FRONTMATTER_FIELD_RE.finditer(text[3:end])}
    return values.get("name") or path.parent.name, values.get("description") or ""


def _find_project_root(value: str | None) -> Path:
    candidate = Path(value or os.getcwd()).expanduser().resolve()
    if not candidate.exists() or not candidate.is_dir():
        raise ValueError(f"Project directory does not exist: {candidate}")
    try:
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return candidate


def _resolve_codex_cli() -> str | None:
    configured = os.environ.get("CODEX_CLI_PATH")
    if configured and Path(configured).is_file():
        return configured
    names = ["codex.exe", "codex.cmd", "codex"] if os.name == "nt" else ["codex"]
    for name in names:
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return None


def _run_codex_json(
    cli: str | None,
    args: list[str],
    project: Path,
    warnings: list[str],
) -> Any:
    if not cli:
        warnings.append("Codex CLI was not found; current plugin and MCP state is partial.")
        return None
    try:
        result = subprocess.run(
            [cli, *args],
            cwd=str(project),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        warnings.append(f"Codex {' '.join(args)} failed: {type(exc).__name__}")
        return None
    if result.returncode != 0:
        warnings.append(f"Codex {' '.join(args)} exited with code {result.returncode}.")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        warnings.append(f"Codex {' '.join(args)} returned invalid JSON.")
        return None


def _manifest_path(root: Path) -> Path | None:
    for relative in (
        Path(".codex-plugin") / "plugin.json",
        Path("plugin.json"),
        Path(".claude-plugin") / "plugin.json",
    ):
        candidate = root / relative
        if candidate.is_file():
            return candidate
    return None


def _resolve_plugin_root(item: dict[str, Any], codex_home: Path) -> Path | None:
    source = item.get("source") if isinstance(item.get("source"), dict) else {}
    path_value = source.get("path")
    if isinstance(path_value, str) and path_value:
        candidate = Path(path_value)
        if candidate.is_dir():
            return candidate.resolve()

    marketplace = str(item.get("marketplaceName") or "")
    name = str(item.get("name") or "")
    version = str(item.get("version") or "")
    candidates = [
        codex_home / "plugins" / "cache" / marketplace / name / version,
        codex_home / ".tmp" / "plugins" / "plugins" / name,
        codex_home / ".tmp" / "bundled-marketplaces" / marketplace / "plugins" / name,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    cache_parent = codex_home / "plugins" / "cache" / marketplace / name
    if cache_parent.is_dir():
        versions = sorted((p for p in cache_parent.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
        if versions:
            return versions[0].resolve()
    return None


def _resolve_component(root: Path, value: Any, default: str) -> list[Path]:
    if value is None:
        candidate = root / default
        return [candidate] if candidate.exists() else []
    values = value if isinstance(value, list) else [value]
    paths: list[Path] = []
    for raw in values:
        if isinstance(raw, str) and raw:
            candidate = (root / raw).resolve()
            if candidate.exists() and _is_within(candidate, root):
                paths.append(candidate)
    return paths


def _load_component_json(root: Path, value: Any, default: str, warnings: list[str]) -> list[Any]:
    if isinstance(value, (dict, list)):
        return [value]
    documents: list[Any] = []
    for path in _resolve_component(root, value, default):
        if path.is_file():
            document = _read_json(path, warnings)
            if document is not None:
                documents.append(document)
    return documents


def _app_entries(document: Any) -> list[dict[str, str]]:
    if not isinstance(document, dict):
        return []
    mapping = document.get("apps") if isinstance(document.get("apps"), dict) else document
    entries: list[dict[str, str]] = []
    if not isinstance(mapping, dict):
        return entries
    for alias, spec in mapping.items():
        if isinstance(spec, str):
            app_id = spec
        elif isinstance(spec, dict):
            app_id = spec.get("id")
        else:
            app_id = None
        if isinstance(app_id, str) and app_id:
            entries.append({"name": str(alias), "id": app_id})
    return entries


def _mcp_names(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return []
    mapping = document.get("mcpServers") if isinstance(document.get("mcpServers"), dict) else document
    if not isinstance(mapping, dict):
        return []
    return [str(name) for name, value in mapping.items() if isinstance(value, dict)]


def _plugin_inventory(
    raw: Any,
    codex_home: Path,
    warnings: list[str],
) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, str], list[tuple[Path, str, bool]]]:
    items = raw.get("installed", []) if isinstance(raw, dict) else []
    plugins: list[dict[str, Any]] = []
    app_owners: dict[str, str] = {}
    mcp_owners: dict[str, str] = {}
    skill_roots: list[tuple[Path, str, bool]] = []

    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        plugin_id = str(item.get("pluginId") or "")
        if not plugin_id:
            continue
        root = _resolve_plugin_root(item, codex_home)
        manifest: dict[str, Any] = {}
        manifest_file = _manifest_path(root) if root else None
        if manifest_file:
            loaded = _read_json(manifest_file, warnings)
            if isinstance(loaded, dict):
                manifest = loaded
        enabled = bool(item.get("enabled"))
        description = str(
            manifest.get("description")
            or (manifest.get("interface") or {}).get("shortDescription")
            or ""
        )
        plugin_apps: list[dict[str, str]] = []
        plugin_mcps: list[str] = []
        hooks_present = False
        if root:
            for skill_root in _resolve_component(root, manifest.get("skills"), "skills"):
                if skill_root.is_dir():
                    skill_roots.append((skill_root, plugin_id, enabled))
            for document in _load_component_json(root, manifest.get("apps"), ".app.json", warnings):
                plugin_apps.extend(_app_entries(document))
            for document in _load_component_json(root, manifest.get("mcpServers"), ".mcp.json", warnings):
                plugin_mcps.extend(_mcp_names(document))
            hooks_present = bool(_resolve_component(root, manifest.get("hooks"), str(Path("hooks") / "hooks.json")))
        for app in plugin_apps:
            app_owners[app["id"]] = plugin_id
        for name in plugin_mcps:
            mcp_owners[name] = plugin_id
        plugins.append(
            {
                "id": plugin_id,
                "name": str(item.get("name") or manifest.get("name") or plugin_id),
                "marketplace": str(item.get("marketplaceName") or ""),
                "version": str(item.get("version") or manifest.get("version") or ""),
                "installed": bool(item.get("installed", True)),
                "enabled": enabled,
                "description": description,
                "root_resolved": root is not None,
                "components": {
                    "apps": sorted(plugin_apps, key=lambda value: value["id"]),
                    "mcp_servers": sorted(set(plugin_mcps)),
                    "hooks_present": hooks_present,
                },
            }
        )
    return sorted(plugins, key=lambda value: value["id"]), app_owners, mcp_owners, skill_roots


def _config_layers(codex_home: Path, project: Path, warnings: list[str]) -> list[tuple[Path, dict[str, Any]]]:
    paths = [codex_home / "config.toml", project / ".codex" / "config.toml"]
    return [(path, _read_toml(path, warnings)) for path in paths if path.is_file()]


def _project_trust(project: Path, global_config: dict[str, Any]) -> dict[str, Any]:
    matches: list[tuple[int, str, str]] = []
    projects = global_config.get("projects")
    if isinstance(projects, dict):
        for raw_path, value in projects.items():
            if not isinstance(raw_path, str) or not isinstance(value, dict):
                continue
            if _is_within(project, raw_path):
                matches.append((len(_canonical(raw_path)), raw_path, str(value.get("trust_level") or "unknown")))
    if not matches:
        return {"trusted": None, "level": "unknown", "matched_path": None}
    _, matched_path, level = max(matches)
    return {"trusted": level.lower() == "trusted", "level": level, "matched_path": matched_path}


def _skill_overrides(layers: list[tuple[Path, dict[str, Any]]]) -> dict[str, bool]:
    overrides: dict[str, bool] = {}
    for config_path, config in layers:
        skills = config.get("skills")
        entries = skills.get("config") if isinstance(skills, dict) else None
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                continue
            raw_path = Path(os.path.expandvars(os.path.expanduser(entry["path"])))
            resolved = raw_path if raw_path.is_absolute() else (config_path.parent / raw_path)
            overrides[_canonical(resolved)] = bool(entry.get("enabled", True))
    return overrides


def _iter_skill_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return []
    return (path for path in root.rglob("SKILL.md") if path.is_file())


def _skills_inventory(
    project: Path,
    codex_home: Path,
    plugin_skill_roots: list[tuple[Path, str, bool]],
    layers: list[tuple[Path, dict[str, Any]]],
    warnings: list[str],
) -> list[dict[str, Any]]:
    roots: list[tuple[Path, str, str | None, bool]] = [
        (project / ".agents" / "skills", "project", None, True),
        (Path.home() / ".agents" / "skills", "user", None, True),
        (codex_home / "skills", "user", None, True),
    ]
    roots.extend((root, "plugin", owner, enabled) for root, owner, enabled in plugin_skill_roots)
    overrides = _skill_overrides(layers)
    seen: set[str] = set()
    skills: list[dict[str, Any]] = []
    for root, scope, owner, owner_enabled in roots:
        for path in _iter_skill_files(root):
            canonical = _canonical(path)
            if canonical in seen:
                continue
            seen.add(canonical)
            name, description = _skill_metadata(path, warnings)
            effective = overrides.get(canonical, True) and owner_enabled
            actual_scope = "system" if _is_within(path, codex_home / "skills" / ".system") else scope
            skills.append(
                {
                    "name": name,
                    "description": description,
                    "path": str(path.resolve()),
                    "scope": actual_scope,
                    "owner_plugin": owner,
                    "enabled": effective,
                }
            )
    return sorted(skills, key=lambda value: (value["name"].lower(), value["path"].lower()))


def _effective_app_config(layers: list[tuple[Path, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    effective: dict[str, dict[str, Any]] = {}
    for _, config in layers:
        apps = config.get("apps")
        if not isinstance(apps, dict):
            continue
        for app_id, value in apps.items():
            if app_id == "_default" or not isinstance(value, dict):
                continue
            entry = effective.setdefault(str(app_id), {})
            if "enabled" in value:
                entry["enabled"] = bool(value["enabled"])
    return effective


def _cached_app_catalog(codex_home: Path, warnings: list[str]) -> dict[str, dict[str, Any]]:
    cache_root = codex_home / "plugins" / "cache"
    catalog: dict[str, dict[str, Any]] = {}
    if not cache_root.is_dir():
        return catalog
    for app_file in cache_root.glob("*/*/*/.app.json"):
        try:
            relative = app_file.relative_to(cache_root)
            marketplace, plugin_name, version = relative.parts[:3]
            modified = app_file.stat().st_mtime_ns
        except (ValueError, OSError):
            continue
        document = _read_json(app_file, warnings)
        root = app_file.parent
        manifest_file = _manifest_path(root)
        manifest = _read_json(manifest_file, warnings) if manifest_file else {}
        description = str(manifest.get("description") or "") if isinstance(manifest, dict) else ""
        interface = manifest.get("interface") if isinstance(manifest, dict) and isinstance(manifest.get("interface"), dict) else {}
        display_name = str(interface.get("displayName") or "")
        for app in _app_entries(document):
            existing = catalog.get(app["id"])
            if existing and int(existing.get("_modified", 0)) >= modified:
                continue
            catalog[app["id"]] = {
                "name": display_name or app["name"],
                "owner_plugin": f"{plugin_name}@{marketplace}",
                "version": version,
                "description": description,
                "_modified": modified,
            }
    for value in catalog.values():
        value.pop("_modified", None)
    return catalog


def _apps_inventory(
    plugins: list[dict[str, Any]],
    app_owners: dict[str, str],
    layers: list[tuple[Path, dict[str, Any]]],
    cached_catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    plugin_by_id = {plugin["id"]: plugin for plugin in plugins}
    entries: dict[str, dict[str, Any]] = {}
    for plugin in plugins:
        for app in plugin["components"]["apps"]:
            entries[app["id"]] = {
                "id": app["id"],
                "name": app["name"],
                "owner_plugin": plugin["id"],
                "enabled": plugin["enabled"],
                "authorized": "unknown",
                "description": plugin.get("description") or "",
                "owner_installed": True,
            }
    for app_id, config in _effective_app_config(layers).items():
        cached = cached_catalog.get(app_id, {})
        owner = app_owners.get(app_id) or cached.get("owner_plugin")
        entry = entries.setdefault(
            app_id,
            {
                "id": app_id,
                "name": cached.get("name") or app_id,
                "owner_plugin": owner,
                "enabled": plugin_by_id.get(owner, {}).get("enabled", True),
                "authorized": "unknown",
                "description": cached.get("description") or "",
                "owner_installed": owner in plugin_by_id if owner else False,
            },
        )
        if "enabled" in config:
            entry["enabled"] = config["enabled"] and plugin_by_id.get(owner, {}).get("enabled", True)
        entry["configured"] = True
    for entry in entries.values():
        entry.setdefault("configured", False)
        entry.setdefault("description", "")
        entry.setdefault("owner_installed", entry.get("owner_plugin") in plugin_by_id)
    return sorted(entries.values(), key=lambda value: (value["name"].lower(), value["id"]))


def _transport_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"type": "unknown"}
    result: dict[str, Any] = {"type": str(value.get("type") or "unknown")}
    command = value.get("command")
    if isinstance(command, str) and command:
        result["command"] = Path(command).name
    url = value.get("url")
    if isinstance(url, str) and url:
        parsed = urlsplit(url)
        result["host"] = parsed.hostname or ""
    env = value.get("env")
    if isinstance(env, dict) and env:
        result["environment_names"] = sorted(str(name) for name in env)
    headers = value.get("http_headers")
    if isinstance(headers, dict) and headers:
        result["header_names"] = sorted(str(name) for name in headers)
    env_headers = value.get("env_http_headers")
    if isinstance(env_headers, dict) and env_headers:
        result["environment_header_names"] = sorted(str(name) for name in env_headers)
    token_name = value.get("bearer_token_env_var")
    if isinstance(token_name, str) and token_name:
        result["bearer_token_environment_name"] = token_name
    return result


def _mcp_inventory(raw: Any, owners: dict[str, str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        entries.append(
            {
                "name": str(item["name"]),
                "enabled": bool(item.get("enabled")),
                "disabled_reason": item.get("disabled_reason"),
                "owner_plugin": owners.get(str(item["name"])),
                "transport": _transport_summary(item.get("transport")),
                "auth_status": str(item.get("auth_status") or "unknown"),
            }
        )
    return sorted(entries, key=lambda value: value["name"].lower())


def _extract_message_text(content: Any) -> str:
    pieces: list[str] = []
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                value = item.get("text") or item.get("input_text")
                if isinstance(value, str):
                    pieces.append(value)
    return "\n".join(pieces)


def _event_status(result: Any) -> str:
    if isinstance(result, dict):
        keys = {str(key).lower() for key in result}
        if "err" in keys or "error" in keys:
            return "failure"
        if "ok" in keys:
            return "success"
    return "unknown"


def _event_from_mcp(
    timestamp: datetime | None,
    call_id: str,
    server: str,
    tool: str,
    status: str,
) -> dict[str, Any]:
    if server.startswith("mcp__"):
        server = server[5:]
    if server.startswith("codex_apps__"):
        return {
            "key": _stable_hash(f"call:{call_id}"),
            "timestamp": _iso(timestamp),
            "kind": "app",
            "capability": server[len("codex_apps__") :],
            "tool": tool,
            "status": status,
        }
    return {
        "key": _stable_hash(f"call:{call_id}"),
        "timestamp": _iso(timestamp),
        "kind": "mcp",
        "capability": server,
        "tool": tool,
        "status": status,
    }


def _scan_session_file(
    path: Path,
    project: Path,
    cutoff: datetime,
    skill_paths: dict[str, str],
    cached: dict[str, Any] | None,
    refresh: bool,
    warnings: list[str],
) -> dict[str, Any]:
    stat = path.stat()
    can_append = (
        not refresh
        and isinstance(cached, dict)
        and cached.get("project") == _canonical(project)
        and isinstance(cached.get("offset"), int)
        and 0 <= cached["offset"] <= stat.st_size
        and cached.get("size", 0) <= stat.st_size
    )
    start = cached["offset"] if can_append else 0
    events = list(cached.get("events", [])) if can_append else []
    pending = dict(cached.get("pending", {})) if can_append else {}
    active_cwd = str(cached.get("active_cwd") or "") if can_append else ""
    active_turn = str(cached.get("active_turn") or "") if can_append else ""
    session_id = str(cached.get("session_id") or "") if can_append else ""
    parsed_records = 0

    try:
        with path.open("rb") as handle:
            handle.seek(start)
            while True:
                raw = handle.readline()
                if not raw:
                    break
                if not any(marker in raw for marker in RELEVANT_RECORD_MARKERS) and b'"type":"session_meta"' not in raw:
                    continue
                try:
                    record = json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                parsed_records += 1
                payload = record.get("payload") if isinstance(record, dict) else None
                if not isinstance(payload, dict):
                    continue
                payload_type = payload.get("type")
                timestamp = _parse_timestamp(record.get("timestamp"))

                if record.get("type") == "session_meta":
                    session_id = str(payload.get("id") or payload.get("session_id") or session_id)
                    active_cwd = str(payload.get("cwd") or active_cwd)
                    continue
                if record.get("type") == "turn_context":
                    active_cwd = str(payload.get("cwd") or active_cwd)
                    active_turn = str(payload.get("turn_id") or active_turn)
                    continue

                in_scope = bool(active_cwd and _is_within(active_cwd, project))
                if not in_scope or (timestamp and timestamp < cutoff):
                    continue

                if payload_type == "message" and payload.get("role") == "user":
                    text = _extract_message_text(payload.get("content"))
                    for name in set(match.group(1).lower() for match in SKILL_NAME_RE.finditer(text)):
                        scope_id = active_turn or _iso(timestamp) or session_id
                        events.append(
                            {
                                "key": _stable_hash(f"skill:{scope_id}:{name}"),
                                "timestamp": _iso(timestamp),
                                "kind": "skill",
                                "capability": name,
                                "status": "success",
                                "signal": "explicit_invocation",
                            }
                        )
                    continue

                if payload_type == "function_call":
                    arguments = payload.get("arguments")
                    argument_text = arguments if isinstance(arguments, str) else json.dumps(arguments, ensure_ascii=False)
                    normalized_arguments = os.path.normcase(argument_text.replace("\\\\", "\\"))
                    for canonical_path, skill_name in skill_paths.items():
                        if canonical_path in normalized_arguments:
                            scope_id = active_turn or _iso(timestamp) or session_id
                            events.append(
                                {
                                    "key": _stable_hash(f"skill:{scope_id}:{skill_name.lower()}"),
                                    "timestamp": _iso(timestamp),
                                    "kind": "skill",
                                    "capability": skill_name,
                                    "status": "success",
                                    "signal": "skill_file_read",
                                }
                            )
                    namespace = str(payload.get("namespace") or "")
                    if namespace.startswith("mcp__"):
                        call_id = str(payload.get("call_id") or payload.get("id") or "")
                        if call_id:
                            pending[_stable_hash(call_id)] = {
                                "timestamp": _iso(timestamp),
                                "server": namespace,
                                "tool": str(payload.get("name") or ""),
                            }
                    continue

                if payload_type == "custom_tool_call":
                    input_value = payload.get("input")
                    input_text = input_value if isinstance(input_value, str) else json.dumps(input_value, ensure_ascii=False)
                    normalized_input = os.path.normcase(input_text.replace("\\\\", "\\"))
                    for canonical_path, skill_name in skill_paths.items():
                        if canonical_path in normalized_input:
                            scope_id = active_turn or _iso(timestamp) or session_id
                            events.append(
                                {
                                    "key": _stable_hash(f"skill:{scope_id}:{skill_name.lower()}"),
                                    "timestamp": _iso(timestamp),
                                    "kind": "skill",
                                    "capability": skill_name,
                                    "status": "success",
                                    "signal": "skill_file_read",
                                }
                            )
                    continue

                if payload_type == "mcp_tool_call_end":
                    call_id = str(payload.get("call_id") or "")
                    call_key = _stable_hash(call_id)
                    start_record = pending.pop(call_key, {})
                    invocation = payload.get("invocation") if isinstance(payload.get("invocation"), dict) else {}
                    server = str(start_record.get("server") or invocation.get("server") or "")
                    tool = str(start_record.get("tool") or invocation.get("tool") or "")
                    if server and call_id:
                        start_timestamp = _parse_timestamp(start_record.get("timestamp")) or timestamp
                        events.append(
                            _event_from_mcp(
                                start_timestamp,
                                call_id,
                                server,
                                tool,
                                _event_status(payload.get("result")),
                            )
                        )
    except OSError as exc:
        warnings.append(f"Could not scan session log {path.name}: {type(exc).__name__}")

    events = [
        event
        for event in events
        if (_parse_timestamp(event.get("timestamp")) or cutoff) >= cutoff
    ]
    return {
        "project": _canonical(project),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "offset": stat.st_size,
        "session_id": session_id,
        "active_cwd": active_cwd,
        "active_turn": active_turn,
        "events": events,
        "pending": pending,
        "parsed_records": parsed_records,
    }


def _session_meta(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            first = handle.readline()
        record = json.loads(first)
        payload = record.get("payload") if isinstance(record, dict) else {}
        return {
            "cwd": str(payload.get("cwd") or ""),
            "session_id": str(payload.get("id") or payload.get("session_id") or ""),
        }
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {"cwd": "", "session_id": ""}


def _load_cache(path: Path, warnings: list[str]) -> dict[str, Any]:
    if not path.is_file():
        return {"version": CACHE_VERSION, "files": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("version") == CACHE_VERSION and isinstance(value.get("files"), dict):
            return value
    except (OSError, json.JSONDecodeError, AttributeError):
        warnings.append("The usage cache was unreadable and will be rebuilt.")
    return {"version": CACHE_VERSION, "files": {}}


def _write_cache(path: Path, value: dict[str, Any], warnings: list[str]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
            temporary = Path(handle.name)
        os.replace(temporary, path)
    except OSError as exc:
        warnings.append(f"Could not write the local usage cache: {type(exc).__name__}")


def _aggregate_events(
    file_entries: list[dict[str, Any]],
    cutoff: datetime,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    seen: set[str] = set()
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    pending_events: list[dict[str, Any]] = []

    for entry in file_entries:
        for event in entry.get("events", []):
            key = str(event.get("key") or "")
            timestamp = _parse_timestamp(event.get("timestamp"))
            if not key or key in seen or (timestamp and timestamp < cutoff):
                continue
            seen.add(key)
            bucket_key = (str(event.get("kind") or ""), str(event.get("capability") or ""))
            bucket = buckets.setdefault(
                bucket_key,
                {
                    "name": bucket_key[1],
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0,
                    "incomplete": 0,
                    "last_used": None,
                    "signals": set(),
                    "tools": set(),
                },
            )
            bucket["attempts"] += 1
            status = str(event.get("status") or "unknown")
            if status == "success":
                bucket["successes"] += 1
            elif status == "failure":
                bucket["failures"] += 1
            else:
                bucket["incomplete"] += 1
            if timestamp and (bucket["last_used"] is None or timestamp > bucket["last_used"]):
                bucket["last_used"] = timestamp
            if event.get("signal"):
                bucket["signals"].add(str(event["signal"]))
            if event.get("tool"):
                bucket["tools"].add(str(event["tool"]))

        for call_key, pending in entry.get("pending", {}).items():
            timestamp = _parse_timestamp(pending.get("timestamp"))
            if timestamp and timestamp < cutoff:
                continue
            server = str(pending.get("server") or "")
            if not server:
                continue
            pending_events.append(
                _event_from_mcp(
                    timestamp,
                    call_key,
                    server,
                    str(pending.get("tool") or ""),
                    "unknown",
                )
            )

    for event in pending_events:
        key = str(event.get("key") or "")
        if key in seen:
            continue
        seen.add(key)
        bucket_key = (str(event["kind"]), str(event["capability"]))
        bucket = buckets.setdefault(
            bucket_key,
            {
                "name": bucket_key[1],
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "incomplete": 0,
                "last_used": None,
                "signals": set(),
                "tools": set(),
            },
        )
        bucket["attempts"] += 1
        bucket["incomplete"] += 1
        timestamp = _parse_timestamp(event.get("timestamp"))
        if timestamp and (bucket["last_used"] is None or timestamp > bucket["last_used"]):
            bucket["last_used"] = timestamp
        if event.get("tool"):
            bucket["tools"].add(str(event["tool"]))

    result: dict[str, list[dict[str, Any]]] = {"skills": [], "mcps": [], "apps": []}
    plural = {"skill": "skills", "mcp": "mcps", "app": "apps"}
    for (kind, _), bucket in buckets.items():
        target = plural.get(kind)
        if not target:
            continue
        bucket["last_used"] = _iso(bucket["last_used"])
        bucket["signals"] = sorted(bucket["signals"])
        bucket["tools"] = sorted(bucket["tools"])
        result[target].append(bucket)
    for entries in result.values():
        entries.sort(key=lambda value: value["name"].lower())
    return result, pending_events


def _plugin_usage(
    plugins: list[dict[str, Any]],
    skills: list[dict[str, Any]],
    apps: list[dict[str, Any]],
    mcps: list[dict[str, Any]],
    usage: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    owners: dict[tuple[str, str], str] = {}
    for skill in skills:
        if skill.get("owner_plugin"):
            owners[("skill", str(skill["name"]).lower())] = str(skill["owner_plugin"])
    for app in apps:
        if app.get("owner_plugin"):
            owners[("app", str(app["name"]).lower())] = str(app["owner_plugin"])
            owners[("app", str(app["id"]).lower())] = str(app["owner_plugin"])
    for mcp in mcps:
        if mcp.get("owner_plugin"):
            owners[("mcp", str(mcp["name"]).lower())] = str(mcp["owner_plugin"])

    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"attempts": 0, "successes": 0, "failures": 0, "incomplete": 0, "last_used": None, "components": set()}
    )
    for singular, plural in (("skill", "skills"), ("app", "apps"), ("mcp", "mcps")):
        for entry in usage[plural]:
            owner = owners.get((singular, str(entry["name"]).lower()))
            if not owner:
                continue
            total = totals[owner]
            for field in ("attempts", "successes", "failures", "incomplete"):
                total[field] += int(entry[field])
            timestamp = _parse_timestamp(entry.get("last_used"))
            if timestamp and (total["last_used"] is None or timestamp > total["last_used"]):
                total["last_used"] = timestamp
            total["components"].add(f"{singular}:{entry['name']}")
    results: list[dict[str, Any]] = []
    for plugin in plugins:
        total = totals.get(plugin["id"])
        if not total:
            continue
        results.append(
            {
                "name": plugin["id"],
                "attempts": total["attempts"],
                "successes": total["successes"],
                "failures": total["failures"],
                "incomplete": total["incomplete"],
                "last_used": _iso(total["last_used"]),
                "components": sorted(total["components"]),
            }
        )
    return sorted(results, key=lambda value: value["name"])


def _scan_usage(
    project: Path,
    codex_home: Path,
    days: int,
    skills: list[dict[str, Any]],
    no_cache: bool,
    refresh: bool,
    warnings: list[str],
) -> dict[str, Any]:
    now = _utc_now()
    cutoff = now - timedelta(days=days)
    session_root = codex_home / "sessions"
    cache_path = codex_home / "cache" / "codex-stack-selection" / "session-usage-v2.json"
    cache = {"version": CACHE_VERSION, "files": {}} if no_cache else _load_cache(cache_path, warnings)
    cache_files = cache.setdefault("files", {})
    skill_paths = {_canonical(skill["path"]): str(skill["name"]) for skill in skills}
    matched: list[Path] = []
    considered = 0
    bytes_matched = 0

    if session_root.is_dir():
        for path in session_root.rglob("*.jsonl"):
            try:
                stat = path.stat()
            except OSError:
                continue
            if datetime.fromtimestamp(stat.st_mtime, timezone.utc) < cutoff - timedelta(days=1):
                continue
            considered += 1
            meta = _session_meta(path)
            if meta["cwd"] and _is_within(meta["cwd"], project):
                matched.append(path)
                bytes_matched += stat.st_size

    entries: list[dict[str, Any]] = []
    cached_count = 0
    for path in matched:
        try:
            relative = str(path.relative_to(session_root))
        except ValueError:
            relative = str(path)
        previous = cache_files.get(relative)
        stat = path.stat()
        unchanged = (
            not refresh
            and isinstance(previous, dict)
            and previous.get("project") == _canonical(project)
            and previous.get("size") == stat.st_size
            and previous.get("mtime_ns") == stat.st_mtime_ns
        )
        if unchanged:
            entry = previous
            cached_count += 1
        else:
            entry = _scan_session_file(path, project, cutoff, skill_paths, previous, refresh, warnings)
            cache_files[relative] = entry
        entries.append(entry)

    if not no_cache:
        _write_cache(cache_path, cache, warnings)
    usage, _ = _aggregate_events(entries, cutoff)
    parsed_records = sum(int(entry.get("parsed_records", 0)) for entry in entries)
    attributed_events = sum(
        int(item.get("attempts", 0))
        for category in ("skills", "mcps", "apps")
        for item in usage[category]
    )
    if matched and attributed_events == 0:
        warnings.append(
            "Matching project sessions contained no attributable skill, MCP, or app events; "
            "treat missing usage as inconclusive rather than unused."
        )
    return {
        "window": {"days": days, "from": _iso(cutoff), "to": _iso(now)},
        "coverage": {
            "session_root_found": session_root.is_dir(),
            "files_considered": considered,
            "files_matched": len(matched),
            "files_reused_from_cache": cached_count,
            "bytes_matched": bytes_matched,
            "relevant_records_parsed": parsed_records,
            "attributed_events": attributed_events,
            "cache_enabled": not no_cache,
            "cache_path": str(cache_path) if not no_cache else None,
        },
        **usage,
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory Codex capabilities and project-scoped usage without exposing transcript content."
    )
    parser.add_argument("--project", help="Project directory; defaults to the current Git root or cwd.")
    parser.add_argument("--days", type=int, default=14, help="Usage window in days (default: 14).")
    parser.add_argument("--refresh", action="store_true", help="Rescan matched transcript files instead of reusing cached offsets.")
    parser.add_argument("--no-cache", action="store_true", help="Do not read or write the derived local usage cache.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)
    if args.days < 1 or args.days > 365:
        parser.error("--days must be between 1 and 365")
    return args


def build_inventory(args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    project = _find_project_root(args.project)
    codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")).expanduser().resolve()
    layers = _config_layers(codex_home, project, warnings)
    global_config = layers[0][1] if layers and layers[0][0] == codex_home / "config.toml" else _read_toml(codex_home / "config.toml", warnings)
    cli = _resolve_codex_cli()
    raw_plugins = _run_codex_json(cli, ["plugin", "list", "--json"], project, warnings)
    raw_mcps = _run_codex_json(cli, ["mcp", "list", "--json"], project, warnings)
    plugins, app_owners, mcp_owners, plugin_skill_roots = _plugin_inventory(raw_plugins, codex_home, warnings)
    skills = _skills_inventory(project, codex_home, plugin_skill_roots, layers, warnings)
    apps = _apps_inventory(plugins, app_owners, layers, _cached_app_catalog(codex_home, warnings))
    mcps = _mcp_inventory(raw_mcps, mcp_owners)
    usage = _scan_usage(project, codex_home, args.days, skills, args.no_cache, args.refresh, warnings)
    usage["plugins"] = _plugin_usage(plugins, skills, apps, mcps, usage)

    return {
        "schema_version": OUTPUT_VERSION,
        "generated_at": _iso(_utc_now()),
        "project": {
            "path": str(project),
            "trust": _project_trust(project, global_config),
            "config_path": str(project / ".codex" / "config.toml"),
            "config_exists": (project / ".codex" / "config.toml").is_file(),
        },
        "sources": {
            "codex_cli": cli is not None,
            "plugin_json": raw_plugins is not None,
            "mcp_json": raw_mcps is not None,
            "session_logs": usage["coverage"]["session_root_found"],
        },
        "inventory": {
            "skills": skills,
            "plugins": plugins,
            "apps": apps,
            "mcp_servers": mcps,
        },
        "usage": usage,
        "warnings": sorted(set(warnings)),
        "privacy": {
            "message_content_emitted": False,
            "tool_arguments_emitted": False,
            "tool_results_emitted": False,
            "secret_values_emitted": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        result = build_inventory(args)
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=True, indent=indent, separators=None if indent else (",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
