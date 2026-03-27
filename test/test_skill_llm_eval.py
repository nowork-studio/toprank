"""
LLM-as-a-Judge evals for seo-analysis SKILL.md quality.

Guards against regressions — if someone edits SKILL.md in a way that
makes instructions ambiguous, these tests will catch it.

Run: EVALS=1 pytest test/test_skill_llm_eval.py
Cost: ~$0.05 per run
"""

import os
import sys
import time
from pathlib import Path

import pytest

from helpers.llm_judge import judge
from helpers.eval_store import EvalCollector, EvalTestEntry
from helpers.touchfiles import (
    select_tests, detect_base_branch, get_changed_files,
    LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES,
)

ROOT = Path(__file__).parent.parent
SKILL_MD = ROOT / 'seo-analysis' / 'SKILL.md'

EVALS = bool(os.environ.get('EVALS'))
pytestmark = pytest.mark.skipif(not EVALS, reason='Set EVALS=1 to run LLM-judge evals')

# Diff-based selection
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


def _should_run(name: str) -> bool:
    return EVALS and (_selected is None or name in _selected)


_skill_md = SKILL_MD.read_text() if EVALS else ''
_collector = EvalCollector('llm-judge') if EVALS else None


def _extract_section(md: str, start_marker: str, end_marker: str = '') -> str:
    start = md.find(start_marker)
    if start == -1:
        return ''
    if end_marker:
        end = md.find(end_marker, start + len(start_marker))
        return md[start:end].strip() if end != -1 else md[start:].strip()
    return md[start:].strip()


@pytest.mark.skipif(not _should_run('seo-phases-clarity'), reason='not selected')
def test_seo_phases_clarity():
    t0 = time.time()
    section = _extract_section(_skill_md, '## Phase 1', '## Phase 4')
    assert len(section) > 100

    scores = judge('Phase 1–3 (setup & data collection)', section)
    print('Phases 1-3 scores:', scores)

    if _collector:
        _collector.add_test(EvalTestEntry(
            name='seo-phases-clarity',
            suite='seo-analysis SKILL.md quality',
            tier='llm-judge',
            passed=scores.clarity >= 4 and scores.completeness >= 4 and scores.actionability >= 4,
            duration_ms=int((time.time() - t0) * 1000),
            cost_usd=0.02,
            judge_scores={'clarity': scores.clarity, 'completeness': scores.completeness, 'actionability': scores.actionability},
            judge_reasoning=scores.reasoning,
        ))

    assert scores.clarity >= 4
    assert scores.completeness >= 4
    assert scores.actionability >= 4


@pytest.mark.skipif(not _should_run('seo-quick-wins-clarity'), reason='not selected')
def test_seo_quick_wins_clarity():
    t0 = time.time()
    section = _extract_section(_skill_md, '### Quick Wins', '### Search Intent')
    assert len(section) > 50

    scores = judge('Quick Wins analysis instructions', section)
    print('Quick Wins scores:', scores)

    if _collector:
        _collector.add_test(EvalTestEntry(
            name='seo-quick-wins-clarity',
            suite='seo-analysis SKILL.md quality',
            tier='llm-judge',
            passed=scores.clarity >= 4 and scores.completeness >= 4 and scores.actionability >= 4,
            duration_ms=int((time.time() - t0) * 1000),
            cost_usd=0.02,
            judge_scores={'clarity': scores.clarity, 'completeness': scores.completeness, 'actionability': scores.actionability},
            judge_reasoning=scores.reasoning,
        ))

    assert scores.clarity >= 4
    assert scores.completeness >= 4
    assert scores.actionability >= 4


@pytest.mark.skipif(not _should_run('seo-report-format-clarity'), reason='not selected')
def test_seo_report_format_clarity():
    t0 = time.time()
    section = _extract_section(_skill_md, '## Phase 6')
    assert len(section) > 100

    scores = judge('Phase 6 report format', section)
    print('Report format scores:', scores)

    if _collector:
        _collector.add_test(EvalTestEntry(
            name='seo-report-format-clarity',
            suite='seo-analysis SKILL.md quality',
            tier='llm-judge',
            passed=scores.clarity >= 4 and scores.completeness >= 3 and scores.actionability >= 4,
            duration_ms=int((time.time() - t0) * 1000),
            cost_usd=0.02,
            judge_scores={'clarity': scores.clarity, 'completeness': scores.completeness, 'actionability': scores.actionability},
            judge_reasoning=scores.reasoning,
        ))

    assert scores.clarity >= 4
    assert scores.completeness >= 3
    assert scores.actionability >= 4


def teardown_module(module):
    if _collector:
        _collector.finalize()
