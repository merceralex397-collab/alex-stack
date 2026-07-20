#!/usr/bin/env python3
"""Fixture tests for codex_stack_inventory.py."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("codex_stack_inventory.py")
SPEC = importlib.util.spec_from_file_location("codex_stack_inventory", MODULE_PATH)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, separators=(",", ":")) + "\n" for record in records), encoding="utf-8")


class InventoryTests(unittest.TestCase):
    def test_transport_summary_redacts_values(self) -> None:
        result = inventory._transport_summary(
            {
                "type": "streamable_http",
                "url": "https://example.test/private/path?token=secret",
                "command": r"C:\Users\PC\secret\server.exe",
                "env": {"TOKEN": "secret"},
                "http_headers": {"Authorization": "secret"},
                "env_http_headers": {"X-Key": "KEY_ENV"},
                "bearer_token_env_var": "BEARER_TOKEN",
            }
        )
        encoded = json.dumps(result)
        self.assertEqual(result["host"], "example.test")
        self.assertEqual(result["command"], "server.exe")
        self.assertIn("TOKEN", result["environment_names"])
        self.assertNotIn("private/path", encoded)
        self.assertNotIn('"secret"', encoded)

    def test_session_scan_attributes_skill_mcp_app_and_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            project.mkdir()
            skill = root / "skills" / "demo" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: demo\n---\n", encoding="utf-8")
            now = datetime.now(timezone.utc)
            timestamp = now.isoformat().replace("+00:00", "Z")
            session = root / "rollout.jsonl"
            records = [
                {"timestamp": timestamp, "type": "session_meta", "payload": {"id": "session", "cwd": str(project)}},
                {"timestamp": timestamp, "type": "turn_context", "payload": {"type": "turn_context", "turn_id": "turn", "cwd": str(project)}},
                {
                    "timestamp": timestamp,
                    "type": "response_item",
                    "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Use $demo"}]},
                },
                {
                    "timestamp": timestamp,
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "shell_command",
                        "arguments": json.dumps({"command": f'Get-Content "{skill}"'}),
                        "call_id": "shell",
                    },
                },
                {
                    "timestamp": timestamp,
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "search",
                        "namespace": "mcp__docs",
                        "arguments": "{}",
                        "call_id": "mcp-ok",
                    },
                },
                {
                    "timestamp": timestamp,
                    "type": "event_msg",
                    "payload": {
                        "type": "mcp_tool_call_end",
                        "call_id": "mcp-ok",
                        "invocation": {"server": "docs", "tool": "search", "arguments": {}},
                        "result": {"Ok": {}},
                    },
                },
                {
                    "timestamp": timestamp,
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "read",
                        "namespace": "mcp__codex_apps__github",
                        "arguments": "{}",
                        "call_id": "app-fail",
                    },
                },
                {
                    "timestamp": timestamp,
                    "type": "event_msg",
                    "payload": {
                        "type": "mcp_tool_call_end",
                        "call_id": "app-fail",
                        "invocation": {"server": "codex_apps__github", "tool": "read", "arguments": {}},
                        "result": {"Err": "redacted failure"},
                    },
                },
                {
                    "timestamp": timestamp,
                    "type": "response_item",
                    "payload": {"type": "tool_search_output", "tools": [{"name": "mcp__unused"}]},
                },
            ]
            write_jsonl(session, records)
            warnings: list[str] = []
            entry = inventory._scan_session_file(
                session,
                project,
                now - timedelta(days=14),
                {inventory._canonical(skill): "demo"},
                None,
                False,
                warnings,
            )
            usage, _ = inventory._aggregate_events([entry], now - timedelta(days=14))
            self.assertEqual(usage["skills"][0]["name"], "demo")
            self.assertEqual(usage["skills"][0]["attempts"], 1)
            self.assertEqual(usage["mcps"][0]["name"], "docs")
            self.assertEqual(usage["mcps"][0]["successes"], 1)
            self.assertEqual(usage["apps"][0]["name"], "github")
            self.assertEqual(usage["apps"][0]["failures"], 1)
            self.assertNotIn("unused", json.dumps(usage))
            self.assertNotIn("redacted failure", json.dumps(entry))

    def test_cutoff_and_project_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            other = root / "other"
            project.mkdir()
            other.mkdir()
            now = datetime.now(timezone.utc)
            old = (now - timedelta(days=15)).isoformat().replace("+00:00", "Z")
            current = now.isoformat().replace("+00:00", "Z")
            session = root / "rollout.jsonl"
            records = [
                {"timestamp": current, "type": "session_meta", "payload": {"id": "session", "cwd": str(project)}},
                {"timestamp": old, "type": "turn_context", "payload": {"type": "turn_context", "turn_id": "old", "cwd": str(project)}},
                {
                    "timestamp": old,
                    "type": "response_item",
                    "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "$old-skill"}]},
                },
                {"timestamp": current, "type": "turn_context", "payload": {"type": "turn_context", "turn_id": "other", "cwd": str(other)}},
                {
                    "timestamp": current,
                    "type": "response_item",
                    "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "$other-skill"}]},
                },
            ]
            write_jsonl(session, records)
            entry = inventory._scan_session_file(
                session,
                project,
                now - timedelta(days=14),
                {},
                None,
                False,
                [],
            )
            usage, _ = inventory._aggregate_events([entry], now - timedelta(days=14))
            self.assertEqual(usage["skills"], [])

    def test_incremental_scan_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            project.mkdir()
            now = datetime.now(timezone.utc)
            timestamp = now.isoformat().replace("+00:00", "Z")
            session = root / "rollout.jsonl"
            write_jsonl(
                session,
                [
                    {"timestamp": timestamp, "type": "session_meta", "payload": {"id": "session", "cwd": str(project)}},
                    {"timestamp": timestamp, "type": "turn_context", "payload": {"type": "turn_context", "turn_id": "turn", "cwd": str(project)}},
                    {
                        "timestamp": timestamp,
                        "type": "response_item",
                        "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "$demo"}]},
                    },
                ],
            )
            cutoff = now - timedelta(days=14)
            first = inventory._scan_session_file(session, project, cutoff, {}, None, False, [])
            with session.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "timestamp": timestamp,
                            "type": "response_item",
                            "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "$second"}]},
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            second = inventory._scan_session_file(session, project, cutoff, {}, first, False, [])
            usage, _ = inventory._aggregate_events([second], cutoff)
            self.assertEqual([entry["name"] for entry in usage["skills"]], ["demo", "second"])

    def test_custom_tool_call_attributes_skill_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            project.mkdir()
            skill = root / "skills" / "implicit" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: implicit\n---\n", encoding="utf-8")
            now = datetime.now(timezone.utc)
            timestamp = now.isoformat().replace("+00:00", "Z")
            session = root / "rollout.jsonl"
            write_jsonl(
                session,
                [
                    {"timestamp": timestamp, "type": "session_meta", "payload": {"id": "session", "cwd": str(project)}},
                    {"timestamp": timestamp, "type": "turn_context", "payload": {"type": "turn_context", "turn_id": "turn", "cwd": str(project)}},
                    {
                        "timestamp": timestamp,
                        "type": "response_item",
                        "payload": {
                            "type": "custom_tool_call",
                            "name": "exec",
                            "input": f'Get-Content "{skill}"',
                            "call_id": "custom",
                        },
                    },
                ],
            )
            cutoff = now - timedelta(days=14)
            entry = inventory._scan_session_file(
                session,
                project,
                cutoff,
                {inventory._canonical(skill): "implicit"},
                None,
                False,
                [],
            )
            usage, _ = inventory._aggregate_events([entry], cutoff)
            self.assertEqual(usage["skills"][0]["name"], "implicit")
            self.assertEqual(usage["skills"][0]["attempts"], 1)

    def test_cached_app_catalog_enriches_configured_app(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            codex_home = Path(temp) / ".codex"
            plugin = codex_home / "plugins" / "cache" / "market" / "mail" / "1.0.0"
            (plugin / ".codex-plugin").mkdir(parents=True)
            (plugin / ".app.json").write_text(
                json.dumps({"apps": {"Mail": {"id": "connector_mail"}}}),
                encoding="utf-8",
            )
            (plugin / ".codex-plugin" / "plugin.json").write_text(
                json.dumps({"name": "mail", "description": "Read project mail."}),
                encoding="utf-8",
            )
            catalog = inventory._cached_app_catalog(codex_home, [])
            self.assertEqual(catalog["connector_mail"]["name"], "Mail")
            self.assertEqual(catalog["connector_mail"]["owner_plugin"], "mail@market")
            self.assertEqual(catalog["connector_mail"]["description"], "Read project mail.")

    def test_build_inventory_degrades_without_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            codex_home = root / ".codex"
            project.mkdir()
            codex_home.mkdir()
            args = argparse.Namespace(project=str(project), days=14, refresh=False, no_cache=True, pretty=False)
            with patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=False), patch.object(
                inventory, "_resolve_codex_cli", return_value=None
            ):
                result = inventory.build_inventory(args)
            self.assertFalse(result["sources"]["codex_cli"])
            self.assertTrue(any("partial" in warning for warning in result["warnings"]))
            self.assertTrue(result["privacy"]["secret_values_emitted"] is False)


if __name__ == "__main__":
    unittest.main()
