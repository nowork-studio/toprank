"""
Diff-based test selection.

Each test declares which files it depends on. If none of those files
changed relative to the base branch, the test is skipped.
Set EVALS_ALL=1 to run everything regardless of diffs.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional

E2E_TOUCHFILES: dict[str, list[str]] = {
    'seo-no-gsc-technical-audit': ['skills/seo-analysis/**'],
    'seo-fixture-full-audit':     ['skills/seo-analysis/**', 'test/fixtures/sample_gsc_data.json'],
    'seo-report-quality':         ['skills/seo-analysis/**', 'test/fixtures/sample_gsc_data.json'],
}

LLM_JUDGE_TOUCHFILES: dict[str, list[str]] = {
    'seo-phases-clarity':        ['skills/seo-analysis/SKILL.md'],
    'seo-report-format-clarity': ['skills/seo-analysis/SKILL.md'],
    'seo-quick-wins-clarity':    ['skills/seo-analysis/SKILL.md'],
}

ADS_LLM_JUDGE_TOUCHFILES: dict[str, list[str]] = {
    'ads-heuristics-clarity':    ['skills/ads/SKILL.md', 'skills/ads/references/**'],
    'ads-workflows-clarity':     ['skills/ads/SKILL.md'],
    'ads-audit-scoring-clarity': ['skills/ads-audit/SKILL.md', 'skills/ads-audit/references/**'],
    'ads-audit-report-clarity':  ['skills/ads-audit/SKILL.md'],
    'ads-copy-formulas-clarity': ['skills/ads-copy/SKILL.md', 'skills/ads-copy/references/**'],
}

ROUTING_TOUCHFILES: dict[str, list[str]] = {
    'routing-seo-triggers':     ['skills/seo-analysis/SKILL.md'],
    'routing-seo-non-triggers': ['skills/seo-analysis/SKILL.md'],
}

# Changes to these files trigger all tests
GLOBAL_TOUCHFILES = ['test/helpers/**']


def detect_base_branch(repo_root: str) -> Optional[str]:
    for branch in ('main', 'master', 'develop'):
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', branch],
            cwd=repo_root, capture_output=True, timeout=3,
        )
        if result.returncode == 0:
            return branch
    return None


def get_changed_files(base_branch: str, repo_root: str) -> list[str]:
    result = subprocess.run(
        ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
        cwd=repo_root, capture_output=True, text=True, timeout=5,
    )
    if result.returncode != 0:
        return []
    return [f for f in result.stdout.strip().split('\n') if f]


def match_glob(file: str, pattern: str) -> bool:
    regex = (
        pattern
        .replace('.', r'\.')
        .replace('**', '\x00')
        .replace('*', '[^/]*')
        .replace('\x00', '.*')
    )
    return bool(re.fullmatch(regex, file))


def select_tests(
    changed_files: list[str],
    touchfile_map: dict[str, list[str]],
    global_touchfiles: list[str],
) -> dict:
    """Returns {'selected': [...], 'skipped': [...], 'reason': '...'}"""
    # If any global file changed, run all tests
    if any(match_glob(f, g) for f in changed_files for g in global_touchfiles):
        return {
            'selected': list(touchfile_map.keys()),
            'skipped': [],
            'reason': 'global touchfile changed',
        }

    selected, skipped = [], []
    for test_name, patterns in touchfile_map.items():
        if any(match_glob(f, p) for f in changed_files for p in patterns):
            selected.append(test_name)
        else:
            skipped.append(test_name)

    return {'selected': selected, 'skipped': skipped, 'reason': 'diff-based selection'}
