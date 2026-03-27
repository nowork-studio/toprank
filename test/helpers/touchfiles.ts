/**
 * Diff-based test selection.
 *
 * Each test declares which files it depends on. If none of those files
 * changed relative to the base branch, the test is skipped.
 * Set EVALS_ALL=1 to run everything regardless of diffs.
 */

import { spawnSync } from 'child_process';

/**
 * Map test names → file glob patterns they depend on.
 * Tests are skipped unless at least one of their touchfiles changed.
 */
export const E2E_TOUCHFILES: Record<string, string[]> = {
  // seo-analysis skill E2E tests
  'seo-no-gsc-technical-audit': ['seo-analysis/**'],
  'seo-fixture-full-audit':     ['seo-analysis/**', 'test/fixtures/sample_gsc_data.json'],
  'seo-report-quality':         ['seo-analysis/**', 'test/fixtures/sample_gsc_data.json'],
};

export const LLM_JUDGE_TOUCHFILES: Record<string, string[]> = {
  'seo-phases-clarity':         ['seo-analysis/SKILL.md'],
  'seo-report-format-clarity':  ['seo-analysis/SKILL.md'],
  'seo-quick-wins-clarity':     ['seo-analysis/SKILL.md'],
};

export const ROUTING_TOUCHFILES: Record<string, string[]> = {
  'routing-seo-triggers':       ['seo-analysis/SKILL.md'],
  'routing-seo-non-triggers':   ['seo-analysis/SKILL.md'],
};

// Files that affect all tests (changes here → run everything)
export const GLOBAL_TOUCHFILES = [
  'test/helpers/**',
];

// --- Diff helpers ---

export function detectBaseBranch(repoRoot: string): string | null {
  const candidates = ['main', 'master', 'develop'];
  for (const branch of candidates) {
    const result = spawnSync('git', ['rev-parse', '--verify', branch], {
      cwd: repoRoot, stdio: 'pipe', timeout: 3000,
    });
    if (result.status === 0) return branch;
  }
  return null;
}

export function getChangedFiles(baseBranch: string, repoRoot: string): string[] {
  const result = spawnSync('git', ['diff', '--name-only', `${baseBranch}...HEAD`], {
    cwd: repoRoot, stdio: 'pipe', timeout: 5000,
  });
  if (result.status !== 0) return [];
  return result.stdout.toString().trim().split('\n').filter(Boolean);
}

export function matchGlob(file: string, pattern: string): boolean {
  const regex = new RegExp(
    '^' +
    pattern
      .replace(/\./g, '\\.')
      .replace(/\*\*/g, '{{GLOBSTAR}}')
      .replace(/\*/g, '[^/]*')
      .replace(/\{\{GLOBSTAR\}\}/g, '.*') +
    '$'
  );
  return regex.test(file);
}

export function selectTests(
  changedFiles: string[],
  touchfileMap: Record<string, string[]>,
  globalTouchfiles: string[],
): { selected: string[]; skipped: string[]; reason: string } {
  // If any global file changed, run all tests
  const globalChanged = changedFiles.some(f =>
    globalTouchfiles.some(g => matchGlob(f, g))
  );
  if (globalChanged) {
    return {
      selected: Object.keys(touchfileMap),
      skipped: [],
      reason: 'global touchfile changed',
    };
  }

  const selected: string[] = [];
  const skipped: string[] = [];

  for (const [testName, patterns] of Object.entries(touchfileMap)) {
    const touched = changedFiles.some(f => patterns.some(p => matchGlob(f, p)));
    if (touched) {
      selected.push(testName);
    } else {
      skipped.push(testName);
    }
  }

  return { selected, skipped, reason: 'diff-based selection' };
}
