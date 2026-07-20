#!/usr/bin/env node

import { createReadStream, promises as fs } from "node:fs";
import path from "node:path";
import readline from "node:readline";

const codexHome = process.env.CODEX_HOME || path.join(process.env.USERPROFILE || "", ".codex");
const outputDir = path.resolve(process.argv[2] || process.cwd());
const roots = [
  path.join(codexHome, "sessions"),
  path.join(codexHome, "archived_sessions"),
];

const shellToolPattern =
  /(?:^|\.|__)(exec|wait|exec_command|write_stdin|shell|shell_command|bash|powershell|run_command|terminal)$/i;
const exitPatterns = [
  /Process exited with code\s+(-?\d+)/i,
  /Command (?:exited|failed) with (?:exit )?code\s*[:=]?\s*(-?\d+)/i,
  /(?:^|\n)\s*Exit code\s*[:=]\s*(-?\d+)/im,
  /"exit_code"\s*:\s*(-?\d+)/i,
];
const errorIndicatorPattern =
  /\b(?:ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|NativeCommandError|FullyQualifiedErrorId|command not found|not recognized as (?:the name of|an internal or external) command|cannot find path|no such file or directory|permission denied|access (?:is )?denied|syntax error|unexpected (?:token|EOF)|failed|cannot start process|CreateProcess error|fatal|exception|error)\b/i;
const preferredDiagnosticPattern =
  /(?:ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|NativeCommandError|command not found|not recognized as (?:the name of|an internal or external) command|cannot find path|no such file or directory|permission denied|access (?:is )?denied|syntax error|unexpected (?:token|EOF)|failed to spawn|cannot start process|CreateProcess error|npm ERR!|fatal:|exception|(?:^|\s)error(?:\s|:)|\bfailed\b)/i;
const metadataLinePattern =
  /^(?:Chunk ID:|Wall time:|Process exited with code|Final output:|Original token count:|Warning: truncated output|You have \d+ weighted tokens left|$)/i;

const stats = {
  generatedAt: new Date().toISOString(),
  codexHome,
  roots: [],
  filesScanned: 0,
  bytesScanned: 0,
  jsonlLinesScanned: 0,
  shellCallsSeen: 0,
  shellOutputsSeen: 0,
  failedCommandOutputs: 0,
  failedOutputsWithIndicators: 0,
  failedOutputsWithoutIndicators: 0,
  parseErrors: 0,
  unparsedShellRecords: 0,
  recoveredMalformedShellFailures: 0,
  malformedShellRecordsWithoutFailureMarker: 0,
  malformedNonShellRecords: 0,
  parseErrorDetails: [],
};

const signatures = new Map();
const tools = new Map();
const exitCodes = new Map();
const functionNames = new Map();

async function listJsonlFiles(root) {
  const found = [];
  async function walk(directory) {
    let entries;
    try {
      entries = await fs.readdir(directory, { withFileTypes: true });
    } catch (error) {
      if (error?.code === "ENOENT") return;
      throw error;
    }
    for (const entry of entries) {
      const fullPath = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        await walk(fullPath);
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith(".jsonl")) {
        found.push(fullPath);
      }
    }
  }
  await walk(root);
  return found.sort();
}

function increment(map, key, amount = 1) {
  map.set(key, (map.get(key) || 0) + amount);
}

function getExitCode(text) {
  for (const pattern of exitPatterns) {
    const match = text.match(pattern);
    if (match) return Number.parseInt(match[1], 10);
  }
  return null;
}

function cleanLine(line) {
  return line
    .replace(/\u001b\[[0-?]*[ -/]*[@-~]/g, "")
    .replace(/\u0000/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeSignature(value) {
  let normalized = cleanLine(value);
  const userProfile = process.env.USERPROFILE;
  if (userProfile) {
    normalized = normalized.replaceAll(userProfile, "~");
    normalized = normalized.replaceAll(userProfile.replaceAll("\\", "\\\\"), "~");
  }
  normalized = normalized
    .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, "<guid>")
    .replace(/\bcall_[A-Za-z0-9_-]+\b/g, "<call_id>")
    .replace(/\b(?:19|20)\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\b/g, "<timestamp>")
    .replace(/\s+at line:\d+\s+char:\d+.*/i, "")
    .trim();
  if (normalized.length > 500) normalized = `${normalized.slice(0, 497)}...`;
  return normalized;
}

function extractDiagnostic(text, exitCode) {
  const finalOutputIndex = text.indexOf("Final output:");
  const body = finalOutputIndex >= 0 ? text.slice(finalOutputIndex + "Final output:".length) : text;
  const lines = body
    .split(/\r?\n/)
    .map(cleanLine)
    .filter((line) => !metadataLinePattern.test(line))
    .filter((line) => !/^(?:Line|\+|~+|\^+|\|)$/.test(line))
    .filter((line) => !/^\s*(?:at |CategoryInfo\s*:|FullyQualifiedErrorId\s*:)/i.test(line));

  if (lines.length === 0) return `[No diagnostic text; exit code ${exitCode}]`;

  const candidates = lines.filter(
    (line) =>
      preferredDiagnosticPattern.test(line) &&
      !/^["']?[A-Za-z_][\w-]*["']?\s*:\s*["[{]/.test(line) &&
      !/^[A-Za-z_][\w-]*\s*:\s*(?:error\s+instanceof|return|function|const|let|var)\b/i.test(line) &&
      !/^\d+:\s*(?:function|const|let|var|return|if|for|while|class|interface|type|export|import)\b/i.test(line) &&
      !/:\d+:\s*(?:function|const|let|var|return|if|for|while|class|interface|type|export|import)\b/i.test(line),
  );
  const score = (line) => {
    if (
      /ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|NativeCommandError|command not found|not recognized as (?:the name of|an internal or external) command|cannot find path|no such file or directory|permission denied|access (?:is )?denied|syntax error|unexpected (?:token|EOF)|failed to spawn|cannot start process|CreateProcess error|fatal:|rg: regex parse error/i.test(
        line,
      )
    ) {
      return 100;
    }
    if (/npm ERR!|npm error|error TS\d+|\d+:\d+\s+error\b|ExpectError/i.test(line)) return 90;
    if (/^(?:error|exception)\b|:\s*(?:error|exception)\b/i.test(line)) return 80;
    if (/\bfailed\b/i.test(line)) return 70;
    return 10;
  };
  const preferred = candidates
    .map((line, index) => ({ line, index, score: score(line) }))
    .sort((a, b) => b.score - a.score || a.index - b.index)[0]?.line;
  if (!preferred) return `[No common diagnostic text; exit code ${exitCode}]`;
  const selected = preferred;

  if (/^ParserError:?\s*$/i.test(selected)) {
    const detail = lines.find(
      (line) => line !== selected && /unexpected|missing|invalid|terminator|token/i.test(line),
    );
    if (detail) return normalizeSignature(`ParserError: ${detail}`);
  }

  return normalizeSignature(selected) || `[No diagnostic text; exit code ${exitCode}]`;
}

function categorize(signature) {
  if (/^\[No (?:common )?diagnostic text;/i.test(signature)) return "No diagnostic";
  if (
    /ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|NativeCommandError|FullyQualifiedErrorId|Cannot find path|The term .* is not recognized/i.test(
      signature,
    )
  ) {
    return "PowerShell";
  }
  if (
    /bash:|sh:|command not found|No such file or directory|Permission denied|syntax error|unexpected EOF/i.test(
      signature,
    )
  ) {
    return "Bash/POSIX";
  }
  if (/^fatal:|^git:/i.test(signature)) return "Git";
  if (/^rg:|regex parse error/i.test(signature)) return "ripgrep";
  if (/npm (?:ERR!|error)|pnpm|yarn|node:|ERR_MODULE|MODULE_NOT_FOUND/i.test(signature)) return "Node/package";
  if (/test|assert|lint|error TS\d+|\d+:\d+\s+error\b|failed/i.test(signature)) return "Build/test";
  return "Other";
}

function outputText(payload) {
  const output = payload?.output ?? payload?.result ?? payload?.content ?? "";
  if (typeof output === "string") return output;
  try {
    return JSON.stringify(output);
  } catch {
    return String(output);
  }
}

async function scanFile(filePath, snapshotSize) {
  const fileStat = await fs.stat(filePath);
  stats.filesScanned += 1;
  stats.bytesScanned += snapshotSize;

  const shellCalls = new Map();
  const input = createReadStream(filePath, {
    encoding: "utf8",
    end: snapshotSize > 0 ? snapshotSize - 1 : undefined,
  });
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let lineNumber = 0;

  for await (const line of lines) {
    lineNumber += 1;
    stats.jsonlLinesScanned += 1;
    if (
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
    } catch (error) {
      stats.parseErrors += 1;
      const contentIndex = line.indexOf('"content":');
      const outerHeader = contentIndex >= 0 ? line.slice(0, contentIndex) : line;
      const rawCallId = outerHeader.match(/"call_id":"([^"]+)"/)?.[1] || "";
      const rawName = outerHeader.match(/"name":"([^"]+)"/)?.[1] || "";
      const outerPayloadType = line.match(/"payload":\{"type":"([^"]+)"/)?.[1] || "";
      const mightBeShell =
        shellCalls.has(rawCallId) ||
        ((outerPayloadType === "function_call" || outerPayloadType === "custom_tool_call") &&
          shellToolPattern.test(rawName));
      if (mightBeShell) {
        const rawExitCode = getExitCode(line);
        if (rawExitCode !== null && rawExitCode !== 0) {
          const toolName = shellCalls.get(rawCallId) || rawName || "[unknown shell tool]";
          const recoveredText = line
            .replaceAll("\\r\\n", "\n")
            .replaceAll("\\n", "\n")
            .replaceAll('\\"', '"');
          const hasIndicator = errorIndicatorPattern.test(recoveredText);
          const signature = extractDiagnostic(recoveredText, rawExitCode);
          const key = `${rawExitCode}\u0000${toolName}\u0000${signature}`;
          const existing = signatures.get(key);
          if (existing) {
            existing.count += 1;
          } else {
            signatures.set(key, {
              count: 1,
              exitCode: rawExitCode,
              tool: toolName,
              category: categorize(signature),
              signature,
              indicatorMatched: hasIndicator,
            });
          }
          stats.failedCommandOutputs += 1;
          stats.recoveredMalformedShellFailures += 1;
          if (hasIndicator) stats.failedOutputsWithIndicators += 1;
          else stats.failedOutputsWithoutIndicators += 1;
          increment(tools, toolName);
          increment(exitCodes, String(rawExitCode));
        } else {
          stats.malformedShellRecordsWithoutFailureMarker += 1;
        }
      } else {
        stats.malformedNonShellRecords += 1;
      }
      if (stats.parseErrorDetails.length < 20) {
        stats.parseErrorDetails.push({
          file: filePath,
          line: lineNumber,
          mightBeShell,
          explicitExitCode: getExitCode(line),
          message: String(error?.message || error),
        });
      }
      continue;
    }

    const payload = record?.payload;
    if (!payload) continue;

    if (payload.type === "function_call" || payload.type === "custom_tool_call") {
      const name = String(payload.name || "");
      const callId = String(payload.call_id || payload.id || "");
      increment(functionNames, name || "[unnamed]");
      if (callId && shellToolPattern.test(name)) {
        shellCalls.set(callId, name);
        stats.shellCallsSeen += 1;
      }
      continue;
    }

    if (payload.type !== "function_call_output" && payload.type !== "custom_tool_call_output") {
      continue;
    }

    const callId = String(payload.call_id || payload.id || "");
    const toolName = shellCalls.get(callId);
    if (!toolName) continue;

    stats.shellOutputsSeen += 1;
    const text = outputText(payload);
    const exitCode = getExitCode(text);
    if (exitCode === null || exitCode === 0) continue;

    stats.failedCommandOutputs += 1;
    increment(tools, toolName);
    increment(exitCodes, String(exitCode));

    const hasIndicator = errorIndicatorPattern.test(text);
    if (hasIndicator) stats.failedOutputsWithIndicators += 1;
    else stats.failedOutputsWithoutIndicators += 1;

    const signature = extractDiagnostic(text, exitCode);
    const key = `${exitCode}\u0000${toolName}\u0000${signature}`;
    const existing = signatures.get(key);
    if (existing) {
      existing.count += 1;
    } else {
      signatures.set(key, {
        count: 1,
        exitCode,
        tool: toolName,
        category: categorize(signature),
        signature,
        indicatorMatched: hasIndicator,
      });
    }
  }
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function formatBytes(bytes) {
  const units = ["B", "KiB", "MiB", "GiB", "TiB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(unit === 0 ? 0 : 2)} ${units[unit]}`;
}

await fs.mkdir(outputDir, { recursive: true });

const files = [];
for (const root of roots) {
  const rootFiles = await listJsonlFiles(root);
  let rootBytes = 0;
  for (const file of rootFiles) {
    const size = (await fs.stat(file)).size;
    rootBytes += size;
    files.push({ path: file, size });
  }
  stats.roots.push({ path: root, files: rootFiles.length, bytes: rootBytes });
}

for (let index = 0; index < files.length; index += 1) {
  if (index % 25 === 0 || index === files.length - 1) {
    process.stderr.write(`Scanning ${index + 1}/${files.length}: ${files[index].path}\n`);
  }
  await scanFile(files[index].path, files[index].size);
}

const sorted = [...signatures.values()].sort(
  (a, b) =>
    b.count - a.count ||
    a.category.localeCompare(b.category) ||
    a.exitCode - b.exitCode ||
    a.tool.localeCompare(b.tool) ||
    a.signature.localeCompare(b.signature),
);

const csv = [
  ["count", "category", "exit_code", "tool", "common_error_indicator", "normalized_error"]
    .map(csvCell)
    .join(","),
  ...sorted.map((row) =>
    [row.count, row.category, row.exitCode, row.tool, row.indicatorMatched, row.signature]
      .map(csvCell)
      .join(","),
  ),
].join("\n");

const rootRows = stats.roots
  .map((root) => `| \`${root.path}\` | ${root.files.toLocaleString()} | ${formatBytes(root.bytes)} |`)
  .join("\n");
const toolRows = [...tools.entries()]
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([tool, count]) => `| \`${tool}\` | ${count.toLocaleString()} |`)
  .join("\n");
const exitRows = [...exitCodes.entries()]
  .sort((a, b) => b[1] - a[1] || Number(a[0]) - Number(b[0]))
  .map(([code, count]) => `| ${code} | ${count.toLocaleString()} |`)
  .join("\n");
const categoryRows = [...sorted.reduce((map, row) => {
  map.set(row.category, (map.get(row.category) || 0) + row.count);
  return map;
}, new Map())]
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([category, count]) => `| ${category} | ${count.toLocaleString()} |`)
  .join("\n");
const errorRows = sorted
  .map(
    (row) =>
      `| ${row.count.toLocaleString()} | ${row.category} | ${row.exitCode} | \`${row.tool}\` | ${row.indicatorMatched ? "yes" : "no"} | ${row.signature.replaceAll("|", "\\|")} |`,
  )
  .join("\n");

const markdown = `# Codex Session Command Error Inventory

Generated: ${stats.generatedAt}

## Scope and method

This is a streaming scan of Codex session JSONL under the global folder \`${codexHome}\`. It parses only terminal tool-call and tool-output records, identifies failed command outputs by an explicit nonzero exit code, and assigns exactly one normalized diagnostic signature to each failed command. It does not load entire session files into memory or copy prompts and responses into this report.

Indicator matching is reported as supporting context only. A failure is counted from its nonzero exit code, so failures without familiar PowerShell, Bash, or generic error wording are still included.

| Log root | Files | Size |
|---|---:|---:|
${rootRows}

The SQLite application log \`${path.join(codexHome, "logs_2.sqlite")}\` and non-session files were not scanned because this inventory is specifically for session command records.

## Totals

- Session files scanned: ${stats.filesScanned.toLocaleString()}
- JSONL size streamed: ${formatBytes(stats.bytesScanned)}
- JSONL records streamed: ${stats.jsonlLinesScanned.toLocaleString()}
- Terminal calls seen: ${stats.shellCallsSeen.toLocaleString()}
- Terminal outputs seen: ${stats.shellOutputsSeen.toLocaleString()}
- Failed command outputs: ${stats.failedCommandOutputs.toLocaleString()}
- Unique normalized error rows: ${sorted.length.toLocaleString()}
- Failures matching common error wording: ${stats.failedOutputsWithIndicators.toLocaleString()}
- Failures without common error wording: ${stats.failedOutputsWithoutIndicators.toLocaleString()}
- Malformed selected JSONL records encountered: ${stats.parseErrors.toLocaleString()}
- Failed shell outputs recovered from malformed JSONL: ${stats.recoveredMalformedShellFailures.toLocaleString()}
- Malformed shell-linked records without a nonzero exit marker: ${stats.malformedShellRecordsWithoutFailureMarker.toLocaleString()}
- Unresolved malformed shell records: ${stats.unparsedShellRecords.toLocaleString()}

## Failures by terminal tool

| Tool | Failed commands |
|---|---:|
${toolRows || "| — | 0 |"}

## Failures by exit code

| Exit code | Failed commands |
|---:|---:|
${exitRows || "| — | 0 |"}

## Failures by category

| Category | Failed commands |
|---|---:|
${categoryRows || "| — | 0 |"}

## Full normalized error list

Counts in this table sum to the failed-command total above.

| Count | Category | Exit code | Tool | Common indicator | Normalized error |
|---:|---|---:|---|:---:|---|
${errorRows || "| 0 | — | — | — | — | No failed commands found. |"}
`;

stats.completedAt = new Date().toISOString();
stats.functionToolCounts = Object.fromEntries(
  [...functionNames.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])),
);
await Promise.all([
  fs.writeFile(path.join(outputDir, "command-errors.csv"), `${csv}\n`, "utf8"),
  fs.writeFile(path.join(outputDir, "command-error-report.md"), markdown, "utf8"),
  fs.writeFile(path.join(outputDir, "scan-summary.json"), `${JSON.stringify(stats, null, 2)}\n`, "utf8"),
]);

process.stdout.write(
  `${JSON.stringify(
    {
      outputDir,
      filesScanned: stats.filesScanned,
      bytesScanned: stats.bytesScanned,
      failedCommandOutputs: stats.failedCommandOutputs,
      uniqueNormalizedErrors: sorted.length,
      parseErrors: stats.parseErrors,
    },
    null,
    2,
  )}\n`,
);
