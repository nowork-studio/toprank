/**
 * LLM-as-a-Judge evals for seo-analysis SKILL.md quality.
 *
 * Uses the Anthropic API to evaluate whether SKILL.md sections are
 * clear, complete, and actionable for an AI agent following them.
 *
 * Guards against regressions — if someone edits SKILL.md in a way that
 * makes instructions ambiguous, these tests will catch it.
 *
 * Run: EVALS=1 bun test test/skill-llm-eval.test.ts
 * Cost: ~$0.05 per run
 */

import { describe, test, expect, afterAll } from 'bun:test';
import * as fs from 'fs';
import * as path from 'path';
import { judge } from './helpers/llm-judge';
import type { JudgeScore } from './helpers/llm-judge';
import { EvalCollector } from './helpers/eval-store';
import {
  selectTests,
  detectBaseBranch,
  getChangedFiles,
  LLM_JUDGE_TOUCHFILES,
  GLOBAL_TOUCHFILES,
} from './helpers/touchfiles';

const ROOT = path.resolve(import.meta.dir, '..');
const SKILL_MD = path.join(ROOT, 'seo-analysis', 'SKILL.md');

const evalsEnabled = !!process.env.EVALS;
const describeEval = evalsEnabled ? describe : describe.skip;

const evalCollector = evalsEnabled ? new EvalCollector('llm-judge') : null;

// Diff-based selection
let selectedTests: string[] | null = null;
if (evalsEnabled && !process.env.EVALS_ALL) {
  const baseBranch = process.env.EVALS_BASE || detectBaseBranch(ROOT) || 'main';
  const changedFiles = getChangedFiles(baseBranch, ROOT);
  if (changedFiles.length > 0) {
    const selection = selectTests(changedFiles, LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES);
    selectedTests = selection.selected;
    process.stderr.write(
      `\nLLM-judge selection (${selection.reason}): ${selection.selected.length}/${Object.keys(LLM_JUDGE_TOUCHFILES).length} tests\n`
    );
  }
}

function testIfSelected(name: string, fn: () => Promise<void>, timeout: number) {
  const shouldRun = evalsEnabled && (selectedTests === null || selectedTests.includes(name));
  (shouldRun ? test : test.skip)(name, fn, timeout);
}

// Read SKILL.md once
let skillMd = '';
if (evalsEnabled) {
  skillMd = fs.readFileSync(SKILL_MD, 'utf-8');
}

// --- Helpers to extract named sections ---

function extractSection(md: string, startMarker: string, endMarker?: string): string {
  const start = md.indexOf(startMarker);
  if (start === -1) return '';
  const end = endMarker ? md.indexOf(endMarker, start + startMarker.length) : md.length;
  return md.slice(start, end === -1 ? undefined : end).trim();
}

// --- Tests ---

describeEval('seo-analysis SKILL.md quality', () => {

  testIfSelected('seo-phases-clarity', async () => {
    const t0 = Date.now();
    // Phases 1–3 describe what Claude should do before analysis starts
    const phases = extractSection(skillMd, '## Phase 1', '## Phase 4');
    expect(phases.length).toBeGreaterThan(100);

    const scores = await judge('Phase 1–3 (setup & data collection)', phases);
    console.log('Phases 1-3 scores:', JSON.stringify(scores, null, 2));

    evalCollector?.addTest({
      name: 'seo-phases-clarity',
      suite: 'seo-analysis SKILL.md quality',
      tier: 'llm-judge',
      passed: scores.clarity >= 4 && scores.completeness >= 4 && scores.actionability >= 4,
      duration_ms: Date.now() - t0,
      cost_usd: 0.02,
      judge_scores: { clarity: scores.clarity, completeness: scores.completeness, actionability: scores.actionability },
      judge_reasoning: scores.reasoning,
    });

    expect(scores.clarity).toBeGreaterThanOrEqual(4);
    expect(scores.completeness).toBeGreaterThanOrEqual(4);
    expect(scores.actionability).toBeGreaterThanOrEqual(4);
  }, 30_000);

  testIfSelected('seo-quick-wins-clarity', async () => {
    const t0 = Date.now();
    // The Quick Wins section is the highest-value part — must be crystal clear
    const section = extractSection(skillMd, '### Quick Wins', '### Search Intent');
    expect(section.length).toBeGreaterThan(50);

    const scores = await judge('Quick Wins analysis instructions', section);
    console.log('Quick Wins scores:', JSON.stringify(scores, null, 2));

    evalCollector?.addTest({
      name: 'seo-quick-wins-clarity',
      suite: 'seo-analysis SKILL.md quality',
      tier: 'llm-judge',
      passed: scores.clarity >= 4 && scores.completeness >= 4 && scores.actionability >= 4,
      duration_ms: Date.now() - t0,
      cost_usd: 0.02,
      judge_scores: { clarity: scores.clarity, completeness: scores.completeness, actionability: scores.actionability },
      judge_reasoning: scores.reasoning,
    });

    expect(scores.clarity).toBeGreaterThanOrEqual(4);
    expect(scores.completeness).toBeGreaterThanOrEqual(4);
    expect(scores.actionability).toBeGreaterThanOrEqual(4);
  }, 30_000);

  testIfSelected('seo-report-format-clarity', async () => {
    const t0 = Date.now();
    // The report format section defines the exact output structure
    const section = extractSection(skillMd, '## Phase 6', '');
    expect(section.length).toBeGreaterThan(100);

    const scores = await judge('Phase 6 report format', section);
    console.log('Report format scores:', JSON.stringify(scores, null, 2));

    evalCollector?.addTest({
      name: 'seo-report-format-clarity',
      suite: 'seo-analysis SKILL.md quality',
      tier: 'llm-judge',
      passed: scores.clarity >= 4 && scores.completeness >= 3 && scores.actionability >= 4,
      duration_ms: Date.now() - t0,
      cost_usd: 0.02,
      judge_scores: { clarity: scores.clarity, completeness: scores.completeness, actionability: scores.actionability },
      judge_reasoning: scores.reasoning,
    });

    expect(scores.clarity).toBeGreaterThanOrEqual(4);
    expect(scores.completeness).toBeGreaterThanOrEqual(3);
    expect(scores.actionability).toBeGreaterThanOrEqual(4);
  }, 30_000);

  afterAll(async () => {
    await evalCollector?.finalize();
  });
});
