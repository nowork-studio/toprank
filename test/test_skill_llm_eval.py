"""
LLM-as-a-Judge evals for seo-analysis SKILL.md quality.

Run: EVALS=1 pytest test/test_skill_llm_eval.py
Cost: ~$0.05 per run (Gemini Flash)
"""

import os
import sys
from pathlib import Path

import pytest

from helpers.llm_judge import extract_section, run_judge_test
from helpers.eval_store import EvalCollector
from helpers.touchfiles import (
    select_tests, detect_base_branch, get_changed_files,
    LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES,
)

ROOT = Path(__file__).parent.parent
SKILL_MD = ROOT / 'skills' / 'seo-analysis' / 'SKILL.md'

EVALS = bool(os.environ.get('EVALS'))
pytestmark = pytest.mark.skipif(not EVALS, reason='Set EVALS=1 to run LLM-judge evals')

_selected: list[str] | None = None
if EVALS and not os.environ.get('EVALS_ALL'):
    _base = os.environ.get('EVALS_BASE') or detect_base_branch(str(ROOT)) or 'main'
    _changed = get_changed_files(_base, str(ROOT))
    if _changed:
        _sel = select_tests(_changed, LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES)
        _selected = _sel['selected']
        print(
            f"\nLLM-judge selection ({_sel['reason']}): "
            f"{len(_selected)}/{len(LLM_JUDGE_TOUCHFILES)} tests",
            file=sys.stderr,
        )

_skill_md = SKILL_MD.read_text() if EVALS else ''
_collector = EvalCollector('llm-judge') if EVALS else None

SUITE = 'seo-analysis SKILL.md quality'


def _skip(name: str) -> bool:
    return not EVALS or (_selected is not None and name not in _selected)


@pytest.mark.skipif(_skip('seo-phases-clarity'), reason='not selected')
def test_seo_phases_clarity():
    run_judge_test('seo-phases-clarity', SUITE,
        'Phase 1-3 (setup & data collection)',
        extract_section(_skill_md, '## Phase 1', '## Phase 4'),
        _collector)


@pytest.mark.skipif(_skip('seo-quick-wins-clarity'), reason='not selected')
def test_seo_quick_wins_clarity():
    run_judge_test('seo-quick-wins-clarity', SUITE,
        'Quick Wins analysis instructions',
        extract_section(_skill_md, '### Quick Wins', '### Search Intent'),
        _collector)


@pytest.mark.skipif(_skip('seo-report-format-clarity'), reason='not selected')
def test_seo_report_format_clarity():
    run_judge_test('seo-report-format-clarity', SUITE,
        'Phase 6 report format',
        extract_section(_skill_md, '## Phase 6'),
        _collector, min_completeness=3)


def teardown_module(module):
    if _collector:
        _collector.finalize()
