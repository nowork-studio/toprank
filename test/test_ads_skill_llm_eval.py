"""
LLM-as-a-Judge evals for Google Ads SKILL.md quality.

Run: EVALS=1 pytest test/test_ads_skill_llm_eval.py -v
Cost: ~$0.10 per run (Gemini Flash)
"""

import os
import sys
from pathlib import Path

import pytest

from helpers.llm_judge import extract_section, run_judge_test
from helpers.eval_store import EvalCollector
from helpers.touchfiles import (
    select_tests, detect_base_branch, get_changed_files,
    ADS_LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES,
)

ROOT = Path(__file__).parent.parent
ADS_SKILL = ROOT / 'skills' / 'ads' / 'SKILL.md'
AUDIT_SKILL = ROOT / 'skills' / 'ads-audit' / 'SKILL.md'
COPY_SKILL = ROOT / 'skills' / 'ads-copy' / 'SKILL.md'

EVALS = bool(os.environ.get('EVALS'))
pytestmark = pytest.mark.skipif(not EVALS, reason='Set EVALS=1 to run LLM-judge evals')

_selected: list[str] | None = None
if EVALS and not os.environ.get('EVALS_ALL'):
    _base = os.environ.get('EVALS_BASE') or detect_base_branch(str(ROOT)) or 'main'
    _changed = get_changed_files(_base, str(ROOT))
    if _changed:
        _sel = select_tests(_changed, ADS_LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES)
        _selected = _sel['selected']
        print(
            f"\nAds LLM-judge selection ({_sel['reason']}): "
            f"{len(_selected)}/{len(ADS_LLM_JUDGE_TOUCHFILES)} tests",
            file=sys.stderr,
        )

_ads_md = ADS_SKILL.read_text() if EVALS else ''
_audit_md = AUDIT_SKILL.read_text() if EVALS else ''
_copy_md = COPY_SKILL.read_text() if EVALS else ''
_collector = EvalCollector('ads-llm-judge') if EVALS else None

SUITE = 'Google Ads SKILL.md quality'


def _skip(name: str) -> bool:
    return not EVALS or (_selected is not None and name not in _selected)


@pytest.mark.skipif(_skip('ads-heuristics-clarity'), reason='not selected')
def test_ads_heuristics_clarity():
    run_judge_test('ads-heuristics-clarity', SUITE,
        'Google Ads analysis heuristics (numeric thresholds for QS, bids, keywords, impression share)',
        extract_section(_ads_md, '## Analysis Heuristics', '## Wasted Spend'),
        _collector)


@pytest.mark.skipif(_skip('ads-workflows-clarity'), reason='not selected')
def test_ads_workflows_clarity():
    run_judge_test('ads-workflows-clarity', SUITE,
        'Google Ads common workflows (step-by-step optimization procedures)',
        extract_section(_ads_md, '## Common Workflows', '## Report Template'),
        _collector)


@pytest.mark.skipif(_skip('ads-audit-scoring-clarity'), reason='not selected')
def test_ads_audit_scoring_clarity():
    run_judge_test('ads-audit-scoring-clarity', SUITE,
        'Google Ads audit scoring rubric (7 health dimensions with 0-5 numeric scores)',
        extract_section(_audit_md, '## Phase 2: Analyze and Score', '## Phase 2.5'),
        _collector)


@pytest.mark.skipif(_skip('ads-audit-report-clarity'), reason='not selected')
def test_ads_audit_report_clarity():
    run_judge_test('ads-audit-report-clarity', SUITE,
        'Google Ads audit report format (scorecard, health score, wasted spend, actions)',
        extract_section(_audit_md, '## Phase 4: Deliver the Audit Report', '## Conditional Handoffs'),
        _collector, min_completeness=3)


@pytest.mark.skipif(_skip('ads-copy-formulas-clarity'), reason='not selected')
def test_ads_copy_formulas_clarity():
    run_judge_test('ads-copy-formulas-clarity', SUITE,
        'Google Ads RSA copy formulas (headline templates, description templates, character counts, pinning)',
        extract_section(_copy_md, '## Workflow', '## Rules'),
        _collector)


def teardown_module(module):
    if _collector:
        _collector.finalize()
