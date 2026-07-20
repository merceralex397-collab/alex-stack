#!/usr/bin/env python3
"""Validate the hand-authored Codex subagent catalogue."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import tomllib
from typing import Any


CATEGORIES = ("general-agents", "specific-agents")
REQUIRED_FIELDS = ("name", "description", "developer_instructions")
ALLOWED_FIELDS = {
    "name",
    "description",
    "developer_instructions",
    "sandbox_mode",
}
REQUIRED_PROMPT_SECTIONS = (
    "Mission:",
    "Use when:",
    "Boundaries:",
    "Working method:",
    "Return contract:",
    "Completion criteria:",
)
SPECIFIC_PROMPT_SECTIONS = ("Specialist checks:",)
PLACEHOLDERS = (
    "replace-me",
    "[general outcome",
    "[narrow specialist",
    "[Positive trigger",
    "[State one",
    "TODO",
    "TBD",
)
LEGACY_MARKERS = (
    "a-level",
    "b-level",
    "c-level",
    "development-workflow-orchestrator",
    "parent workstream:",
    "direct reports:",
    "direct b-level",
    "direct c-level",
)
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
READ_ONLY_SENTENCE = (
    "This role is read-only. Inspect and report; do not modify workspace files."
)
EDIT_AUTHORITY_SENTENCE = (
    "Edits are permitted only when the delegated task explicitly authorises "
    "them and gives you non-overlapping file ownership. Otherwise remain read-only."
)
NO_DELEGATION_SENTENCE = "Do not spawn or delegate to other agents."


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _catalogue_files(root: pathlib.Path) -> dict[str, list[pathlib.Path]]:
    return {
        category: sorted((root / category).glob("*.toml"))
        if (root / category).is_dir()
        else []
        for category in CATEGORIES
    }


def _local_link_targets(markdown: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    raw = markdown.read_text(encoding="utf-8")
    targets: list[tuple[str, pathlib.Path]] = []
    for match in LOCAL_LINK.finditer(raw):
        target_text = match.group(1).split("#", 1)[0].strip()
        if not target_text:
            continue
        targets.append((target_text, (markdown.parent / target_text).resolve()))
    return targets


def _validate_markdown_links(
    root: pathlib.Path, errors: list[str]
) -> tuple[int, dict[str, set[str]]]:
    markdown_files = sorted(root.rglob("*.md"))
    indexed_agents = {category: set() for category in CATEGORIES}

    for markdown in markdown_files:
        for target_text, target in _local_link_targets(markdown):
            if not target.exists():
                errors.append(f"{markdown}: broken local link {target_text}")

    for category in CATEGORIES:
        category_dir = root / category
        readme = category_dir / "README.md"
        if not readme.is_file():
            errors.append(f"Missing category index: {readme}")
            continue

        seen_targets: set[pathlib.Path] = set()
        for target_text, target in _local_link_targets(readme):
            if target.suffix.lower() != ".toml":
                continue
            if target.parent != category_dir.resolve():
                errors.append(
                    f"{readme}: agent link leaves its category: {target_text}"
                )
                continue
            if target in seen_targets:
                errors.append(f"{readme}: duplicate agent link {target_text}")
                continue
            seen_targets.add(target)
            indexed_agents[category].add(target.stem)

    return len(markdown_files), indexed_agents


def _validate_selection_cases(
    root: pathlib.Path, known_names: set[str], errors: list[str]
) -> tuple[int, set[str]]:
    fixture_path = root / "evals" / "selection-cases.json"
    if not fixture_path.is_file():
        errors.append(f"Missing selection fixture: {fixture_path}")
        return 0, set()

    try:
        document = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{fixture_path}: JSON parse failed: {exc}")
        return 0, set()

    if not isinstance(document, dict):
        errors.append(f"{fixture_path}: top level must be an object")
        return 0, set()
    if document.get("version") != 1:
        errors.append(f"{fixture_path}: version must be 1")

    cases = document.get("cases")
    if not isinstance(cases, list):
        errors.append(f"{fixture_path}: cases must be a list")
        return 0, set()

    seen_ids: set[str] = set()
    covered_agents: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"{fixture_path}: case {index}"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue

        case_id = case.get("id")
        if not _non_empty_string(case_id):
            errors.append(f"{prefix}: missing non-empty id")
        elif case_id in seen_ids:
            errors.append(f"{prefix}: duplicate id {case_id!r}")
        else:
            seen_ids.add(case_id)

        for field in ("prompt", "reason"):
            if not _non_empty_string(case.get(field)):
                errors.append(f"{prefix}: missing non-empty {field}")

        expected = case.get("expected_agent")
        if not _non_empty_string(expected):
            errors.append(f"{prefix}: missing non-empty expected_agent")
        elif expected not in known_names:
            errors.append(f"{prefix}: unknown expected_agent {expected!r}")
        else:
            covered_agents.add(expected)

        rejected = case.get("should_not_select")
        if not isinstance(rejected, list) or not rejected:
            errors.append(f"{prefix}: should_not_select must be a non-empty list")
            continue
        if len(rejected) != len(set(rejected)):
            errors.append(f"{prefix}: should_not_select contains duplicates")
        for name in rejected:
            if not _non_empty_string(name):
                errors.append(
                    f"{prefix}: should_not_select entries must be non-empty strings"
                )
            elif name not in known_names:
                errors.append(f"{prefix}: unknown should_not_select agent {name!r}")
            elif name == expected:
                errors.append(
                    f"{prefix}: expected_agent also appears in should_not_select"
                )

    missing_coverage = sorted(known_names - covered_agents)
    for name in missing_coverage:
        errors.append(f"{fixture_path}: no positive selection case for {name}")

    return len(cases), covered_agents


def validate(root: pathlib.Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []

    if not root.is_dir():
        return {
            "root": str(root),
            "errors": [f"Catalogue root does not exist: {root}"],
            "error_count": 1,
        }

    root_readme = root / "README.md"
    if not root_readme.is_file():
        errors.append(f"Missing root README: {root_readme}")

    category_like_dirs = {
        entry.name
        for entry in root.iterdir()
        if entry.is_dir() and entry.name.endswith("-agents")
    }
    expected_categories = set(CATEGORIES)
    if category_like_dirs != expected_categories:
        missing = sorted(expected_categories - category_like_dirs)
        extra = sorted(category_like_dirs - expected_categories)
        if missing:
            errors.append(f"Missing catalogue categories: {', '.join(missing)}")
        if extra:
            errors.append(f"Unexpected catalogue categories: {', '.join(extra)}")

    files_by_category = _catalogue_files(root)
    seen_names: dict[str, pathlib.Path] = {}
    parsed_agents: dict[str, dict[str, Any]] = {}
    read_only_agents = 0
    inheriting_agents = 0

    for category, files in files_by_category.items():
        category_dir = root / category
        if category_dir.is_dir():
            nested = [
                file
                for file in category_dir.rglob("*.toml")
                if file.parent != category_dir
            ]
            for file in nested:
                errors.append(f"{file}: catalogue agents must not be nested")

        for file in files:
            raw = file.read_text(encoding="utf-8")
            try:
                data = tomllib.loads(raw)
            except Exception as exc:  # noqa: BLE001 - report every parse failure.
                errors.append(f"{file}: TOML parse failed: {exc}")
                continue

            unknown_fields = sorted(set(data) - ALLOWED_FIELDS)
            if unknown_fields:
                errors.append(
                    f"{file}: unsupported top-level fields: "
                    f"{', '.join(unknown_fields)}"
                )

            for field in REQUIRED_FIELDS:
                if not _non_empty_string(data.get(field)):
                    errors.append(f"{file}: missing non-empty {field}")

            name = data.get("name")
            if isinstance(name, str):
                if name != file.stem:
                    errors.append(
                        f"{file}: name {name!r} does not match filename"
                    )
                if not NAME_PATTERN.fullmatch(name):
                    errors.append(f"{file}: invalid agent name {name!r}")
                if name in seen_names:
                    errors.append(
                        f"{file}: duplicate name also used by {seen_names[name]}"
                    )
                else:
                    seen_names[name] = file
                    parsed_agents[name] = {
                        "category": category,
                        "file": file,
                        "data": data,
                    }

            description = data.get("description", "")
            if isinstance(description, str):
                if not description.startswith("Use when "):
                    errors.append(
                        f"{file}: description must begin with positive 'Use when' guidance"
                    )
                if " Do not use " not in description:
                    errors.append(
                        f"{file}: description must include negative 'Do not use' guidance"
                    )

            prompt = data.get("developer_instructions", "")
            if isinstance(prompt, str):
                for section in REQUIRED_PROMPT_SECTIONS:
                    if section not in prompt:
                        errors.append(f"{file}: missing prompt section {section}")
                if category == "specific-agents":
                    for section in SPECIFIC_PROMPT_SECTIONS:
                        if section not in prompt:
                            errors.append(
                                f"{file}: missing specialist prompt section {section}"
                            )
                if NO_DELEGATION_SENTENCE not in prompt:
                    errors.append(
                        f"{file}: missing flat-catalogue no-delegation boundary"
                    )

                prompt_lower = prompt.lower()
                for marker in LEGACY_MARKERS:
                    if marker in prompt_lower:
                        errors.append(
                            f"{file}: legacy hierarchy marker {marker!r}"
                        )

            for placeholder in PLACEHOLDERS:
                if placeholder in raw:
                    errors.append(
                        f"{file}: unresolved placeholder {placeholder!r}"
                    )

            sandbox = data.get("sandbox_mode")
            if sandbox is not None:
                if sandbox != "read-only":
                    errors.append(
                        f"{file}: sandbox_mode may only be 'read-only'"
                    )
                read_only_agents += 1
                if READ_ONLY_SENTENCE not in prompt:
                    errors.append(
                        f"{file}: read-only sandbox lacks matching prompt boundary"
                    )
                if EDIT_AUTHORITY_SENTENCE in prompt:
                    errors.append(
                        f"{file}: read-only agent contains edit-authority language"
                    )
            else:
                inheriting_agents += 1
                if EDIT_AUTHORITY_SENTENCE not in prompt:
                    errors.append(
                        f"{file}: inheriting agent lacks explicit edit-authority boundary"
                    )
                if READ_ONLY_SENTENCE in prompt:
                    errors.append(
                        f"{file}: inheriting agent contains the read-only role boundary"
                    )

    markdown_count, indexed_agents = _validate_markdown_links(root, errors)
    for category, files in files_by_category.items():
        file_names = {file.stem for file in files}
        missing_from_index = sorted(file_names - indexed_agents[category])
        extra_in_index = sorted(indexed_agents[category] - file_names)
        for name in missing_from_index:
            errors.append(
                f"{root / category / 'README.md'}: agent not indexed: {name}"
            )
        for name in extra_in_index:
            errors.append(
                f"{root / category / 'README.md'}: indexed agent missing: {name}"
            )

    known_names = set(seen_names)
    selection_case_count, covered_agents = _validate_selection_cases(
        root, known_names, errors
    )

    category_counts = {
        category: len(files) for category, files in files_by_category.items()
    }
    total_agents = sum(category_counts.values())
    return {
        "root": str(root),
        "categories": category_counts,
        "toml_files": total_agents,
        "unique_names": len(seen_names),
        "read_only_agents": read_only_agents,
        "inheriting_agents": inheriting_agents,
        "markdown_files": markdown_count,
        "selection_cases": selection_case_count,
        "selection_coverage": len(covered_agents),
        "errors": errors,
        "error_count": len(errors),
    }


def main() -> int:
    default_root = pathlib.Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=pathlib.Path,
        default=default_root,
        help="Catalogue root (defaults to the parent of this script directory)",
    )
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, indent=2))
    return 1 if result["error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
