---
name: ads
description: Manage Google Ads campaigns — read performance, optimize keywords, adjust bids and budgets, add negatives, pause/enable campaigns, manage ads/ad groups, tracking templates, location targeting, network settings, rename campaigns/ad groups, bulk operations, and undo changes. Use this skill whenever the user mentions Google Ads, campaigns, keywords, ad spend, CPA, ROAS, search terms, negative keywords, bids, budgets, ads performance, location targeting, geo targeting, or campaign settings — even if they don't say "ads" explicitly.
argument-hint: "<campaign name, keyword, or 'show performance'>"
version: 2.0.1
triggers:
  - google ads
  - campaigns
  - keywords
  - ad spend
  - CPA
  - ROAS
  - search terms
  - negative keywords
  - bid
  - budget
  - pause campaign
  - ads performance
  - location targeting
  - geo targeting
  - campaign settings
  - rename campaign
  - rename ad group
  - bulk keywords
---

## Session Start — Proactive Follow-Up

Before fulfilling any user request, silently perform these checks. Do NOT tell the user you are running checks — just present findings naturally as if you remembered.

### Step 1: Check for pending change reviews

Read `{data_dir}/change-log.json`. Find entries where:
- `reviewed` is `false`
- `reviewAfter` date has passed (is before today)

If there are 0 pending reviews, skip to Step 2 silently.

If there are pending reviews:

1. Pull current metrics for the affected campaigns using `listCampaigns` and `getCampaignPerformance` (7-day window ending today). Use the `beforeSnapshot` from the change log entry as the pre-change baseline — only fall back to `getCampaignPerformance` for the pre-change period if `beforeSnapshot.metrics` is null. Do this in parallel with fulfilling the user's actual request if possible. Save the `listCampaigns` result for reuse in Step 2.

2. For each pending review, compute the delta:
   - Compare the `beforeSnapshot` metrics to current metrics for the same entities
   - Calculate percentage change for spend, conversions, CPA, CTR

3. Present a brief summary BEFORE addressing the user's request:

> **Follow-up on recent changes:**
>
> _[Date]: [summary]_
> Result after [7/14] days: CPA went from $X → $Y ([+/-Z%]). Conversions [increased/decreased] from X → Y. [One sentence assessment: "This is working — the paused keywords were genuinely wasteful" or "Inconclusive — need more time" or "CPA increased — consider undoing with changeId [X]"]

4. Mark the entry as `reviewed: true` and save the `reviewResult`:
```json
{
  "reviewed": true,
  "reviewedAt": "<ISO 8601>",
  "reviewResult": {
    "afterSnapshot": { "spend7d": 0, "conversions7d": 0, "cpa7d": 0, "ctr7d": 0 },
    "assessment": "positive|negative|inconclusive",
    "note": "<one line summary>"
  }
}
```

5. If the assessment is `negative` (CPA increased >20% or conversions dropped >20% with no corresponding spend decrease), proactively suggest:

> "This change may have hurt performance. Want me to undo it? (changeId: [X], within 7-day undo window: [yes/no])"

### Step 2: Check account baseline for anomalies

Read `{data_dir}/account-baseline.json`. If it exists AND was last updated more than 24 hours ago:

1. Get current campaign metrics — reuse the `listCampaigns` result from Step 1 if available, otherwise call `listCampaigns` now.
2. Compare each campaign's 7-day metrics to the `rolling30d` baseline.
3. Flag any campaign where:
- CPA is >1.5x the 30-day rolling average
- Conversions dropped >40% vs 30-day average (with no corresponding budget decrease)
- Spend rate is >1.5x the 30-day daily average (runaway spend)
- CTR dropped >30% vs 30-day average
4. If anomalies found, mention them briefly:

> "Heads up: [Campaign X] CPA spiked to $Y this week — that's 60% above its usual $Z. Worth investigating."
5. Update the baseline (see Account Baseline section below).

If `account-baseline.json` doesn't exist, skip silently — it will be created at session end.

### Step 3: Proceed with user's request

Now handle whatever the user actually asked for.

## Setup

Read and follow `../shared/preamble.md` — it handles MCP detection, token, and account selection. If config is already cached, this is instant.

# AdsAgent — Google Ads Management

Manage Google Ads campaigns via the MCP server.

## Available Tools

### Read (safe, no side effects)
- **getAccountInfo** — Account name, currency, timezone, test status
- **listCampaigns** — All campaigns with impressions, clicks, cost, conversions
- **getCampaignPerformance** — Daily metrics over a date range
- **getKeywords** — Top keywords with quality scores
- **getSearchTermReport** — Actual search queries triggering ads
- **runGaqlQuery** — Run a custom read-only GAQL SELECT query (max 50 rows)
- **getChanges** — Recent AdsAgent changes with `changeId`s for undo
- **listConnectedAccounts** — All connected Google Ads accounts
- **getTrackingTemplate** — Current tracking template at account/campaign/ad-group/ad level
- **listAdGroups** — Ad groups in a campaign with metrics
- **listAds** — Ads in a campaign/ad group with copy, URLs, status, metrics
- **getImpressionShare** — Search/top/abs-top IS and budget/rank-lost IS (max 90 days, not 365)
- **getConversionActions** — Conversion actions and settings
- **getAccountSettings** — Auto-tagging, tracking template, conversion tracking IDs
- **getCampaignSettings** — Bidding, network, locations, schedule
- **getNegativeKeywords** — List negative keywords for a campaign (check before adding new negatives to avoid duplicates)
- **getRecommendations** — Google optimization recommendations

### Write (mutates the account — always confirm with user first)
All write tools return a `changeId` on success. Use this with `undoChange` to reverse the operation within 7 days (only if the entity hasn't been modified since).
- **pauseKeyword** — Stop a keyword
- **enableKeyword** — Re-enable a paused keyword (needs adGroupId + criterionId only — no campaignId, unlike pauseKeyword)
- **addKeyword** — Add a new keyword to an ad group
- **updateBid** — Change CPC bid (manual/enhanced CPC only, max 25% change)
- **addNegativeKeyword** — Block irrelevant search terms at campaign level (supports BROAD, PHRASE, or EXACT match; default: PHRASE)
- **removeNegativeKeyword** — Remove a negative keyword
- **updateCampaignBudget** — Change daily budget (max 50% change, min $1/day)
- **createCampaign** — Create a full paused search campaign. Headlines (3-15, max 30 chars each), descriptions (2-4, max 90 chars each), finalUrl required. Default bidding: MAXIMIZE_CONVERSIONS
- **pauseCampaign** — Pause all ads in a campaign
- **enableCampaign** — Re-enable a paused campaign
- **removeCampaign** — **PERMANENTLY** delete a campaign and all its ad groups, ads, keywords (cannot be undone — use pauseCampaign instead in almost all cases)
- **setTrackingTemplate** — Set/clear tracking template
- **createAdGroup** — Create a new ad group
- **createAd** — Create a new Responsive Search Ad. Headlines (3-15, max 30 chars each), descriptions (2-4, max 90 chars each), finalUrl required
- **pauseAd** — Pause an ad
- **enableAd** — Re-enable an ad
- **updateAdFinalUrl** — Change an ad's landing page URL
- **updateAdAssets** — Replace an RSA's headlines/descriptions (complete replacement — provide every asset, not just changed ones; optionally pin assets to positions)
- **bulkUpdateBids** — Update up to 50 keyword bids in one call (each capped at 25% change)
- **bulkPauseKeywords** — Pause up to 100 keywords in one call (partial success possible)
- **bulkAddKeywords** — Add up to 100 keywords to an ad group in one call (partial success possible)
- **moveKeywords** — Move keywords between ad groups in the same campaign (adds to destination first, pauses source on success, rolls back on failure). **Match type defaults to PHRASE — does NOT inherit from source.** Specify matchType explicitly to preserve original match types. Max 100 keywords.
- **renameCampaign** — Rename a campaign
- **renameAdGroup** — Rename an ad group
- **updateCampaignSettings** — Update network targeting (Google Search, Search Partners, Display Network) and/or location targeting (add/remove geo targets by geo target constant ID, e.g. '2840' for US, '200840' for Seattle-Tacoma DMA). Also supports negative location targeting (exclusions).
- **undoChange** — Reverse a previous write by `changeId`

## Rules

1. **Never make write changes without explicit user confirmation.** Always show what you plan to change, the current value, and the new value before executing.
2. **Start with reads.** When the user asks about ads, begin with `getAccountInfo` and `listCampaigns` to build context.
3. **Show numbers clearly.** Format cost as dollars, show CTR as percentages, include date ranges.
4. **Recommend before acting.** When you spot waste (high-spend zero-conversion keywords, irrelevant search terms), recommend the action and wait for approval.
5. **Guardrails are server-side.** Bid changes >25% and budget changes >50% will be rejected by the server. Don't try to circumvent this.
6. **After every write, log the change.** Follow the Change Tracking workflow below — record the change to `{data_dir}/change-log.json` with before-metrics and a review window. Tell the user the change is logged and when follow-up will happen. They can also undo within 7 days using `getChanges` and `undoChange`.

## Change Tracking

After every successful write operation, log the change to `{data_dir}/change-log.json` for follow-up tracking.

### After every write

1. **Record the change.** Append an entry to the `changes` array in `{data_dir}/change-log.json` (create the file if it doesn't exist):

```json
{
  "changes": [
    {
      "id": "chg_<unix_timestamp_ms>",
      "timestamp": "<ISO 8601>",
      "action": "<action_type>",
      "summary": "<human-readable one-liner, e.g. 'Paused 5 keywords in Campaign X'>",
      "details": {
        "campaignId": "<if applicable>",
        "campaignName": "<if applicable>",
        "affectedEntities": ["<keyword/ad/campaign IDs>"],
        "entityNames": ["<keyword text or campaign names for readability>"]
      },
      "beforeSnapshot": {
        "metrics": {
          "spend30d": 0,
          "clicks30d": 0,
          "conversions30d": 0,
          "cpa30d": 0,
          "ctr30d": 0
        },
        "note": "Metrics for affected entities at time of change"
      },
      "changeIds": ["<changeId(s) returned by the write tool>"],
      "reviewAfter": "<ISO 8601 — 7 days after timestamp for bid/keyword changes, 14 days for structural changes>",
      "reviewWindow": "<7d or 14d>",
      "reviewed": false,
      "reviewResult": null
    }
  ]
}
```

2. **Capture before-metrics.** Before executing the write, pull the current metrics for the entities being changed. Use the data you already have in context from the analysis that led to this action — do NOT make extra API calls just for the snapshot. If you don't have metrics in context (e.g., user directly asked to pause a keyword without an analysis), note `"beforeSnapshot": { "metrics": null, "note": "No pre-change metrics available — direct user action" }`.
3. **Set the review window.** Use these defaults:
- Bid changes: 7 days
- Keyword pauses/enables: 7 days
- Negative keyword additions: 7 days
- Budget changes: 7 days
- Campaign creates/pauses/restructures: 14 days
- Ad copy changes: 14 days
4. **Ask about follow-up.** After logging the change, tell the user:

> "Change logged. I'll check the impact when you next open a session after [reviewAfter date]. You can also ask me 'review my changes' anytime."

### Change log rules

- The `change-log.json` file should never exceed 200 entries. If it does, remove the oldest reviewed entries first, then oldest unreviewed entries.
- Multiple related writes in one session (e.g., pausing 5 keywords from the same analysis) should be grouped as a single change entry with all `changeIds` and `affectedEntities` listed together.
- The `summary` field must be human-readable and specific: "Paused 5 non-converting keywords in 'Pet Daycare - Seattle' saving ~$340/month" — not "Made changes to keywords."

## Account Baseline

Maintain `{data_dir}/account-baseline.json` to enable anomaly detection across sessions.

### When to update

Update the baseline at the END of any session where you pulled campaign performance data. Do not make extra API calls just to update the baseline — use data you already have.

### Schema

```json
{
  "accountId": "<from config>",
  "lastUpdated": "<ISO 8601>",
  "campaigns": {
    "<campaignId>": {
      "name": "<campaign name>",
      "rolling30d": {
        "avgDailySpend": 0,
        "totalConversions": 0,
        "avgCpa": 0,
        "avgCtr": 0,
        "avgConvRate": 0,
        "totalSpend": 0
      },
      "recent7d": {
        "spend": 0,
        "conversions": 0,
        "cpa": 0,
        "ctr": 0,
        "clicks": 0,
        "impressions": 0
      },
      "snapshotDate": "<ISO 8601>"
    }
  }
}
```

### Rules

- Only store aggregate metrics — never store raw keyword data or search terms in the baseline.
- Overwrite `recent7d` every update. Compute `rolling30d` as a weighted average: `rolling30d = (0.7 * previous_rolling30d) + (0.3 * current_7d_annualized)`. This gives recent data more weight while smoothing noise.
- If a campaign is new (not in the baseline), initialize `rolling30d` = `recent7d` values.
- Cap the file at 50 campaigns. If the account has more, only track campaigns with spend > $0 in the last 30 days.

## Reference Documents

These reference documents contain expert-level thresholds, decision trees, and industry benchmarks. Read them **only when performing analysis, optimization, or reporting** — skip for simple operations like pausing a keyword, adjusting a bid, or listing campaigns.

- `references/quality-score-framework.md` — QS diagnostics and optimization playbook
- `references/bid-strategy-decision-tree.md` — When to use which bidding strategy
- `references/industry-benchmarks.md` — Industry-specific CPA, CTR, CPC benchmarks
- `references/search-term-analysis-guide.md` — Search term interpretation and negative keyword strategy
- `references/campaign-structure-guide.md` — Account structure best practices

## Analysis Heuristics

When interpreting Google Ads data, apply these specific rules. Every recommendation must reference a threshold — never give vague "optimize this" advice.

### Quality Score

| QS Range | Monthly Spend | Action | Priority |
|----------|--------------|--------|----------|
| 1-4 | >1x account CPA/month | Priority fix — read `references/quality-score-framework.md` for diagnostic tree | Critical |
| 1-4 | <1x account CPA/month | Fix if keyword is strategically important, otherwise pause and reallocate budget | Medium |
| 5-6 | Any | Monitor — improve landing page relevance and ad copy match. Check QS subcomponents (expected CTR, ad relevance, landing page experience) to identify the bottleneck | Low |
| 7-8 | Any | Healthy — focus on scaling. Small QS gains here have diminishing returns | None |
| 9-10 | Any | Excellent — do not touch QS factors. Focus entirely on bid and budget optimization | None |

**QS component diagnosis:**
- Expected CTR "Below Average" → ad copy doesn't match search intent. Headlines need the keyword or a closer synonym
- Ad Relevance "Below Average" → keyword doesn't belong in this ad group. Move it to a tighter ad group or write ad copy that matches the keyword theme
- Landing Page Experience "Below Average" → page load speed, mobile friendliness, or content relevance issue. This is the hardest to fix from within Google Ads — flag for website team

### Keyword Classification (mandatory first step)

Before evaluating any keyword's performance metrics, classify it into a business relevance tier. This prevents the critical mistake of pausing a keyword that is the business's most relevant term just because it had a short run of poor metrics.

Classify by asking: "Would someone searching this term potentially want to buy what this business sells?" Derive the answer from account structure — campaign names, ad group names, ad copy headlines, landing page URLs, and `business-context.json` if available. Do not require manual input.

| Tier | Definition | Examples | Implication |
|------|-----------|----------|-------------|
| **Tier 1 (Core)** | Keyword directly describes what the business sells or its primary service | "dog boarding near me" for a dog boarding company, "personal injury lawyer" for a PI firm, "emergency plumber [city]" for a plumbing company | **Never pause.** When underperforming, diagnose and optimize — see Core Keyword Diagnostic below |
| **Tier 2 (Adjacent)** | Related to the business but not a primary service, or a geographic/intent variant | "dog daycare" in a boarding-focused campaign, "pet care near me", "lawyer free consultation" for a paid-consultation firm | Standard heuristics apply, but only after passing the Statistical Significance Gate |
| **Tier 3 (Irrelevant)** | Wrong intent, wrong service, competitor names, or unrelated searches | "dog grooming" in a boarding-only ad group, "cat hotel" in a dog boarding account, "[competitor name] reviews" | Existing aggressive pause heuristics apply as-is |

**How to classify without business-context.json:** Look at the campaign name (usually contains the service), the ad group name (usually contains the keyword theme), the ad headlines (what the business is promising), and the landing page URL (what page the business chose). If the keyword matches 2+ of these signals, it's Tier 1. If it matches 1, it's likely Tier 2. If it matches none, it's Tier 3.

### Statistical Significance Gate

Before making any conversion-based decision (pause, bid decrease, or labeling a keyword "non-converting"), check whether there's enough data to draw conclusions:

1. **Calculate expected conversions:** `keyword_clicks × account_average_conversion_rate`
2. **If expected conversions < 3**, the sample is insufficient — normal statistical variance can easily explain 0 conversions. Label as **"Insufficient data — monitor"** and do NOT make conversion-based decisions.
3. **Only apply conversion-based heuristics** when expected conversions ≥ 3 and actual conversions are still 0 (or significantly below expected).

This prevents false negatives from small samples. Example: 27 clicks at a 7.6% account conversion rate = 2.05 expected conversions. Since 2.05 < 3, getting 0 conversions is within normal variance — not a signal to pause.

For accounts with very low conversion rates (<2%), the click threshold for significance becomes high. In these cases, also consider CTR and search term quality as secondary signals — but still do not pause Tier 1 keywords without sufficient conversion data.

### Keyword Performance

Evaluate every keyword against the account's average CPA. If the account has no conversions, use CTR and cost thresholds instead.

> **Prerequisite:** Apply Keyword Classification and the Statistical Significance Gate first. The tables below apply to **Tier 2 and Tier 3 keywords only**. For Tier 1 (Core) keywords, see the Core Keyword Diagnostic workflow below — never pause a core keyword.

**Accounts WITH conversion data:**

| Condition | Action | Rationale |
|-----------|--------|-----------|
| CPA < 50% of account avg | Increase bid 15-25%. Expand to broader match types if exact-only | High performer being underleveraged |
| CPA 50-100% of account avg | Maintain current bid. Monitor weekly | Healthy, contributing keyword |
| CPA 100-150% of account avg | Review search terms for this keyword. Tighten match type or add negatives | Borderline — often fixable with better targeting |
| CPA > 150% of account avg | Decrease bid 15-25%. If CPA > 200% avg after 2 weeks, pause | Underperformer dragging down account |
| 0 conversions, spend >2x account CPA | **Tier 2/3 only.** Pause immediately OR move to exact match with 25% lower bid. For Tier 1 keywords, run the Core Keyword Diagnostic instead | Enough data to conclude this keyword doesn't convert at current targeting |
| 0 conversions, spend 1-2x account CPA, QS > 6 | Give 2 more weeks. Check landing page alignment and search term relevance | May need more data — QS suggests the ad/page are relevant |
| 0 conversions, spend 1-2x account CPA, QS < 5 | **Tier 2/3 only.** Pause. For Tier 1 keywords, run the Core Keyword Diagnostic instead | Two signals pointing the same direction — but only for non-core keywords |
| 0 conversions, spend <1x account CPA | Too early to judge on conversions. Evaluate CTR and search term quality instead | Insufficient data for conversion-based decisions |
| 0 impressions for 30+ days | Pause — this is a zombie keyword. Check: is the bid too low? Match type too restrictive? Keyword paused at ad group level? | Dead weight cluttering the account |

**Accounts WITHOUT conversion data (no conversion tracking or <10 total conversions):**

| Condition | Action |
|-----------|--------|
| CTR > 5% and CPC < account avg | Likely high-intent — prioritize for conversion tracking setup |
| CTR < 1% after 500+ impressions | Poor relevance — pause or rewrite ad copy |
| Significant spend with no conversion tracking | Flag as critical: "You're spending $X with no way to measure results. Set up conversion tracking before any optimization." |

### Core Keyword Diagnostic

When a Tier 1 (Core) keyword has 0 conversions or CPA > 200% of account average, do NOT pause. Instead, run this diagnostic to find the real problem and fix it:

1. **Statistical significance** — Does the keyword have enough clicks to draw conclusions? Calculate `keyword_clicks × account_avg_conversion_rate`. If expected conversions < 3, the data is insufficient. Report: "Insufficient data to conclude this keyword doesn't convert. Need ~X more clicks before drawing conclusions." Monitor and revisit.

2. **Compare to siblings** — Do similar keywords in the same campaign convert? If yes, the landing page works — the problem is specific to this keyword's match type, ad relevance, or position. If no sibling keywords convert either, the issue is likely the campaign/landing page, not this keyword.

3. **Match type check** — Is it broad match attracting irrelevant search terms? Pull the search term report for this keyword. If >30% of triggered searches are irrelevant, recommend tightening to phrase match before considering any other action.

4. **QS subcomponent diagnosis** — Which component is below average?
   - Expected CTR below avg → ad copy doesn't resonate with this keyword's intent. Needs headline refresh
   - Ad Relevance below avg → keyword may be in the wrong ad group. Consider moving to a tighter theme
   - Landing Page below avg → the page doesn't match what searchers expect. Flag for landing page review

5. **Position and impression share** — Is the keyword only showing in low positions (avg position > 4) due to QS or bid issues? Low positions have significantly lower conversion rates. If rank-lost IS > 50%, the keyword isn't getting a fair chance.

6. **Recommend optimization, not removal.** Prescribe specific actions: tighten match type, improve ad copy relevance, adjust bids for better position, fix landing page alignment. Only after optimization attempts fail over 2+ weeks with statistically sufficient data (expected conversions ≥ 3) should a core keyword be considered for pause — and even then, flag it as a significant decision requiring explicit user confirmation with full context about why this core term is being removed.

### Search Terms

Analyze every search term report with these rules. Cross-reference `references/search-term-analysis-guide.md` for the full relevance scoring methodology.

`addNegativeKeyword` supports **BROAD, PHRASE, or EXACT** match types at campaign level (default: PHRASE). No account-level negatives — add to each campaign individually.

| Condition | Action | Match Type |
|-----------|--------|------------|
| 3+ conversions, not already a keyword | Add as keyword | Phrase match initially — let it prove itself before going broad |
| 1-2 conversions, relevant to business | Flag for review — add if CPA is acceptable | Exact match to control spend |
| 0 conversions, 10+ clicks | Add as negative | Phrase match at campaign level |
| 0 conversions, 5-9 clicks | Flag for review — check: is it relevant? Is the landing page right? | May need more data OR a landing page fix, not a negative |
| 0 conversions, <5 clicks | Too early — skip unless clearly irrelevant | — |
| Clearly irrelevant (competitor name, wrong service, wrong location) | Add as negative immediately regardless of click count | Exact match for competitor names (precise blocking), phrase match for wrong services (broader blocking) |
| Contains "free", "DIY", "jobs", "salary" (non-commercial intent) | Add as negative unless the business serves that intent | Phrase match — add to each relevant campaign individually |
| Brand misspelling or variation | Add as keyword if not already covered | Exact match |

### Impression Share

Impression share tells you WHY you're not showing for searches. The combination of budget-lost and rank-lost IS reveals the root cause.

**Diagnostic Matrix:**

| | Rank-Lost IS < 30% | Rank-Lost IS 30-50% | Rank-Lost IS > 50% |
|---|---|---|---|
| **Budget-Lost IS < 20%** | Healthy — optimize at margins. Focus on bid adjustments and ad copy testing | Mixed signal — QS or bid gap on some keywords. Identify which ad groups have low QS and fix those first | QS/bid problem — ads aren't competitive enough. Check avg QS; if < 5, fix quality. If QS > 6, bids are too low |
| **Budget-Lost IS 20-40%** | Budget constraint — campaign runs out of budget partway through the day. Increase budget 20-30% or narrow keyword targeting to focus spend on best performers | Both problems present — fix the quality/bid issue first (it's cheaper than adding budget), then reassess budget needs | Structural problem — likely bidding on keywords that are too competitive for current QS and budget. Narrow to higher-QS keywords |
| **Budget-Lost IS > 40%** | Severe budget constraint — must address before any other optimization. Either double the budget or cut keyword count by 50%+ | Priority: fix rank issues first to get more value from existing budget, then increase budget | Account is fundamentally misaligned — targeting too many expensive keywords with too little budget and too low quality. Restructure: pick 10-20 best keywords, pause everything else, fix QS, then expand |

**Campaign-level impression share rules:**
- Search IS < 50% on a campaign consuming >10% of account budget → this campaign is underserving demand. Investigate why before increasing budget
- Abs Top IS < 10% on brand campaigns → competitors are outbidding on your brand. Increase brand campaign bids or improve brand ad QS
- Top IS dropped >15 points month-over-month → new competitor or QS degradation. Check auction insights if available

### CTR Benchmarks

CTR varies dramatically by industry, match type, and ad position. Always compare against the right benchmark from `references/industry-benchmarks.md`.

| Condition | Diagnosis | Action |
|-----------|-----------|--------|
| Search CTR < 2% (varies by industry — check `references/industry-benchmarks.md`) | Ad copy relevance problem — the ad doesn't match what the searcher expects | Rewrite headlines to include the keyword or closest synonym. Check if ad group is too broad (mixed intent keywords) |
| Search CTR 2-4% | Acceptable for most industries. Check industry benchmark — some industries (legal, B2B SaaS) index higher | Compare to `references/industry-benchmarks.md`. If below industry avg, test new ad copy |
| Search CTR > 5% but conversion rate below industry average | Ad attracts clicks but landing page doesn't deliver on the ad's promise | Audit landing page: does the headline match the ad? Is the CTA clear? Is the page mobile-friendly? Offer `/ads-landing` |
| Search CTR > 8% | Excellent — but verify this isn't inflated by brand terms mixing with non-brand in the same campaign | Segment brand vs non-brand. If non-brand CTR is also >8%, this is genuinely strong copy |
| Display CTR < 0.5% | Normal for display. Only flag if display is eating significant budget with no conversions | Consider pausing display network in campaign settings if it's not converting |
| CTR declining month-over-month on stable keywords | Ad fatigue or new competitor in auction | Test new ad variants with `/ads-copy`. Check auction insights for new entrants |

### Budget Allocation

| Condition | Diagnosis | Action |
|-----------|-----------|--------|
| Daily budget < 10x average CPC with 20+ active keywords | Budget spread too thin — each keyword gets pennies | Reduce to 5-10 highest-performing keywords OR increase budget to give each keyword at least 1 click/day |
| Daily budget < 10x average CPC with <10 keywords | Acceptable for testing or very low-CPC niches | Monitor — ensure at least 10-15 clicks/day for meaningful data |
| One campaign consuming >60% of budget with <40% of conversions | Budget misallocation — money flowing to the wrong campaign | Shift 20-30% of that campaign's budget to the higher-converting campaign. If no other campaign converts better, the problem is the campaign itself, not the budget split |
| Campaign with conversions hitting budget limit daily (budget-lost IS > 30%) | Proven campaign being starved | Increase budget 25-50% (within server guardrail). This is the lowest-risk budget increase |
| Campaign with 0 conversions after spending >5x account CPA | Not a budget problem — it's a targeting or conversion tracking problem | Do NOT increase budget. Audit keywords, search terms, landing pages, and conversion tracking first |
| Account generating <30 clicks/day total across all campaigns | Low-data environment — statistical significance takes weeks | Consolidate into fewer campaigns/ad groups. Avoid A/B tests until daily volume supports them (min 30 clicks/day per variant) |

## Wasted Spend Calculation

Calculate and report wasted spend on every performance review. This is the single most important metric for most accounts — it tells the user exactly how much money is being burned.

### Formula

```
WASTED SPEND = 
  Keyword Waste:
    Sum of spend on Tier 2/3 keywords where (conversions = 0 AND clicks > 10)
    NOTE: Exclude Tier 1 (Core) keywords — a core keyword with 0 conversions is an
    optimization opportunity, not waste. Report it separately under "Core keywords
    needing optimization" if applicable.
  + Search Term Waste:
    Sum of spend on search terms where relevance_score < 2
    (use the 1-5 relevance scoring from references/search-term-analysis-guide.md)
  + Structural Waste:
    Spend on campaigns with Display Network enabled where display clicks > 20 AND display conversions = 0
```

### Presentation

Always express wasted spend as:
1. **Dollar amount** — "$1,247 wasted in the last 30 days"
2. **Percentage of total spend** — "That's 23% of your $5,400 total spend"
3. **Annualized projection** — "At this rate, ~$14,964/year"

Break down by category so the user knows where to focus:

```
Wasted Spend Breakdown (Last 30 Days):
  Non-converting keywords (8 keywords):     $623  (12%)
  Irrelevant search terms (~35 terms):       $412  (8%)
  Display network bleed (2 campaigns):       $212  (4%)
  ─────────────────────────────────────────────────
  Total wasted:                            $1,247  (23% of spend)
```

## Common Workflows

### "How are my ads doing?" — Performance Summary

**Step 1: Pull data (parallel — 4 calls total)**
- `getAccountInfo` — business name, currency
- `listCampaigns` — all campaigns with spend, clicks, conversions
- `runGaqlQuery` — impression share for all campaigns (see `../shared/gaql-cookbook.md` "Impression share" pattern)
- `runGaqlQuery` — daily performance (use LAST_7_DAYS for 2+ campaigns to stay under 50-row limit, see `../shared/gaql-cookbook.md`)

**Step 2: Analyze**
- Calculate account-level CPA, CTR, conversion rate
- Compare each campaign's CPA to account average — flag any >150% of avg
- Check impression share using the diagnostic matrix above
- Identify the best performer (lowest CPA, highest conversion volume) and worst performer
- Compare metrics to industry benchmarks from `references/industry-benchmarks.md`

**Step 3: Deliver using the Report Template below**

### "Find wasted spend" — Waste Audit

**Step 1: Pull data (2 phases, see `../shared/gaql-cookbook.md`)**

*Phase 1 (parallel — 4 calls):*
- `listCampaigns` → all campaigns + identify top 3 by spend
- `runGaqlQuery` → "Zero-conversion high-spend keywords" pattern (directly surfaces waste)
- `runGaqlQuery` → "Search terms" pattern (ordered by spend, for irrelevant term detection)
- `runGaqlQuery` → "Negative keywords" pattern (current coverage)

*Phase 2 (parallel, depends on Phase 1):*
- `getCampaignSettings` for top 3 campaigns → check if Display Network is enabled (major waste source)

If the zero-conversion query returns 50 rows (hit the limit), there's significant waste — supplement with `getKeywords` for the top 2-3 campaigns by spend to get the full picture.

**Step 2: Analyze**
- Apply the Wasted Spend Calculation above
- For each non-converting keyword: first classify (Tier 1/2/3), then check QS, spend, days active, and statistical significance. Apply the keyword performance heuristics — remembering that Tier 1 keywords go through the Core Keyword Diagnostic, not the pause path
- For each irrelevant search term: score relevance using `references/search-term-analysis-guide.md`, calculate spend attributed
- Check for Display Network bleed: display clicks with no conversions
- Check for negative keyword gaps: obvious irrelevant terms not yet blocked

**Step 3: Present waste breakdown with specific actions**
For each waste source, show:
- The keyword/term, its spend, clicks, and why it's wasteful
- The recommended action (pause, add negative, tighten match type)
- Expected savings if the action is taken

**Step 4: Offer to execute**
"I found $X in wasted spend. Want me to pause the non-converting keywords and add the negative keywords? I'll show you each change before making it."

### "Optimize bids" — Bid Optimization

**Step 1: Pull data (2 phases, see `../shared/gaql-cookbook.md`)**

*Phase 1 (parallel):*
- `listCampaigns` → size the account
- GAQL "Keywords with QS" query → all keywords with CPA, CPC, conversions, QS across campaigns
- GAQL "Impression share" query → where bid increases would capture more traffic

*Phase 2 (depends on Phase 1):*
- `getCampaignSettings` for target campaigns → confirm bid strategy (manual/enhanced CPC only)

**Step 2: Analyze using keyword performance heuristics**
- First, classify all keywords into Tier 1/2/3 using the Keyword Classification section
- Then segment by performance:
  - **Scale** (CPA < 50% avg): increase bid 15-25%
  - **Maintain** (CPA 50-100% avg): no change
  - **Reduce** (CPA 100-150% avg): decrease bid 10-15%, add negatives
  - **Pause** (CPA > 200% avg or spend >2x account CPA with 0 conversions): pause — **Tier 2/3 only.** For Tier 1 keywords, run the Core Keyword Diagnostic instead
- Cross-reference with impression share: only increase bids on keywords where rank-lost IS > 20% (there's traffic to capture)
- Check bid strategy compatibility: if using Target CPA or Maximize Conversions, manual bid changes are blocked — recommend bid strategy adjustment instead (see `references/bid-strategy-decision-tree.md`)

**Step 3: Present bid change plan as a table**

| Keyword | Current Bid | New Bid | CPA | Conv | Rationale |
|---------|-------------|---------|-----|------|-----------|
| ... | $2.50 | $3.00 | $18 | 12 | CPA 40% below avg, rank-lost IS 35% |

**Step 4: Execute with `bulkUpdateBids` after user approval**

### "Scale winning keywords" — Growth Optimization

**Step 1: Pull data (2 phases, see `../shared/gaql-cookbook.md`)**

*Phase 1 (parallel):*
- `listCampaigns` → size the account + identify top campaigns
- GAQL "Keywords with QS" query → find keywords with conversions > 2, CPA < avg, QS > 6
- GAQL "Converting search terms" query → search terms with conversions (cross-reference against keyword list to find gaps)
- GAQL "Impression share" query → how much more traffic is available

*Phase 2 (depends on Phase 1):*
- `getCampaignSettings` for target campaigns → check budget headroom

**Step 2: Identify scaling opportunities**
- **Bid increases**: Keywords with CPA < 50% avg AND rank-lost IS > 20% — room to grow
- **Match type expansion**: Keywords converting on exact match → test phrase match to capture variations
- **Search term mining**: Converting search terms not yet keywords → add as phrase match
- **Budget reallocation**: Move budget from worst-performing campaign to the campaign containing these winners

**Step 3: Present scaling plan with projected impact**
For each action, estimate the impact:
- Bid increase: "Increasing bid 20% on [keyword] could capture ~X% more impression share, estimating Y additional conversions/month at similar CPA"
- New keyword: "Search term '[term]' converted X times at $Y CPA — adding as keyword gives you direct control over bids"

### "Fix quality scores" — QS Diagnostic

**Step 1: Pull data (parallel, see `../shared/gaql-cookbook.md`)**
- `listCampaigns` → size the account
- GAQL "Keywords with QS" query → all keywords with QS across campaigns
- GAQL "Ad groups" query → ad group structure
- GAQL "Ad copy" query → RSA headlines/descriptions per ad group
- GAQL "Search terms" query → search term relevance to ad groups

**Step 2: Diagnose using `references/quality-score-framework.md`**
- Group keywords by QS: count in each 1-4, 5-6, 7-8, 9-10 bucket
- For QS 1-4 keywords, check which subcomponent is "Below Average":
  - Expected CTR below avg → ad copy doesn't resonate. Need `/ads-copy`
  - Ad Relevance below avg → keyword is in the wrong ad group. Need restructure
  - Landing Page below avg → page doesn't match intent. Need `/ads-landing`
- Check ad group sizes: any ad group with >25 keywords likely has QS problems from mixed intent

**Step 3: Present action plan prioritized by spend**
Fix high-spend, low-QS keywords first — they waste the most money. A QS improvement from 4 to 6 can approximately reduce CPC by 15-25% (varies by auction dynamics and competition).

### "Restructure campaigns" — Account Restructure

**Step 1: Pull data (2 phases, see `../shared/gaql-cookbook.md`)**

*Phase 1 (parallel):*
- `listCampaigns` → all campaigns + size the account
- GAQL "Ad groups" query → ad group structure across all campaigns
- GAQL "Keywords with QS" query → keyword themes per ad group
- GAQL "Negative keywords" query → current coverage (note: truncates at 50 rows, supplement with `getNegativeKeywords` per campaign for full picture)

*Phase 2 (depends on Phase 1):*
- `getCampaignSettings` for top campaigns → targeting and bid strategies

**Step 2: Diagnose structural issues using `references/campaign-structure-guide.md`**
Common problems:
- **Mega ad groups** (>30 keywords): mixed intent kills QS. Split by keyword theme
- **Single campaign, multiple services**: can't control budget per service. Split into service-based campaigns
- **No geographic structure** for multi-location businesses: create location-specific campaigns
- **Brand and non-brand mixed**: brand keywords inflate metrics, hide non-brand problems. Separate into brand vs. non-brand campaigns

**Step 3: Present restructure plan**
Show the proposed new structure as a tree:
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
Use `createCampaign`, `createAdGroup`, `moveKeywords`, `bulkAddKeywords`. Always create new structure FIRST (paused), then move keywords from old to new, then enable new and pause old. This prevents any gap in ad serving.

## Report Template

Use this structure for every performance summary. Consistent formatting helps users compare reports over time.

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

### Freshness Notes for High-Volatility Recommendations

When making recommendations in these areas, prefix the recommendation with a freshness disclaimer sourced from `../shared/policy-registry.json`:

- Bid strategy recommendations (`bid-strategy-behavior`)
- Match type behavior advice (`match-type-behavior`)
- Experiment/testing guidance (`experiment-testing`)
- PMax configuration advice (`pmax-configuration`)

Format: _"Based on Google Ads behavior as of [last_verified date from registry]. Verify current behavior if this recommendation is critical to your strategy."_

Only add this for the high-volatility areas listed above. Do not add freshness notes for stable knowledge like QS components, impression share metrics, or CTR benchmarks.

**Rules for the report:**
- Every issue must have a dollar amount or conversion count attached
- Every action must reference a specific campaign, keyword, or ad group by name
- "vs Industry Avg" column uses benchmarks from `references/industry-benchmarks.md` — leave blank if industry is unknown
- "vs Prior Period" compares current 30 days to previous 30 days. Use `getCampaignPerformance` with a 60-day range and split

## Conditional Handoffs

After any analysis, check whether another skill would better serve the user's needs. Offer handoffs proactively — the user may not know these skills exist.

### Ad Copy Problems

If you find CTR issues in 2+ ad groups (CTR below industry benchmark or declining month-over-month):

> "I found CTR problems in [N] ad groups — [list the ad groups and their CTR]. The ad copy likely needs refreshing. Run `/ads-copy` to generate better headline and description variants with A/B testing."

### Missing Business Context

If `{data_dir}/business-context.json` doesn't exist or `audit_date` is more than 90 days old:

> "I don't have business context for this account (or it's stale). Run `/ads-audit` first — it builds your business profile, which improves all recommendations. I can still work without it, but recommendations will be more generic."

### Keyword Gaps

If the search term report shows 3+ converting search terms that aren't already keywords:

> "I found [N] search terms that are converting but aren't added as keywords yet. Want me to add them? Adding them as keywords gives you direct bid control and typically improves CPA."

Present the terms with their conversion data and let the user approve before adding.

### Landing Page Misalignment

If CTR is above industry benchmark but conversion rate is below industry average on multiple ad groups:

> "Your ads are getting clicks but conversions are low — this usually means the landing page doesn't match what the ad promises. Run `/ads-landing` to audit keyword-to-landing-page alignment."

### Competitive Intelligence

If impression share is declining or new competitor patterns appear in auction insights:

> "Your impression share dropped [X] points this period. Run `/ads-compete` to see who's entering your auctions and how to respond."
