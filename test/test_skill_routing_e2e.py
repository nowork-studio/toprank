"""
Routing E2E tests — does the seo-analysis skill trigger on the right prompts?

Run: EVALS=1 pytest test/test_skill_routing_e2e.py
"""

import os
import shutil
import sys
from pathlib import Path

import pytest

from helpers.session_runner import run_skill_test, create_skill_workdir
from helpers.eval_store import EvalCollector, EvalTestEntry
from helpers.touchfiles import (
    select_tests, detect_base_branch, get_changed_files,
    ROUTING_TOUCHFILES, GLOBAL_TOUCHFILES,
)

ROOT = Path(__file__).parent.parent
SKILL_PATH = ROOT / 'seo-analysis'

EVALS = bool(os.environ.get('EVALS'))
pytestmark = pytest.mark.skipif(not EVALS, reason='Set EVALS=1 to run routing evals')

_selected: list[str] | None = None
if EVALS and not os.environ.get('EVALS_ALL'):
    _base = os.environ.get('EVALS_BASE') or detect_base_branch(str(ROOT)) or 'main'
    _changed = get_changed_files(_base, str(ROOT))
    if _changed:
        _sel = select_tests(_changed, ROUTING_TOUCHFILES, GLOBAL_TOUCHFILES)
        _selected = _sel['selected']
        print(
            f"\nRouting E2E selection ({_sel['reason']}): "
            f"{len(_selected)}/{len(ROUTING_TOUCHFILES)} tests",
            file=sys.stderr,
        )


def _should_run(name: str) -> bool:
    return EVALS and (_selected is None or name in _selected)


_tmp_dirs: list[str] = []
_collector = EvalCollector('routing') if EVALS else None

SHOULD_TRIGGER = [
    {'name': 'traffic-drop-question',
     'prompt': "My website traffic dropped 40% last month and I don't know why. I'm getting way fewer clicks from Google. Can you figure out what happened?"},
    {'name': 'seo-audit-explicit',
     'prompt': "Can you run an SEO audit on my site? I want to know what's hurting my Google rankings."},
    {'name': 'keyword-rankings',
     'prompt': "What keywords am I ranking for in Google? I want to see which queries are bringing traffic to my site."},
    {'name': 'search-console-analysis',
     'prompt': "I have Google Search Console connected. Can you pull my search data and tell me what opportunities I'm missing?"},
    {'name': 'improve-organic-traffic',
     'prompt': "I need to improve my organic search traffic. Where should I focus first to get more clicks from Google?"},
]

SHOULD_NOT_TRIGGER = [
    {'name': 'css-debugging',
     'prompt': "My CSS grid layout is broken on mobile — the columns aren't stacking correctly. Can you help me debug it?"},
    {'name': 'python-refactoring',
     'prompt': "I need to refactor this Python function to be more efficient. It's currently O(n²) and I need it to be O(n log n)."},
    {'name': 'google-ads-performance',
     'prompt': "My Google Ads CPA jumped from $12 to $28 this week. What happened and how do I fix it?"},
    {'name': 'content-writing',
     'prompt': "Can you write a blog post about the benefits of using project management software for remote teams?"},
    {'name': 'database-query',
     'prompt': "This SQL query is timing out — it's taking 8 seconds on a 2M row table. Can you optimize it?"},
]

_SEO_MARKERS = [
    'phase 1', 'phase 2', 'phase 3',
    'google search console',
    'quick wins',
    'position 4',
    'gcloud',
    'analyze_gsc',
    'sc-domain:',
]


def _did_use_seo_skill(result) -> bool:
    if any(m in result.output.lower() for m in _SEO_MARKERS):
        return True
    return any(c.tool == 'Bash' and 'analyze_gsc' in str(c.input) for c in result.tool_calls)


def _run_routing_test(prompt_config: dict, should_trigger: bool) -> None:
    workdir = create_skill_workdir(str(SKILL_PATH), 'seo-analysis')
    _tmp_dirs.append(workdir)

    result = run_skill_test(
        prompt=prompt_config['prompt'],
        working_directory=workdir,
        max_turns=8,
        timeout_ms=90 * 1000,
        test_name=prompt_config['name'],
    )

    triggered = _did_use_seo_skill(result)
    passed = triggered if should_trigger else not triggered
    label = 'SHOULD' if should_trigger else 'SHOULD NOT'

    if not passed:
        print(
            f"ROUTING FAIL: \"{prompt_config['name']}\" {label} have triggered seo-analysis "
            f"but {'DID' if triggered else 'DID NOT'}",
            file=sys.stderr,
        )

    if _collector:
        _collector.add_test(EvalTestEntry(
            name=prompt_config['name'],
            suite='should-trigger' if should_trigger else 'should-not-trigger',
            tier='routing',
            passed=passed,
            duration_ms=result.duration,
            cost_usd=result.cost_estimate.estimated_cost,
            should_trigger=should_trigger,
            did_trigger=triggered,
            exit_reason=result.exit_reason,
            model=result.model,
            output=result.output[:500] if result.output else None,
        ))

    assert triggered == should_trigger


@pytest.mark.skipif(not _should_run('routing-seo-triggers'), reason='not selected')
@pytest.mark.timeout(10 * 60)
def test_routing_seo_triggers():
    for p in SHOULD_TRIGGER:
        _run_routing_test(p, True)


@pytest.mark.skipif(not _should_run('routing-seo-non-triggers'), reason='not selected')
@pytest.mark.timeout(10 * 60)
def test_routing_seo_non_triggers():
    for p in SHOULD_NOT_TRIGGER:
        _run_routing_test(p, False)


def teardown_module(module):
    if _collector:
        _collector.finalize()
    for d in _tmp_dirs:
        shutil.rmtree(d, ignore_errors=True)
