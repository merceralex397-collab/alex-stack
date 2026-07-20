from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest


SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "validate-agents.py"
)
SPEC = importlib.util.spec_from_file_location("validate_agents", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator from {SCRIPT_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


READ_ONLY_PROMPT = """You are a general test role.

Mission:
Return a bounded result.

Use when:
- The fixture needs a valid general agent.

Boundaries:
- This role is read-only. Inspect and report; do not modify workspace files.
- Do not spawn or delegate to other agents.

Working method:
1. Inspect evidence.

Return contract:
- Return evidence.

Completion criteria:
- The task is answered.
"""

WRITABLE_SPECIFIC_PROMPT = """You are a specific test role.

Mission:
Return a bounded specialist result.

Use when:
- The fixture needs a valid specialist.

Specialist checks:
- Apply a distinctive check.

Boundaries:
- Edits are permitted only when the delegated task explicitly authorises them and gives you non-overlapping file ownership. Otherwise remain read-only.
- Do not spawn or delegate to other agents.

Working method:
1. Inspect evidence.

Return contract:
- Return evidence.

Completion criteria:
- The task is answered.
"""


def agent_toml(
    name: str,
    prompt: str,
    *,
    read_only: bool,
) -> str:
    lines = [
        f'name = "{name}"',
        (
            'description = "Use when a validator fixture needs this role. '
            'Do not use for another fixture role."'
        ),
        "",
        'developer_instructions = """',
        prompt.rstrip(),
        '"""',
    ]
    if read_only:
        lines.extend(["", 'sandbox_mode = "read-only"'])
    lines.append("")
    return "\n".join(lines)


class CatalogueFixture:
    def __init__(self, root: pathlib.Path) -> None:
        self.root = root
        self.general = root / "general-agents" / "general-test-agent.toml"
        self.specific = root / "specific-agents" / "specific-test-agent.toml"
        self.selection = root / "evals" / "selection-cases.json"

    def create(self) -> None:
        for directory in (
            self.root / "general-agents",
            self.root / "specific-agents",
            self.root / "evals",
        ):
            directory.mkdir(parents=True, exist_ok=True)

        self.general.write_text(
            agent_toml(
                "general-test-agent",
                READ_ONLY_PROMPT,
                read_only=True,
            ),
            encoding="utf-8",
        )
        self.specific.write_text(
            agent_toml(
                "specific-test-agent",
                WRITABLE_SPECIFIC_PROMPT,
                read_only=False,
            ),
            encoding="utf-8",
        )
        (self.root / "general-agents" / "README.md").write_text(
            "# General\n\n[General](general-test-agent.toml)\n",
            encoding="utf-8",
        )
        (self.root / "specific-agents" / "README.md").write_text(
            "# Specific\n\n[Specific](specific-test-agent.toml)\n",
            encoding="utf-8",
        )
        (self.root / "README.md").write_text(
            "# Catalogue\n\n"
            "[General](general-agents/README.md)\n\n"
            "[Specific](specific-agents/README.md)\n\n"
            "[Cases](evals/selection-cases.json)\n",
            encoding="utf-8",
        )
        self.selection.write_text(
            json.dumps(
                {
                    "version": 1,
                    "cases": [
                        {
                            "id": "general-case",
                            "prompt": "Use the general role.",
                            "expected_agent": "general-test-agent",
                            "should_not_select": ["specific-test-agent"],
                            "reason": "General fixture coverage.",
                        },
                        {
                            "id": "specific-case",
                            "prompt": "Use the specific role.",
                            "expected_agent": "specific-test-agent",
                            "should_not_select": ["general-test-agent"],
                            "reason": "Specific fixture coverage.",
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


class ValidateAgentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp_dir.name)
        self.fixture = CatalogueFixture(self.root)
        self.fixture.create()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self) -> dict[str, object]:
        return VALIDATOR.validate(self.root)

    def assert_error_contains(self, result: dict[str, object], text: str) -> None:
        errors = result["errors"]
        self.assertIsInstance(errors, list)
        self.assertTrue(
            any(text in error for error in errors),
            f"Expected an error containing {text!r}; got {errors!r}",
        )

    def test_valid_catalogue_passes(self) -> None:
        result = self.validate()
        self.assertEqual(result["error_count"], 0, result["errors"])

    def test_repository_catalogue_passes(self) -> None:
        repository_root = pathlib.Path(__file__).resolve().parents[1]
        result = VALIDATOR.validate(repository_root)
        self.assertEqual(result["error_count"], 0, result["errors"])
        self.assertEqual(
            result["categories"],
            {"general-agents": 9, "specific-agents": 6},
        )

    def test_duplicate_name_is_rejected(self) -> None:
        duplicate = self.root / "specific-agents" / "duplicate-agent.toml"
        duplicate.write_text(
            agent_toml(
                "general-test-agent",
                WRITABLE_SPECIFIC_PROMPT,
                read_only=False,
            ),
            encoding="utf-8",
        )
        with (self.root / "specific-agents" / "README.md").open(
            "a", encoding="utf-8"
        ) as stream:
            stream.write("[Duplicate](duplicate-agent.toml)\n")

        result = self.validate()
        self.assert_error_contains(result, "duplicate name")

    def test_name_filename_mismatch_is_rejected(self) -> None:
        raw = self.fixture.general.read_text(encoding="utf-8")
        self.fixture.general.write_text(
            raw.replace(
                'name = "general-test-agent"',
                'name = "different-agent"',
            ),
            encoding="utf-8",
        )

        result = self.validate()
        self.assert_error_contains(result, "does not match filename")

    def test_missing_prompt_section_is_rejected(self) -> None:
        raw = self.fixture.general.read_text(encoding="utf-8")
        self.fixture.general.write_text(
            raw.replace("Completion criteria:", "Finished when:"),
            encoding="utf-8",
        )

        result = self.validate()
        self.assert_error_contains(result, "missing prompt section")

    def test_permission_mismatch_is_rejected(self) -> None:
        raw = self.fixture.general.read_text(encoding="utf-8")
        self.fixture.general.write_text(
            raw.replace('\n\nsandbox_mode = "read-only"\n', "\n"),
            encoding="utf-8",
        )

        result = self.validate()
        self.assert_error_contains(
            result,
            "inheriting agent lacks explicit edit-authority boundary",
        )

    def test_unlisted_agent_is_rejected(self) -> None:
        (self.root / "general-agents" / "README.md").write_text(
            "# General\n",
            encoding="utf-8",
        )

        result = self.validate()
        self.assert_error_contains(result, "agent not indexed")

    def test_broken_link_is_rejected(self) -> None:
        with (self.root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n[Missing](missing.md)\n")

        result = self.validate()
        self.assert_error_contains(result, "broken local link")

    def test_missing_selection_coverage_is_rejected(self) -> None:
        document = json.loads(self.fixture.selection.read_text(encoding="utf-8"))
        document["cases"] = document["cases"][:1]
        self.fixture.selection.write_text(
            json.dumps(document, indent=2) + "\n",
            encoding="utf-8",
        )

        result = self.validate()
        self.assert_error_contains(result, "no positive selection case")

    def test_legacy_hierarchy_marker_is_rejected(self) -> None:
        marker = "A" + "-level"
        raw = self.fixture.general.read_text(encoding="utf-8")
        self.fixture.general.write_text(
            raw.replace("Mission:", f"{marker}\n\nMission:"),
            encoding="utf-8",
        )

        result = self.validate()
        self.assert_error_contains(result, "legacy hierarchy marker")


if __name__ == "__main__":
    unittest.main()
