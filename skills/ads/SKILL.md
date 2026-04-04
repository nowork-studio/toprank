---
name: ads
description: Manage Google Ads campaigns — read performance, optimize keywords, adjust bids and budgets, add negatives, pause/enable campaigns, manage ads/ad groups, tracking templates, location targeting, network settings, rename campaigns/ad groups, bulk operations, and undo changes. Use this skill whenever the user mentions Google Ads, campaigns, keywords, ad spend, CPA, ROAS, search terms, negative keywords, bids, budgets, ads performance, location targeting, geo targeting, or campaign settings — even if they don't say "ads" explicitly.
version: 2.0.0
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

## MCP Server Detection

Before calling any Google Ads tool, detect which MCP server is available:

1. Check for AdsAgent tools: try calling `mcp__adsagent__listConnectedAccounts`
2. If not found, check for Google's official MCP: look for tools matching `mcp__google_ads_mcp__*` in the available tools
3. If neither exists, guide the user:

> No Google Ads MCP server detected. The easiest setup:
>
> 1. Get a free API key at [adsagent.org](https://www.adsagent.org)
> 2. Set the environment variable: `export ADSAGENT_API_KEY=your_key`
> 3. Restart Claude Code (the toprank plugin's .mcp.json will auto-configure the server)
>
> Or configure any Google Ads MCP server manually in your MCP settings.

Use whichever MCP server's tool prefix is available for all subsequent calls in this session.

# AdsAgent — Google Ads Management

Manage Google Ads campaigns via the MCP server.

## Configuration

All persistent config lives in `~/.adsagent/config.json`. This file survives across sessions and works in every context — Claude Code, Claude Desktop, MCP servers, etc.

The config file has this shape:

```json
{
  "apiKey": "asa_...",
  "accountId": "1234567890"
}
```

## Onboarding

Before doing anything else, check whether the user is set up. Follow these steps in order — stop at the first issue and resolve it before continuing.

### Step 0: Check for the AdsAgent MCP server

Follow the **MCP Server Detection** section above. If no MCP server is found, guide the user through setup before continuing.

### Step 1: Check for token

Read `~/.adsagent/config.json` (create `~/.adsagent/` if it doesn't exist).

Look for `apiKey` (the token) in the config file. If it's present, skip to Step 2.

If it's missing, tell the user:

> To use AdsAgent, you need a free token. You can get one from [adsagent.org](https://www.adsagent.org).
> Once you have it, paste it here and I'll save it for you.

When the user provides the key, save it to `~/.adsagent/config.json`.

Then continue to Step 2.

### Step 2: Select a Google Ads account

Look for `accountId` in the config file. If it's present, proceed to fulfil the user's request.

If `accountId` is not set:

1. Run `listConnectedAccounts` to get all connected Google Ads accounts.
2. **If there is exactly one account**, save it automatically — no need to bother the user. Write `accountId` to `~/.adsagent/config.json` and tell the user which account was selected (show account name and ID).
3. **If there are multiple accounts**, present them as a numbered list showing account name and ID, then ask the user to pick one. Save their choice to `~/.adsagent/config.json`.
4. **If there are zero accounts**, tell the user they don't have any Google Ads accounts connected yet and direct them to [adsagent.org](https://www.adsagent.org) to connect one.

### Switching accounts

If the user wants to switch accounts, run `listConnectedAccounts`, let them pick, and update `accountId` in `~/.adsagent/config.json`.

## Calling tools

Tools are available directly via the MCP server. Call them using the detected prefix (see MCP Server Detection above).

**With AdsAgent MCP (default):**
- `mcp__adsagent__listCampaigns` with `accountId` parameter
- `mcp__adsagent__getKeywords` with `accountId` and `campaignId`
- etc.

**With Google's official MCP:**
- Tool names follow the `mcp__google_ads_mcp__*` pattern
- Consult the server's tool list for exact names

Always pass `accountId` from `~/.adsagent/config.json` to every tool call (except `listConnectedAccounts`). All responses are JSON.

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
- **getImpressionShare** — Search/top/abs-top IS and budget/rank-lost IS
- **getConversionActions** — Conversion actions and settings
- **getAccountSettings** — Auto-tagging, tracking template, conversion tracking IDs
- **getCampaignSettings** — Bidding, network, locations, schedule
- **getNegativeKeywords** — List negative keywords for a campaign (check before adding new negatives to avoid duplicates)
- **getRecommendations** — Google optimization recommendations

### Write (mutates the account — always confirm with user first)
All write tools return a `changeId` on success. Use this with `undoChange` to reverse the operation within 7 days.
- **pauseKeyword** — Stop a keyword
- **enableKeyword** — Re-enable a paused keyword
- **addKeyword** — Add a new keyword to an ad group
- **updateBid** — Change CPC bid (manual/enhanced CPC only, max 25% change)
- **addNegativeKeyword** — Block irrelevant search terms (phrase match)
- **removeNegativeKeyword** — Remove a negative keyword
- **updateCampaignBudget** — Change daily budget (max 50% change)
- **createCampaign** — Create a full paused search campaign
- **pauseCampaign** — Pause all ads in a campaign
- **enableCampaign** — Re-enable a paused campaign
- **setTrackingTemplate** — Set/clear tracking template
- **createAdGroup** — Create a new ad group
- **createAd** — Create a new Responsive Search Ad
- **pauseAd** — Pause an ad
- **enableAd** — Re-enable an ad
- **updateAdFinalUrl** — Change an ad's landing page URL
- **updateAdAssets** — Replace an RSA's headlines/descriptions (complete replacement — provide every asset, not just changed ones; optionally pin assets to positions)
- **bulkUpdateBids** — Update up to 50 keyword bids in one call (each capped at 25% change)
- **bulkPauseKeywords** — Pause up to 100 keywords in one call (partial success possible)
- **bulkAddKeywords** — Add up to 100 keywords to an ad group in one call (partial success possible)
- **moveKeywords** — Move keywords between ad groups in the same campaign (adds to destination first, pauses source on success, rolls back on failure)
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
6. **After every write, note the `changeId`.** Tell the user they can undo the change within 7 days. Use `getChanges` to review recent operations.

## Reference Documents

Before performing any analysis, read the following reference documents for expert-level context:

- `references/quality-score-framework.md` — QS diagnostics and optimization playbook
- `references/bid-strategy-decision-tree.md` — When to use which bidding strategy
- `references/industry-benchmarks.md` — Industry-specific CPA, CTR, CPC benchmarks
- `references/search-term-analysis-guide.md` — Search term interpretation and negative keyword strategy
- `references/campaign-structure-guide.md` — Account structure best practices

Read these at the start of any analysis or optimization session. They contain the numeric thresholds, decision trees, and industry context that separate generic advice from expert recommendations.

## Analysis Heuristics

When interpreting Google Ads data, apply these specific rules. Every recommendation must reference a threshold — never give vague "optimize this" advice.

### Quality Score

| QS Range | Monthly Spend | Action | Priority |
|----------|--------------|--------|----------|
| 1-4 | >$100/month | Priority fix — read `references/quality-score-framework.md` for diagnostic tree | Critical |
| 1-4 | <$100/month | Fix if keyword is strategically important, otherwise pause and reallocate budget | Medium |
| 5-6 | Any | Monitor — improve landing page relevance and ad copy match. Check QS subcomponents (expected CTR, ad relevance, landing page experience) to identify the bottleneck | Low |
| 7-8 | Any | Healthy — focus on scaling. Small QS gains here have diminishing returns | None |
| 9-10 | Any | Excellent — do not touch QS factors. Focus entirely on bid and budget optimization | None |

**QS component diagnosis:**
- Expected CTR "Below Average" → ad copy doesn't match search intent. Headlines need the keyword or a closer synonym
- Ad Relevance "Below Average" → keyword doesn't belong in this ad group. Move it to a tighter ad group or write ad copy that matches the keyword theme
- Landing Page Experience "Below Average" → page load speed, mobile friendliness, or content relevance issue. This is the hardest to fix from within Google Ads — flag for website team

### Keyword Performance

Evaluate every keyword against the account's average CPA. If the account has no conversions, use CTR and cost thresholds instead.

**Accounts WITH conversion data:**

| Condition | Action | Rationale |
|-----------|--------|-----------|
| CPA < 50% of account avg | Increase bid 15-25%. Expand to broader match types if exact-only | High performer being underleveraged |
| CPA 50-100% of account avg | Maintain current bid. Monitor weekly | Healthy, contributing keyword |
| CPA 100-150% of account avg | Review search terms for this keyword. Tighten match type or add negatives | Borderline — often fixable with better targeting |
| CPA > 150% of account avg | Decrease bid 15-25%. If CPA > 200% avg after 2 weeks, pause | Underperformer dragging down account |
| 0 conversions, >$200 spend | Pause immediately OR move to exact match with 25% lower bid | Enough data to conclude this keyword doesn't convert at current targeting |
| 0 conversions, $100-200 spend, QS > 6 | Give 2 more weeks. Check landing page alignment and search term relevance | May need more data — QS suggests the ad/page are relevant |
| 0 conversions, $100-200 spend, QS < 5 | Pause. QS + no conversions = wrong keyword or wrong landing page | Two signals pointing the same direction |
| 0 conversions, <$100 spend | Too early to judge on conversions. Evaluate CTR and search term quality instead | Insufficient data for conversion-based decisions |
| 0 impressions for 30+ days | Pause — this is a zombie keyword. Check: is the bid too low? Match type too restrictive? Keyword paused at ad group level? | Dead weight cluttering the account |

**Accounts WITHOUT conversion data (no conversion tracking or <10 total conversions):**

| Condition | Action |
|-----------|--------|
| CTR > 5% and CPC < account avg | Likely high-intent — prioritize for conversion tracking setup |
| CTR < 1% after 500+ impressions | Poor relevance — pause or rewrite ad copy |
| Spend > $500 total with no conversion tracking | Flag as critical: "You're spending $X with no way to measure results. Set up conversion tracking before any optimization." |

### Search Terms

Analyze every search term report with these rules. Cross-reference `references/search-term-analysis-guide.md` for the full relevance scoring methodology.

| Condition | Action | Match Type |
|-----------|--------|------------|
| 3+ conversions, not already a keyword | Add as keyword | Phrase match initially — let it prove itself before going broad |
| 1-2 conversions, relevant to business | Flag for review — add if CPA is acceptable | Exact match to control spend |
| 0 conversions, 10+ clicks | Add as negative | Phrase match at campaign level |
| 0 conversions, 5-9 clicks | Flag for review — check: is it relevant? Is the landing page right? | May need more data OR a landing page fix, not a negative |
| 0 conversions, <5 clicks | Too early — skip unless clearly irrelevant | — |
| Clearly irrelevant (competitor name, wrong service, wrong location) | Add as negative immediately regardless of click count | Exact match for competitor names, phrase match for wrong services |
| Contains "free", "DIY", "jobs", "salary" (non-commercial intent) | Add as negative unless the business serves that intent | Phrase match at account level (shared negative list) |
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
- Search IS < 50% on a campaign spending >$1,000/month → this campaign is underserving demand. Investigate why before increasing budget
- Abs Top IS < 10% on brand campaigns → competitors are outbidding on your brand. Increase brand campaign bids or improve brand ad QS
- Top IS dropped >15 points month-over-month → new competitor or QS degradation. Check auction insights if available

### CTR Benchmarks

CTR varies dramatically by industry, match type, and ad position. Always compare against the right benchmark from `references/industry-benchmarks.md`.

| Condition | Diagnosis | Action |
|-----------|-----------|--------|
| Search CTR < 2% (any industry) | Ad copy relevance problem — the ad doesn't match what the searcher expects | Rewrite headlines to include the keyword or closest synonym. Check if ad group is too broad (mixed intent keywords) |
| Search CTR 2-4% | Acceptable for most industries. Check industry benchmark — some industries (legal, B2B SaaS) index higher | Compare to `references/industry-benchmarks.md`. If below industry avg, test new ad copy |
| Search CTR > 5% but conversion rate < 2% | Ad attracts clicks but landing page doesn't deliver on the ad's promise | Audit landing page: does the headline match the ad? Is the CTA clear? Is the page mobile-friendly? Offer `/ads-landing` |
| Search CTR > 8% | Excellent — but verify this isn't inflated by brand terms mixing with non-brand in the same campaign | Segment brand vs non-brand. If non-brand CTR is also >8%, this is genuinely strong copy |
| Display CTR < 0.5% | Normal for display. Only flag if display is eating significant budget with no conversions | Consider pausing display network in campaign settings if it's not converting |
| CTR declining month-over-month on stable keywords | Ad fatigue or new competitor in auction | Test new ad variants with `/ads-copy`. Check auction insights for new entrants |

### Budget Allocation

| Condition | Diagnosis | Action |
|-----------|-----------|--------|
| Daily budget < $10 with 20+ active keywords | Budget spread too thin — each keyword gets pennies | Reduce to 5-10 highest-performing keywords OR increase budget to give each keyword $0.50-1.00/day minimum |
| Daily budget < $10 with <10 keywords | Acceptable for testing or very low-CPC niches | Monitor — ensure at least 10-15 clicks/day for meaningful data |
| One campaign consuming >60% of budget with <40% of conversions | Budget misallocation — money flowing to the wrong campaign | Shift 20-30% of that campaign's budget to the higher-converting campaign. If no other campaign converts better, the problem is the campaign itself, not the budget split |
| Campaign with conversions hitting budget limit daily (budget-lost IS > 30%) | Proven campaign being starved | Increase budget 25-50% (within server guardrail). This is the lowest-risk budget increase |
| Campaign with 0 conversions after $500+ total spend | Not a budget problem — it's a targeting or conversion tracking problem | Do NOT increase budget. Audit keywords, search terms, landing pages, and conversion tracking first |
| Account spending <$50/day total across all campaigns | Low-data environment — statistical significance takes weeks | Consolidate into fewer campaigns/ad groups. Avoid A/B tests until daily volume supports them (min 30 clicks/day per variant) |

## Wasted Spend Calculation

Calculate and report wasted spend on every performance review. This is the single most important metric for most accounts — it tells the user exactly how much money is being burned.

### Formula

```
WASTED SPEND = 
  Keyword Waste:
    Sum of spend on keywords where (conversions = 0 AND clicks > 10)
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

**Step 1: Pull data (parallel)**
- `getAccountInfo` — business name, currency
- `listCampaigns` — all campaigns with spend, clicks, conversions
- `getImpressionShare` — traffic coverage
- `getCampaignPerformance` — daily trends (last 30 days)

**Step 2: Analyze**
- Calculate account-level CPA, CTR, conversion rate
- Compare each campaign's CPA to account average — flag any >150% of avg
- Check impression share using the diagnostic matrix above
- Identify the best performer (lowest CPA, highest conversion volume) and worst performer
- Compare metrics to industry benchmarks from `references/industry-benchmarks.md`

**Step 3: Deliver using the Report Template below**

### "Find wasted spend" — Waste Audit

**Step 1: Pull data (parallel)**
- `listCampaigns` → identify top 3-5 campaigns by spend
- `getKeywords` for each top campaign → all keywords with spend, conversions, QS
- `getSearchTermReport` for each top campaign → actual queries
- `getCampaignSettings` for each → check if Display Network is enabled
- `getNegativeKeywords` for each → current negative coverage

**Step 2: Analyze**
- Apply the Wasted Spend Calculation above
- For each non-converting keyword: check QS, check spend, check days active. Apply the keyword performance heuristics
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

**Step 1: Pull data (parallel)**
- `getKeywords` → all keywords with CPA, CPC, conversions, QS
- `getImpressionShare` → identify where bid increases would capture more traffic
- `getCampaignSettings` → confirm bid strategy (manual/enhanced CPC — bid changes only work with these)

**Step 2: Analyze using keyword performance heuristics**
- Segment keywords into tiers:
  - **Scale** (CPA < 50% avg): increase bid 15-25%
  - **Maintain** (CPA 50-100% avg): no change
  - **Reduce** (CPA 100-150% avg): decrease bid 10-15%, add negatives
  - **Pause** (CPA > 200% avg or $200+ spend with 0 conversions): pause
- Cross-reference with impression share: only increase bids on keywords where rank-lost IS > 20% (there's traffic to capture)
- Check bid strategy compatibility: if using Target CPA or Maximize Conversions, manual bid changes are blocked — recommend bid strategy adjustment instead (see `references/bid-strategy-decision-tree.md`)

**Step 3: Present bid change plan as a table**

| Keyword | Current Bid | New Bid | CPA | Conv | Rationale |
|---------|-------------|---------|-----|------|-----------|
| ... | $2.50 | $3.00 | $18 | 12 | CPA 40% below avg, rank-lost IS 35% |

**Step 4: Execute with `bulkUpdateBids` after user approval**

### "Scale winning keywords" — Growth Optimization

**Step 1: Pull data (parallel)**
- `getKeywords` → find keywords with: conversions > 2, CPA < account avg, QS > 6
- `getSearchTermReport` → find converting search terms not yet added as keywords
- `getImpressionShare` → check how much more traffic is available
- `getCampaignSettings` → check budget headroom

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

**Step 1: Pull data (parallel)**
- `getKeywords` → all keywords with QS and QS subcomponents
- `listAdGroups` → ad group structure (keyword count per group)
- `listAds` → ad copy per ad group
- `getSearchTermReport` → search term relevance to ad groups

**Step 2: Diagnose using `references/quality-score-framework.md`**
- Group keywords by QS: count in each 1-4, 5-6, 7-8, 9-10 bucket
- For QS 1-4 keywords, check which subcomponent is "Below Average":
  - Expected CTR below avg → ad copy doesn't resonate. Need `/ads-copy`
  - Ad Relevance below avg → keyword is in the wrong ad group. Need restructure
  - Landing Page below avg → page doesn't match intent. Need `/ads-landing`
- Check ad group sizes: any ad group with >25 keywords likely has QS problems from mixed intent

**Step 3: Present action plan prioritized by spend**
Fix high-spend, low-QS keywords first — they waste the most money. A QS improvement from 4 to 6 typically reduces CPC by 15-25%.

### "Restructure campaigns" — Account Restructure

**Step 1: Pull data (parallel)**
- `listCampaigns` → all campaigns
- `listAdGroups` for each → ad group count and themes
- `getKeywords` for top campaigns → keyword count and themes per ad group
- `getCampaignSettings` → current targeting and bid strategies
- `getNegativeKeywords` → current negative coverage

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

If `~/.adsagent/business-context.json` doesn't exist or `audit_date` is more than 90 days old:

> "I don't have business context for this account (or it's stale). Run `/ads-audit` first — it builds your business profile, which improves all recommendations. I can still work without it, but recommendations will be more generic."

### Keyword Gaps

If the search term report shows 3+ converting search terms that aren't already keywords:

> "I found [N] search terms that are converting but aren't added as keywords yet. Want me to add them? Adding them as keywords gives you direct bid control and typically improves CPA."

Present the terms with their conversion data and let the user approve before adding.

### Landing Page Misalignment

If CTR is strong (>4%) but conversion rate is below 2% on multiple ad groups:

> "Your ads are getting clicks but conversions are low — this usually means the landing page doesn't match what the ad promises. Run `/ads-landing` to audit keyword-to-landing-page alignment."

### Competitive Intelligence

If impression share is declining or new competitor patterns appear in auction insights:

> "Your impression share dropped [X] points this period. Run `/ads-compete` to see who's entering your auctions and how to respond."
