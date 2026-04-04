"""
LLM-as-judge helpers for toprank evals.

Uses Gemini (cheapest option). Set GEMINI_API_KEY or GOOGLE_GENERATIVE_AI_API_KEY.

Requires: `google-genai` package installed (pip install google-genai).
"""

import json
import os
import time
from dataclasses import dataclass

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client

    api_key = (
        os.environ.get('GEMINI_API_KEY')
        or os.environ.get('GOOGLE_GENERATIVE_AI_API_KEY')
    )
    if not api_key:
        raise EnvironmentError(
            'No Gemini API key found. Set GEMINI_API_KEY or GOOGLE_GENERATIVE_AI_API_KEY.'
        )

    try:
        from google import genai
    except ImportError:
        raise ImportError(
            'google-genai package required — run: pip install google-genai'
        )

    _client = genai.Client(api_key=api_key)
    return _client


def call_judge(prompt: str) -> dict:
    """Call Gemini, return parsed JSON. Retries up to 3 times on rate limit."""
    client = _get_client()

    def make_request():
        response = client.models.generate_content(
            model=JUDGE_MODEL,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.0,
            },
        )
        return response.text

    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            text = make_request()
            break
        except Exception as e:
            status = getattr(e, 'status_code', None) or getattr(e, 'code', None)
            if status == 429 or 'rate' in str(e).lower() or 'quota' in str(e).lower():
                last_exc = e
                time.sleep(2 ** attempt)
            else:
                raise
    else:
        raise last_exc  # all retries exhausted

    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError as e:
        raise ValueError(f'Judge returned non-JSON: {text[:200]}') from e


@dataclass
class JudgeScore:
    clarity: int        # 1-5: can an agent understand what to do?
    completeness: int   # 1-5: is all needed info present?
    actionability: int  # 1-5: can an agent act without guessing?
    reasoning: str


@dataclass
class SeoReportScore:
    has_quick_wins: bool           # Report includes a Quick Wins section
    recommendations_specific: bool # Recommendations include specific URLs and query names
    has_action_plan: bool          # Report includes a 30-day action plan
    quantified_impact: bool        # At least one recommendation quantifies impact
    score: int                     # 1-5 overall quality
    reasoning: str


JUDGE_MODEL = 'gemini-2.0-flash'

MIN_CLARITY = 4
MIN_COMPLETENESS = 4
MIN_ACTIONABILITY = 4


def extract_section(md: str, start_marker: str, end_marker: str = '') -> str:
    """Extract a section from a markdown document between two markers."""
    start = md.find(start_marker)
    if start == -1:
        return ''
    if end_marker:
        end = md.find(end_marker, start + len(start_marker))
        return md[start:end].strip() if end != -1 else md[start:].strip()
    return md[start:].strip()


def run_judge_test(
    name: str,
    suite: str,
    section_label: str,
    content: str,
    collector,
    min_clarity: int = MIN_CLARITY,
    min_completeness: int = MIN_COMPLETENESS,
    min_actionability: int = MIN_ACTIONABILITY,
    cost_usd: float = 0.02,
) -> JudgeScore:
    """Run a judge test, add to collector, and assert scores. Returns the scores."""
    import time as _time
    t0 = _time.time()
    assert len(content) > 100, f'{name}: section not found or too short'

    scores = judge(section_label, content)
    print(f'{name} scores:', scores)

    passed = (
        scores.clarity >= min_clarity
        and scores.completeness >= min_completeness
        and scores.actionability >= min_actionability
    )

    if collector:
        from helpers.eval_store import EvalTestEntry
        collector.add_test(EvalTestEntry(
            name=name,
            suite=suite,
            tier='llm-judge',
            passed=passed,
            duration_ms=int((_time.time() - t0) * 1000),
            cost_usd=cost_usd,
            judge_scores={
                'clarity': scores.clarity,
                'completeness': scores.completeness,
                'actionability': scores.actionability,
            },
            judge_reasoning=scores.reasoning,
        ))

    assert scores.clarity >= min_clarity, f'{name}: clarity {scores.clarity} < {min_clarity}'
    assert scores.completeness >= min_completeness, f'{name}: completeness {scores.completeness} < {min_completeness}'
    assert scores.actionability >= min_actionability, f'{name}: actionability {scores.actionability} < {min_actionability}'
    return scores


def judge(section: str, content: str) -> JudgeScore:
    """Score a SKILL.md section for documentation quality."""
    result = call_judge(f"""You are evaluating instructions for an AI agent performing SEO analysis.

The agent reads these instructions to learn how to run a structured SEO audit. It needs to:
1. Know what steps to take and in what order
2. Know what tools/scripts to call and with what arguments
3. Know what the output should look like and what to include

Rate the following {section} on three dimensions (1-5):

- **clarity** (1-5): Can an agent understand what each step does from the description alone?
- **completeness** (1-5): Are commands, arguments, and expected behavior documented? Would an agent need to guess anything?
- **actionability** (1-5): Can an agent execute this section correctly without asking follow-up questions?

Scoring guide:
- 5: Excellent — no ambiguity, all info present
- 4: Good — minor gaps an experienced agent can infer
- 3: Adequate — some guessing required
- 2: Poor — significant info missing
- 1: Unusable — agent would fail without external help

Respond with ONLY valid JSON:
{{"clarity": N, "completeness": N, "actionability": N, "reasoning": "brief explanation"}}

Content to evaluate:

{content}""")

    return JudgeScore(
        clarity=result['clarity'],
        completeness=result['completeness'],
        actionability=result['actionability'],
        reasoning=result.get('reasoning', ''),
    )


def seo_report_judge(report: str) -> SeoReportScore:
    """Evaluate a generated SEO report against quality criteria."""
    result = call_judge(f"""You are evaluating the quality of an SEO analysis report generated by an AI agent.

A high-quality SEO report must:
1. Include a "Quick Wins" section with specific page URLs and query names
2. Make recommendations that are specific and actionable (not vague like "improve your SEO")
3. Include a 30-day action plan with prioritized steps
4. Quantify expected impact (e.g. estimated click increases) for at least one recommendation

Evaluate the following report:

---
{report[:6000]}
---

Respond with ONLY valid JSON:
{{
  "has_quick_wins": true/false,
  "recommendations_specific": true/false,
  "has_action_plan": true/false,
  "quantified_impact": true/false,
  "score": 1-5,
  "reasoning": "brief explanation"
}}
""")

    return SeoReportScore(
        has_quick_wins=bool(result.get('has_quick_wins')),
        recommendations_specific=bool(result.get('recommendations_specific')),
        has_action_plan=bool(result.get('has_action_plan')),
        quantified_impact=bool(result.get('quantified_impact')),
        score=int(result.get('score', 0)),
        reasoning=result.get('reasoning', ''),
    )
