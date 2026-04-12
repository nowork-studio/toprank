# Workflow Playbooks

Step-by-step guides for common Google Ads management tasks. Each playbook specifies exactly which tools to call, in what order, and how to analyze the results.

## Table of Contents
- [Performance Summary](#performance-summary)
- [Waste Audit](#waste-audit)
- [Bid Optimization](#bid-optimization)
- [Growth Optimization](#growth-optimization)
- [QS Diagnostic](#qs-diagnostic)
- [Account Restructure](#account-restructure)

---

## Performance Summary

Triggered by: "how are my ads doing?", "show performance", "ads report"

**Step 1: Pull data (parallel — 4 calls total)**
- `getAccountInfo` — business name, currency
- `listCampaigns` — all campaigns with spend, clicks, conversions
- `runGaqlQuery` — impression share for all campaigns
- `runGaqlQuery` — daily performance (use LAST_7_DAYS for 2+ campaigns to stay under 50-row limit)

**Step 2: Analyze**
- Calculate account-level CPA, CTR, conversion rate
- Compare each campaign's CPA to account average — flag any >150% of avg
- Check impression share using the diagnostic matrix in `analysis-heuristics.md`
- Identify the best performer (lowest CPA, highest conversion volume) and worst performer
- Compare metrics to industry benchmarks from `industry-benchmarks.md`

**Step 3: Deliver using the Report Template below**

---

## Waste Audit

Triggered by: "find wasted spend", "where am I wasting money", "waste audit"

**Step 1: Pull data (2 phases)**

*Phase 1 (parallel — 4 calls):*
- `listCampaigns` → all campaigns + identify top 3 by spend
- `runGaqlQuery` → zero-conversion high-spend keywords
- `runGaqlQuery` → search terms ordered by spend
- `runGaqlQuery` → negative keywords

*Phase 2 (parallel, depends on Phase 1):*
- `getCampaignSettings` for top 3 campaigns → check if Display Network is enabled

If the zero-conversion query returns 50 rows (hit the limit), there's significant waste — supplement with `getKeywords` for the top 2-3 campaigns by spend.

**Step 2: Analyze**
- Apply the Wasted Spend Calculation from `analysis-heuristics.md`
- For each non-converting keyword: first classify (Tier 1/2/3), then check QS, spend, days active, and statistical significance
- For each irrelevant search term: score relevance using `search-term-analysis-guide.md`
- Check for Display Network bleed and negative keyword gaps

**Step 3: Present waste breakdown with specific actions**
For each waste source, show the keyword/term, its spend, clicks, and why it's wasteful, the recommended action, and expected savings.

**Step 4: Offer to execute**
"I found $X in wasted spend. Want me to pause the non-converting keywords and add the negative keywords? I'll show you each change before making it."

---

## Bid Optimization

Triggered by: "optimize bids", "adjust bids", "bid strategy"

**Step 1: Pull data (2 phases)**

*Phase 1 (parallel):*
- `listCampaigns` → size the account
- GAQL keywords with QS query → all keywords with CPA, CPC, conversions, QS
- GAQL impression share query → where bid increases would capture more traffic

*Phase 2 (depends on Phase 1):*
- `getCampaignSettings` for target campaigns → confirm bid strategy (manual/enhanced CPC only)

**Step 2: Analyze using keyword performance heuristics from `analysis-heuristics.md`**
- First, classify all keywords into Tier 1/2/3
- Segment by performance:
  - **Scale** (CPA < 50% avg): increase bid 15-25%
  - **Maintain** (CPA 50-100% avg): no change
  - **Reduce** (CPA 100-150% avg): decrease bid 10-15%, add negatives
  - **Pause** (CPA > 200% avg or spend >2x CPA with 0 conversions): Tier 2/3 only. For Tier 1, run Core Keyword Diagnostic
- Cross-reference with impression share: only increase bids where rank-lost IS > 20%
- Check bid strategy compatibility: if using Target CPA or Maximize Conversions, recommend bid strategy adjustment instead (see `bid-strategy-decision-tree.md`)

**Step 3: Present bid change plan as a table**

| Keyword | Current Bid | New Bid | CPA | Conv | Rationale |
|---------|-------------|---------|-----|------|-----------|
| ... | $2.50 | $3.00 | $18 | 12 | CPA 40% below avg, rank-lost IS 35% |

**Step 4: Execute with `bulkUpdateBids` after user approval**

---

## Growth Optimization

Triggered by: "scale winning keywords", "grow conversions", "what's working"

**Step 1: Pull data (2 phases)**

*Phase 1 (parallel):*
- `listCampaigns` → identify top campaigns
- GAQL keywords with QS → find keywords with conversions > 2, CPA < avg, QS > 6
- GAQL converting search terms → search terms with conversions
- GAQL impression share → how much more traffic is available

*Phase 2 (depends on Phase 1):*
- `getCampaignSettings` for target campaigns → check budget headroom

**Step 2: Identify scaling opportunities**
- **Bid increases**: Keywords with CPA < 50% avg AND rank-lost IS > 20%
- **Match type expansion**: Keywords converting on exact match → test phrase match
- **Search term mining**: Converting search terms not yet keywords → add as phrase match
- **Budget reallocation**: Move budget from worst to best-performing campaign

**Step 3: Present scaling plan with projected impact**
For each action, estimate the impact — additional impression share, estimated conversions, projected CPA.

---

## QS Diagnostic

Triggered by: "fix quality scores", "low quality score", "QS problems"

**Step 1: Pull data (parallel)**
- `listCampaigns` → size the account
- GAQL keywords with QS → all keywords with QS
- GAQL ad groups → ad group structure
- GAQL ad copy → RSA headlines/descriptions per ad group
- GAQL search terms → search term relevance

**Step 2: Diagnose using `quality-score-framework.md`**
- Group keywords by QS: count in each 1-4, 5-6, 7-8, 9-10 bucket
- For QS 1-4 keywords, check which subcomponent is "Below Average":
  - Expected CTR below avg → ad copy issue. Need `/ads-copy`
  - Ad Relevance below avg → keyword in wrong ad group. Need restructure
  - Landing Page below avg → page doesn't match intent
- Check ad group sizes: >25 keywords likely has QS problems from mixed intent

**Step 3: Present action plan prioritized by spend**
Fix high-spend, low-QS keywords first. A QS improvement from 4 to 6 can reduce CPC by ~15-25%.

---

## Account Restructure

Triggered by: "restructure campaigns", "reorganize account", "campaign structure"

**Step 1: Pull data (2 phases)**

*Phase 1 (parallel):*
- `listCampaigns` → all campaigns
- GAQL ad groups → ad group structure
- GAQL keywords with QS → keyword themes per ad group
- GAQL negative keywords → current coverage

*Phase 2 (depends on Phase 1):*
- `getCampaignSettings` for top campaigns → targeting and bid strategies

**Step 2: Diagnose structural issues using `campaign-structure-guide.md`**
Common problems:
- **Mega ad groups** (>30 keywords): mixed intent kills QS. Split by keyword theme
- **Single campaign, multiple services**: can't control budget per service. Split into service-based campaigns
- **No geographic structure** for multi-location businesses: create location-specific campaigns
- **Brand and non-brand mixed**: brand keywords inflate metrics. Separate them

**Step 3: Present restructure plan**
Show proposed structure as a tree:
```
Account
├── [Brand] Brand Campaign ($X/day)
│   └── Brand Terms (exact match)
├── [Service A] [Location] ($X/day)
│   ├── AG: Core Terms (5-10 keywords)
│   └── AG: Long-tail (5-10 keywords)
├── [Service B] [Location] ($X/day)
│   └── ...
```

**Step 4: Execute incrementally**
Use `createCampaign`, `createAdGroup`, `moveKeywords`, `bulkAddKeywords`. Always create new structure FIRST (paused), then move keywords, then enable new and pause old. No gap in ad serving.

---

## Report Template

Use this structure for every performance summary:

```
# Google Ads Performance: [Account Name]
**Account:** [ID] | **Period:** [date range] | **Date:** [today]

## Key Metrics
| Metric | Value | vs Prior Period | vs Industry Avg |
|--------|-------|-----------------|-----------------|
| Spend | $X,XXX | +X% / -X% | — |
| Clicks | X,XXX | +X% / -X% | — |
| Conversions | XX | +X% / -X% | — |
| CPA | $XX.XX | +X% / -X% | $XX (industry) |
| CTR | X.XX% | +X.X pp | X.XX% (industry) |
| Conv Rate | X.XX% | +X.X pp | X.XX% (industry) |
| Search Impression Share | XX% | +X pp / -X pp | — |

## Campaign Breakdown
| Campaign | Spend | Conv | CPA | CTR | Imp Share | Status |
|----------|-------|------|-----|-----|-----------|--------|
| [name] | $X,XXX | XX | $XX | X.X% | XX% | [Healthy/Needs Work/Critical] |

## Wasted Spend (30 days)
**Total:** $X,XXX (XX% of spend) — Annualized: ~$XX,XXX
- Non-converting keywords: $XXX across N keywords
- Irrelevant search terms: ~$XXX across N terms
- Display bleed: $XXX (if applicable)

## Top Issues (ranked by dollar impact)
1. **[Specific issue]** — $XXX impact — [Root cause]
2. **[Specific issue]** — $XXX impact — [Root cause]
3. **[Specific issue]** — $XXX impact — [Root cause]

## Recommended Actions
| # | Action | Expected Impact | Effort | Skill |
|---|--------|-----------------|--------|-------|
| 1 | [Specific action] | Save $XXX/month or gain X conversions | Low/Med/High | /ads |
| 2 | [Specific action] | ... | ... | ... |
| 3 | [Specific action] | ... | ... | ... |

## What's Working (keep doing this)
- [Specific positive finding with numbers]
- [Specific positive finding with numbers]
```

**Rules for the report:**
- Every issue must have a dollar amount or conversion count attached
- Every action must reference a specific campaign, keyword, or ad group by name
- "vs Industry Avg" column uses benchmarks from `industry-benchmarks.md` — leave blank if industry is unknown
- "vs Prior Period" compares current 30 days to previous 30 days. Use `getCampaignPerformance` with a 60-day range and split

### Freshness Notes for High-Volatility Recommendations

When making recommendations in these areas, prefix with a freshness disclaimer sourced from `../../shared/policy-registry.json`:
- Bid strategy recommendations (`bid-strategy-behavior`)
- Match type behavior advice (`match-type-behavior`)
- Experiment/testing guidance (`experiment-testing`)
- PMax configuration advice (`pmax-configuration`)

Format: _"Based on Google Ads behavior as of [last_verified date from registry]. Verify current behavior if this recommendation is critical to your strategy."_

Only add this for the high-volatility areas listed above.
