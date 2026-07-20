#!/usr/bin/env python3
"""Create, validate, preview, and install portable Codex profile packs."""

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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROFILE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TABLE_HEADER_RE = re.compile(r"^\s*\[\[?([^\]]+?)\]\]?\s*(?:#.*)?$")
FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.DOTALL)
COMPONENTS = {
    "skill",
    "agent",
    "rule",
    "agents-md",
    "hook",
    "mcp",
    "config",
    "profile",
}
SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


class PackError(RuntimeError):
    """An expected pack validation or installation error."""


@dataclass(frozen=True)
class DestinationContext:
    scope: str
    project_root: Path | None
    codex_home: Path
    user_home: Path
    config_layer: Path
    profile: str | None


@dataclass(frozen=True)
class FileOperation:
    source: Path
    destination: Path
    component: str
    action: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def try_read_text(path: Path) -> str | None:
    try:
        return read_text(path)
    except UnicodeDecodeError:
        return None


def write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", delete=False, dir=path.parent
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_toml(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(read_text(path))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise PackError(f"{path}: invalid TOML: {exc}") from exc


def load_manifest(pack: Path) -> dict[str, Any]:
    manifest_path = pack / "pack.toml"
    if not manifest_path.is_file():
        raise PackError(f"Missing manifest: {manifest_path}")
    manifest = load_toml(manifest_path)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise PackError(
            f"{manifest_path}: schema_version must be {SCHEMA_VERSION}"
        )
    name = manifest.get("name")
    if not isinstance(name, str) or not SLUG_RE.fullmatch(name):
        raise PackError(
            f"{manifest_path}: name must use lowercase letters, digits, and hyphens"
        )
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        raise PackError(f"{manifest_path}: description must be non-empty")
    install = manifest.get("install", {})
    if not isinstance(install, dict):
        raise PackError(f"{manifest_path}: install must be a table")
    default_scope = install.get("default_scope", "project")
    if default_scope not in {"project", "global"}:
        raise PackError(
            f"{manifest_path}: install.default_scope must be project or global"
        )
    profile = install.get("profile", "")
    if profile and (
        not isinstance(profile, str) or not PROFILE_RE.fullmatch(profile)
    ):
        raise PackError(f"{manifest_path}: install.profile is not a valid name")
    return manifest


def parse_components(value: str) -> list[str]:
    requested = [item.strip() for item in value.split(",") if item.strip()]
    unknown = sorted(set(requested) - COMPONENTS)
    if unknown:
        raise PackError(f"Unknown components: {', '.join(unknown)}")
    if not requested:
        raise PackError("Select at least one component")
    return requested


def init_pack(path: Path, name: str, components: list[str], scope: str) -> None:
    if not SLUG_RE.fullmatch(name):
        raise PackError("Pack name must use lowercase letters, digits, and hyphens")
    if path.exists():
        raise PackError(f"Destination already exists: {path}")
    path.mkdir(parents=True)
    profile = name if "profile" in components else ""
    write_text_atomic(
        path / "pack.toml",
        (
            f'schema_version = {SCHEMA_VERSION}\n'
            f'name = "{name}"\n'
            f'description = "TODO: describe the {name} Codex pack."\n\n'
            "[install]\n"
            f'default_scope = "{scope}"\n'
            f'profile = "{profile}"\n'
        ),
    )
    if "skill" in components:
        write_text_atomic(
            path / "skills" / name / "SKILL.md",
            (
                "---\n"
                f"name: {name}\n"
                "description: TODO: explain what this skill does and when to use it.\n"
                "---\n\n"
                f"# {name.replace('-', ' ').title()}\n\n"
                "TODO: write imperative workflow instructions.\n"
            ),
        )
    if "agent" in components:
        write_text_atomic(
            path / "agents" / f"{name}.toml",
            (
                f'name = "{name}"\n'
                'description = "TODO: explain when to delegate to this agent."\n'
                'developer_instructions = """\n'
                "TODO: define one narrow delegated role.\n"
                '"""\n'
            ),
        )
    if "rule" in components:
        write_text_atomic(
            path / "rules" / f"{name}.rules",
            (
                "# TODO: replace this safe example with an intentional command policy.\n"
                "prefix_rule(\n"
                '    pattern = ["git", "status"],\n'
                '    decision = "allow",\n'
                '    justification = "Read repository status.",\n'
                '    match = ["git status", "git status --short"],\n'
                '    not_match = ["git diff"],\n'
                ")\n"
            ),
        )
    if "agents-md" in components:
        write_text_atomic(
            path / "AGENTS.md",
            (
                f"# {name.replace('-', ' ').title()}\n\n"
                "TODO: add concise durable guidance for the selected scope.\n"
            ),
        )
    if "hook" in components:
        write_text_atomic(
            path / "hooks" / "hooks.json",
            json.dumps(
                {
                    "description": f"Lifecycle hooks for {name}.",
                    "hooks": {},
                },
                indent=2,
            )
            + "\n",
        )
    if "mcp" in components:
        write_text_atomic(
            path / "mcp.toml",
            (
                "# TODO: define [mcp_servers.<name>] using environment references "
                "for credentials.\n"
            ),
        )
    if "config" in components:
        write_text_atomic(
            path / "config.toml",
            "# TODO: add only the base Codex settings this pack requires.\n",
        )
    if "profile" in components:
        write_text_atomic(
            path / "profile.toml",
            "# TODO: add only profile-specific Codex overrides.\n",
        )


def iter_pack_files(pack: Path) -> Iterable[Path]:
    for path in pack.rglob("*"):
        if path.is_symlink():
            yield path
        elif path.is_file():
            yield path


def parse_frontmatter(path: Path) -> dict[str, str]:
    match = FRONTMATTER_RE.match(read_text(path))
    if not match:
        raise PackError(f"{path}: missing YAML frontmatter")
    values: dict[str, str] = {}
    block_key: str | None = None
    block_lines: list[str] = []
    for raw_line in match.group(1).splitlines():
        if block_key and (raw_line.startswith(" ") or raw_line.startswith("\t")):
            block_lines.append(raw_line.strip())
            continue
        if block_key:
            values[block_key] = " ".join(block_lines).strip()
            block_key = None
            block_lines = []
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            raise PackError(f"{path}: unsupported frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {"|", "|-", ">", ">-"}:
            block_key = key
        else:
            values[key] = value.strip("\"'")
    if block_key:
        values[block_key] = " ".join(block_lines).strip()
    if set(values) != {"name", "description"}:
        raise PackError(f"{path}: frontmatter must contain only name and description")
    if not SLUG_RE.fullmatch(values["name"]):
        raise PackError(f"{path}: invalid skill name")
    if not values["description"]:
        raise PackError(f"{path}: empty skill description")
    return values


def validate_hooks(path: Path) -> None:
    try:
        value = json.loads(read_text(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PackError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("hooks"), dict):
        raise PackError(f"{path}: expected an object containing a hooks object")
    for event, hooks in value["hooks"].items():
        if not isinstance(event, str) or not isinstance(hooks, list):
            raise PackError(f"{path}: hook event values must be arrays")
        for hook_group in hooks:
            if not isinstance(hook_group, dict):
                raise PackError(f"{path}: each hook event entry must be an object")


def scan_for_secrets(path: Path) -> list[str]:
    content = try_read_text(path)
    if content is None:
        return []
    return [label for label, pattern in SECRET_PATTERNS.items() if pattern.search(content)]


def check_rule_file(path: Path) -> str | None:
    executable = shutil.which("codex")
    if not executable:
        return "codex executable not found; rule syntax was not checked"
    result = subprocess.run(
        [
            executable,
            "execpolicy",
            "check",
            "--rules",
            str(path),
            "--",
            "git",
            "status",
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise PackError(f"{path}: codex execpolicy check failed: {detail}")
    return None


def validate_pack(pack: Path, check_rules: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        manifest = load_manifest(pack)
    except PackError as exc:
        return [str(exc)], warnings

    files = list(iter_pack_files(pack))
    for path in files:
        if path.is_symlink():
            errors.append(f"{path}: symlinks are not allowed in packs")
            continue
        for label in scan_for_secrets(path):
            errors.append(f"{path}: possible {label} detected")
        content = try_read_text(path)
        if content is not None and "TODO" in content:
            errors.append(f"{path}: unresolved TODO marker")

    components = 0
    skills = pack / "skills"
    if skills.exists():
        components += 1
        skill_children = list(skills.iterdir())
        if not skill_children:
            errors.append(f"{skills}: directory contains no skills")
        for child in skill_children:
            skill_file = child / "SKILL.md"
            if not child.is_dir() or not skill_file.is_file():
                errors.append(f"{child}: expected a skill directory containing SKILL.md")
                continue
            try:
                metadata = parse_frontmatter(skill_file)
                if metadata["name"] != child.name:
                    errors.append(
                        f"{skill_file}: skill name must match directory {child.name}"
                    )
            except PackError as exc:
                errors.append(str(exc))

    agents = pack / "agents"
    if agents.exists():
        components += 1
        agent_files = list(agents.glob("*.toml"))
        if not agent_files:
            errors.append(f"{agents}: directory contains no agent TOML files")
        for path in agent_files:
            try:
                value = load_toml(path)
                for field in ("name", "description", "developer_instructions"):
                    if not isinstance(value.get(field), str) or not value[field].strip():
                        errors.append(f"{path}: missing required string {field}")
                if isinstance(value.get("name"), str) and value["name"] != path.stem:
                    warnings.append(f"{path}: filename differs from agent name")
            except PackError as exc:
                errors.append(str(exc))

    rules = pack / "rules"
    if rules.exists():
        components += 1
        rule_files = list(rules.glob("*.rules"))
        if not rule_files:
            errors.append(f"{rules}: directory contains no .rules files")
        for path in rule_files:
            if check_rules:
                try:
                    warning = check_rule_file(path)
                    if warning:
                        warnings.append(f"{path}: {warning}")
                except (PackError, subprocess.TimeoutExpired) as exc:
                    errors.append(str(exc))

    agents_md = pack / "AGENTS.md"
    if agents_md.exists():
        components += 1
        if not read_text(agents_md).strip():
            errors.append(f"{agents_md}: file is empty")

    hooks = pack / "hooks" / "hooks.json"
    if (pack / "hooks").exists():
        components += 1
        if not hooks.is_file():
            errors.append(f"{hooks}: missing hooks.json")
        else:
            try:
                validate_hooks(hooks)
            except PackError as exc:
                errors.append(str(exc))

    for name in ("config.toml", "mcp.toml", "profile.toml"):
        path = pack / name
        if path.exists():
            components += 1
            try:
                value = load_toml(path)
                if name == "mcp.toml":
                    allowed = {
                        "mcp_servers",
                        "mcp_oauth_callback_port",
                        "mcp_oauth_callback_url",
                    }
                    unexpected = sorted(set(value) - allowed)
                    if unexpected:
                        errors.append(
                            f"{path}: unexpected non-MCP keys: {', '.join(unexpected)}"
                        )
                    if "mcp_servers" not in value:
                        errors.append(f"{path}: define at least one mcp_servers table")
            except PackError as exc:
                errors.append(str(exc))

    if components == 0:
        errors.append(f"{pack}: pack contains no components")
    if (pack / "profile.toml").exists():
        default_scope = manifest.get("install", {}).get("default_scope", "project")
        if default_scope == "project":
            warnings.append("profile.toml is global-only but default_scope is project")
    return errors, warnings


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    raise PackError("Could not infer a project root; pass --project-root")


def destination_context(
    manifest: dict[str, Any],
    scope: str,
    project_root: str | None,
    codex_home: str | None,
    user_home: str | None,
    profile: str | None,
) -> DestinationContext:
    home = Path(user_home).expanduser().resolve() if user_home else Path.home().resolve()
    resolved_codex_home = (
        Path(codex_home).expanduser().resolve()
        if codex_home
        else Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser().resolve()
    )
    resolved_project: Path | None = None
    if scope == "project":
        resolved_project = (
            Path(project_root).expanduser().resolve()
            if project_root
            else find_project_root(Path.cwd())
        )
        layer = resolved_project / ".codex"
        if (Path(manifest["_pack"]) / "profile.toml").exists():
            raise PackError("profile.toml cannot be installed at project scope")
    else:
        layer = resolved_codex_home
    selected_profile = profile or manifest.get("install", {}).get("profile") or None
    if selected_profile and not PROFILE_RE.fullmatch(selected_profile):
        raise PackError("Profile names may contain letters, digits, hyphens, underscores")
    return DestinationContext(
        scope=scope,
        project_root=resolved_project,
        codex_home=resolved_codex_home,
        user_home=home,
        config_layer=layer,
        profile=selected_profile,
    )


def destination_for_file(
    pack: Path, source: Path, context: DestinationContext
) -> tuple[Path, str] | None:
    relative = source.relative_to(pack)
    if relative == Path("pack.toml"):
        return None
    if relative.parts[0] == "skills":
        destination_root = (
            context.project_root / ".agents" / "skills"
            if context.scope == "project" and context.project_root
            else context.user_home / ".agents" / "skills"
        )
        return destination_root / Path(*relative.parts[1:]), "skill"
    if relative.parts[0] == "agents":
        return context.config_layer / "agents" / Path(*relative.parts[1:]), "agent"
    if relative.parts[0] == "rules":
        return context.config_layer / "rules" / Path(*relative.parts[1:]), "rule"
    if relative.parts[0] == "hooks" and relative.name != "hooks.json":
        return context.config_layer / "hooks" / Path(*relative.parts[1:]), "hook-support"
    return None


def file_action(source: Path, destination: Path) -> str:
    if not destination.exists():
        return "create"
    if destination.is_file() and sha256_file(source) == sha256_file(destination):
        return "unchanged"
    return "collision"


def collect_file_operations(
    pack: Path, context: DestinationContext
) -> list[FileOperation]:
    operations: list[FileOperation] = []
    for source in iter_pack_files(pack):
        mapped = destination_for_file(pack, source, context)
        if not mapped:
            continue
        destination, component = mapped
        operations.append(
            FileOperation(
                source=source,
                destination=destination,
                component=component,
                action=file_action(source, destination),
            )
        )
    return operations


def managed_agents_text(existing: str, addition: str, pack_name: str) -> tuple[str, str]:
    start = f"<!-- codex-profile-pack:{pack_name}:start -->"
    end = f"<!-- codex-profile-pack:{pack_name}:end -->"
    block = f"{start}\n{addition.strip()}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(existing):
        updated = pattern.sub(block, existing)
        action = "unchanged" if updated == existing else "update managed block"
        return updated, action
    separator = "\n\n" if existing.strip() else ""
    return existing.rstrip() + separator + block + "\n", "append managed block"


def explicit_tables(text: str) -> set[str]:
    tables: set[str] = set()
    for line in text.splitlines():
        match = TABLE_HEADER_RE.match(line)
        if match:
            tables.add(match.group(1).strip())
    return tables


def find_value_conflicts(
    existing: Any, incoming: Any, prefix: tuple[str, ...] = ()
) -> list[str]:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        conflicts: list[str] = []
        for key in sorted(set(existing) & set(incoming)):
            conflicts.extend(
                find_value_conflicts(existing[key], incoming[key], (*prefix, key))
            )
        return conflicts
    return [".".join(prefix)]


def contains_values(existing: Any, incoming: Any) -> bool:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        return all(
            key in existing and contains_values(existing[key], value)
            for key, value in incoming.items()
        )
    return existing == incoming


def split_root_and_tables(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if TABLE_HEADER_RE.match(line):
            return "".join(lines[:index]), "".join(lines[index:])
    return text, ""


def merge_toml_text(existing: str, incoming: str, label: str) -> tuple[str, str]:
    try:
        existing_value = tomllib.loads(existing) if existing.strip() else {}
        incoming_value = tomllib.loads(incoming) if incoming.strip() else {}
    except tomllib.TOMLDecodeError as exc:
        raise PackError(f"{label}: invalid TOML: {exc}") from exc
    if not incoming_value:
        return existing, "unchanged"
    if contains_values(existing_value, incoming_value):
        return existing, "unchanged"
    conflicts = find_value_conflicts(existing_value, incoming_value)
    repeated_tables = sorted(explicit_tables(existing) & explicit_tables(incoming))
    if conflicts or repeated_tables:
        details = sorted(set(conflicts + repeated_tables))
        raise PackError(f"{label}: conflicting TOML paths: {', '.join(details)}")
    incoming_root, incoming_tables = split_root_and_tables(incoming)
    existing_root, existing_tables = split_root_and_tables(existing)
    root_parts = [part.rstrip() for part in (existing_root, incoming_root) if part.strip()]
    table_parts = [
        part.strip() for part in (existing_tables, incoming_tables) if part.strip()
    ]
    merged = "\n\n".join(root_parts + table_parts).rstrip() + "\n"
    try:
        tomllib.loads(merged)
    except tomllib.TOMLDecodeError as exc:
        raise PackError(f"{label}: merged TOML would be invalid: {exc}") from exc
    return merged, "merge"


def merge_hooks(existing: dict[str, Any], incoming: dict[str, Any]) -> tuple[dict[str, Any], int]:
    result = json.loads(json.dumps(existing)) if existing else {"hooks": {}}
    result.setdefault("hooks", {})
    if not isinstance(result["hooks"], dict):
        raise PackError("Existing hooks.json does not contain a hooks object")
    added = 0
    for event, groups in incoming.get("hooks", {}).items():
        destination_groups = result["hooks"].setdefault(event, [])
        if not isinstance(destination_groups, list):
            raise PackError(f"Existing hook event {event} is not an array")
        for group in groups:
            if group not in destination_groups:
                destination_groups.append(group)
                added += 1
    if not result.get("description") and incoming.get("description"):
        result["description"] = incoming["description"]
    return result, added


def plan_install(
    pack: Path, context: DestinationContext
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    manifest = load_manifest(pack)
    pack_name = manifest["name"]
    plan: list[dict[str, Any]] = []
    rendered: dict[str, str] = {}

    for operation in collect_file_operations(pack, context):
        plan.append(
            {
                "component": operation.component,
                "source": str(operation.source),
                "destination": str(operation.destination),
                "action": operation.action,
            }
        )

    agents_source = pack / "AGENTS.md"
    if agents_source.exists():
        destination = (
            context.project_root / "AGENTS.md"
            if context.scope == "project" and context.project_root
            else context.codex_home / "AGENTS.md"
        )
        existing = read_text(destination) if destination.exists() else ""
        merged, action = managed_agents_text(
            existing, read_text(agents_source), pack_name
        )
        rendered[str(destination)] = merged
        plan.append(
            {
                "component": "AGENTS.md",
                "source": str(agents_source),
                "destination": str(destination),
                "action": action,
            }
        )

    hooks_source = pack / "hooks" / "hooks.json"
    if hooks_source.exists():
        destination = context.config_layer / "hooks.json"
        existing = json.loads(read_text(destination)) if destination.exists() else {}
        incoming = json.loads(read_text(hooks_source))
        merged_hooks, added = merge_hooks(existing, incoming)
        rendered[str(destination)] = json.dumps(merged_hooks, indent=2) + "\n"
        plan.append(
            {
                "component": "hooks",
                "source": str(hooks_source),
                "destination": str(destination),
                "action": f"merge {added} hook entries" if added else "unchanged",
            }
        )

    config_destination = context.config_layer / "config.toml"
    config_existing = read_text(config_destination) if config_destination.exists() else ""
    config_changed = False
    config_sources: list[str] = []
    for filename in ("config.toml", "mcp.toml"):
        source = pack / filename
        if source.exists():
            config_existing, action = merge_toml_text(
                config_existing, read_text(source), str(config_destination)
            )
            config_sources.append(str(source))
            config_changed = config_changed or action != "unchanged"
    if config_sources:
        rendered[str(config_destination)] = config_existing
        plan.append(
            {
                "component": "config",
                "source": ", ".join(config_sources),
                "destination": str(config_destination),
                "action": "merge" if config_changed else "unchanged",
            }
        )

    profile_source = pack / "profile.toml"
    if profile_source.exists():
        if context.scope != "global":
            raise PackError("profile.toml cannot be installed at project scope")
        if not context.profile:
            raise PackError("profile.toml requires --profile or install.profile")
        destination = context.codex_home / f"{context.profile}.config.toml"
        existing = read_text(destination) if destination.exists() else ""
        merged, action = merge_toml_text(
            existing, read_text(profile_source), str(destination)
        )
        rendered[str(destination)] = merged
        plan.append(
            {
                "component": "profile",
                "source": str(profile_source),
                "destination": str(destination),
                "action": action,
            }
        )
    return plan, rendered


def backup_path(
    destination: Path, context: DestinationContext, backup_root: Path
) -> Path:
    for label, base in (
        ("codex-home", context.codex_home),
        ("user-home", context.user_home),
        ("project", context.project_root),
    ):
        if base:
            try:
                return backup_root / label / destination.relative_to(base)
            except ValueError:
                pass
    safe_name = hashlib.sha256(str(destination).encode()).hexdigest()[:12]
    return backup_root / "external" / safe_name / destination.name


def install_pack(
    pack: Path,
    context: DestinationContext,
    apply: bool,
    replace: bool,
) -> tuple[list[dict[str, Any]], Path | None, Path]:
    errors, warnings = validate_pack(pack, check_rules=False)
    if errors:
        raise PackError("Pack validation failed:\n- " + "\n- ".join(errors))
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    plan, rendered = plan_install(pack, context)
    collisions = [item for item in plan if item["action"] == "collision"]
    if collisions and not replace:
        destinations = ", ".join(item["destination"] for item in collisions)
        raise PackError(
            f"Different destination files already exist: {destinations}. "
            "Review them, then use --replace if replacement is intended."
        )
    if not apply:
        raise PackError("Refusing to install without --apply; run plan first")

    manifest = load_manifest(pack)
    pack_name = manifest["name"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    state_root = context.config_layer / "profile-packs"
    backup_root = state_root / "backups" / f"{pack_name}-{timestamp}"
    backed_up = False
    installed_files: list[dict[str, str]] = []

    file_operations = collect_file_operations(pack, context)
    for operation in file_operations:
        if operation.action == "unchanged":
            installed_files.append(
                {
                    "component": operation.component,
                    "destination": str(operation.destination),
                    "sha256": sha256_file(operation.destination),
                }
            )
            continue
        if operation.destination.exists():
            backup = backup_path(operation.destination, context, backup_root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(operation.destination, backup)
            backed_up = True
        operation.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(operation.source, operation.destination)
        installed_files.append(
            {
                "component": operation.component,
                "destination": str(operation.destination),
                "sha256": sha256_file(operation.destination),
            }
        )

    for destination_string, content in rendered.items():
        destination = Path(destination_string)
        current = read_text(destination) if destination.exists() else None
        if current == content:
            installed_files.append(
                {
                    "component": "merged",
                    "destination": str(destination),
                    "sha256": sha256_file(destination),
                }
            )
            continue
        if destination.exists():
            backup = backup_path(destination, context, backup_root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
            backed_up = True
        write_text_atomic(destination, content)
        installed_files.append(
            {
                "component": "merged",
                "destination": str(destination),
                "sha256": sha256_file(destination),
            }
        )

    state_root.mkdir(parents=True, exist_ok=True)
    record_path = state_root / f"{pack_name}.json"
    record = {
        "schema_version": SCHEMA_VERSION,
        "pack": pack_name,
        "source": str(pack),
        "scope": context.scope,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "profile": context.profile,
        "files": installed_files,
        "backup": str(backup_root) if backed_up else None,
    }
    write_text_atomic(record_path, json.dumps(record, indent=2) + "\n")
    return plan, backup_root if backed_up else None, record_path


def print_validation(errors: list[str], warnings: list[str]) -> None:
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("Pack is valid.")


def print_plan(plan: list[dict[str, Any]], context: DestinationContext) -> None:
    print(f"Scope: {context.scope}")
    print(f"Config layer: {context.config_layer}")
    if any(item["component"] == "skill" for item in plan):
        skills_root = (
            context.project_root / ".agents" / "skills"
            if context.scope == "project" and context.project_root
            else context.user_home / ".agents" / "skills"
        )
        print(f"Skills root: {skills_root}")
    if context.profile:
        print(f"Profile: {context.profile}")
    for item in plan:
        print(
            f"[{item['action']}] {item['component']}: "
            f"{item['source']} -> {item['destination']}"
        )


def add_destination_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--pack", required=True)
    parser.add_argument("--scope", choices=("project", "global"), required=True)
    parser.add_argument("--project-root")
    parser.add_argument("--codex-home")
    parser.add_argument("--user-home")
    parser.add_argument("--profile")
    parser.add_argument("--json", action="store_true", dest="as_json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a source pack skeleton")
    init_parser.add_argument("--path", required=True)
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument(
        "--components",
        default="skill,agent,rule,agents-md,hook,mcp,config",
        help="Comma-separated component names",
    )
    init_parser.add_argument(
        "--default-scope", choices=("project", "global"), default="project"
    )

    validate_parser = subparsers.add_parser("validate", help="Validate a source pack")
    validate_parser.add_argument("--pack", required=True)
    validate_parser.add_argument("--check-rules", action="store_true")

    plan_parser = subparsers.add_parser("plan", help="Preview destination changes")
    add_destination_arguments(plan_parser)

    install_parser = subparsers.add_parser("install", help="Install a validated pack")
    add_destination_arguments(install_parser)
    install_parser.add_argument("--apply", action="store_true")
    install_parser.add_argument("--replace", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            components = parse_components(args.components)
            init_pack(
                Path(args.path).expanduser().resolve(),
                args.name,
                components,
                args.default_scope,
            )
            print(f"Created pack skeleton: {Path(args.path).resolve()}")
            return 0

        pack = Path(args.pack).expanduser().resolve()
        if args.command == "validate":
            errors, warnings = validate_pack(pack, check_rules=args.check_rules)
            print_validation(errors, warnings)
            return 1 if errors else 0

        manifest = load_manifest(pack)
        manifest["_pack"] = str(pack)
        context = destination_context(
            manifest,
            args.scope,
            args.project_root,
            args.codex_home,
            args.user_home,
            args.profile,
        )
        if args.command == "plan":
            errors, warnings = validate_pack(pack, check_rules=False)
            if errors:
                raise PackError("Pack validation failed:\n- " + "\n- ".join(errors))
            for warning in warnings:
                print(f"WARNING: {warning}", file=sys.stderr)
            plan, _ = plan_install(pack, context)
            if args.as_json:
                print(
                    json.dumps(
                        {
                            "scope": context.scope,
                            "config_layer": str(context.config_layer),
                            "profile": context.profile,
                            "operations": plan,
                        },
                        indent=2,
                    )
                )
            else:
                print_plan(plan, context)
            return 0

        plan, backup, record = install_pack(
            pack, context, apply=args.apply, replace=args.replace
        )
        if args.as_json:
            print(
                json.dumps(
                    {
                        "operations": plan,
                        "backup": str(backup) if backup else None,
                        "record": str(record),
                    },
                    indent=2,
                )
            )
        else:
            print_plan(plan, context)
            print(f"Installation record: {record}")
            print(f"Backup: {backup if backup else 'not required'}")
        return 0
    except (PackError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
