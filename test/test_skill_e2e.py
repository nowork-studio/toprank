"""
End-to-end tests for the seo-analysis skill.

Spawns `claude -p` with the skill installed in a temp working directory.
Uses mock scripts and fixture data so no real Google credentials are needed.

Run: EVALS=1 pytest test/test_skill_e2e.py
"""

import os
import shutil
import sys
import time
from pathlib import Path

import pytest

from helpers.session_runner import run_skill_test, create_skill_workdir
from helpers.llm_judge import seo_report_judge
from helpers.eval_store import EvalCollector, EvalTestEntry
from helpers.touchfiles import (
    select_tests, detect_base_branch, get_changed_files,
    E2E_TOUCHFILES, GLOBAL_TOUCHFILES,
)

ROOT = Path(__file__).parent.parent
SKILL_PATH = ROOT / 'skills' / 'seo-analysis'
FIXTURES_DIR = ROOT / 'test' / 'fixtures'

EVALS = bool(os.environ.get('EVALS'))
pytestmark = pytest.mark.skipif(not EVALS, reason='Set EVALS=1 to run E2E evals')

# Diff-based selection
_selected: list[str] | None = None
if EVALS and not os.environ.get('EVALS_ALL'):
    _base = os.environ.get('EVALS_BASE') or detect_base_branch(str(ROOT)) or 'main'
    _changed = get_changed_files(_base, str(ROOT))
    if _changed:
        _sel = select_tests(_changed, E2E_TOUCHFILES, GLOBAL_TOUCHFILES)
        _selected = _sel['selected']
        print(
            f"\nE2E selection ({_sel['reason']}): "
            f"{len(_selected)}/{len(E2E_TOUCHFILES)} tests",
            file=sys.stderr,
        )


def _should_run(name: str) -> bool:
    return EVALS and (_selected is None or name in _selected)


_tmp_dirs: list[str] = []
_collector = EvalCollector('e2e') if EVALS else None


def _create_fixture_workdir() -> tuple[str, str]:
    """Create workdir with mock GSC scripts pre-installed."""
    workdir = create_skill_workdir(str(SKILL_PATH), 'seo-analysis')
    _tmp_dirs.append(workdir)  # register before any further setup so cleanup runs on error

    skill_scripts_dir = Path(workdir) / '.claude' / 'skills' / 'seo-analysis' / 'scripts'
    shutil.copy(FIXTURES_DIR / 'mock-analyze-gsc.py', skill_scripts_dir / 'analyze_gsc.py')
    shutil.copy(FIXTURES_DIR / 'sample_gsc_data.json', skill_scripts_dir / 'sample_gsc_data.json')

    mock_bin = Path(workdir) / 'bin'
    mock_bin.mkdir(exist_ok=True)
    mock_gcloud = mock_bin / 'gcloud'
    shutil.copy(FIXTURES_DIR / 'mock-gcloud.sh', mock_gcloud)
    mock_gcloud.chmod(0o755)

    return workdir, str(mock_bin)


@pytest.mark.skipif(not _should_run('seo-no-gsc-technical-audit'), reason='not selected')
@pytest.mark.timeout(4 * 60)
def test_seo_no_gsc_technical_audit():
    t0 = time.time()
    workdir = create_skill_workdir(str(SKILL_PATH), 'seo-analysis')
    _tmp_dirs.append(workdir)  # register before run so cleanup happens on error

    result = run_skill_test(
        prompt=(
            'Use the seo-analysis skill to do a technical SEO audit. '
            "I don't have GSC access — skip that, just audit the URL directly. "
            'Site: https://example-saas.com '
            'Focus on the technical audit (Phase 5) and produce the report (Phase 6). '
            'Keep it brief — you can skip pulling real data, just audit what you can from the URL structure.'
        ),
        working_directory=workdir,
        max_turns=20,
        timeout_ms=3 * 60 * 1000,
        test_name='seo-no-gsc-technical-audit',
    )

    duration = int((time.time() - t0) * 1000)

    if _collector:
        _collector.add_test(EvalTestEntry(
            name='seo-no-gsc-technical-audit',
            suite='seo-analysis skill E2E',
            tier='e2e',
            passed=result.exit_reason == 'success',
            duration_ms=duration,
            cost_usd=result.cost_estimate.estimated_cost,
            output=result.output[:1000] if result.output else None,
            turns_used=result.cost_estimate.turns_used,
            exit_reason=result.exit_reason,
            model=result.model,
        ))

    assert result.exit_reason == 'success'
    assert len(result.tool_calls) > 0
    assert any(kw in result.output.lower() for kw in ('seo', 'technical', 'audit'))


@pytest.mark.skipif(not _should_run('seo-fixture-full-audit'), reason='not selected')
@pytest.mark.timeout(6 * 60)
def test_seo_fixture_full_audit():
    t0 = time.time()
    workdir, mock_bin = _create_fixture_workdir()

    result = run_skill_test(
        prompt=(
            'Run the seo-analysis skill for sc-domain:example-saas.com. '
            "Use the skill's full workflow including the GSC data pull. "
            'The analysis data is available — go through all phases.'
        ),
        working_directory=workdir,
        max_turns=35,
        timeout_ms=5 * 60 * 1000,
        test_name='seo-fixture-full-audit',
        env_overrides={'PATH': f"{mock_bin}:{os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}"},
    )

    duration = int((time.time() - t0) * 1000)

    report_score = None
    if result.exit_reason == 'success' and len(result.output) > 200:
        try:
            report_score = seo_report_judge(result.output)
        except Exception:
            pass

    if _collector:
        _collector.add_test(EvalTestEntry(
            name='seo-fixture-full-audit',
            suite='seo-analysis skill E2E',
            tier='e2e',
            passed=result.exit_reason == 'success',
            duration_ms=duration,
            cost_usd=result.cost_estimate.estimated_cost,
            output=result.output[:2000] if result.output else None,
            turns_used=result.cost_estimate.turns_used,
            exit_reason=result.exit_reason,
            model=result.model,
            judge_scores={'score': report_score.score} if report_score else None,
            judge_reasoning=report_score.reasoning if report_score else None,
        ))

    assert result.exit_reason == 'success'
    bash_calls = [c for c in result.tool_calls if c.tool == 'Bash']
    assert len(bash_calls) > 0
    assert 'quick win' in result.output.lower()


@pytest.mark.skipif(not _should_run('seo-report-quality'), reason='not selected')
@pytest.mark.timeout(6 * 60)
def test_seo_report_quality():
    t0 = time.time()
    workdir, mock_bin = _create_fixture_workdir()

    result = run_skill_test(
        prompt=(
            'Use the seo-analysis skill for sc-domain:example-saas.com. '
            'The fixture data has position 4-10 quick wins and traffic drops — find them. '
            'Produce a full report with specific recommendations.'
        ),
        working_directory=workdir,
        max_turns=35,
        timeout_ms=5 * 60 * 1000,
        test_name='seo-report-quality',
        env_overrides={'PATH': f"{mock_bin}:{os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}"},
    )

    duration = int((time.time() - t0) * 1000)

    if result.exit_reason != 'success':
        if _collector:
            _collector.add_test(EvalTestEntry(
                name='seo-report-quality',
                suite='seo-analysis skill E2E',
                tier='e2e',
                passed=False,
                duration_ms=duration,
                cost_usd=result.cost_estimate.estimated_cost,
                exit_reason=result.exit_reason,
                model=result.model,
                error=f'Skill failed: {result.exit_reason}',
            ))
        assert result.exit_reason == 'success'
        return

    report_score = seo_report_judge(result.output)
    passed = report_score.has_quick_wins and report_score.recommendations_specific and report_score.score >= 3

    if _collector:
        _collector.add_test(EvalTestEntry(
            name='seo-report-quality',
            suite='seo-analysis skill E2E',
            tier='e2e',
            passed=passed,
            duration_ms=duration,
            cost_usd=result.cost_estimate.estimated_cost,
            output=result.output[:2000] if result.output else None,
            turns_used=result.cost_estimate.turns_used,
            exit_reason=result.exit_reason,
            model=result.model,
            judge_scores={
                'score': report_score.score,
                'has_quick_wins': int(report_score.has_quick_wins),
                'recommendations_specific': int(report_score.recommendations_specific),
            },
            judge_reasoning=report_score.reasoning,
        ))

    assert report_score.has_quick_wins
    assert report_score.recommendations_specific
    assert report_score.score >= 3


def teardown_module(module):
    if _collector:
        _collector.finalize()
    for d in _tmp_dirs:
        shutil.rmtree(d, ignore_errors=True)
