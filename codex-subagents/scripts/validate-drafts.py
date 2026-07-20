#!/usr/bin/env python3
"""Validate the generated Codex custom-agent draft library."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import tomllib
from typing import Any


REQUIRED_FIELDS = ("name", "description", "developer_instructions")
REQUIRED_PROMPT_SECTIONS = (
    "Mission:",
    "Authority and boundaries:",
    "Working method:",
    "Return contract:",
    "Completion criteria:",
)
PLACEHOLDERS = (
    "replace-me",
    "[specific specialty",
    "[Primary responsibility]",
    "TODO",
    "TBD",
)
LOCAL_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")


def flatten_roles(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    roles = [manifest["root"]]
    for team in manifest["teams"]:
        roles.append(team["manager"])
        for lead in team["leads"]:
            roles.append(lead)
            roles.extend(lead["specialists"])
    return roles


def validate(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return {"errors": [f"Missing manifest: {manifest_path}"], "error_count": 1}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    toml_files = sorted(root.glob("*/*.toml"))
    seen_names: dict[str, pathlib.Path] = {}

    for file in toml_files:
        raw = file.read_text(encoding="utf-8")
        try:
            data = tomllib.loads(raw)
        except Exception as exc:  # noqa: BLE001 - report all TOML parser errors.
            errors.append(f"{file}: TOML parse failed: {exc}")
            continue

        for field in REQUIRED_FIELDS:
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append(f"{file}: missing non-empty {field}")

        name = data.get("name")
        if name != file.stem:
            errors.append(f"{file}: name {name!r} does not match filename")
        if name in seen_names:
            errors.append(f"{file}: duplicate name also used by {seen_names[name]}")
        elif isinstance(name, str):
            seen_names[name] = file

        prompt = data.get("developer_instructions", "")
        for section in REQUIRED_PROMPT_SECTIONS:
            if section not in prompt:
                errors.append(f"{file}: missing prompt section {section}")
        for placeholder in PLACEHOLDERS:
            if placeholder in raw:
                errors.append(f"{file}: unresolved placeholder {placeholder!r}")

    roles = flatten_roles(manifest)
    known_ids = {role["id"] for role in roles}
    expected_count = manifest["counts"]["total_agents"]
    if len(toml_files) != expected_count:
        errors.append(
            f"TOML count {len(toml_files)} does not match manifest {expected_count}"
        )
    if len(roles) != expected_count:
        errors.append(
            f"Manifest role count {len(roles)} does not match declared {expected_count}"
        )
    if len(known_ids) != len(roles):
        errors.append("Manifest contains duplicate role IDs")

    for role in roles:
        matches = list(root.glob(f"*/{role['id']}.toml"))
        if len(matches) != 1:
            errors.append(
                f"Role {role['id']}: expected one TOML file, found {len(matches)}"
            )
            continue
        data = tomllib.loads(matches[0].read_text(encoding="utf-8"))
        if role["read_only"] and data.get("sandbox_mode") != "read-only":
            errors.append(f"{matches[0]}: read-only role does not pin read-only sandbox")
        if not role["read_only"] and "sandbox_mode" in data:
            errors.append(
                f"{matches[0]}: implementation-capable role unexpectedly pins sandbox"
            )
        parent = role.get("parent")
        if (
            parent
            and parent not in known_ids
            and parent != "development-workflow-orchestrator"
        ):
            errors.append(f"Role {role['id']}: unknown parent {parent}")

    expected_folders = manifest["counts"]["team_folders"] + 1
    actual_folders = len([entry for entry in root.iterdir() if entry.is_dir()])
    if actual_folders != expected_folders:
        errors.append(
            f"Team-folder count {actual_folders} does not match {expected_folders}"
        )

    markdown_files = sorted(root.rglob("*.md"))
    for file in markdown_files:
        raw = file.read_text(encoding="utf-8")
        for match in LOCAL_LINK.finditer(raw):
            target_text = match.group(1).split("#", 1)[0]
            if not target_text:
                continue
            target = (file.parent / target_text).resolve()
            if not target.exists():
                errors.append(f"{file}: broken local link {target_text}")

    return {
        "root": str(root),
        "team_folders_including_root": actual_folders,
        "toml_files": len(toml_files),
        "unique_names": len(seen_names),
        "manifest_roles": len(roles),
        "markdown_files": len(markdown_files),
        "read_only_agents": sum(1 for role in roles if role["read_only"]),
        "inheriting_sandbox_agents": sum(
            1 for role in roles if not role["read_only"]
        ),
        "errors": errors,
        "error_count": len(errors),
    }


def main() -> int:
    default_root = pathlib.Path(__file__).resolve().parent.parent / "drafts"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=pathlib.Path,
        default=default_root,
        help="Drafts directory (defaults to ../drafts relative to this script)",
    )
    args = parser.parse_args()
    result = validate(args.root.resolve())
    print(json.dumps(result, indent=2))
    return 1 if result["error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
