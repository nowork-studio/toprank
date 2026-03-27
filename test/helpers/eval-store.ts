/**
 * Eval result persistence for toprank tests.
 *
 * Accumulates test results, writes them to ~/.toprank-evals/,
 * prints a summary table, and auto-compares with the previous run.
 *
 * Adapted from garrytan/gstack eval-store.ts.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { spawnSync } from 'child_process';

const EVAL_DIR = path.join(os.homedir(), '.toprank-evals');

export interface EvalTestEntry {
  name: string;
  suite: string;
  tier: 'e2e' | 'llm-judge' | 'routing';
  passed: boolean;
  duration_ms: number;
  cost_usd: number;

  // E2E
  transcript?: any[];
  output?: string;
  turns_used?: number;

  // LLM judge
  judge_scores?: Record<string, number>;
  judge_reasoning?: string;

  // Routing
  should_trigger?: boolean;
  did_trigger?: boolean;

  // Diagnostics
  exit_reason?: string;
  model?: string;
  error?: string;
}

export interface EvalResult {
  version: string;
  branch: string;
  git_sha: string;
  timestamp: string;
  tier: string;
  total_tests: number;
  passed: number;
  failed: number;
  total_cost_usd: number;
  total_duration_ms: number;
  tests: EvalTestEntry[];
}

function getGitInfo(): { branch: string; sha: string } {
  try {
    const branch = spawnSync('git', ['rev-parse', '--abbrev-ref', 'HEAD'], { stdio: 'pipe', timeout: 3000 });
    const sha = spawnSync('git', ['rev-parse', '--short', 'HEAD'], { stdio: 'pipe', timeout: 3000 });
    return {
      branch: branch.stdout?.toString().trim() || 'unknown',
      sha: sha.stdout?.toString().trim() || 'unknown',
    };
  } catch {
    return { branch: 'unknown', sha: 'unknown' };
  }
}

function getVersion(): string {
  try {
    const pkgPath = path.resolve(__dirname, '..', '..', 'package.json');
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
    return pkg.version || 'unknown';
  } catch {
    return 'unknown';
  }
}

export class EvalCollector {
  private tier: EvalTestEntry['tier'];
  private tests: EvalTestEntry[] = [];
  private finalized = false;
  private createdAt = Date.now();

  constructor(tier: EvalTestEntry['tier']) {
    this.tier = tier;
  }

  addTest(entry: EvalTestEntry): void {
    this.tests.push(entry);
  }

  async finalize(): Promise<string> {
    if (this.finalized) return '';
    this.finalized = true;

    const git = getGitInfo();
    const version = getVersion();
    const timestamp = new Date().toISOString();
    const passed = this.tests.filter(t => t.passed).length;
    const totalCost = this.tests.reduce((s, t) => s + t.cost_usd, 0);
    const totalDuration = this.tests.reduce((s, t) => s + t.duration_ms, 0);

    const result: EvalResult = {
      version,
      branch: git.branch,
      git_sha: git.sha,
      timestamp,
      tier: this.tier,
      total_tests: this.tests.length,
      passed,
      failed: this.tests.length - passed,
      total_cost_usd: Math.round(totalCost * 100) / 100,
      total_duration_ms: totalDuration,
      tests: this.tests,
    };

    fs.mkdirSync(EVAL_DIR, { recursive: true });
    const dateStr = timestamp.replace(/[:.]/g, '').replace('T', '-').slice(0, 15);
    const safeBranch = git.branch.replace(/[^a-zA-Z0-9._-]/g, '-');
    const filename = `${version}-${safeBranch}-${this.tier}-${dateStr}.json`;
    const filepath = path.join(EVAL_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(result, null, 2) + '\n');

    this.printSummary(result, filepath, git);
    return filepath;
  }

  private printSummary(result: EvalResult, filepath: string, git: { branch: string; sha: string }): void {
    const lines: string[] = [''];
    lines.push(`Eval Results — v${result.version} @ ${git.branch} (${git.sha}) — ${this.tier}`);
    lines.push('═'.repeat(65));

    for (const t of this.tests) {
      const status = t.passed ? ' PASS ' : ' FAIL ';
      const cost = `$${t.cost_usd.toFixed(3)}`;
      const dur = t.duration_ms ? `${Math.round(t.duration_ms / 1000)}s` : '';
      const name = t.name.length > 38 ? t.name.slice(0, 35) + '...' : t.name.padEnd(38);
      lines.push(`  ${name}  ${status}  ${cost.padStart(7)}  ${dur.padStart(5)}`);
    }

    lines.push('─'.repeat(65));
    lines.push(`  Total: ${result.passed}/${result.total_tests} passed   $${result.total_cost_usd.toFixed(2)}   ${Math.round(result.total_duration_ms / 1000)}s`);
    lines.push(`Saved: ${filepath}`);

    process.stderr.write(lines.join('\n') + '\n');
  }
}
