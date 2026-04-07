---
name: ads-audit
description: Google Ads account audit and business context setup. Run this first — it gathers business information, analyzes account health, and saves context that all other ads skills reuse. Trigger on "audit my ads", "ads audit", "set up my ads", "onboard", "account overview", "how's my account", "ads health check", "what should I fix in my ads", or when the user is new to AdsAgent and hasn't run an audit before. Also trigger proactively when other ads skills detect that business-context.json is missing.
argument-hint: "<account name or 'audit my ads'>"
---

## Setup

Read and follow `../shared/preamble.md` — it handles MCP detection, token, and account selection. If config is already cached, this is instant.

# Google Ads Audit + Business Context Setup

This is the starting point for any Google Ads account. It does two things:

1. **Audits the account** — surfaces what's working, what's wasting money, and what to fix first
2. **Builds business context** — gathers and saves business information to `{data_dir}/business-context.json` so every other ads skill (copy, landing pages, competitive analysis) can use it without re-asking

Run this before anything else. If another ads skill finds `business-context.json` missing, it should point the user here.

## Scope Detection

The user may pass arguments that narrow the audit to specific campaigns, services, or focus areas. Parse the arguments before starting data collection.

### How to determine scope

| User says | Scope | Behavior |
|-----------|-------|----------|
| No arguments / "audit my ads" | **Full account** | Audit all campaigns, all dimensions |
| "focus on grooming" / "grooming campaigns" | **Service-scoped** | Filter to campaigns matching the service keyword. Still pull account-level data for context (conversion tracking, account settings), but deep-dive analysis, scoring, and recommendations focus on the matched campaigns only |
| "campaign X" / specific campaign name | **Campaign-scoped** | Same as service-scoped but matched to exact campaign(s) |
| "just check wasted spend" / "impression share" | **Dimension-scoped** | Full data pull but report only the requested dimension(s) in depth. Scorecard still shows all 7 dimensions for context, but detailed findings and actions focus on the requested area |

### Scope threading rules

1. **Always pull `listCampaigns` unfiltered first** — you need the full picture to identify which campaigns match the scope and to calculate account-wide metrics like total spend (needed for waste percentages)
2. **Filter deep-dive data to scoped campaigns** — In Phase 1B, only pull per-campaign data (`getCampaignSettings`, `getKeywords`, `getSearchTermReport`, `listAds`) for campaigns matching the scope. This saves API calls and keeps the analysis focused
3. **Score dimensions relative to scope** — If scoped to grooming campaigns, keyword health score reflects grooming keywords only, not the whole account. Make this explicit in the report header: "Scoped to: [Grooming campaigns]"
4. **Account-wide dimensions still get scored** — Conversion tracking and account settings are account-level regardless of scope. Score them normally but note when issues affect the scoped campaigns specifically
5. **Persona discovery uses scoped data** — Build personas from search terms within the scoped campaigns only
6. **Business context is always full-account** — `business-context.json` captures the whole business, not just the scoped segment. Don't narrow business context to the scope

### Scope matching

Match campaign names, ad group names, and keyword themes using case-insensitive substring matching. For example, "grooming" matches campaigns named "Tukwila Grooming Search", "Grooming Test", etc. If no campaigns match, tell the user what campaigns exist and ask them to clarify.

## Reference Documents

Read these reference documents during analysis for expert-level context:

- `references/account-health-scoring.md` — Detailed scoring rubrics for each dimension (0-5 scale with specific criteria)
- Read from ads skill: `../ads/references/industry-benchmarks.md` — Compare account metrics to industry averages
- Read from ads skill: `../ads/references/quality-score-framework.md` — QS diagnostics and component-level analysis
- Read from ads skill: `../ads/references/search-term-analysis-guide.md` — Search term relevance scoring methodology
- Read from ads skill: `../ads/references/campaign-structure-guide.md` — Account structure best practices

Read these before starting Phase 2 analysis. They contain the numeric thresholds that separate a generic audit from an expert one.

## Step 0: Policy Freshness Check

Before auditing, verify that the policy assumptions underpinning this audit are current.

1. Read `../shared/policy-registry.json` and check each entry: if `last_verified` + `stale_after_days` < today's date, the entry is stale.
2. **High-volatility stale entries:** Use WebSearch to check for recent Google Ads changes related to each stale entry's `area` (e.g., "Google Ads broad match behavior changes 2026"). Compare findings against the `assumption` field. If discrepancies are found:
   - Display a warning banner at the top of the audit: `⚠️ Policy drift detected: [area] — [brief description of what changed]. Recommendations in this area may need manual verification.`
   - Suggest updating `policy-registry.json` with corrected assumptions and today's date.
3. **Moderate-volatility stale entries:** Note them in the audit output as an informational line (e.g., "ℹ️ [area] last verified [date] — may warrant a check") but do not block the audit.
4. **Stable stale entries:** Skip — these rarely change.

If no high-volatility entries are stale, proceed directly to Phase 1 with no output from this step.

## Phase 1: Pull Account Data

Gather everything in parallel before asking the user a single question. The goal is to show up informed.

**Use the adaptive data fetching algorithm from `../shared/gaql-cookbook.md`.** The approach varies by account size — read the cookbook's "Adaptive data fetching algorithm" section. Here's the summary:

### Phase 1A: Account basics + sizing probe (parallel)

Pull these simultaneously — they don't require campaign IDs and they tell you the account size:

- `getAccountInfo` — business name, currency, timezone
- `getAccountSettings` — auto-tagging, tracking template, conversion setup
- `listCampaigns` — all campaigns with spend, clicks, conversions **(also serves as the sizing probe — default limit is 100)**
- `getConversionActions` — what conversions are set up
- `getRecommendations` — Google's optimization suggestions

**After Phase 1A, apply scope filtering:** If the user specified a scope (see Scope Detection above), identify which campaigns match. Log the matched campaigns and their IDs. If no campaigns match, stop and ask the user to clarify. For the rest of the audit, "active campaigns" means scope-matched campaigns (or all campaigns if no scope was specified).

**Also after Phase 1A: kick off the website crawl.** Once `listAds` data is available, resolve the website URL and start the website crawl (Phase 3, Step 2) immediately — don't wait for Phase 1B or Phase 2. The crawl results aren't needed until Phase 3's user questions, so it runs in the background while you finish data collection and scoring.

### Phase 1B: Adaptive data pull (depends on account size)

Count the **in-scope** enabled campaigns with spend from Phase 1A, then follow the cookbook. When scoped, only pull per-campaign data for in-scope campaigns — but still run account-wide GAQL queries (they're cheap and provide context for scoring):

- **1-3 in-scope campaigns:** Run all 7 standard GAQL queries in parallel. Also run `getCampaignSettings(campaignId)` and `listAds(campaignId)` per in-scope campaign (needed for Display Network detection, bidding strategy assessment, and ad copy scoring). Done.
- **4-10 in-scope campaigns:** Run all 7 GAQL queries + `getCampaignSettings` and `listAds` for top 3-5 in-scope campaigns by spend. If keywords or search terms hit the 50-row limit, supplement with `getKeywords`/`getSearchTermReport` for the top 2-3 in-scope campaigns.
- **10+ in-scope campaigns:** Use the tiered approach — GAQL for account-wide overview (impression share, ad groups, negatives, daily performance), then per-campaign helpers (`getCampaignSettings`, `getKeywords`, `getSearchTermReport`, `listAds`) for the top in-scope campaigns that cover 80% of in-scope spend.

### Geo-targeting verification

`getCampaignSettings` has a known blind spot: it often returns empty `locationTargeting` and `null` `proximityTargeting` even when campaigns have active geo-targeting. Always verify geo-targeting via GAQL for each in-scope campaign:

```
SELECT campaign.id, campaign.name,
       campaign_criterion.type, campaign_criterion.negative,
       campaign_criterion.location.geo_target_constant,
       campaign_criterion.proximity.radius,
       campaign_criterion.proximity.radius_units
FROM campaign_criterion
WHERE campaign.id IN (<in-scope campaign IDs>)
  AND campaign_criterion.type IN ('LOCATION', 'PROXIMITY')
```

`radius_units` values: 0 = meters, 1 = kilometers, 2 = miles. Do NOT claim "no geo-targeting" based solely on `getCampaignSettings` — the GAQL query is authoritative.

### Fallback

If `runGaqlQuery` errors or is unavailable, fall back to per-campaign helper tools for each active campaign, run in parallel.

**Minimum data for a meaningful audit:** Campaign list, keyword data, impression share, and conversion actions must return data. If the account has zero campaigns or zero spend, skip to Phase 3 (business context).

## Phase 2: Analyze and Score

Work through each dimension. For each one, assign a numeric score (0-5) and a status label.

**Scope-aware scoring:** When the audit is scoped, score campaign-level dimensions (structure, keyword health, search terms, ad copy, impression share, spend efficiency) using only in-scope data. Account-level dimensions (conversion tracking) are scored account-wide but with notes about how issues affect the scoped campaigns. The overall health score reflects scoped performance — this gives the user a focused view of the area they care about.

### Scoring Framework

Read `references/account-health-scoring.md` for the detailed rubric per dimension. Use this summary for quick reference:

**Score definitions:**

| Score | Label | Meaning |
|-------|-------|---------|
| 0 | Critical | Broken or missing entirely — actively losing money |
| 1 | Poor | Major problems — significant waste or missed opportunity |
| 2 | Needs Work | Below acceptable — several clear issues to fix |
| 3 | Acceptable | Functional but room for meaningful improvement |
| 4 | Good | Well-managed with minor optimization opportunities |
| 5 | Excellent | Best-practice level — maintain and scale |

**Overall Health Score:** Sum all 7 dimension scores, multiply by (100/35), round to nearest integer. This gives a 0-100 score.

| Overall Score | Label | Summary |
|---------------|-------|---------|
| 0-25 | Critical | Account has fundamental problems. Stop spending until fixed |
| 26-50 | Needs Work | Significant waste. Focus on top 3 issues before scaling |
| 51-75 | OK | Functional but leaving money on the table |
| 76-90 | Strong | Well-managed. Focus on scaling and marginal gains |
| 91-100 | Excellent | Top-tier account. Maintain and test incrementally |

### Account Health Dimensions

**1. Conversion tracking** (Score 0-5)

| Score | Criteria |
|-------|----------|
| 0 | No conversion actions set up. Spending blind |
| 1 | Conversion actions exist but aren't firing (0 conversions recorded despite clicks) |
| 2 | Conversions tracked but auto-tagging disabled, or using only micro-conversions (page views, not leads/sales) |
| 3 | Primary conversion action firing, auto-tagging on, but multiple conversion actions counting duplicates or no value assigned |
| 4 | Clean conversion setup: primary action firing, auto-tagging on, values assigned, no duplicate counting |
| 5 | Full setup: primary + secondary actions, proper attribution window, enhanced conversions or offline conversion import |

- Red flag: spending money with no conversion tracking = flying blind. Score 0-1 is a STOP condition — recommend pausing spend until tracking is fixed
- Check: is auto-tagging enabled? If not, Google Analytics integration breaks
- Check: are conversion actions using "Every" or "One" counting? Lead gen should use "One", e-commerce should use "Every"

**2. Campaign structure** (Score 0-5)

| Score | Criteria |
|-------|----------|
| 0 | Single campaign with one ad group containing 50+ unrelated keywords |
| 1 | Some structure but ad groups have 30+ keywords with mixed intent (e.g., "plumber" and "plumbing school" in same group) |
| 2 | Campaigns exist per service/product but ad groups are too broad (15-30 keywords of mixed theme) |
| 3 | Campaigns per service, ad groups by theme (5-20 keywords), but missing brand campaign separation or geo structure |
| 4 | Clean structure: brand separated, services split, tight ad groups, appropriate geo targeting |
| 5 | Optimal: brand/non-brand split, service campaigns, geo-specific where relevant, ad groups of 5-15 tightly themed keywords, negative keyword lists at appropriate levels |

- Red flag: one ad group with 200 keywords = poor relevance, QS will suffer
- Check: are brand and non-brand keywords in separate campaigns? Mixing them inflates brand CTR and hides non-brand problems
- Check: for multi-location businesses, is there geo-specific structure?
- Reference `../ads/references/campaign-structure-guide.md` for the ideal structure patterns

**3. Keyword health** (Score 0-5)

| Score | Criteria |
|-------|----------|
| 0 | No keywords with conversions. Average QS < 3. >50% of keywords are zombies (0 impressions 30+ days) |
| 1 | Average QS 3-4. >30% of spend on non-converting keywords. Heavy use of broad match without negatives |
| 2 | Average QS 4-5. 20-30% of spend on non-converting keywords. Some match type issues |
| 3 | Average QS 5-6. 10-20% wasted spend. Reasonable match type mix but gaps in negative coverage |
| 4 | Average QS 6-7. <10% wasted spend. Good match type strategy. Solid negative keyword lists |
| 5 | Average QS 7+. <5% wasted spend. Tight match types. Comprehensive negatives. Regular search term mining |

- Calculate: what % of total keyword spend goes to keywords with 0 conversions and >10 clicks? This is your keyword waste rate
- Calculate: average QS weighted by spend (not by keyword count — a QS-3 keyword spending $2,000/month matters more than a QS-3 keyword spending $5/month)
- Check for zombie keywords: 0 impressions for 30+ days. These clutter the account and should be paused

**4. Search term quality** (Score 0-5)

| Score | Criteria |
|-------|----------|
| 0 | >40% of search terms are irrelevant. No negative keywords in place |
| 1 | 30-40% irrelevant terms. Minimal negative keyword coverage |
| 2 | 20-30% irrelevant terms. Some negatives but obvious gaps |
| 3 | 10-20% irrelevant terms. Decent negative coverage. Some converting terms not yet added as keywords |
| 4 | <10% irrelevant terms. Good negative lists. Most high-converting terms already added as keywords |
| 5 | <5% irrelevant terms. Comprehensive negative lists at account and campaign level. Active search term mining program |

- Score search term relevance using the methodology in `../ads/references/search-term-analysis-guide.md`
- Calculate: spend on irrelevant search terms (relevance score < 2) as % of total spend
- Flag converting search terms (2+ conversions) not yet added as keywords — these are free money
- Flag obvious negative keyword gaps: competitor names, "free" variants, "jobs"/"careers" variants, wrong service types

**5. Ad copy** (Score 0-5)

| Score | Criteria |
|-------|----------|
| 0 | No active ads, or only legacy expanded text ads (no RSAs) |
| 1 | RSAs exist but only 1 per ad group. Headline/description variety is poor (repetitive messaging) |
| 2 | 1-2 RSAs per ad group. Some variety but headlines don't include keywords or location |
| 3 | 2+ RSAs per major ad group. Headlines include keywords. Pinning used on H1. Some CTR variation suggests testing is happening |
| 4 | 2-3 RSAs per ad group with distinct messaging angles. Good headline variety (service, value prop, trust, CTA). CTR above industry average |
| 5 | Active A/B testing program. Multiple RSAs with measurably different angles. Regular losers paused, winners iterated. CTR consistently above benchmark |

- Count RSAs per ad group: <2 means no testing is possible
- Check headline diversity: are the 15 headlines actually different, or are they minor variations of the same message?
- Check if keywords appear in headlines (direct QS and relevance impact)
- Check pin strategy: H1 should typically be pinned to the most relevant service+location headline
- Identify ad groups with CTR below industry benchmark — these need copy refresh

**6. Impression share** (Score 0-5) — **Data limit:** `getImpressionShare` supports max 90 days (not 365 like other tools). For GAQL impression share queries, the same 90-day practical limit applies.

| Score | Criteria |
|-------|----------|
| 0 | Search IS < 20%. Missing >80% of potential traffic |
| 1 | Search IS 20-35%. Budget-lost IS > 40% OR rank-lost IS > 60% |
| 2 | Search IS 35-50%. Significant losses from both budget and rank |
| 3 | Search IS 50-65%. Moderate losses — budget-lost IS < 25% and rank-lost IS < 40% |
| 4 | Search IS 65-80%. Losses primarily from rank (fixable with QS improvements) |
| 5 | Search IS > 80%. Brand campaign IS > 95%. Losses are marginal and strategic (intentionally not competing on some queries) |

Use the Impression Share Interpretation Matrix to diagnose the root cause:

| | Rank-Lost IS < 30% | Rank-Lost IS 30-50% | Rank-Lost IS > 50% |
|---|---|---|---|
| **Budget-Lost IS < 20%** | Healthy — optimize at margins | QS/Bid Problem — improve ads, landing pages, or raise bids on high-QS keywords | Quality Crisis — QS is the bottleneck. Fix ad relevance and landing page experience before spending more |
| **Budget-Lost IS 20-40%** | Budget Problem — increase budget or narrow targeting. Check if the campaign is profitable enough to justify more spend | Mixed Problem — fix quality first (cheaper than adding budget), then reassess | Structural Problem — bidding on too-competitive keywords. Shift to long-tail and exact match |
| **Budget-Lost IS > 40%** | Severe Budget Gap — if CPA is good, this is the highest-ROI fix in the account. Double budget or cut keyword count by 50% | Priority: fix rank issues to get more from existing budget, then add budget | Fundamental Misalignment — pause, restructure, then restart. Current approach is burning money |

**7. Spend efficiency** (Score 0-5)

| Score | Criteria |
|-------|----------|
| 0 | No conversion data available. Flying blind on efficiency |
| 1 | CPA > 200% of industry average. >40% of spend on non-converting entities |
| 2 | CPA 150-200% of industry avg. 25-40% wasted spend. Major budget misallocation between campaigns |
| 3 | CPA 100-150% of industry avg. 15-25% wasted spend. Some misallocation |
| 4 | CPA within industry norms. <15% wasted spend. Budget roughly proportional to conversion share per campaign |
| 5 | CPA below industry avg. <5% wasted spend. Budget allocation optimized — each campaign's budget share matches its conversion share |

- Calculate: % of spend going to converting keywords vs non-converting
- Calculate: per-campaign CPA and compare to account average. Flag any campaign with CPA > 150% of account avg
- Calculate: budget allocation efficiency — does each campaign's % of total budget match its % of total conversions?
- If one campaign gets 60% of budget but delivers only 30% of conversions, that's a $X reallocation opportunity

### Wasted Spend Deep Dive

Calculate wasted spend using this formula (same as `/ads` skill for consistency):

```
WASTED SPEND = 
  Keyword Waste:
    Sum of spend on keywords where (conversions = 0 AND clicks > 10)
  + Search Term Waste:
    Sum of spend on search terms where relevance_score < 2
    (use the 1-5 relevance scoring from ../ads/references/search-term-analysis-guide.md)
  + Structural Waste:
    Spend on campaigns with Display Network enabled where display clicks > 20 AND display conversions = 0
```

Use these numbers internally for scoring. In the report, mention the total waste figure in the verdict paragraph. Individual wasteful keywords/terms appear as evidence under the relevant dimension (keyword health or search term quality) — max 3 examples per category, not exhaustive lists.

## Phase 2.5: Persona Discovery

Discover 2-3 customer personas from the ad data. This runs in parallel with Phase 3 (business context questions) — it uses only the data already pulled in Phase 1.

### Data Sources for Persona Construction

| Source | What it reveals | How to access |
|--------|----------------|---------------|
| Search terms | What customers actually search for — their language, pain points, urgency | `getSearchTermReport` from Phase 1 |
| Converting keywords | What they buy — the terms that lead to conversions reveal purchase intent | `getKeywords` filtered to converting |
| Ad group themes | How the business segments its services — each theme may serve a different persona | `listAdGroups` from Phase 1 |
| Landing page URLs | Where they land — different pages suggest different customer journeys | `listAds` final URLs from Phase 1 |
| Geographic data | Where they are — metro vs rural, specific cities | `getCampaignSettings` location targets |
| Device split | How they search — mobile-heavy suggests on-the-go/urgent need | Infer from ad performance patterns |
| Time-of-day patterns | When they search — business hours vs evenings vs weekends | `getCampaignPerformance` daily data |

### Persona Template

Use this full template for the persisted JSON file. In the **report output**, personas appear as a compact 3-column table (name, example searches, value) — see Phase 4. The JSON file has the full detail for downstream skills like `/ads-copy`:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Descriptive label capturing their defining trait | "The Emergency Caller" |
| **Demographics** | Role, context, location type | Homeowner, suburban, dual-income household |
| **Primary goal** | What they're trying to accomplish RIGHT NOW | Fix a burst pipe before it damages the floor |
| **Pain points** | What's driving them to search | Can't wait for regular business hours. Worried about cost. Doesn't know who to trust |
| **Search language** | Actual search terms from the data that this persona uses | "emergency plumber near me", "plumber open now", "burst pipe repair cost" |
| **Decision trigger** | What makes them click the ad and convert | Seeing "24/7" and "Same Day" in the headline. Phone number in the ad. Reviews mentioned |
| **Value to business** | Estimated revenue or conversion value | High urgency = willing to pay premium. Avg ticket $350-800 |

### Derivation Rules

- Each persona MUST be grounded in actual search term clusters from the data. If you can't point to 5+ search terms that this persona would use, the persona is speculative — drop it
- If all search terms look the same (single-intent account), identify 1-2 personas max. Don't force 3
- Name personas by their dominant behavior, not demographics: "The Comparison Shopper" is more useful than "Female 35-44"
- Include the actual search terms from the data that map to each persona — this directly informs ad copy decisions

### Persist Personas

Save to `{data_dir}/personas/{accountId}.json`:

```json
{
  "account_id": "1234567890",
  "saved_at": "2024-01-15T10:30:00Z",
  "personas": [
    {
      "name": "The Emergency Caller",
      "demographics": "Homeowner, suburban, any age",
      "primary_goal": "Fix an urgent problem right now",
      "pain_points": ["Can't wait", "Worried about cost", "Doesn't know who's reliable"],
      "search_terms": ["emergency plumber near me", "plumber open now", "burst pipe repair"],
      "decision_trigger": "24/7 availability, phone number visible, reviews",
      "value": "High — willing to pay premium for urgency"
    }
  ]
}
```

These personas feed directly into `/ads-copy` for headline generation and `/ads` for keyword strategy.

## Phase 3: Build Business Context

**Skip this phase for scoped audits if `{data_dir}/business-context.json` already exists and has a recent `audit_date`.** A scoped audit (e.g., "focus on grooming") should deliver findings fast, not re-interview the user. Only run Phase 3 on the first full-account audit or if business-context.json is missing/stale (>90 days old).

Pull as much as possible from the data you already have — only ask the user for what you can't infer.

### What to infer from account data

| Field | Source |
|-------|--------|
| `business_name` | `getAccountInfo` |
| `services` | Campaign and ad group names, keyword themes |
| `locations` | Campaign geo-targeting, location extensions |
| `brand_voice` | Existing ad copy tone and word choices |
| `keyword_landscape.high_intent_terms` | Top-converting keywords |
| `keyword_landscape.competitive_terms` | Low impression share keywords with high CPC |
| `keyword_landscape.long_tail_opportunities` | Converting search terms not yet added as keywords |
| `website` | Ad final URLs (extract root domain from `listAds` data) |

### Website crawl (kicked off after Phase 1A, results used here)

This crawl starts in the background after Phase 1A (see note in Phase 1A). By the time you reach Phase 3, the results should be ready.

**Step 1: Resolve the website URL**

Find the website URL from Phase 1 data, in priority order:
1. Ad final URLs from `listAds` — extract the root domain (e.g., `https://example.com`). Normalize to the apex domain (strip `www.` and subdomain prefixes) before frequency-counting across all ads. Use the most common domain.
2. If no URL found in ad data, ask the user: "What's your website URL?"

**Step 2: Crawl the website**

Issue all `WebFetch` calls in a single tool-use turn so they run in parallel. If any individual fetch fails (404, timeout, blocked), skip that page and continue.

| Page | URL pattern | Why |
|------|-------------|-----|
| Homepage | `{root_url}` | Services overview, hero messaging, trust signals, brand voice |
| About page | `{root_url}/about` | Differentiators, history, team, social proof |
| Services page | `{root_url}/services` | Full service list, service descriptions |
| Top ad landing pages | Up to 3 unique final URLs from ads, **excluding any URL that matches the homepage, about, or services pages already being fetched** | What the ads actually link to — offers, CTAs, messaging |

**Fallback if `/about` or `/services` return 404:** Try one fallback each:
- About: try `/about-us` (most common variant)
- Services: try `/our-services` (most common variant)

If the fallback also 404s, move on — don't spider the site.

**Detecting unusable pages:** If a fetched page has fewer than 50 words of visible text (excluding HTML tags, scripts, and navigation), or if the primary content is a login/auth form (email/password fields, "Sign In" as the main heading), treat it as a failed fetch and skip it for extraction.

**Step 3: Extract business context from crawled pages**

Scan the fetched page content for these signals. Merge with what you already inferred from account data — website data fills gaps, account data confirms what's active.

| Field | What to look for on the website |
|-------|-------------------------------|
| `services` | Service names from navigation, headings, service cards. **Merge** with services inferred from campaigns — the website may list services not yet advertised |
| `differentiators` | "Why choose us" sections, hero subheadings, unique value claims (e.g., "Family-owned since 1998", "Same-day service guaranteed") |
| `social_proof` | Review counts, star ratings, award badges, "As seen in" logos, certifications, years in business, number of customers served |
| `offers_or_promotions` | Banner offers, hero CTAs with discounts, seasonal promotions, "Free estimate" or "X% off" |
| `brand_voice` | Tone of headlines and body copy — professional vs casual, technical vs approachable. Capture 3-5 literal phrases from the site that exemplify the tone |
| `target_audience` | Who the site speaks to — homeowners vs businesses, specific industries, demographic cues |
| `locations` | Footer addresses, "Areas we serve" pages, location-specific content |
| `landing_pages` | Map each ad final URL to a summary of what's on that page (headline, primary CTA, offer if any) |
| `industry` | What the business clearly does — confirm or refine what campaign names suggest |
| `competitors` | Look for comparison tables or "vs" pages linked from the nav |

**Important:** Only extract from pages you actually retrieved with usable content. If the homepage is all you got, that's fine — it usually has the most signal. Extract in the site's original language — downstream skills handle translation when generating English ad copy.

**If all pages failed or returned no usable content**, skip website extraction entirely and proceed to the full question set below (do not skip any questions).

### What to ask the user

Present what you inferred from **both** account data and the website crawl, then ask for what's still missing.

**Always ask** (these are rarely on websites):
- "What makes you different from competitors?" → `differentiators` (ask even if the website had a "why us" section — the owner's answer is often sharper than marketing copy)
- "Who are your main competitors?" → `competitors`
- "Is your business seasonal? When's your busiest time?" → `seasonality`

**Ask only if not found in account data or website crawl:**
- Industry
- Services
- Target audience
- Social proof (reviews, awards, years in business)
- Current offers or promotions

### Save the context

Write the complete business context to `{data_dir}/business-context.json`:

```json
{
  "business_name": "",
  "industry": "",
  "website": "",
  "services": [],
  "locations": [],
  "target_audience": "",
  "brand_voice": {
    "tone": "",
    "words_to_avoid": [],
    "words_to_use": []
  },
  "differentiators": [],
  "competitors": [],
  "seasonality": {
    "peak_months": [],
    "slow_months": [],
    "seasonal_hooks": []
  },
  "keyword_landscape": {
    "high_intent_terms": [],
    "competitive_terms": [],
    "long_tail_opportunities": []
  },
  "social_proof": [],
  "offers_or_promotions": [],
  "landing_pages": {},
  "notes": "",
  "audit_date": "",
  "account_id": ""
}
```

Include `audit_date` (today's date) and `account_id` so future skills know when this was last refreshed.

## Phase 4: Deliver the Audit Report

The report follows an **onion structure** — lead with the verdict, then actions, then evidence. The reader should get the full picture in the first 10 lines, and only needs to keep reading if they want the supporting data.

**The #1 rule: no duplication.** Each finding appears in exactly one place. The scorecard summarizes, the actions tell you what to do, the evidence shows why. If something is in the scorecard's "Key Finding" column, don't repeat it in the evidence section.

### Report structure

```
# [Business Name] — Ads Audit
**[Score]/100 · $X,XXX spent (30d) · XX conversions at $XX CPA**
[If scoped] Scoped to: [description]

[2-3 sentence verdict. What's working, what's broken, and the single biggest
opportunity in dollar terms. This paragraph should be enough for someone who
won't read further.]

## What to Fix (in order)

1. **[Specific action]** — [1-line why + expected dollar/conversion impact]
2. **[Specific action]** — [1-line why + expected impact]
3. **[Specific action]** — [1-line why + expected impact]

Run `/ads` to execute any of these.

## Scorecard

| Dimension | Score | Key Finding |
|-----------|-------|-------------|
| Conversion tracking | X/5 | [one line] |
| Campaign structure | X/5 | [one line] |
| Keyword health | X/5 | [one line] |
| Search term quality | X/5 | [one line] |
| Ad copy | X/5 | [one line] |
| Impression share | X/5 | [one line] |
| Spend efficiency | X/5 | [one line] |

## Evidence

[Only include dimensions scoring 0-2. Each dimension gets ONE compact block.
Do NOT repeat what's already in the scorecard or actions — add the supporting
data that explains the score.]

### [Dimension] (X/5)
[2-4 lines of data: the specific keywords, search terms, or metrics that
drove the score. Top 3 examples max — not exhaustive lists. End with the
fix if it wasn't already an action item above.]

## Personas

| Persona | Example searches | Value |
|---------|-----------------|-------|
| [name] | [2-3 terms] | [why they matter] |

## Questions for You

[Only if business context has gaps that matter for the recommendations.
Max 2-3 questions. Don't ask what you can infer from the data.]
```

### What makes a good action item

- **Specific:** "Pause keyword 'free dog food' — $847 spent, 0 conversions" not "Review underperforming keywords"
- **Quantified:** Include the spend, impressions, or conversions at stake
- **Prioritized:** Highest-impact items first. Stopping waste > starting new things
- **Actionable with /ads:** Every recommendation should be something the user can execute immediately using the `/ads` skill
- **Dollar-denominated:** Express impact as "save $X/month" or "gain X conversions/month at $Y CPA"

### Output discipline

These rules prevent the bloated, repetitive reports that make audits hard to read:

1. **No standalone "Key Numbers" section.** The headline already has spend, conversions, and CPA. Don't repeat them.
2. **No standalone "Wasted Spend Analysis" section.** Waste data belongs in the relevant Evidence dimension (keyword health or search term quality). Mention the total in the verdict paragraph.
3. **No standalone "Impression Share Analysis" section.** The diagnosis belongs in the scorecard line + Evidence block if IS scored 0-2.
4. **Max 3 examples per finding.** Show the top 3 by spend, not an exhaustive list. The user can drill deeper with `/ads`.
5. **Evidence sections are for data, not narrative.** Don't explain what QS is or how impression share works — just show the numbers that matter.
6. **The entire report should fit in ~60-80 lines of markdown.** If you're over 100 lines, you're duplicating or over-explaining.

### Conditional handoff (pick the single most relevant one)

After the report, add ONE handoff based on the biggest issue found:

| Condition | Handoff |
|-----------|---------|
| Ad copy scored 0-2 | Suggest `/ads-copy` for RSA variants |
| Impression share scored 0-2 | Suggest `/ads` for bid optimization |
| 3+ converting search terms not yet keywords | Offer to add them via `/ads` |
| Wasted spend > 15% | Offer to pause/negative via `/ads` |
| High CTR but low conversion rate | Suggest landing page audit |

Don't list all possible handoffs — pick the one that matches the #1 action item.

## Rules

1. **Data first, questions second.** Pull all account data before asking the user anything. Show up informed.
2. **Infer before asking.** Don't ask "what industry are you in?" if the campaigns clearly say "plumbing services."
3. **Be specific.** Name the campaigns, keywords, and dollar amounts. Vague advice is useless.
4. **Prioritize by money.** The biggest waste or biggest opportunity comes first.
5. **Save the context.** Always write `business-context.json` — this is the handoff to every other ads skill.
6. **Don't fix things here.** This skill diagnoses and recommends. The user executes fixes with `/ads`. Offer to switch to `/ads` for implementation.
7. **Score everything.** Every dimension gets a 0-5 score. The overall health score gives the user a single number to track over time. Re-auditing in 30 days should show improvement.
8. **Name names.** Every finding should reference specific campaigns, keywords, ad groups, or search terms. "Some keywords are underperforming" is not an audit finding — "$423 spent on 'free plumbing advice' with 0 conversions" is.
