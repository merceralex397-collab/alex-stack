#!/usr/bin/env node

import { createReadStream, promises as fs } from "node:fs";
import path from "node:path";
import readline from "node:readline";

const codexHome = process.env.CODEX_HOME || path.join(process.env.USERPROFILE || "", ".codex");
const roots = [path.join(codexHome, "sessions"), path.join(codexHome, "archived_sessions")];
const shellToolPattern =
  /(?:^|\.|__)(exec|wait|exec_command|write_stdin|shell|shell_command|bash|powershell|run_command|terminal)$/i;
const preferredDiagnosticPattern =
  /(?:ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|NativeCommandError|command not found|not recognized as (?:the name of|an internal or external) command|cannot find path|no such file or directory|permission denied|access (?:is )?denied|syntax error|unexpected (?:token|EOF)|failed to spawn|cannot start process|CreateProcess error|npm ERR!|fatal:|exception|(?:^|\s)error(?:\s|:)|\bfailed\b)/i;

async function listFiles(root) {
  const result = [];
  async function walk(directory) {
    let entries;
    try {
      entries = await fs.readdir(directory, { withFileTypes: true });
    } catch (error) {
      if (error?.code === "ENOENT") return;
      throw error;
    }
    for (const entry of entries) {
      const full = path.join(directory, entry.name);
      if (entry.isDirectory()) await walk(full);
      else if (entry.isFile() && entry.name.endsWith(".jsonl")) result.push(full);
    }
  }
  await walk(root);
  return result.sort();
}

function increment(map, key) {
  map.set(key, (map.get(key) || 0) + 1);
}

function outputText(payload) {
  const output = payload?.output ?? payload?.result ?? payload?.content ?? "";
  return typeof output === "string" ? output : JSON.stringify(output);
}

function exitCode(text) {
  const patterns = [
    /Process exited with code\s+(-?\d+)/i,
    /Command (?:exited|failed) with (?:exit )?code\s*[:=]?\s*(-?\d+)/i,
    /(?:^|\n)\s*Exit code\s*[:=]\s*(-?\d+)/im,
    /"exit_code"\s*:\s*(-?\d+)/i,
  ];
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return Number.parseInt(match[1], 10);
  }
  return null;
}

function commandFrom(payload) {
  let args = payload?.arguments ?? payload?.input ?? {};
  if (typeof args === "string") {
    try {
      args = JSON.parse(args);
    } catch {
      return args.slice(0, 500);
    }
  }
  return String(args?.cmd ?? args?.command ?? args?.script ?? args?.chars ?? "").slice(0, 500);
}

function workdirFrom(payload, fallback) {
  let args = payload?.arguments ?? payload?.input ?? {};
  if (typeof args === "string") {
    try {
      args = JSON.parse(args);
    } catch {
      return fallback;
    }
  }
  return String(args?.workdir ?? args?.cwd ?? fallback ?? "[unknown]");
}

function commandFamily(command, tool) {
  if (!command) return tool === "write_stdin" || tool === "wait" ? `[${tool} continuation]` : "[empty]";
  const clean = command.replace(/\s+/g, " ").trim();
  const lower = clean.toLowerCase();
  const known = [
    "rg",
    "git",
    "gh",
    "npm",
    "npx",
    "pnpm",
    "yarn",
    "node",
    "python",
    "python3",
    "az",
    "curl",
    "docker",
    "dotnet",
    "pytest",
  ];
  for (const name of known) {
    if (lower === name || lower.startsWith(`${name} `) || lower.startsWith(`${name}.exe `)) return name;
  }
  const psCmdlet = clean.match(
    /^(Get|Set|New|Remove|Test|Select|Where|ForEach|Resolve|Invoke|Start|Stop|Write|Read|Join|Split|Convert|Import|Export|Measure|Sort|Copy|Move|Add|Clear|Compare|Format)-[A-Za-z]+/,
  );
  if (psCmdlet) return psCmdlet[0];
  if (/^(?:\$|if\b|foreach\b|for\b|while\b|try\b|function\b|&\s*\{)/i.test(clean)) {
    return "PowerShell compound";
  }
  return clean.split(/\s+/)[0].slice(0, 80);
}

function normalizedCommand(command) {
  if (!command) return "[continuation/no command text]";
  let value = command.replace(/\s+/g, " ").trim();
  const profile = process.env.USERPROFILE;
  if (profile) value = value.replaceAll(profile, "~");
  return value.length > 240 ? `${value.slice(0, 237)}...` : value;
}

function diagnosticLines(text) {
  const marker = text.indexOf("Final output:");
  const body = marker >= 0 ? text.slice(marker + "Final output:".length) : text;
  return body
    .split(/\r?\n/)
    .map((line) => line.replace(/\u001b\[[0-?]*[ -/]*[@-~]/g, "").replace(/\s+/g, " ").trim())
    .filter(
      (line) =>
        line &&
        !/^(?:Chunk ID:|Wall time:|Process exited with code|Final output:|Original token count:|Warning: truncated output)/i.test(
          line,
        ),
    );
}

function hasCommonDiagnostic(text) {
  return diagnosticLines(text).some((line) => preferredDiagnosticPattern.test(line));
}

function top(map, limit = 20) {
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .slice(0, limit);
}

const aggregate = {
  files: 0,
  failed: 0,
  noDiagnosticExit1: 0,
  parserErrors: 0,
  noDiagnosticByTool: new Map(),
  noDiagnosticByCwd: new Map(),
  noDiagnosticByFamily: new Map(),
  noDiagnosticByCommand: new Map(),
  parserByTool: new Map(),
  parserByCwd: new Map(),
  parserByFamily: new Map(),
  parserByCommand: new Map(),
};

const files = (await Promise.all(roots.map(listFiles))).flat();
for (const file of files) {
  aggregate.files += 1;
  let cwd = "[unknown]";
  const calls = new Map();
  const input = createReadStream(file, { encoding: "utf8" });
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    if (
      !line.includes('"type":"session_meta"') &&
      !line.includes('"type":"turn_context"') &&
      !line.includes('"type":"function_call"') &&
      !line.includes('"type":"custom_tool_call"') &&
      !line.includes('"type":"function_call_output"') &&
      !line.includes('"type":"custom_tool_call_output"')
    ) {
      continue;
    }
    let record;
    try {
      record = JSON.parse(line);
    } catch {
      continue;
    }
    const payload = record?.payload;
    if (record.type === "session_meta" && payload?.cwd) cwd = String(payload.cwd);
    if (record.type === "turn_context" && payload?.cwd) cwd = String(payload.cwd);
    if (payload?.type === "function_call" || payload?.type === "custom_tool_call") {
      const name = String(payload.name || "");
      const callId = String(payload.call_id || payload.id || "");
      if (callId && shellToolPattern.test(name)) {
        const command = commandFrom(payload);
        calls.set(callId, {
          tool: name,
          command,
          family: commandFamily(command, name),
          cwd: workdirFrom(payload, cwd),
        });
      }
      continue;
    }
    if (payload?.type !== "function_call_output" && payload?.type !== "custom_tool_call_output") continue;
    const callId = String(payload.call_id || payload.id || "");
    const call = calls.get(callId);
    if (!call) continue;
    const text = outputText(payload);
    const code = exitCode(text);
    if (code === null || code === 0) continue;
    aggregate.failed += 1;

    const command = normalizedCommand(call.command);
    if (code === 1 && !hasCommonDiagnostic(text)) {
      aggregate.noDiagnosticExit1 += 1;
      increment(aggregate.noDiagnosticByTool, call.tool);
      increment(aggregate.noDiagnosticByCwd, call.cwd);
      increment(aggregate.noDiagnosticByFamily, call.family);
      increment(aggregate.noDiagnosticByCommand, command);
    }
    if (/\bParserError\b/i.test(text)) {
      aggregate.parserErrors += 1;
      increment(aggregate.parserByTool, call.tool);
      increment(aggregate.parserByCwd, call.cwd);
      increment(aggregate.parserByFamily, call.family);
      increment(aggregate.parserByCommand, command);
    }
  }
}

const result = {
  files: aggregate.files,
  failed: aggregate.failed,
  noDiagnosticExit1: {
    count: aggregate.noDiagnosticExit1,
    byTool: top(aggregate.noDiagnosticByTool),
    byWorkingDirectory: top(aggregate.noDiagnosticByCwd),
    byCommandFamily: top(aggregate.noDiagnosticByFamily),
    topExactCommands: top(aggregate.noDiagnosticByCommand, 15),
  },
  parserErrors: {
    count: aggregate.parserErrors,
    byTool: top(aggregate.parserByTool),
    byWorkingDirectory: top(aggregate.parserByCwd),
    byCommandFamily: top(aggregate.parserByFamily),
    topExactCommands: top(aggregate.parserByCommand, 15),
  },
};

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
