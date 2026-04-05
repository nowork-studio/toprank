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
2. **Builds business context** — gathers and saves business information to `~/.adsagent/business-context.json` so every other ads skill (copy, landing pages, competitive analysis) can use it without re-asking

Run this before anything else. If another ads skill finds `business-context.json` missing, it should point the user here.

## Reference Documents

Read these reference documents during analysis for expert-level context:

- `references/account-health-scoring.md` — Detailed scoring rubrics for each dimension (0-5 scale with specific criteria)
- Read from ads skill: `../ads/references/industry-benchmarks.md` — Compare account metrics to industry averages
- Read from ads skill: `../ads/references/quality-score-framework.md` — QS diagnostics and component-level analysis
- Read from ads skill: `../ads/references/search-term-analysis-guide.md` — Search term relevance scoring methodology
- Read from ads skill: `../ads/references/campaign-structure-guide.md` — Account structure best practices

Read these before starting Phase 2 analysis. They contain the numeric thresholds that separate a generic audit from an expert one.

## Phase 1: Pull Account Data

Gather everything in parallel before asking the user a single question. The goal is to show up informed.

**Pull all data calls simultaneously to minimize wait time. Use parallel tool calls — every call below is independent and can run at the same time.**

**Account basics:**
- `mcp__adsagent__getAccountInfo` — business name, currency, timezone
- `mcp__adsagent__getAccountSettings` — auto-tagging, tracking template, conversion setup

**Campaign structure:**
- `mcp__adsagent__listCampaigns` — all campaigns with spend, clicks, conversions
- `mcp__adsagent__listAdGroups` — ad groups per campaign (focus on top-spend campaigns)

**Performance data:**
- `mcp__adsagent__getCampaignPerformance` — daily trends for the last 30 days
- `mcp__adsagent__getKeywords` — top keywords with quality scores, bids, conversions
- `mcp__adsagent__getSearchTermReport` — actual search queries triggering ads
- `mcp__adsagent__getImpressionShare` — search IS, top IS, budget-lost IS, rank-lost IS

**Ads and conversions:**
- `mcp__adsagent__listAds` — ad copy, status, and per-ad metrics
- `mcp__adsagent__getConversionActions` — what conversions are set up and how they're configured
- `mcp__adsagent__getNegativeKeywords` — existing negative keyword coverage

**Recommendations:**
- `mcp__adsagent__getRecommendations` — Google's optimization suggestions (evaluate critically, don't blindly follow)

**Minimum data for a meaningful audit:** `listCampaigns`, `getKeywords`, and `getImpressionShare` must return data. If the account has zero campaigns or zero spend, skip to Phase 3 (business context) — there's nothing to audit yet, but the context is still valuable for account setup.

## Phase 2: Analyze and Score

Work through each dimension. For each one, assign a numeric score (0-5) and a status label.

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

**6. Impression share** (Score 0-5)

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

Express as:
1. Dollar amount (30 days)
2. Percentage of total spend
3. Annualized projection
4. Breakdown by category with specific keywords/terms named

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

For each discovered persona:

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

Save to `~/.adsagent/personas/{accountId}.json`:

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

Now that you understand the account, fill in the business context. Pull as much as possible from the data you already have — only ask the user for what you can't infer.

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

### What to ask the user

Present what you inferred, then ask for what's missing. Frame it conversationally, not as a checklist.

**Always ask:**
- "What makes you different from competitors?" → `differentiators`
- "Who are your main competitors?" → `competitors`
- "Is your business seasonal? When's your busiest time?" → `seasonality`
- "What's your website URL?" → for landing page context

**Ask if not obvious from data:**
- Industry (if campaign names don't make it clear)
- Target audience (if search terms don't reveal it)
- Current offers or promotions
- Social proof (reviews, awards, years in business)

### Website analysis

If the user provides their website URL (or it's visible in ad final URLs):

- Note the URL in `landing_pages`
- Look at what the ads link to — do headlines match landing page content?
- Note any offers, trust signals, or CTAs visible on the site that could inform ad copy

### Save the context

Write the complete business context to `~/.adsagent/business-context.json`:

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

Present findings as a concise, actionable report. No fluff — every line should either inform a decision or recommend an action.

### Report format

```
# Google Ads Audit: [Business Name]
**Account:** [ID] | **Period:** Last 30 days | **Date:** [today]

## Scorecard
| Dimension            | Score (0-5) | Status    | Key Finding                          |
|----------------------|-------------|-----------|--------------------------------------|
| Conversion tracking  | X           | [label]   | [one line — the most important fact] |
| Campaign structure   | X           | [label]   | [one line]                           |
| Keyword health       | X           | [label]   | [one line]                           |
| Search term quality  | X           | [label]   | [one line]                           |
| Ad copy              | X           | [label]   | [one line]                           |
| Impression share     | X           | [label]   | [one line]                           |
| Spend efficiency     | X           | [label]   | [one line]                           |

## Overall Health: [0-100] — [Critical / Needs Work / OK / Strong / Excellent]

## Key Numbers
- **Total spend (30d):** $X,XXX
- **Conversions:** XX at $XX.XX CPA
- **Top campaign:** [name] — XX% of spend, XX% of conversions
- **Wasted spend (30d):** $X,XXX (XX% of total)
- **Annualized waste:** ~$XX,XXX

## Wasted Spend Analysis
**Total wasted spend (30d):** $X,XXX (XX% of total spend)
- Non-converting keywords: $X,XXX across N keywords
  - [keyword 1]: $XXX spent, XX clicks, 0 conversions — [diagnosis]
  - [keyword 2]: $XXX spent, XX clicks, 0 conversions — [diagnosis]
  - ... (top 5 by spend)
- Irrelevant search terms: ~$X,XXX estimated
  - [term 1]: $XXX, XX clicks — [why it's irrelevant]
  - [term 2]: $XXX, XX clicks — [why it's irrelevant]
  - ... (top 5 by spend)
- Display/structural waste: $XXX (if applicable)

## Impression Share Analysis
**Current Search IS:** XX% | **Budget-Lost:** XX% | **Rank-Lost:** XX%

[Use the 2x2 matrix interpretation to diagnose]

Diagnosis: [e.g., "This is primarily a budget problem — the campaign runs out of budget by 2pm daily. 
Increasing budget 30% would capture an estimated X additional conversions at similar CPA."]

## Personas Discovered
| Persona | Searches like... | Converts on... | Value |
|---------|-----------------|----------------|-------|
| [name] | [2-3 example search terms] | [converting keywords/services] | [high/med/low + why] |

Personas saved to `~/.adsagent/personas/{accountId}.json` — used by `/ads-copy` for headline generation.

## Top 3 Actions (do these first)
1. **[Action]** — [why, expected impact in dollars or conversions]
2. **[Action]** — [why, expected impact]
3. **[Action]** — [why, expected impact]

## Detailed Findings
[Organized by dimension — only include dimensions that scored 0-3.
For each, state the problem, show the data, recommend the fix.]

### [Dimension Name] — Score X/5
**Problem:** [specific issue with numbers]
**Data:** [the evidence]
**Fix:** [specific action, which tool/skill to use]
**Impact:** [estimated improvement in dollars or conversions]

## Business Context Saved
Saved to `~/.adsagent/business-context.json` — other ads skills
(/ads-copy, /ads-landing, /ads-compete) will use this automatically.
[List any fields that are incomplete and need user input later.]
```

### What makes a good action item

- **Specific:** "Pause keyword 'free dog food' — $847 spent, 0 conversions" not "Review underperforming keywords"
- **Quantified:** Include the spend, impressions, or conversions at stake
- **Prioritized:** Highest-impact items first. Stopping waste > starting new things
- **Actionable with /ads:** Every recommendation should be something the user can execute immediately using the `/ads` skill
- **Dollar-denominated:** Whenever possible, express impact as "save $X/month" or "gain X conversions/month at $Y CPA"

### Scoring thresholds for action priority

| Overall Score | Recommended Next Step |
|---------------|----------------------|
| 0-25 | "Your account has critical issues. I'd recommend pausing spend on the worst campaigns and fixing conversion tracking and structure before resuming." |
| 26-50 | "There's significant waste to eliminate. Let's fix the top 3 issues — I estimate that saves $X/month. Run `/ads` to execute." |
| 51-75 | "The account is functional but leaving money on the table. The optimizations below could improve CPA by 15-30%." |
| 76-100 | "This is a well-managed account. The suggestions below are marginal improvements — focus on scaling what's working." |

## Conditional Handoffs

After delivering the report, proactively offer the right next step based on what the audit found.

### Ad Copy Issues

If ad copy scored 0-2 (low CTR, low headline variety, few RSAs per ad group):

> "Your ad copy needs work — [N] ad groups have CTR below [X]% (industry average is [Y]%). Run `/ads-copy` to generate better RSA variants with A/B testing. It'll use the business context I just saved."

### Impression Share / Bid Issues

If impression share scored 0-2 (high budget-lost or rank-lost IS):

> "You're losing [X]% of potential traffic to [budget/rank]. Run `/ads` to optimize bids on your best keywords — I estimate [N] additional conversions/month are available."

### Keyword Gaps

If search term analysis found 3+ converting terms not yet added as keywords:

> "I found [N] search terms converting that aren't keywords yet. Want me to add them now via `/ads`? Here they are:
> | Term | Conversions | CPA | Recommended Match Type |"

### Waste Elimination

If wasted spend > 15% of total:

> "You're wasting ~$[X]/month ([Y]% of spend). Want me to pause the non-converting keywords and add the negative keywords? I'll show each change before making it. Run `/ads` to execute."

### Landing Page Problems

If CTR is healthy (>3%) but conversion rate is below 2% across multiple ad groups:

> "Your ads get clicks but conversions are low — the landing pages likely don't match the ad promise. Run `/ads-landing` to audit keyword-to-landing-page alignment."

### Competitive Intelligence

If impression share is declining or the user asks about competitors:

> "Run `/ads-compete` to monitor your competitive landscape — see who's bidding on your terms and how your share is trending."

### Always Offer

At the end of every audit:

> "Run `/ads` to execute any of these recommendations. I've saved your business context and personas — all ads skills will use them automatically."

## Rules

1. **Data first, questions second.** Pull all account data before asking the user anything. Show up informed.
2. **Infer before asking.** Don't ask "what industry are you in?" if the campaigns clearly say "plumbing services."
3. **Be specific.** Name the campaigns, keywords, and dollar amounts. Vague advice is useless.
4. **Prioritize by money.** The biggest waste or biggest opportunity comes first.
5. **Save the context.** Always write `business-context.json` — this is the handoff to every other ads skill.
6. **Don't fix things here.** This skill diagnoses and recommends. The user executes fixes with `/ads`. Offer to switch to `/ads` for implementation.
7. **Score everything.** Every dimension gets a 0-5 score. The overall health score gives the user a single number to track over time. Re-auditing in 30 days should show improvement.
8. **Name names.** Every finding should reference specific campaigns, keywords, ad groups, or search terms. "Some keywords are underperforming" is not an audit finding — "$423 spent on 'free plumbing advice' with 0 conversions" is.
