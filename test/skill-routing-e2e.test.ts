/**
 * Routing E2E tests — does the seo-analysis skill trigger on the right prompts?
 *
 * Tests that Claude correctly decides to invoke the seo-analysis skill for
 * SEO-related queries, and doesn't invoke it for unrelated queries.
 *
 * This catches skill description regressions: if someone edits the description
 * in a way that makes it over- or under-trigger, these tests will flag it.
 *
 * Run: EVALS=1 bun test test/skill-routing-e2e.test.ts
 */

import { describe, test, expect, afterAll } from 'bun:test';
import { runSkillTest, createSkillWorkdir } from './helpers/session-runner';
import { EvalCollector } from './helpers/eval-store';
import {
  selectTests,
  detectBaseBranch,
  getChangedFiles,
  ROUTING_TOUCHFILES,
  GLOBAL_TOUCHFILES,
} from './helpers/touchfiles';
import * as fs from 'fs';
import * as path from 'path';

const ROOT = path.resolve(import.meta.dir, '..');
const SKILL_PATH = path.join(ROOT, 'seo-analysis');

const evalsEnabled = !!process.env.EVALS;
const describeE2E = evalsEnabled ? describe : describe.skip;

const evalCollector = evalsEnabled ? new EvalCollector('routing') : null;

// Diff-based selection
let selectedTests: string[] | null = null;
if (evalsEnabled && !process.env.EVALS_ALL) {
  const baseBranch = process.env.EVALS_BASE || detectBaseBranch(ROOT) || 'main';
  const changedFiles = getChangedFiles(baseBranch, ROOT);
  if (changedFiles.length > 0) {
    const selection = selectTests(changedFiles, ROUTING_TOUCHFILES, GLOBAL_TOUCHFILES);
    selectedTests = selection.selected;
    process.stderr.write(
      `\nRouting E2E selection (${selection.reason}): ${selection.selected.length}/${Object.keys(ROUTING_TOUCHFILES).length} tests\n`
    );
  }
}

function testIfSelected(name: string, fn: () => Promise<void>, timeout: number) {
  const shouldRun = evalsEnabled && (selectedTests === null || selectedTests.includes(name));
  (shouldRun ? test : test.skip)(name, fn, timeout);
}

const tmpDirs: string[] = [];

afterAll(async () => {
  await evalCollector?.finalize();
  for (const dir of tmpDirs) {
    try { fs.rmSync(dir, { recursive: true }); } catch { /* non-fatal */ }
  }
});

// Detect whether a result used the skill by looking for skill-specific behavior.
// The skill always starts with a gcloud check or site identification — we look
// for those markers in the output or tool calls.
function didUseSeoSkill(result: { output: string; toolCalls: Array<{ tool: string; input: any }> }): boolean {
  const outputLower = result.output.toLowerCase();

  // Skill-specific phrases that only appear when following SKILL.md
  const skillMarkers = [
    'phase 1', 'phase 2', 'phase 3',
    'google search console',
    'quick wins',
    'position 4',
    'gcloud',
    'analyze_gsc',
    'sc-domain:',
  ];

  if (skillMarkers.some(m => outputLower.includes(m))) return true;

  // Skill runs analyze_gsc.py via Bash
  const ranGscScript = result.toolCalls.some(
    c => c.tool === 'Bash' && JSON.stringify(c.input).includes('analyze_gsc')
  );
  if (ranGscScript) return true;

  return false;
}

// --- Prompts that should trigger seo-analysis ---

const SHOULD_TRIGGER = [
  {
    name: 'traffic-drop-question',
    prompt: "My website traffic dropped 40% last month and I don't know why. I'm getting way fewer clicks from Google. Can you figure out what happened?",
  },
  {
    name: 'seo-audit-explicit',
    prompt: "Can you run an SEO audit on my site? I want to know what's hurting my Google rankings.",
  },
  {
    name: 'keyword-rankings',
    prompt: "What keywords am I ranking for in Google? I want to see which queries are bringing traffic to my site.",
  },
  {
    name: 'search-console-analysis',
    prompt: "I have Google Search Console connected. Can you pull my search data and tell me what opportunities I'm missing?",
  },
  {
    name: 'improve-organic-traffic',
    prompt: "I need to improve my organic search traffic. Where should I focus first to get more clicks from Google?",
  },
];

// --- Prompts that should NOT trigger seo-analysis ---

const SHOULD_NOT_TRIGGER = [
  {
    name: 'css-debugging',
    prompt: "My CSS grid layout is broken on mobile — the columns aren't stacking correctly. Can you help me debug it?",
  },
  {
    name: 'python-refactoring',
    prompt: "I need to refactor this Python function to be more efficient. It's currently O(n²) and I need it to be O(n log n).",
  },
  {
    name: 'google-ads-performance',
    prompt: "My Google Ads CPA jumped from $12 to $28 this week. What happened and how do I fix it?",
  },
  {
    name: 'content-writing',
    prompt: "Can you write a blog post about the benefits of using project management software for remote teams?",
  },
  {
    name: 'database-query',
    prompt: "This SQL query is timing out — it's taking 8 seconds on a 2M row table. Can you optimize it?",
  },
];

// --- Test runner ---

async function runRoutingTest(
  promptConfig: { name: string; prompt: string },
  shouldTrigger: boolean,
): Promise<void> {
  const workdir = createSkillWorkdir(SKILL_PATH, 'seo-analysis');
  tmpDirs.push(workdir);

  const result = await runSkillTest({
    prompt: promptConfig.prompt,
    workingDirectory: workdir,
    maxTurns: 8, // Routing tests are short — just need to see initial response
    timeoutMs: 90 * 1000,
    testName: promptConfig.name,
  });

  const triggered = didUseSeoSkill(result);
  const passed = shouldTrigger ? triggered : !triggered;
  const t = shouldTrigger ? 'SHOULD' : 'SHOULD NOT';

  if (!passed) {
    console.error(
      `ROUTING FAIL: "${promptConfig.name}" ${t} have triggered seo-analysis but ${triggered ? 'DID' : 'DID NOT'}`
    );
    console.error(`Output snippet: ${result.output.slice(0, 300)}`);
  }

  evalCollector?.addTest({
    name: promptConfig.name,
    suite: shouldTrigger ? 'should-trigger' : 'should-not-trigger',
    tier: 'routing',
    passed,
    duration_ms: result.duration,
    cost_usd: result.costEstimate.estimatedCost,
    should_trigger: shouldTrigger,
    did_trigger: triggered,
    exit_reason: result.exitReason,
    model: result.model,
    output: result.output?.slice(0, 500),
  });

  expect(triggered).toBe(shouldTrigger);
}

// --- Test suites ---

describeE2E('seo-analysis routing — should trigger', () => {

  testIfSelected('routing-seo-triggers', async () => {
    // Run should-trigger cases sequentially to avoid rate limits
    for (const p of SHOULD_TRIGGER) {
      await runRoutingTest(p, true);
    }
  }, 10 * 60 * 1000);

});

describeE2E('seo-analysis routing — should not trigger', () => {

  testIfSelected('routing-seo-non-triggers', async () => {
    for (const p of SHOULD_NOT_TRIGGER) {
      await runRoutingTest(p, false);
    }
  }, 10 * 60 * 1000);

});
