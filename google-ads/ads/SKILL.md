---
name: ads
description: Manage Google Ads — performance, keywords, bids, budgets, negatives, campaigns, ads, search terms, QS, location targeting, bulk operations. Use for any mention of Google Ads, CPA, ROAS, ad spend, or campaign settings.
argument-hint: "<campaign name, keyword, or 'show performance'>"
version: 3.2.0
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
  - check my changes
  - did my changes work
  - review my changes
  - how are my changes doing
  - change impact
---

## Setup

Read and follow `../shared/preamble.md` — it handles MCP detection, token, and account selection. If config is already cached, this is instant.

## Interaction Modes

This skill handles two very different request types. Recognizing which one you're in avoids unnecessary work.

**Direct action (fast path):**
> User: "pause the keyword 'dog grooming' in the Seattle campaign"
> 1. Confirm: "I'll pause 'dog grooming' in Pet Daycare - Seattle. Go ahead?"
> 2. On approval: call `pauseKeyword`, log per `references/change-tracking.md`
> 3. Done. No session checks, no performance analysis.

**Change impact review:**
> User: "check my changes" / "did my changes work?" / "review my changes"
> 1. Read `references/session-checks.md` and run the change review checks
> 2. If no pending changes: tell the user no recent changes are logged
> 3. If changes exist but review window hasn't passed: show maturation message (see `references/session-checks.md`)
> 4. If ready for review: pull before/after metrics, compute deltas, show results

**Analysis request:**
> User: "how are my ads doing?"
> 1. Read `references/session-checks.md` and run those checks (pending reviews, anomalies)
> 2. Pull data following the Performance Summary playbook in `references/workflow-playbooks.md`
> 3. Read `references/analysis-heuristics.md` for thresholds
> 4. Deliver report using the template in `references/workflow-playbooks.md`

## Rules

1. **Confirm before writing.** Show what you plan to change, the current value, and the new value. Users need to see the impact before approving — a blind "done" erodes trust.
2. **Start with reads.** When the user asks about ads, begin with `getAccountInfo` and `listCampaigns` to orient yourself.
3. **Show numbers clearly.** Format cost as dollars, CTR as percentages, include date ranges. Vague metrics are useless.
4. **Recommend before acting.** When you spot waste, present the finding and wait for approval.
5. **Guardrails are server-side.** Bid changes >25% and budget changes >50% will be rejected by the API.
6. **Log every write** per `references/change-tracking.md`.
7. **moveKeywords defaults to PHRASE match** and does NOT inherit from the source keyword. Always specify matchType explicitly — otherwise exact match keywords silently become phrase match.

## Reference Routing

For simple operations (pause, rename, single bid change), you typically don't need reference files. For analysis, pick the right one:

| Situation | Read |
|-----------|------|
| Performance analysis, keyword evaluation, waste calculation | `references/analysis-heuristics.md` (start here — routes to deeper files) |
| Step-by-step playbooks, report template | `references/workflow-playbooks.md` |
| QS diagnostics, component-level fixes | `references/quality-score-framework.md` |
| Bid strategy selection, migration, Smart Bidding | `references/bid-strategy-decision-tree.md` |
| Industry CPA/CTR/CPC benchmarks, seasonal adjustments | `references/industry-benchmarks.md` |
| Search term scoring, n-gram analysis, negative strategy | `references/search-term-analysis-guide.md` |
| Campaign/ad group structure, naming, restructuring | `references/campaign-structure-guide.md` |
| GAQL query patterns, adaptive fetching by account size | `../shared/gaql-cookbook.md` |

## Available Tools

### Read (safe, no side effects)
- **getAccountInfo** — Account name, currency, timezone, test status
- **listCampaigns** — All campaigns with impressions, clicks, cost, conversions
- **getCampaignPerformance** — Daily metrics over a date range
- **getKeywords** — Top keywords with quality scores
- **getSearchTermReport** — Actual search queries triggering ads
- **runGaqlQuery** — Custom read-only GAQL SELECT query (max 50 rows; see `../shared/gaql-cookbook.md`)
- **getChanges** — Recent AdsAgent changes with `changeId`s for undo
- **listConnectedAccounts** — All connected Google Ads accounts
- **getTrackingTemplate** — Current tracking template at any level
- **listAdGroups** — Ad groups in a campaign with metrics
- **listAds** — Ads in a campaign/ad group with copy, URLs, status, metrics
- **getImpressionShare** — Search/top/abs-top IS and budget/rank-lost IS (max 90 days)
- **getConversionActions** — Conversion actions and settings
- **getAccountSettings** — Auto-tagging, tracking template, conversion tracking IDs
- **getCampaignSettings** — Bidding, network, locations, schedule
- **getNegativeKeywords** — Negative keywords for a campaign (check before adding to avoid duplicates)
- **getRecommendations** — Google optimization recommendations
- **getKeywordIdeas** — Keyword research suggestions based on seed keywords or URL
- **getPmaxAssetGroups** — Performance Max asset groups with metrics
- **getPmaxAssets** — Assets within a PMax asset group
- **searchGeoTargets** — Find geo target constant IDs for location targeting

### Write (mutates the account — confirm with user first)
All write tools return a `changeId` for undo within 7 days.

- **pauseKeyword / enableKeyword** — Stop or re-enable a keyword
- **addKeyword** — Add a new keyword to an ad group
- **updateBid** — Change CPC bid (manual/enhanced CPC only, max 25% change)
- **addNegativeKeyword** — Block irrelevant terms at campaign level (BROAD, PHRASE, or EXACT; default: PHRASE)
- **removeNegativeKeyword** — Remove a negative keyword
- **updateCampaignBudget** — Change daily budget (max 50% change, min $1/day)
- **updateCampaignBidding** — Change bid strategy (e.g., switch to Target CPA, Maximize Conversions). This is how you implement recommendations from `references/bid-strategy-decision-tree.md`
- **updateCampaignGoals** — Change campaign conversion goals
- **createCampaign** — Create a full paused search campaign. Headlines (3-15, max 30 chars), descriptions (2-4, max 90 chars), finalUrl required. Default: MAXIMIZE_CONVERSIONS
- **pauseCampaign / enableCampaign** — Pause or re-enable a campaign
- **removeCampaign** — PERMANENTLY delete (cannot undo — prefer pauseCampaign)
- **setTrackingTemplate** — Set/clear tracking template
- **createAdGroup** — Create a new ad group
- **createAd** — Create RSA. Headlines (3-15, max 30 chars), descriptions (2-4, max 90 chars), finalUrl required
- **pauseAd / enableAd** — Pause or re-enable an ad
- **removeAd** — Permanently delete an ad
- **updateAdFinalUrl** — Change an ad's landing page URL
- **updateAdAssets** — Replace RSA headlines/descriptions (complete replacement — provide every asset)
- **bulkUpdateBids** — Update up to 50 keyword bids (each capped at 25% change)
- **bulkPauseKeywords** — Pause up to 100 keywords (partial success possible — report what succeeded and what failed)
- **bulkAddKeywords** — Add up to 100 keywords to an ad group (partial success possible)
- **moveKeywords** — Move keywords between ad groups in same campaign. Max 100. See Rule 7 about match type.
- **renameCampaign / renameAdGroup** — Rename a campaign or ad group
- **updateCampaignSettings** — Update network and/or location targeting (geo target constant IDs, e.g. '2840' for US). Supports negative locations.
- **pausePmaxAssetGroup / enablePmaxAssetGroup** — Pause or enable a Performance Max asset group
- **undoChange** — Reverse a previous write by `changeId`

## Account Baseline

Maintain `{data_dir}/account-baseline.json` for anomaly detection. Update at the END of any session where you pulled campaign data — no extra API calls needed.

```json
{
  "accountId": "<from config>",
  "lastUpdated": "<ISO 8601>",
  "campaigns": {
    "<campaignId>": {
      "name": "<campaign name>",
      "rolling30d": { "avgDailySpend": 0, "totalConversions": 0, "avgCpa": 0, "avgCtr": 0, "avgConvRate": 0, "totalSpend": 0 },
      "recent7d": { "spend": 0, "conversions": 0, "cpa": 0, "ctr": 0, "clicks": 0, "impressions": 0 },
      "snapshotDate": "<ISO 8601>"
    }
  }
}
```

Update formula: `rolling30d = (0.7 x previous_rolling30d) + (0.3 x recent_7d x (30/7))`. The `(30/7)` factor projects 7-day values to 30-day equivalents. New campaigns: initialize rolling30d from recent7d directly. Cap at 50 campaigns (spend > $0 in last 30 days only).

## Conditional Handoffs

After analysis, proactively offer relevant skills:

- **Ad copy problems** (CTR issues in 2+ ad groups): suggest `/ads-copy`
- **Missing business context** (no `business-context.json` or >90 days old): suggest `/ads-audit` first
- **Keyword gaps** (3+ converting search terms not yet keywords): offer to add them
- **Landing page misalignment** (CTR above industry benchmark but conversion rate below on multiple ad groups): suggest `/ads-landing`
- **Competitive intelligence** (impression share declining or new competitor patterns): suggest `/ads-compete`
