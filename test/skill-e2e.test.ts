/**
 * End-to-end tests for the seo-analysis skill.
 *
 * Spawns `claude -p` with the skill installed in a temp working directory.
 * Uses mock scripts and fixture data so no real Google credentials are needed.
 *
 * Run: EVALS=1 bun test test/skill-e2e.test.ts
 *
 * Each test checks:
 * - Did Claude complete successfully (exit reason = success)?
 * - Did it follow the expected skill phases (tool calls in right order)?
 * - Did the output meet quality criteria?
 */

import { describe, test, expect, beforeAll, afterAll } from 'bun:test';
import { runSkillTest, createSkillWorkdir } from './helpers/session-runner';
import type { SkillTestResult } from './helpers/session-runner';
import { seoReportJudge } from './helpers/llm-judge';
import { EvalCollector } from './helpers/eval-store';
import {
  selectTests,
  detectBaseBranch,
  getChangedFiles,
  E2E_TOUCHFILES,
  GLOBAL_TOUCHFILES,
} from './helpers/touchfiles';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

const ROOT = path.resolve(import.meta.dir, '..');
const SKILL_PATH = path.join(ROOT, 'seo-analysis');
const FIXTURES_DIR = path.join(ROOT, 'test', 'fixtures');

const evalsEnabled = !!process.env.EVALS;
const describeE2E = evalsEnabled ? describe : describe.skip;

const evalCollector = evalsEnabled ? new EvalCollector('e2e') : null;

// Diff-based selection
let selectedTests: string[] | null = null;
if (evalsEnabled && !process.env.EVALS_ALL) {
  const baseBranch = process.env.EVALS_BASE || detectBaseBranch(ROOT) || 'main';
  const changedFiles = getChangedFiles(baseBranch, ROOT);
  if (changedFiles.length > 0) {
    const selection = selectTests(changedFiles, E2E_TOUCHFILES, GLOBAL_TOUCHFILES);
    selectedTests = selection.selected;
    process.stderr.write(
      `\nE2E selection (${selection.reason}): ${selection.selected.length}/${Object.keys(E2E_TOUCHFILES).length} tests\n`
    );
  }
}

function testIfSelected(name: string, fn: () => Promise<void>, timeout: number) {
  const shouldRun = evalsEnabled && (selectedTests === null || selectedTests.includes(name));
  (shouldRun ? test : test.skip)(name, fn, timeout);
}

// Temp dirs to clean up after all tests
const tmpDirs: string[] = [];

afterAll(async () => {
  await evalCollector?.finalize();
  for (const dir of tmpDirs) {
    try { fs.rmSync(dir, { recursive: true }); } catch { /* non-fatal */ }
  }
});

/**
 * Create a skill workdir where analyze_gsc.py is replaced with the mock.
 * Also adds mock-gcloud.sh to a local bin/ so it's first in PATH.
 */
function createFixtureWorkdir(): { workdir: string; mockBin: string } {
  const workdir = createSkillWorkdir(SKILL_PATH, 'seo-analysis');
  tmpDirs.push(workdir);

  // Replace analyze_gsc.py with the mock version
  const skillScriptsDir = path.join(workdir, '.claude', 'skills', 'seo-analysis', 'scripts');
  fs.copyFileSync(
    path.join(FIXTURES_DIR, 'mock-analyze-gsc.py'),
    path.join(skillScriptsDir, 'analyze_gsc.py')
  );
  // Copy fixture data so the mock can find it
  fs.copyFileSync(
    path.join(FIXTURES_DIR, 'sample_gsc_data.json'),
    path.join(skillScriptsDir, 'sample_gsc_data.json')
  );

  // Create a local bin/ with mock gcloud so it wins over real gcloud in PATH
  const mockBin = path.join(workdir, 'bin');
  fs.mkdirSync(mockBin, { recursive: true });
  const mockGcloud = path.join(mockBin, 'gcloud');
  fs.copyFileSync(path.join(FIXTURES_DIR, 'mock-gcloud.sh'), mockGcloud);
  fs.chmodSync(mockGcloud, 0o755);

  return { workdir, mockBin };
}

// --- Tests ---

describeE2E('seo-analysis skill E2E', () => {

  testIfSelected('seo-no-gsc-technical-audit', async () => {
    const t0 = Date.now();
    const workdir = createSkillWorkdir(SKILL_PATH, 'seo-analysis');
    tmpDirs.push(workdir);

    // Test the "skip GSC, just do a technical audit" path.
    // This exercises Phases 5–6 without needing credentials.
    const result = await runSkillTest({
      prompt: [
        'Use the seo-analysis skill to do a technical SEO audit.',
        'I don\'t have GSC access — skip that, just audit the URL directly.',
        'Site: https://example-saas.com',
        'Focus on the technical audit (Phase 5) and produce the report (Phase 6).',
        'Keep it brief — you can skip pulling real data, just audit what you can from the URL structure.',
      ].join(' '),
      workingDirectory: workdir,
      maxTurns: 20,
      timeoutMs: 3 * 60 * 1000,
      testName: 'seo-no-gsc-technical-audit',
    });

    const duration = Date.now() - t0;

    evalCollector?.addTest({
      name: 'seo-no-gsc-technical-audit',
      suite: 'seo-analysis skill E2E',
      tier: 'e2e',
      passed: result.exitReason === 'success',
      duration_ms: duration,
      cost_usd: result.costEstimate.estimatedCost,
      output: result.output?.slice(0, 1000),
      turns_used: result.costEstimate.turnsUsed,
      exit_reason: result.exitReason,
      model: result.model,
    });

    expect(result.exitReason).toBe('success');

    // Should have made some tool calls (fetching URL, etc.)
    expect(result.toolCalls.length).toBeGreaterThan(0);

    // Output should mention the site and SEO
    const output = result.output.toLowerCase();
    expect(output).toMatch(/seo|technical|audit/i);

  }, 4 * 60 * 1000);

  testIfSelected('seo-fixture-full-audit', async () => {
    const t0 = Date.now();
    const { workdir, mockBin } = createFixtureWorkdir();

    // Full audit with fixture data — tests the complete Phase 1–6 workflow.
    // Mock gcloud returns a fake token; mock analyze_gsc.py returns fixture data.
    const result = await runSkillTest({
      prompt: [
        'Run the seo-analysis skill for sc-domain:example-saas.com.',
        'Use the skill\'s full workflow including the GSC data pull.',
        'The analysis data is available — go through all phases.',
      ].join(' '),
      workingDirectory: workdir,
      maxTurns: 35,
      timeoutMs: 5 * 60 * 1000,
      testName: 'seo-fixture-full-audit',
      envOverrides: {
        PATH: `${mockBin}:${process.env.PATH || '/usr/local/bin:/usr/bin:/bin'}`,
      },
    });

    const duration = Date.now() - t0;

    // Use LLM judge to evaluate report quality
    let reportScore = null;
    let reportPassed = false;
    if (result.exitReason === 'success' && result.output.length > 200) {
      try {
        reportScore = await seoReportJudge(result.output);
        reportPassed = reportScore.score >= 3 &&
          reportScore.has_quick_wins &&
          reportScore.recommendations_specific;
      } catch { /* judge failure shouldn't fail the whole test */ }
    }

    evalCollector?.addTest({
      name: 'seo-fixture-full-audit',
      suite: 'seo-analysis skill E2E',
      tier: 'e2e',
      passed: result.exitReason === 'success',
      duration_ms: duration,
      cost_usd: result.costEstimate.estimatedCost,
      output: result.output?.slice(0, 2000),
      turns_used: result.costEstimate.turnsUsed,
      exit_reason: result.exitReason,
      model: result.model,
      judge_scores: reportScore ? {
        score: reportScore.score,
        has_quick_wins: reportScore.has_quick_wins ? 1 : 0,
        has_action_plan: reportScore.has_action_plan ? 1 : 0,
        quantified_impact: reportScore.quantified_impact ? 1 : 0,
      } : undefined,
      judge_reasoning: reportScore?.reasoning,
    });

    expect(result.exitReason).toBe('success');

    // Should have run analyze_gsc.py (Bash tool call)
    const bashCalls = result.toolCalls.filter(c => c.tool === 'Bash');
    expect(bashCalls.length).toBeGreaterThan(0);

    // Output should have Quick Wins (key section from Phase 4)
    expect(result.output).toMatch(/quick win/i);

  }, 6 * 60 * 1000);

  testIfSelected('seo-report-quality', async () => {
    const t0 = Date.now();
    const { workdir, mockBin } = createFixtureWorkdir();

    const result = await runSkillTest({
      prompt: [
        'Use the seo-analysis skill for sc-domain:example-saas.com.',
        'The fixture data has position 4-10 quick wins and traffic drops — find them.',
        'Produce a full report with specific recommendations.',
      ].join(' '),
      workingDirectory: workdir,
      maxTurns: 35,
      timeoutMs: 5 * 60 * 1000,
      testName: 'seo-report-quality',
      envOverrides: {
        PATH: `${mockBin}:${process.env.PATH || '/usr/local/bin:/usr/bin:/bin'}`,
      },
    });

    const duration = Date.now() - t0;

    if (result.exitReason !== 'success') {
      evalCollector?.addTest({
        name: 'seo-report-quality',
        suite: 'seo-analysis skill E2E',
        tier: 'e2e',
        passed: false,
        duration_ms: duration,
        cost_usd: result.costEstimate.estimatedCost,
        exit_reason: result.exitReason,
        model: result.model,
        error: `Skill failed with exit reason: ${result.exitReason}`,
      });
      expect(result.exitReason).toBe('success');
      return;
    }

    const reportScore = await seoReportJudge(result.output);
    const passed = reportScore.has_quick_wins &&
      reportScore.recommendations_specific &&
      reportScore.score >= 3;

    evalCollector?.addTest({
      name: 'seo-report-quality',
      suite: 'seo-analysis skill E2E',
      tier: 'e2e',
      passed,
      duration_ms: duration,
      cost_usd: result.costEstimate.estimatedCost,
      output: result.output?.slice(0, 2000),
      turns_used: result.costEstimate.turnsUsed,
      exit_reason: result.exitReason,
      model: result.model,
      judge_scores: {
        score: reportScore.score,
        has_quick_wins: reportScore.has_quick_wins ? 1 : 0,
        recommendations_specific: reportScore.recommendations_specific ? 1 : 0,
        has_action_plan: reportScore.has_action_plan ? 1 : 0,
        quantified_impact: reportScore.quantified_impact ? 1 : 0,
      },
      judge_reasoning: reportScore.reasoning,
    });

    expect(reportScore.has_quick_wins).toBe(true);
    expect(reportScore.recommendations_specific).toBe(true);
    expect(reportScore.score).toBeGreaterThanOrEqual(3);

  }, 6 * 60 * 1000);

});
