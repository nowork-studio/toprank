/**
 * Claude CLI subprocess runner for skill E2E testing.
 *
 * Spawns `claude -p` as an independent process so it works inside Claude Code
 * sessions. Pipes the prompt via the -p flag, streams NDJSON output for
 * real-time progress.
 *
 * Adapted from garrytan/gstack session-runner.ts.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// Strip Claude* env vars so nested sessions don't inherit the outer session's context.
const STRIPPED_ENV_PREFIXES = ['CLAUDE_', 'ANTHROPIC_'];

export interface CostEstimate {
  inputChars: number;
  outputChars: number;
  estimatedTokens: number;
  estimatedCost: number; // USD
  turnsUsed: number;
}

export interface SkillTestResult {
  toolCalls: Array<{ tool: string; input: any; output: string }>;
  exitReason: string;
  duration: number;
  output: string;
  costEstimate: CostEstimate;
  transcript: any[];
  model: string;
  firstResponseMs: number;
}

// --- NDJSON parser (pure, testable) ---

export interface ParsedNDJSON {
  transcript: any[];
  resultLine: any | null;
  turnCount: number;
  toolCalls: Array<{ tool: string; input: any; output: string }>;
}

export function parseNDJSON(lines: string[]): ParsedNDJSON {
  const transcript: any[] = [];
  let resultLine: any = null;
  let turnCount = 0;
  const toolCalls: ParsedNDJSON['toolCalls'] = [];

  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const event = JSON.parse(line);
      transcript.push(event);

      if (event.type === 'assistant') {
        turnCount++;
        const content = event.message?.content || [];
        for (const item of content) {
          if (item.type === 'tool_use') {
            toolCalls.push({ tool: item.name || 'unknown', input: item.input || {}, output: '' });
          }
        }
      }

      if (event.type === 'result') resultLine = event;
    } catch { /* skip malformed lines */ }
  }

  return { transcript, resultLine, turnCount, toolCalls };
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + '…' : s;
}

// --- Install skill into a temp working dir so Claude discovers it ---

/**
 * Create a temp working directory with the skill installed at .claude/skills/<name>/.
 * Claude Code auto-discovers skills from this location.
 * Returns the temp dir path (caller is responsible for cleanup).
 */
export function createSkillWorkdir(skillPath: string, skillName: string): string {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), `toprank-test-`));
  const skillsDir = path.join(tmpDir, '.claude', 'skills', skillName);
  fs.mkdirSync(skillsDir, { recursive: true });

  // Copy entire skill directory recursively
  copyDir(skillPath, skillsDir);

  return tmpDir;
}

function copyDir(src: string, dest: string): void {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// --- Main runner ---

export async function runSkillTest(options: {
  prompt: string;
  workingDirectory?: string;
  maxTurns?: number;
  timeoutMs?: number;
  testName?: string;
  envOverrides?: Record<string, string>;
}): Promise<SkillTestResult> {
  const {
    prompt,
    workingDirectory = os.tmpdir(),
    maxTurns = 30,
    timeoutMs = 5 * 60 * 1000, // 5 min
    testName,
    envOverrides = {},
  } = options;

  // Strip CLAUDE_* env vars to avoid nested session pollution
  const filteredEnv: Record<string, string> = {};
  for (const [k, v] of Object.entries(process.env)) {
    if (v !== undefined && !STRIPPED_ENV_PREFIXES.some(p => k.startsWith(p))) {
      filteredEnv[k] = v;
    }
  }
  Object.assign(filteredEnv, envOverrides);

  // Keep ANTHROPIC_API_KEY — it's needed for the subprocess to call the API
  if (process.env.ANTHROPIC_API_KEY) {
    filteredEnv['ANTHROPIC_API_KEY'] = process.env.ANTHROPIC_API_KEY;
  }

  const startTime = Date.now();
  let liveTurnCount = 0;
  let liveToolCount = 0;
  let firstResponseMs = 0;

  const proc = Bun.spawn(
    ['claude', '--output-format', 'stream-json', '--verbose', '--max-turns', String(maxTurns), '-p', prompt],
    {
      cwd: workingDirectory,
      stdout: 'pipe',
      stderr: 'pipe',
      env: filteredEnv,
    }
  );

  let timedOut = false;
  const timeoutId = setTimeout(() => {
    timedOut = true;
    proc.kill();
  }, timeoutMs);

  const collectedLines: string[] = [];
  let stderr = '';
  let exitReason = 'unknown';
  const model = filteredEnv['CLAUDE_MODEL'] || 'claude-sonnet-4-6';

  // Collect stderr in background
  const stderrPromise = (async () => {
    const chunks: string[] = [];
    for await (const chunk of proc.stderr) {
      chunks.push(Buffer.from(chunk).toString());
    }
    return chunks.join('');
  })();

  // Stream stdout NDJSON
  try {
    let buf = '';
    for await (const chunk of proc.stdout) {
      buf += Buffer.from(chunk).toString();
      const newlineIdx = buf.lastIndexOf('\n');
      if (newlineIdx === -1) continue;

      const complete = buf.slice(0, newlineIdx);
      buf = buf.slice(newlineIdx + 1);

      for (const line of complete.split('\n')) {
        if (!line.trim()) continue;
        collectedLines.push(line);

        try {
          const event = JSON.parse(line);
          if (event.type === 'assistant') {
            liveTurnCount++;
            const content = event.message?.content || [];
            for (const item of content) {
              if (item.type === 'tool_use') {
                liveToolCount++;
                if (firstResponseMs === 0) firstResponseMs = Date.now() - startTime;
                const elapsed = Math.round((Date.now() - startTime) / 1000);
                process.stderr.write(
                  `  [${elapsed}s t${liveTurnCount}] ${item.name}(${truncate(JSON.stringify(item.input || {}), 80)})\n`
                );
              }
            }
          }
        } catch { /* skip */ }
      }
    }
    if (buf.trim()) collectedLines.push(buf);
  } catch { /* stream error — fall through */ }

  stderr = await stderrPromise;
  const exitCode = await proc.exited;
  clearTimeout(timeoutId);

  if (timedOut) {
    exitReason = 'timeout';
  } else if (exitCode === 0) {
    exitReason = 'success';
  } else {
    exitReason = `exit_code_${exitCode}`;
  }

  const duration = Date.now() - startTime;
  const { transcript, resultLine, toolCalls } = parseNDJSON(collectedLines);

  if (resultLine) {
    if (resultLine.is_error) {
      exitReason = 'error_api';
    } else if (resultLine.subtype === 'success') {
      exitReason = 'success';
    } else if (resultLine.subtype) {
      exitReason = resultLine.subtype;
    }
  }

  const turnsUsed = resultLine?.num_turns || 0;
  const estimatedCost = resultLine?.total_cost_usd || 0;

  const costEstimate: CostEstimate = {
    inputChars: prompt.length,
    outputChars: (resultLine?.result || '').length,
    estimatedTokens:
      (resultLine?.usage?.input_tokens || 0) +
      (resultLine?.usage?.output_tokens || 0) +
      (resultLine?.usage?.cache_read_input_tokens || 0),
    estimatedCost: Math.round(estimatedCost * 100) / 100,
    turnsUsed,
  };

  return {
    toolCalls,
    exitReason,
    duration,
    output: resultLine?.result || '',
    costEstimate,
    transcript,
    model,
    firstResponseMs,
  };
}
