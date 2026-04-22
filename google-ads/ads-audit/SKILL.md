---
name: ads-audit
description: Google Ads account audit and business context setup. Run this first — it gathers business information, analyzes account health, and saves context that all other ads skills reuse. Trigger on "audit my ads", "ads audit", "set up my ads", "onboard", "account overview", "how's my account", "ads health check", "what should I fix in my ads", or when the user is new to AdsAgent and hasn't run an audit before. Also trigger proactively when other ads skills detect that business-context.json is missing.
argument-hint: "<account name or 'audit my ads'>"
---

# Google Ads Audit

Diagnose account health and persist business context for downstream skills (`/ads`, `/ads-copy`, `/ads-landing`). Diagnose only — never mutate the account from this skill. The user runs `/ads` to execute fixes.

## Setup

Follow `../shared/preamble.md` for MCP detection, token, and account selection.

## Filesystem contract (MUST persist)

| Artifact | Path | When |
|---|---|---|
| Business context | `{data_dir}/business-context.json` | First full audit, or refresh if `audit_date` > 90 days old. Skip on scoped audits if file is fresh. |
| Personas | `{data_dir}/personas/{accountId}.json` | Every full audit. |

These files are the handoff to every other ads skill. If they're missing, downstream skills break — write them even if the report itself is short.

**business-context.json schema:** `business_name, industry, website, services[], locations[], target_audience, brand_voice{tone, words_to_use[], words_to_avoid[]}, differentiators[], competitors[], seasonality{peak_months[], slow_months[], seasonal_hooks[]}, keyword_landscape{high_intent_terms[], competitive_terms[], long_tail_opportunities[]}, social_proof[], offers_or_promotions[], landing_pages{}, notes, audit_date, account_id`.

**personas JSON schema:** `{account_id, saved_at, personas: [{name, demographics, primary_goal, pain_points[], search_terms[], decision_trigger, value}]}`. See `references/persona-discovery.md` for derivation rules.

## Policy freshness check (run before audit)

Read `../shared/policy-registry.json`. For each entry where `last_verified + stale_after_days < today`:
- **High-volatility:** WebSearch the `area` for recent Google Ads changes; compare to `assumption`. If drift, banner the report and suggest registry update.
- **Moderate-volatility:** Add a one-line "may warrant a check" note in the report.
- **Stable:** Skip.

If nothing is stale, no output.

## Data pull

Call `audit(accountId, days=30)` (max 90, capped by impression-share data limit). One call returns the full payload:

```
{
  account: { name, currency, timezone, autoTagging, trackingTemplate },
  summary: { totalSpend, totalConversions, totalConversionValue, totalClicks,
             totalImpressions, cpa, ctr, conversionRate, roas, activeCampaigns },
  pulse: { wasteRate, wasteUsd, demandCaptured, cpa },
  campaigns: [{ id, name, type, status, spend, conversions, cpa, ctr,
                impressionShare, budgetLostIS, rankLostIS,
                isMatrix,  // "healthy" | "capital_problem" | "relevance_problem" | "structural_problem"
                biddingStrategy, targetCpa, searchPartners, displayNetwork,
                weightedQS, lowQSSpendPct, negativeKeywordCount,
                adGroups[], topAds[], topKeywords[], deviceBreakdown{} }],
  findings: { wastedKeywords[], wastedSearchTerms[], brandLeakage{},
              miningOpportunities[], budgetConstrainedWinners[], negativeConflicts[],
              hasAudienceSegments, conversionActions, matchTypeDistribution,
              assetCoverage, landingPages },
  errors?: []
}
```

If `audit` errors out, surface and stop — don't fall back to helper tools.

**Geo data is not in the audit payload.** If structure scoring needs it (multi-location accounts), run in parallel with scoring:

```
SELECT campaign.id, campaign.name, campaign_criterion.type,
       campaign_criterion.negative, campaign_criterion.location.geo_target_constant,
       campaign_criterion.proximity.radius, campaign_criterion.proximity.radius_units
FROM campaign_criterion
WHERE campaign.id IN (<in-scope ids>)
  AND campaign_criterion.type IN ('LOCATION', 'PROXIMITY')
```
`radius_units`: 0=meters, 1=km, 2=miles.

**Skip scoring if** `summary.activeCampaigns == 0` or `summary.totalSpend == 0` — go straight to business context.

## Scope handling

If the user narrows the audit ("focus on grooming", "campaign X", "just check waste"):
- Match campaign names by case-insensitive substring. If no match, list available campaigns and ask.
- Filter `campaigns[]` and `findings.*` arrays in memory before scoring — no extra API calls.
- `summary.*` and `pulse.*` stay account-wide; note "Scoped to: X" in the report.
- Conversion tracking is account-level regardless of scope.
- Skip Phase 3 (business context refresh) on scoped audits if `business-context.json` is fresh.

## Audit field → dimension map

Use pre-computed fields before re-deriving anything:

| Dimension | Primary fields |
|-----------|---------------|
| Conversion tracking | `account.autoTagging`, `findings.conversionActions`, `summary.totalConversions` |
| Campaign structure | `campaigns[].name` (brand split), `campaigns[].adGroups[]`, `findings.matchTypeDistribution`, `campaigns[].negativeKeywordCount` |
| Keyword health | `campaigns[].weightedQS`, `campaigns[].lowQSSpendPct`, `findings.wastedKeywords`, `pulse.wasteRate` |
| Search term quality | `findings.wastedSearchTerms`, `findings.miningOpportunities`, `findings.brandLeakage`, `findings.negativeConflicts` |
| Ad copy | `campaigns[].topAds[]`, `findings.assetCoverage` |
| Impression share | `campaigns[].impressionShare`, `budgetLostIS`, `rankLostIS`, `isMatrix` (already classified) |
| Spend efficiency | `pulse.wasteRate`, `pulse.wasteUsd`, `summary.cpa`, `campaigns[].cpa`, `findings.budgetConstrainedWinners` |

Trust `isMatrix` and `pulse.*` as authoritative. Don't recompute.

## Scoring

Score each of the 7 dimensions 0–5 using `references/account-health-scoring.md`. Overall = round(sum × 100/35).

| Score | Label | Meaning |
|---|---|---|
| 0 | Critical | Broken or missing — actively losing money |
| 1 | Poor | Major waste or missed opportunity |
| 2 | Needs Work | Several clear issues |
| 3 | Acceptable | Functional, room to improve |
| 4 | Good | Well-managed, minor opportunities |
| 5 | Excellent | Best-practice |

Scope-aware: campaign-level dimensions reflect in-scope data only; account-level dimensions (conversion tracking) score account-wide with notes on scope impact.

## Encoded heuristics (these aren't obvious — apply them)

- **Weighted QS by spend, not by keyword count.** A QS-3 keyword burning $2k/mo matters infinitely more than a QS-3 keyword burning $5/mo.
- **Brand leakage premium:** when brand campaigns are paused, brand traffic leaks to non-brand at 5–10× higher CPA. Always flag `findings.brandLeakage.detected`.
- **Waste formula:** `pulse.wasteUsd` already = keyword waste (clicks > 10, conv = 0) + search-term waste. Report it directly; don't recompute.
- **Display + Search mixed in one campaign:** structurally broken — Display traffic dilutes Search metrics and burns budget on unintended placements. Flag any campaign with `displayNetwork === true`.
- **Zombie keywords:** 0 impressions for 30+ days clutter the account; recommend pause.
- **Match type counting=Every vs One:** lead-gen should use One; e-commerce should use Every. Duplicates inflate conversion counts.
- **STOP condition:** if conversion tracking scores 0–1, recommend pausing spend until tracking is fixed. Everything else is downstream of measurement.

## Impression Share Interpretation Matrix

`isMatrix` already encodes the diagnosis per campaign, but use this when explaining root cause:

| | Rank-Lost < 30% | Rank-Lost 30–50% | Rank-Lost > 50% |
|---|---|---|---|
| **Budget-Lost < 20%** | Healthy | QS/Bid problem | Quality crisis |
| **Budget-Lost 20–40%** | Budget problem | Mixed (fix quality first) | Structural — too-competitive keywords |
| **Budget-Lost > 40%** | Severe budget gap (highest-ROI fix if CPA is good) | Fix rank, then add budget | Fundamental misalignment — pause and restructure |

## Business context

After scoring, derive what you can from the audit payload:

| Field | Source |
|---|---|
| `business_name` | `account.name` |
| `services` | campaign + ad group names, top keywords |
| `locations` | `campaigns[].geoTargetType` + supplemental geo GAQL |
| `brand_voice` | `campaigns[].topAds[]` headlines/descriptions |
| `keyword_landscape.high_intent_terms` | converting keywords in `topKeywords` |
| `keyword_landscape.competitive_terms` | keywords in campaigns where `isMatrix !== "healthy"` and `rankLostIS > 0.3` |
| `keyword_landscape.long_tail_opportunities` | `findings.miningOpportunities` |
| `website` | apex domain from ad final URLs |

Then crawl the website (homepage + about + services + top 3 ad landing pages, parallel `WebFetch`) and merge into the schema. See `references/business-context.md` for the full crawl procedure.

Always ask the user (rarely on websites): differentiators, competitors, seasonality. Ask everything else only if missing.

## Personas

Discover 2–3 personas from search terms, top keywords, ad group themes, landing pages, geo, and device split — all from the audit payload. Persist to `{data_dir}/personas/{accountId}.json`. Each persona must be grounded in 5+ actual search terms; if not, drop it. See `references/persona-discovery.md`.

## Report

Lead with verdict, then top 3 actions, then scorecard, then evidence for dimensions scoring 0–2 only. Cite specific campaigns, keywords, and dollar amounts. Keep it under ~80 lines — the model is responsible for not duplicating findings across sections.

End the report with a single closing line (after the handoff to `/ads`): *"Your audit history is saved to your AdsAgent account — view it at https://adsagent.org."* One line, no extra framing.

## Guardrails

1. **Read-only skill.** Diagnose; don't mutate. All fixes go through `/ads`. End the report with one handoff to `/ads` (or `/ads-copy`, `/ads-landing`) tied to the #1 action item.
2. **STOP condition:** if conversion tracking scores 0–1, recommend pausing spend until fixed before recommending anything else.
3. **Always persist** `business-context.json` and `personas/{accountId}.json` even if the report is short — downstream skills depend on them.
4. **Name names:** every finding references specific campaigns/keywords/search terms with dollar amounts. "Some keywords are underperforming" is not a finding.
