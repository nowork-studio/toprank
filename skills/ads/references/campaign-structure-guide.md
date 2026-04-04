# Campaign Structure Guide

Account structure best practices for Google Ads. Covers campaign organization, ad group design, naming conventions, budget allocation, and settings. Every recommendation includes concrete thresholds and decision criteria.

---

## Ad Group Strategy: SKAG vs. STAG vs. Themed

### Evolution of Ad Group Strategy

| Era | Strategy | Keywords per Ad Group | Rationale | Current Status |
|-----|----------|-----------------------|-----------|----------------|
| 2012-2017 | **SKAG** (Single Keyword Ad Groups) | 1 | Maximize ad relevance; exact control over which ad shows for which keyword | **Deprecated** — close variants and smart bidding made this counterproductive |
| 2017-2020 | **STAG** (Single Theme Ad Groups) | 3-7 | Group close variants; reduce account complexity while maintaining relevance | **Transitional** — still viable but often too granular |
| 2020-present | **Themed Ad Groups** | 10-20 | Leverage smart bidding; consolidate conversion data; match Google's AI-driven auction system | **Current best practice** |

### Why SKAGs No Longer Work

| Problem | Explanation |
|---------|------------|
| Close variants eliminated keyword-level control | Google matches exact match keywords to synonyms, paraphrases, and implied-intent queries regardless of ad group structure |
| Data fragmentation kills smart bidding | A SKAG with 5 conversions/month cannot feed tCPA effectively; the same 50 conversions consolidated into one themed ad group can |
| Account management overhead | 500 SKAGs = 500 ad groups to manage, each needing unique ads; 25 themed groups covers the same keywords with 95% less maintenance |
| Google rewards consolidation | Google's recommendation engine and smart bidding algorithms perform better with fewer, larger ad groups |

### Current Recommendation: Themed Ad Groups

| Parameter | Guideline |
|-----------|-----------|
| Keywords per ad group | 10-20 closely themed keywords |
| Theme definition | Keywords should share the same intent AND could be answered by the same landing page |
| Ads per ad group | 2-3 RSAs (Responsive Search Ads) |
| Landing page | 1 primary landing page per ad group (all keywords should be relevant to that page) |
| Match types | Mix of exact and phrase match within the same ad group is fine; broad match only with smart bidding |

### Theme Grouping Examples

| Business | Theme | Keywords in Ad Group | Landing Page |
|----------|-------|---------------------|-------------|
| Plumbing | Emergency repair | emergency plumber, 24 hour plumber, plumber emergency service, urgent plumbing repair, after hours plumber | /emergency-plumbing |
| Plumbing | Drain cleaning | drain cleaning service, clogged drain repair, drain unclogging, sewer line cleaning, blocked drain plumber | /drain-cleaning |
| SaaS | Free trial | [brand] free trial, try [brand] free, [brand] demo, test [brand], [brand] trial account | /free-trial |
| SaaS | Pricing | [brand] pricing, [brand] cost, [brand] plans, how much is [brand], [brand] subscription price | /pricing |
| E-commerce | Running shoes men | men's running shoes, running shoes for men, male running shoes, men's jogging shoes, athletic running shoes men | /mens-running-shoes |

---

## Campaign Organization Patterns

### When to Create Separate Campaigns

Create a new campaign when you need any of these to differ:

| Reason to Split | Example | Why It Requires a Separate Campaign |
|----------------|---------|-------------------------------------|
| **Different daily budgets** | Brand ($50/day) vs. Non-brand ($200/day) | Budget is set at campaign level |
| **Different bid strategies** | Brand (Target IS) vs. Non-brand (tCPA) | Bid strategy is set at campaign level |
| **Different geographic targets** | New York vs. Los Angeles | Location targeting is campaign-level |
| **Different ad schedules** | B2B (Mon-Fri 8am-6pm) vs. B2C (all hours) | Ad schedule is campaign-level |
| **Different networks** | Search Only vs. Search + Display | Network targeting is campaign-level |
| **Different languages** | English vs. Spanish | Language targeting is campaign-level |
| **Fundamentally different services** | Plumbing vs. HVAC | Different landing pages, ads, and conversion goals |

### When NOT to Split Campaigns

| Scenario | Why Splitting Hurts | Better Approach |
|----------|-------------------|-----------------|
| Splitting by match type (Exact campaign, Phrase campaign, Broad campaign) | Fragments conversion data; smart bidding needs all data in one place | Mix match types within ad groups |
| Splitting every service into its own campaign | 20 campaigns with 5 conversions/month each = too thin for smart bidding | Group related services into one campaign with themed ad groups |
| Splitting brand + non-brand into 10+ campaigns each | Management overhead; inconsistent settings | 1 brand campaign + 2-4 non-brand campaigns organized by service line |
| Splitting by device (mobile campaign, desktop campaign) | Fragments data; smart bidding adjusts bids by device automatically | Use device bid adjustments within one campaign if needed |

**Rule of thumb**: Fewer campaigns with more data each > more campaigns with less data each. Only split when there is a structural reason (budget, bid strategy, geo, schedule).

### Standard Campaign Architecture

| Campaign | Purpose | Bid Strategy | Budget Allocation |
|----------|---------|-------------|-------------------|
| **Brand** | Own brand terms | Target IS (95% top of page) or Manual CPC | 5-10% of total budget |
| **Non-Brand Core** | Highest-value services/products | tCPA or tROAS | 50-60% of total budget |
| **Non-Brand Secondary** | Lower-priority or newer services | tCPA or Maximize Conversions | 15-20% of total budget |
| **Competitor** | Competitor brand terms (optional) | Manual CPC (tight control) | 5-10% of total budget |
| **Testing** | New keywords, audiences, ad copy tests | Maximize Conversions or Manual CPC | 10-15% of total budget |
| **Remarketing (Display/Search)** | Re-engage past visitors | tCPA | 5-10% of total budget |

---

## Naming Conventions

### Convention Format

```
[Network]-[Product/Service]-[Location]-[Audience/Targeting]-[Match/Strategy]
```

### Campaign Naming Examples

| Campaign Name | What It Tells You |
|--------------|-------------------|
| `SRC-Plumbing-Emergency-NYC-tCPA` | Search, Emergency Plumbing, New York City, Target CPA bidding |
| `SRC-Brand-National-TargetIS` | Search, Brand terms, National targeting, Target Impression Share |
| `SRC-HVAC-Install-Chicago-MaxConv` | Search, HVAC Installation, Chicago, Maximize Conversions |
| `DSP-Remarketing-AllServices-National` | Display, Remarketing, All Services, National |
| `SHP-RunningShoes-Mens-US` | Shopping, Running Shoes, Men's, United States |
| `VID-Brand-Awareness-National` | Video (YouTube), Brand Awareness, National |
| `PFM-LeadGen-HomeSvc-TX-tCPA` | Performance Max, Lead Gen, Home Services, Texas, tCPA |

### Network Prefixes

| Prefix | Network |
|--------|---------|
| `SRC` | Search |
| `DSP` | Display |
| `SHP` | Shopping |
| `VID` | Video (YouTube) |
| `PFM` | Performance Max |
| `DSA` | Dynamic Search Ads |
| `APP` | App campaigns |

### Ad Group Naming Examples

| Ad Group Name | Parent Campaign |
|--------------|-----------------|
| `Emergency-Plumber-General` | SRC-Plumbing-Emergency-NYC-tCPA |
| `Emergency-Plumber-24Hour` | SRC-Plumbing-Emergency-NYC-tCPA |
| `Emergency-Plumber-Burst-Pipe` | SRC-Plumbing-Emergency-NYC-tCPA |
| `Brand-Exact` | SRC-Brand-National-TargetIS |
| `Brand-Phrase` | SRC-Brand-National-TargetIS |
| `Competitor-AcmePlumbing` | SRC-Competitor-NYC-ManualCPC |

---

## Budget Allocation Framework

### The 70/20/10 Model

| Tier | Allocation | Purpose | Campaign Types |
|------|-----------|---------|----------------|
| **Proven (70%)** | 70% of total budget | Campaigns with established CPA/ROAS that consistently deliver | Brand, core non-brand with 60+ days of data |
| **Testing (20%)** | 20% of total budget | Campaigns being optimized or scaling into new areas | New service lines, new geo expansions, bid strategy tests |
| **Experimental (10%)** | 10% of total budget | High-risk, high-reward experiments | Competitor campaigns, new match types, new networks, DSA |

### Budget Allocation by Campaign Type

| Campaign Type | % of Total Budget | Minimum Daily Budget | Rationale |
|--------------|-------------------|---------------------|-----------|
| Brand | 5-10% | $10/day or 10x brand CPC | Protect brand; high ROAS; don't underfund |
| Non-Brand Core | 50-60% | 10x target CPA | Main revenue driver; needs scale |
| Non-Brand Secondary | 15-20% | 5x target CPA | Growth channel; needs enough to learn |
| Competitor | 5-10% | 5x competitor CPC | Higher CPC; cap spend tightly |
| Testing / Experimental | 10-15% | 10x expected CPC | Enough to gather statistically meaningful data |
| Remarketing | 5-10% | $20/day minimum | High ROI; often underfunded |

### Budget Sufficiency Test

```
Minimum daily budget per campaign = Target CPA x 10

If budget < CPA x 5:
  Campaign is critically underfunded. Smart bidding cannot learn.
  Action: Increase budget or consolidate into another campaign.

If budget = CPA x 5-10:
  Campaign is minimally funded. Results will be inconsistent.
  Action: Acceptable for testing phase; increase for scaling.

If budget >= CPA x 10:
  Campaign is properly funded. Smart bidding can optimize.
  Action: Monitor performance; scale if CPA is at target.

If budget >= CPA x 20:
  Campaign has headroom. Smart bidding has room to explore.
  Action: Best scenario for automated bidding; expect stable results.
```

---

## Ad Group Structure Checklist

| Element | Guideline | Why |
|---------|-----------|-----|
| Keywords per ad group | 10-20 tightly themed | Enough data for smart bidding; tight enough for ad relevance |
| RSAs per ad group | 2-3 | Google recommends 1+ RSA; 2-3 gives testing variety. More than 3 fragments impressions |
| Unique headlines per RSA | 8-15 (Google's maximum) | More headlines = more combinations for Google to test |
| Unique descriptions per RSA | 4 (Google's maximum) | Include keyword, benefits, CTA, and social proof |
| Landing page per ad group | 1 primary URL | All keywords in the group should be relevant to this page |
| Extensions | At minimum: 4 sitelinks, 4 callouts, 1 structured snippet | Extensions increase ad real estate and CTR by 10-20% |

### RSA Best Practices

| Element | Requirements |
|---------|-------------|
| Headline 1 | Must contain the primary keyword or close variant |
| Headline 2 | Unique value proposition or benefit |
| Headline 3 | CTA or trust signal |
| Headlines 4-15 | Variations: numbers, questions, urgency, different benefits, brand name |
| Description 1 | Expand on the value prop; include keyword naturally |
| Description 2 | CTA + differentiator (guarantee, free quote, years in business) |
| Pin sparingly | Only pin Headline 1 (for keyword relevance) and Description 1 (for primary message). Pinning reduces Google's ability to optimize combinations |

---

## Campaign Settings Checklist

Review these settings for every new campaign. Incorrect defaults waste budget.

| Setting | Recommended Value | Default (Beware) | Why It Matters |
|---------|-------------------|-------------------|----------------|
| **Networks** | Search only (uncheck Display and Search Partners) | Search + Display + Partners (checked) | Display and Partners have very different performance; run them as separate campaigns |
| **Location targeting** | "Presence: People in or regularly in your targeted locations" | "Presence or interest" (default) | "Interest" shows ads to people searching ABOUT your location but not IN it; wastes budget for local businesses |
| **Location exclusion** | "Presence: People in your excluded locations" | Same as targeting | Ensure excluded locations are actually excluded |
| **Language** | Target your audience's language(s) only | All languages (sometimes default) | Prevent ads showing for queries in languages you don't serve |
| **Ad rotation** | "Optimize: Prefer best performing ads" | Optimize (default is fine) | Let Google's algorithm pick the best ad combination |
| **Start / end dates** | Set end dates for promotions; no end date for evergreen | No end date (default) | Promotional campaigns should auto-stop |
| **Ad schedule** | Set to business hours if B2B; 24/7 if B2C with online conversion | 24/7 (default) | B2B: Why pay for 2am clicks? B2C: online conversions happen at all hours |
| **Device targeting** | All devices (use bid adjustments if needed) | All devices (default is fine) | Smart bidding adjusts by device; manual campaigns may need mobile bid adjustment |
| **Brand exclusions** | Exclude own brand from non-brand campaigns | None (default) | Prevent brand queries from inflating non-brand campaign performance metrics |
| **Dynamic search ads** | Off unless intentionally using DSA | Sometimes on by default | DSA can match to unexpected pages; use only when deliberately set up |

### Location Targeting Detail

| Business Type | Location Setting | Target Radius / Areas |
|--------------|-----------------|----------------------|
| Local service (plumber, dentist) | Presence only | 15-30 mile radius around service area |
| Regional business | Presence only | State or metro area |
| National e-commerce | Presence only | Entire country |
| International | Presence only | Specific countries; separate campaigns per country/language |
| Local + willing to travel | Presence only | Primary area (tight radius) + Secondary area (wider radius, separate campaign with lower bids) |

---

## When to Restructure an Account

### Red Flags That Indicate Structural Problems

| Signal | Likely Structural Issue | Restructure Action |
|--------|------------------------|-------------------|
| 50% of campaigns have < 10 conversions/month | Over-segmentation; data too thin for smart bidding | Consolidate campaigns with same goal into fewer campaigns |
| Ad groups have 50+ keywords each | Under-segmentation; ads cannot be relevant to all keywords | Split into themed groups of 10-20 keywords |
| Same keyword appears in 3+ campaigns | Keyword cannibalization; campaigns compete against each other | Deduplicate; assign each keyword to one campaign/ad group |
| Brand and non-brand mixed in same campaign | Inflated performance metrics; budget allocation unclear | Separate brand into its own campaign |
| Display network checked on Search campaigns | Display traffic mixed with search; metrics are muddled | Uncheck Display; run Display as separate campaign if needed |
| Location set to "Presence or interest" for local business | Paying for out-of-area clicks | Change to "Presence" only |
| No negative keyword lists applied | Wasting spend on irrelevant queries | Build and apply universal negative lists |
| Campaign names are inconsistent | Impossible to filter, sort, or analyze by dimension | Rename all campaigns using consistent naming convention |

### Restructure Priority Order

1. **Fix campaign settings** (networks, locations, language) -- immediate impact, zero cost
2. **Separate brand from non-brand** -- clarifies performance data
3. **Build and apply negative keyword lists** -- stops wasted spend within days
4. **Consolidate thin campaigns** -- feeds smart bidding with better data
5. **Reorganize ad groups** -- improves ad relevance and QS
6. **Rewrite ad copy** -- matches new structure with relevant messaging
7. **Update landing pages** -- align with new ad group themes
