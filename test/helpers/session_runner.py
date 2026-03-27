"""
Claude CLI subprocess runner for skill E2E testing.

Spawns `claude -p` as an independent process. Pipes the prompt via -p,
captures stream-json NDJSON output.
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Optional

# Strip these env var prefixes so nested sessions don't inherit outer context.
# ANTHROPIC_API_KEY is re-added below — the subprocess needs it.
# Strip ANTHROPIC_* too so ANTHROPIC_BASE_URL / ANTHROPIC_MODEL can't redirect
# the subprocess to a different model or endpoint.
_STRIP_PREFIXES = ('CLAUDE_', 'ANTHROPIC_')


@dataclass
class ToolCall:
    tool: str
    input: dict[str, Any]
    output: str = ''


@dataclass
class CostEstimate:
    turns_used: int
    estimated_cost: float  # USD
    estimated_tokens: int = 0


@dataclass
class SkillTestResult:
    output: str
    exit_reason: str          # 'success', 'timeout', 'error_api', 'exit_code_N', ...
    tool_calls: list[ToolCall]
    cost_estimate: CostEstimate
    duration: int             # ms
    model: str
    transcript: list[Any]


def parse_ndjson(lines: list[str]) -> tuple[list[Any], Any, int, list[ToolCall]]:
    """Parse NDJSON lines from claude stream-json output.

    Returns (transcript, result_line, turn_count, tool_calls).
    """
    transcript: list[Any] = []
    result_line = None
    turn_count = 0
    tool_calls: list[ToolCall] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        transcript.append(event)

        if event.get('type') == 'assistant':
            turn_count += 1
            for item in event.get('message', {}).get('content', []):
                if item.get('type') == 'tool_use':
                    tool_calls.append(ToolCall(
                        tool=item.get('name', 'unknown'),
                        input=item.get('input', {}),
                    ))

        if event.get('type') == 'result':
            result_line = event

    return transcript, result_line, turn_count, tool_calls


def create_skill_workdir(skill_path: str, skill_name: str) -> str:
    """Copy skill into a temp dir so Claude auto-discovers it at .claude/skills/<name>."""
    tmpdir = tempfile.mkdtemp(prefix=f'toprank-test-')
    dest = os.path.join(tmpdir, '.claude', 'skills', skill_name)
    shutil.copytree(skill_path, dest)
    return tmpdir


def run_skill_test(
    prompt: str,
    working_directory: Optional[str] = None,
    max_turns: int = 30,
    timeout_ms: int = 5 * 60 * 1000,
    test_name: str = 'test',
    env_overrides: Optional[dict[str, str]] = None,
) -> SkillTestResult:
    """Run claude -p in a subprocess and return parsed results."""
    if working_directory is None:
        working_directory = tempfile.gettempdir()

    # Build environment: strip CLAUDE_* vars, keep ANTHROPIC_API_KEY
    env = {k: v for k, v in os.environ.items()
           if not any(k.startswith(p) for p in _STRIP_PREFIXES)}
    if os.environ.get('ANTHROPIC_API_KEY'):
        env['ANTHROPIC_API_KEY'] = os.environ['ANTHROPIC_API_KEY']
    if env_overrides:
        env.update(env_overrides)

    cmd = [
        'claude',
        '--output-format', 'stream-json',
        '--verbose',
        '--max-turns', str(max_turns),
        '-p', prompt,
    ]

    start = time.time()
    timed_out = False

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=working_directory,
            env=env,
            timeout=timeout_ms / 1000,
        )
        stdout = proc.stdout
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = (e.stdout or b'').decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
        exit_code = -1

    duration = int((time.time() - start) * 1000)
    lines = stdout.splitlines()
    transcript, result_line, turn_count, tool_calls = parse_ndjson(lines)

    # Determine exit reason
    if timed_out:
        exit_reason = 'timeout'
    elif result_line:
        if result_line.get('is_error'):
            exit_reason = 'error_api'
        else:
            exit_reason = result_line.get('subtype', 'success')
    elif exit_code == 0:
        exit_reason = 'success'
    else:
        exit_reason = f'exit_code_{exit_code}'

    turns_used = result_line.get('num_turns', 0) if result_line else 0
    estimated_cost = result_line.get('total_cost_usd', 0.0) if result_line else 0.0
    usage = result_line.get('usage', {}) if result_line else {}
    estimated_tokens = (
        usage.get('input_tokens', 0) +
        usage.get('output_tokens', 0) +
        usage.get('cache_read_input_tokens', 0)
    )
    model = result_line.get('model', 'unknown') if result_line else 'unknown'

    return SkillTestResult(
        output=result_line.get('result', '') if result_line else '',
        exit_reason=exit_reason,
        tool_calls=tool_calls,
        cost_estimate=CostEstimate(
            turns_used=turns_used,
            estimated_cost=round(estimated_cost, 4),
            estimated_tokens=estimated_tokens,
        ),
        duration=duration,
        model=model,
        transcript=transcript,
    )
