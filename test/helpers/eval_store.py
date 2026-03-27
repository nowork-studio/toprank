"""
Eval result persistence for toprank tests.

Accumulates test results, writes them to ~/.toprank-evals/, prints a summary table.
"""

import atexit
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

EVAL_DIR = Path.home() / '.toprank-evals'


@dataclass
class EvalTestEntry:
    name: str
    suite: str
    tier: str           # 'e2e', 'llm-judge', 'routing'
    passed: bool
    duration_ms: int
    cost_usd: float

    # E2E
    output: Optional[str] = None
    turns_used: Optional[int] = None

    # LLM judge
    judge_scores: Optional[dict[str, float]] = None
    judge_reasoning: Optional[str] = None

    # Routing
    should_trigger: Optional[bool] = None
    did_trigger: Optional[bool] = None

    # Diagnostics
    exit_reason: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None


def _git_info() -> tuple[str, str]:
    try:
        branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, timeout=3,
        ).stdout.strip() or 'unknown'
        sha = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, timeout=3,
        ).stdout.strip() or 'unknown'
        return branch, sha
    except Exception:
        return 'unknown', 'unknown'


def _version() -> str:
    version_file = Path(__file__).parent.parent.parent / 'VERSION'
    try:
        return version_file.read_text().strip()
    except Exception:
        return 'unknown'


class EvalCollector:
    def __init__(self, tier: str):
        self.tier = tier
        self.tests: list[EvalTestEntry] = []
        self._finalized = False
        # Register finalize() so results are persisted even on process crash.
        atexit.register(self.finalize)

    def add_test(self, entry: EvalTestEntry) -> None:
        self.tests.append(entry)

    def finalize(self) -> str:
        if self._finalized:
            return ''
        self._finalized = True

        branch, sha = _git_info()
        version = _version()
        timestamp = datetime.now(timezone.utc).isoformat()
        passed = sum(1 for t in self.tests if t.passed)
        total_cost = sum(t.cost_usd for t in self.tests)
        total_duration = sum(t.duration_ms for t in self.tests)

        result = {
            'version': version,
            'branch': branch,
            'git_sha': sha,
            'timestamp': timestamp,
            'tier': self.tier,
            'total_tests': len(self.tests),
            'passed': passed,
            'failed': len(self.tests) - passed,
            'total_cost_usd': round(total_cost, 2),
            'total_duration_ms': total_duration,
            'tests': [vars(t) for t in self.tests],
        }

        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        date_str = timestamp.replace(':', '').replace('.', '').replace('+', '')[:15]
        safe_branch = branch.replace('/', '-').replace('@', '-')
        filename = f'{version}-{safe_branch}-{self.tier}-{date_str}.json'
        filepath = EVAL_DIR / filename
        filepath.write_text(json.dumps(result, indent=2) + '\n')

        self._print_summary(result, filepath, branch, sha)
        return str(filepath)

    def _print_summary(self, result: dict, filepath: Path, branch: str, sha: str) -> None:
        lines = ['']
        lines.append(f"Eval Results — v{result['version']} @ {branch} ({sha}) — {self.tier}")
        lines.append('═' * 65)

        for t in self.tests:
            status = ' PASS ' if t.passed else ' FAIL '
            cost = f"${t.cost_usd:.3f}"
            dur = f"{round(t.duration_ms / 1000)}s" if t.duration_ms else ''
            name = t.name[:35] + '...' if len(t.name) > 38 else t.name.ljust(38)
            lines.append(f"  {name}  {status}  {cost.rjust(7)}  {dur.rjust(5)}")

        lines.append('─' * 65)
        lines.append(
            f"  Total: {result['passed']}/{result['total_tests']} passed   "
            f"${result['total_cost_usd']:.2f}   {round(result['total_duration_ms'] / 1000)}s"
        )
        lines.append(f'Saved: {filepath}')
        print('\n'.join(lines), file=sys.stderr)
