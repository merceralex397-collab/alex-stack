#!/usr/bin/env python3

import importlib.util
import io
import json
import shutil
import sys
import tempfile
import tomllib
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("codex_profile_pack.py")
SPEC = importlib.util.spec_from_file_location("codex_profile_pack", MODULE_PATH)
assert SPEC and SPEC.loader
profile_pack = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = profile_pack
SPEC.loader.exec_module(profile_pack)


class CodexProfilePackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pack = self.root / "pack"
        profile_pack.init_pack(
            self.pack,
            "review-pack",
            ["skill", "agent", "rule", "agents-md", "hook", "mcp", "config"],
            "project",
        )
        self._resolve_todos()

    def tearDown(self):
        self.temp.cleanup()

    def _resolve_todos(self):
        replacements = {
            self.pack / "pack.toml": (
                'description = "TODO: describe the review-pack Codex pack."',
                'description = "Review workflow pack."',
            ),
            self.pack / "skills" / "review-pack" / "SKILL.md": (
                (
                    "TODO: explain what this skill does and when to use it.\n"
                    "---\n\n"
                    "# Review Pack\n\n"
                    "TODO: write imperative workflow instructions."
                ),
                (
                    "Review changes. Use when a user asks for a focused review.\n"
                    "---\n\n"
                    "# Review Pack\n\n"
                    "Inspect the requested change and return evidence."
                ),
            ),
            self.pack / "agents" / "review-pack.toml": (
                "TODO: explain when to delegate to this agent.",
                "Delegate focused review work.",
            ),
            self.pack / "rules" / "review-pack.rules": (
                "# TODO: replace this safe example with an intentional command policy.\n",
                "",
            ),
            self.pack / "AGENTS.md": (
                "TODO: add concise durable guidance for the selected scope.",
                "Run focused tests after changes.",
            ),
            self.pack / "mcp.toml": (
                "# TODO: define [mcp_servers.<name>] using environment references for credentials.\n",
                '[mcp_servers.docs]\nurl = "https://example.test/mcp"\n',
            ),
            self.pack / "config.toml": (
                "# TODO: add only the base Codex settings this pack requires.\n",
                'personality = "pragmatic"\n',
            ),
        }
        for path, (old, new) in replacements.items():
            content = path.read_text(encoding="utf-8").replace(old, new)
            path.write_text(content, encoding="utf-8")
        agent_path = self.pack / "agents" / "review-pack.toml"
        agent_path.write_text(
            agent_path.read_text(encoding="utf-8").replace(
                "TODO: define one narrow delegated role.",
                "Review evidence and return concise findings.",
            ),
            encoding="utf-8",
        )

    def _context(self, scope="project", profile=None):
        manifest = profile_pack.load_manifest(self.pack)
        manifest["_pack"] = str(self.pack)
        project = self.root / "repo"
        project.mkdir(exist_ok=True)
        (project / ".git").mkdir(exist_ok=True)
        return profile_pack.destination_context(
            manifest,
            scope,
            str(project),
            str(self.root / "codex-home"),
            str(self.root / "home"),
            profile,
        )

    def test_validate_and_project_install_are_idempotent(self):
        errors, warnings = profile_pack.validate_pack(self.pack)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

        context = self._context()
        plan, backup, record = profile_pack.install_pack(
            self.pack, context, apply=True, replace=False
        )
        self.assertTrue(record.is_file())
        self.assertIsNone(backup)
        self.assertTrue(
            (context.project_root / ".agents" / "skills" / "review-pack" / "SKILL.md").is_file()
        )
        config = tomllib.loads(
            (context.project_root / ".codex" / "config.toml").read_text(encoding="utf-8")
        )
        self.assertEqual("pragmatic", config["personality"])
        self.assertEqual(
            "https://example.test/mcp", config["mcp_servers"]["docs"]["url"]
        )
        self.assertIn("create", {item["action"] for item in plan})

        second_plan, second_rendered = profile_pack.plan_install(self.pack, context)
        self.assertFalse(
            any(item["action"] == "collision" for item in second_plan),
            second_plan,
        )
        for destination, content in second_rendered.items():
            self.assertEqual(Path(destination).read_text(encoding="utf-8"), content)

    def test_component_collision_requires_replace_and_creates_backup(self):
        context = self._context()
        destination = (
            context.project_root
            / ".agents"
            / "skills"
            / "review-pack"
            / "SKILL.md"
        )
        destination.parent.mkdir(parents=True)
        destination.write_text("different\n", encoding="utf-8")
        with self.assertRaises(profile_pack.PackError):
            profile_pack.install_pack(self.pack, context, apply=True, replace=False)
        _, backup, _ = profile_pack.install_pack(
            self.pack, context, apply=True, replace=True
        )
        self.assertIsNotNone(backup)
        self.assertTrue(any(path.is_file() for path in backup.rglob("*")))

    def test_toml_conflict_stops_plan(self):
        context = self._context()
        config = context.config_layer / "config.toml"
        config.parent.mkdir(parents=True)
        config.write_text('personality = "friendly"\n', encoding="utf-8")
        with self.assertRaises(profile_pack.PackError):
            profile_pack.plan_install(self.pack, context)

    def test_global_profile_uses_separate_file(self):
        (self.pack / "profile.toml").write_text(
            'model_reasoning_effort = "high"\n', encoding="utf-8"
        )
        manifest_path = self.pack / "pack.toml"
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8").replace(
                'default_scope = "project"', 'default_scope = "global"'
            ),
            encoding="utf-8",
        )
        context = self._context(scope="global", profile="deep-review")
        profile_pack.install_pack(self.pack, context, apply=True, replace=False)
        profile_path = context.codex_home / "deep-review.config.toml"
        self.assertTrue(profile_path.is_file())
        self.assertEqual(
            "high",
            tomllib.loads(profile_path.read_text(encoding="utf-8"))[
                "model_reasoning_effort"
            ],
        )

    def test_obvious_secret_is_rejected(self):
        skill = self.pack / "skills" / "review-pack" / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8")
            + "\nToken sk-proj-abcdefghijklmnopqrstuvwxyz123456\n",
            encoding="utf-8",
        )
        errors, _ = profile_pack.validate_pack(self.pack)
        self.assertTrue(any("API key" in error for error in errors))

    def test_install_record_is_json(self):
        context = self._context()
        _, _, record = profile_pack.install_pack(
            self.pack, context, apply=True, replace=False
        )
        value = json.loads(record.read_text(encoding="utf-8"))
        self.assertEqual("review-pack", value["pack"])
        self.assertEqual("project", value["scope"])

    def test_multiline_skill_description_and_binary_asset(self):
        skill = self.pack / "skills" / "review-pack" / "SKILL.md"
        content = skill.read_text(encoding="utf-8").replace(
            "description: Review changes. Use when a user asks for a focused review.",
            (
                "description: >-\n"
                "  Review changes. Use when a user asks for a focused review."
            ),
        )
        skill.write_text(content, encoding="utf-8")
        asset = skill.parent / "assets" / "icon.bin"
        asset.parent.mkdir()
        asset.write_bytes(b"\x00\xff\x00\xff")
        errors, _ = profile_pack.validate_pack(self.pack)
        self.assertEqual([], errors)

    def test_rule_loads_when_codex_is_available(self):
        if not shutil.which("codex"):
            self.skipTest("codex executable is not available")
        warning = profile_pack.check_rule_file(
            self.pack / "rules" / "review-pack.rules"
        )
        self.assertIsNone(warning)

    def test_cli_plan_and_install_end_to_end(self):
        context = self._context()
        common = [
            "--pack",
            str(self.pack),
            "--scope",
            "project",
            "--project-root",
            str(context.project_root),
            "--codex-home",
            str(context.codex_home),
            "--user-home",
            str(context.user_home),
            "--json",
        ]
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(0, profile_pack.main(["plan", *common]))
            self.assertEqual(
                0, profile_pack.main(["install", *common, "--apply"])
            )
        output = stdout.getvalue()
        self.assertIn('"operations"', output)
        self.assertTrue(
            (context.config_layer / "profile-packs" / "review-pack.json").is_file()
        )


if __name__ == "__main__":
    unittest.main()
