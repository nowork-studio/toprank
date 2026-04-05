# GAQL Cookbook — Adaptive Data Fetching

GAQL (Google Ads Query Language) lets you pull data across ALL campaigns in a single `runGaqlQuery` call. This cookbook provides an **adaptive algorithm** that adjusts strategy based on account size — from 2-campaign local businesses to 50-campaign enterprise accounts.

## The core challenge

`runGaqlQuery` returns max **50 rows** per call. This creates a tension:
- **Small accounts** (2-5 campaigns, <50 keywords): Everything fits in 50 rows. GAQL is perfect.
- **Medium accounts** (5-15 campaigns, 50-200 keywords): Top 50 by spend covers ~80% of value. Supplement for the rest.
- **Large accounts** (15+ campaigns, 200+ keywords): 50 rows is only the tip. Need a smarter approach.

## Adaptive data fetching algorithm

**The strategy: Use `listCampaigns` as a sizing probe, then choose the right fetching approach.**

### Step 1: Size the account

Always start with `listCampaigns`. This returns all campaigns (default limit: 100) with lifetime metrics and requires no campaign IDs — it's the simplest way to understand what you're working with.

From the result, count **enabled campaigns with spend > $0 in the data**. This is your `active_campaign_count`.

### Step 2: Choose strategy based on account size

```
IF active_campaign_count <= 3:
    → STRATEGY A: "Small account — GAQL-only"
    
ELSE IF active_campaign_count <= 10:
    → STRATEGY B: "Medium account — GAQL + targeted supplements"
    
ELSE:
    → STRATEGY C: "Large account — tiered approach"
```

### Strategy A: Small account (1-3 campaigns)

Most queries fit in 50 rows. Use GAQL for everything in parallel:

1. Run all 7 standard GAQL queries (see Query Patterns below) in parallel
2. **Exception: Daily campaign performance** returns `campaigns × days` rows. For 2-3 campaigns with LAST_30_DAYS, that's 60-90 rows (over the 50-row limit). Use `LAST_7_DAYS` for 2+ campaigns, or `LAST_30_DAYS` only for single-campaign accounts.
3. Done. No supplements needed.

**Total API calls: ~8** (1 listCampaigns + 7 GAQL queries)

### Strategy B: Medium account (4-10 campaigns)

GAQL gets the top entities. Supplement only where the 50-row limit matters (keywords and search terms have the most rows).

1. Run all 7 standard GAQL queries in parallel
2. Check if keyword or search term queries returned exactly 50 rows (hit the limit)
3. If yes: identify the top 2-3 campaigns by spend from `listCampaigns`, then run `getKeywords` and `getSearchTermReport` for ONLY those campaigns to get deeper coverage

**Total API calls: ~8-14** (8 base + up to 6 supplements)

### Strategy C: Large account (10+ campaigns)

50 rows won't cover the breadth. Use a **tiered approach**:

**Tier 1 — Account-wide overview (GAQL, parallel):**
- Impression share query (campaign-level, fits easily in 50 rows)
- Ad groups query (top 50 by spend — may miss tail ad groups in large accounts)
- Negative keywords query (no metrics, still capped at 50 rows — supplement with `getNegativeKeywords(campaignId, limit: 500)` per campaign for accounts with extensive negative lists)
- Daily campaign performance (campaign-level, rows = campaigns × days — may need date range narrowed to LAST_7_DAYS)

**Tier 2 — Top campaigns deep dive (helpers, parallel):**
- From `listCampaigns`, rank campaigns by spend. Select the top N campaigns that account for 80% of total spend (usually 3-5 campaigns even in large accounts — spend follows Pareto).
- For each of these top campaigns, run in parallel: `getKeywords(limit: 100)`, `getSearchTermReport(limit: 100)`, `listAds`
- This gives you 100 keywords and 100 search terms per top campaign — much more than GAQL's 50 total.

**Tier 3 — Tail campaigns (GAQL, only if needed):**
- If the analysis requires data from smaller campaigns, use targeted GAQL with a campaign filter:
  ```
  WHERE campaign.id IN (123, 456, 789)
  ```

**Total API calls: ~10-20** (4 GAQL + 3-5 campaigns × 3 helpers + optional tier 3)

This is more calls than Strategy A/B, but FAR fewer than the naive approach of calling every helper for every campaign (which would be 7 × 10+ = 70+ calls).

### Decision flowchart

```
listCampaigns
    │
    ├─ 1-3 active campaigns ──→ 7 GAQL queries (done)
    │
    ├─ 4-10 active campaigns ─→ 7 GAQL queries
    │                              │
    │                              └─ any hit 50-row limit?
    │                                   ├─ no ──→ done
    │                                   └─ yes ─→ supplement top 2-3 campaigns
    │
    └─ 10+ active campaigns ──→ 4 GAQL (overview) + helpers for top 80%-spend campaigns
```

## Important notes

- Cost is in **micros** (millionths). Divide by 1,000,000: `cost_micros / 1000000 = dollars`.
- Date ranges: `DURING LAST_30_DAYS`, `DURING LAST_7_DAYS`, `DURING THIS_MONTH`, or `BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`.
- Always filter `campaign.status = 'ENABLED'` unless you need paused/removed data.
- `ORDER BY metrics.cost_micros DESC` ensures the 50-row limit captures highest-impact entities.
- If `runGaqlQuery` errors or is unavailable, fall back entirely to per-campaign helper tools.

## Standard GAQL query patterns

### Keywords with Quality Score

```
SELECT campaign.id, campaign.name,
       ad_group.id, ad_group.name,
       ad_group_criterion.keyword.text,
       ad_group_criterion.keyword.match_type,
       ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.status,
       metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

### Search terms

```
SELECT campaign.id, campaign.name,
       search_term_view.search_term,
       search_term_view.status,
       metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

### Impression share

```
SELECT campaign.id, campaign.name,
       metrics.search_impression_share,
       metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share,
       metrics.search_absolute_top_impression_share,
       metrics.impressions, metrics.clicks,
       metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
ORDER BY metrics.cost_micros DESC
```

### Ad copy (RSA headlines + descriptions)

```
SELECT campaign.id, campaign.name,
       ad_group.id, ad_group.name,
       ad_group_ad.ad.responsive_search_ad.headlines,
       ad_group_ad.ad.responsive_search_ad.descriptions,
       ad_group_ad.ad.final_urls,
       ad_group_ad.status, ad_group_ad.ad.type,
       metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM ad_group_ad
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
  AND ad_group_ad.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

### Ad groups

```
SELECT campaign.id, campaign.name,
       ad_group.id, ad_group.name,
       ad_group.status,
       metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM ad_group
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

### Negative keywords

Note: This query has no metrics to ORDER BY, and accounts with 50+ campaign-level negatives will be silently truncated. For full negative keyword coverage, supplement with `getNegativeKeywords` per campaign (supports up to 500 rows per campaign, much higher than GAQL's 50-row cap).

```
SELECT campaign.id, campaign.name,
       campaign_criterion.keyword.text,
       campaign_criterion.keyword.match_type
FROM campaign_criterion
WHERE campaign_criterion.type = 'KEYWORD'
  AND campaign_criterion.negative = TRUE
  AND campaign.status = 'ENABLED'
ORDER BY campaign.name
```

### Daily campaign performance

```
SELECT campaign.id, campaign.name,
       segments.date,
       metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions,
       metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
ORDER BY segments.date DESC
```

## Specialized queries

### Zero-conversion high-spend keywords (waste detection)

```
SELECT campaign.name, ad_group.name,
       ad_group_criterion.keyword.text,
       ad_group_criterion.quality_info.quality_score,
       metrics.clicks, metrics.cost_micros
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
  AND metrics.conversions = 0
  AND metrics.clicks > 10
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

### Converting search terms (keyword mining)

```
SELECT campaign.name, search_term_view.search_term,
       metrics.conversions, metrics.cost_micros, metrics.clicks
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
  AND metrics.conversions > 0
ORDER BY metrics.conversions DESC
LIMIT 50
```

### Filter to specific campaigns

When you need data from a subset of campaigns (e.g., tier 3 in Strategy C):

```
WHERE campaign.id IN (123456, 789012, 345678)
  AND segments.date DURING LAST_30_DAYS
```
