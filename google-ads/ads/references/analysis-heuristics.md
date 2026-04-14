# Analysis Heuristics

Quick-decision thresholds for Google Ads analysis. Use these for fast triage, then read the linked deep-dive reference when you need full diagnostic workflows.

## Framing Priority: Margin-Aware First, Account-Average Second

Before running any heuristic below, check `{data_dir}/business-context.json.unit_economics`. Two branches:

**Branch A — Margin-aware (preferred).** If `aov_usd` and `profit_margin` exist (regardless of source), read `../../shared/ppc-math.md` and use break-even-based thresholds:
- Waste = spend on keywords/terms with `CPA > Break-Even CPA` (where Break-Even CPA = AOV × margin)
- Scaling = campaigns with positive Headroom $ AND Budget-Lost IS > 20%
- Every finding expresses dollar impact as "saves $X/mo" or "captures $X/mo headroom" — not "CPA above average"

If `unit_economics.source == "inferred_from_template"`, append this disclaimer beneath the report header: `_Profitability estimates use industry defaults — confirm your actual AOV and margin for sharper recommendations._`

**Branch B — Account-average (fallback).** If `unit_economics` is null or `aov_usd` is missing, use the account-average heuristics in the tables below. Never mix the two branches in one report — pick one framing and stay consistent.

## Industry Template Calibration

Read `../../shared/industry-templates.json` once per audit (cache in memory). Use `business-context.json.industry_template_key` to select the template. Every threshold marked `[template]` below reads from the template first; the listed value is the fallback if no template match.

## Keyword Classification (mandatory first step)

Before evaluating any keyword's performance, classify it by business relevance. This prevents pausing a core business keyword during a short run of poor metrics.

| Tier | Definition | Implication |
|------|-----------|-------------|
| **Tier 1 (Core)** | Keyword directly describes what the business sells | **Never pause.** Diagnose and optimize instead |
| **Tier 2 (Adjacent)** | Related to the business but not a primary service | Standard heuristics apply after Statistical Significance Gate |
| **Tier 3 (Irrelevant)** | Wrong intent, wrong service, unrelated | Aggressive pause heuristics apply |

**How to classify without business-context.json:** Check campaign name, ad group name, ad headlines, landing page URL. Matches 2+ signals = Tier 1. Matches 1 = Tier 2. Matches none = Tier 3.

## Statistical Significance Gate

Before any conversion-based decision (pause, bid decrease, labeling "non-converting"):

1. Calculate: `keyword_clicks x account_average_conversion_rate = expected_conversions`
2. If expected conversions < 3, the sample is insufficient — label **"Insufficient data"** and skip conversion-based decisions.
3. Only apply conversion heuristics when expected conversions >= 3 and actual conversions are still 0 or significantly below expected.

## Keyword Performance Quick Rules

> **Prerequisite:** Classification + Significance Gate first. These rules apply to Tier 2/3 only. For Tier 1, see Core Keyword Diagnostic below.

| Condition | Action |
|-----------|--------|
| CPA < 50% of account avg | Increase bid 15-25%, expand match types |
| CPA 50-100% of account avg | Maintain, monitor weekly |
| CPA 100-150% of account avg | Review search terms, tighten targeting |
| CPA > 150% of account avg | Decrease bid 15-25%. If CPA > 200% after 2 weeks, pause |
| 0 conv, spend > 2x CPA | Tier 2/3: pause. Tier 1: run Core Keyword Diagnostic |
| 0 conv, spend 1-2x CPA, QS > 6 | Give 2 more weeks |
| 0 conv, spend 1-2x CPA, QS < 5 | Tier 2/3: pause. Tier 1: Core Keyword Diagnostic |
| 0 impressions 30+ days | Pause (zombie keyword) |

For accounts WITHOUT conversion data, see `quality-score-framework.md` CTR benchmarks section.

## Core Keyword Diagnostic (Tier 1 only)

When a Tier 1 keyword underperforms, run this sequence instead of pausing:

1. **Statistical significance** — enough clicks? If expected conversions < 3, monitor and revisit.
2. **Compare to siblings** — do similar keywords in the same campaign convert? If not, the issue is campaign/landing-page-level.
3. **Match type check** — if broad match and >30% irrelevant search terms, add negatives aggressively. If CPA remains unacceptable with Smart Bidding active, switch to exact match (phrase and broad overlap ~100% in most verticals, so switching to phrase rarely helps).
4. **QS subcomponent diagnosis** — which component is below average? For full QS diagnostic workflow, read `quality-score-framework.md`.
5. **Position and impression share** — rank-lost IS > 50% means the keyword isn't getting a fair chance.
6. **Recommend optimization, not removal.** Only after 2+ weeks of optimization attempts with sufficient data should pause be considered.

## Search Term Quick Rules

| Condition | Action | Match Type |
|-----------|--------|------------|
| 3+ conversions, not a keyword | Add as keyword | Phrase match |
| 0 conversions, 10+ clicks | Add as negative | Phrase match at campaign level |
| Clearly irrelevant (competitor, wrong service) | Add as negative immediately | Exact for competitors, phrase for wrong services |
| Non-commercial intent ("free", "DIY", "jobs") | Add as negative | Phrase match |

For accounts using Broad match or PMax, negatives have reduced precision — Google's AI-driven query expansion can serve ads on conceptually related queries that don't contain the negative term literally. See `search-term-analysis-guide.md` for full details on relevance scoring, n-gram analysis, and negative strategy.

## Impression Share Diagnostic

| | Rank-Lost IS < 30% | Rank-Lost IS 30-50% | Rank-Lost IS > 50% |
|---|---|---|---|
| **Budget-Lost IS < 20%** | Healthy | QS/bid issue on some keywords | QS/bid problem — fix quality first |
| **Budget-Lost IS 20-40%** | Budget constraint — increase 20-30% | Fix rank first (cheaper), then reassess budget | Structural: too competitive for current QS+budget |
| **Budget-Lost IS > 40%** | Severe budget constraint | Fix rank first, then increase budget | Fundamental misalignment — restructure needed |

## Wasted Spend Calculation

```
WASTED SPEND =
  Keyword Waste: spend on Tier 2/3 keywords where (conversions = 0 AND clicks > 10)
  + Search Term Waste: spend on search terms with relevance_score < 2
  + Structural Waste: spend on Display Network enabled campaigns where display clicks > 20 AND display conversions = 0
```

Exclude Tier 1 keywords — those are optimization opportunities, not waste.

Present as: dollar amount, percentage of total spend, annualized projection. Break down by category.

## Budget Allocation Quick Rules

| Condition | Action |
|-----------|--------|
| Daily budget < 10x avg CPC with 20+ keywords | Budget spread too thin — reduce to 5-10 best keywords or increase budget |
| One campaign >60% of budget with <40% of conversions | Budget misallocation — shift 20-30% to higher-converting campaign |
| Campaign with conversions hitting budget limit (budget-lost IS >30%) | Proven campaign being starved — increase budget 25-50% |
| Campaign with 0 conversions after spending >5x account CPA | Not a budget problem — audit keywords, landing pages, conversion tracking |

