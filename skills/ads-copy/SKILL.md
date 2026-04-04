---
name: ads-copy
description: Generate and A/B test Google Ads copy. Use when asked to write ad copy, headlines, descriptions, create ad variants, test ad messaging, improve CTR, or generate RSA (Responsive Search Ad) components. Trigger on "ad copy", "write ads", "headlines", "descriptions", "RSA", "responsive search ad", "ad text", "ad creative", "improve CTR", "ad A/B test", "ad variants", "write me an ad", or when the user wants to improve click-through rate on existing ads.
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

# Ad Copy Generator + A/B Tester

Write Google Ads RSA copy and run structured A/B tests to find winning messaging.

## Setup

Follow the **MCP Server Detection** section above to verify a Google Ads MCP server is available.

- **If no MCP server is found** → guide the user through setup per the MCP Server Detection instructions, or run `/ads-audit` which walks through full setup (MCP server, token, account selection, and business context).
- **If the MCP server is available** → read `~/.adsagent/config.json` for `apiKey` and `accountId`. If missing, run `/ads-audit` for onboarding.

## Reference Documents

Before generating any copy, read these reference documents for expert-level context:

- `references/rsa-best-practices.md` — Character limits, headline formulas, pinning strategy, A/B methodology, common mistakes
- Read from ads skill: `../ads/references/industry-benchmarks.md` — Industry-specific CTR benchmarks to beat
- Read from ads skill: `../ads/references/quality-score-framework.md` — How ad copy impacts Quality Score components

These contain the specific formulas, character counts, and patterns that separate amateur ad copy from expert-level RSAs.

## Business Context — Read First, Ask Once

Every ad copy decision depends on understanding the business. This skill stores business context in `~/.adsagent/business-context.json` so it only needs to be gathered once.

### On every invocation:

1. **Read `~/.adsagent/business-context.json`**. If it exists and has content, use it — skip the intake interview.
2. **If missing or empty**, run the intake interview below, then save the result.
3. **If the user volunteers new info** (new service, changed positioning, seasonal update), merge it into the existing file.

### Intake interview

Gather these fields. Don't ask them as a rigid checklist — pull what you can from context (the account's existing ads, website, campaign names) and only ask what's missing.

```json
{
  "business_name": "",
  "industry": "",
  "services": [""],
  "locations": [""],
  "target_audience": "",
  "brand_voice": {
    "tone": "",
    "words_to_avoid": [""],
    "words_to_use": [""]
  },
  "differentiators": [""],
  "competitors": [""],
  "seasonality": {
    "peak_months": [""],
    "slow_months": [""],
    "seasonal_hooks": [""]
  },
  "keyword_landscape": {
    "high_intent_terms": [""],
    "competitive_terms": [""],
    "long_tail_opportunities": [""]
  },
  "social_proof": [""],
  "offers_or_promotions": [""],
  "landing_pages": {},
  "notes": ""
}
```

**Why each field matters for copy:**

| Field | How it shapes copy |
|-------|-------------------|
| `industry` | Sets baseline competitive intensity and CPC expectations |
| `services` | Determines headline categories and description angles |
| `locations` | Geo-specific headlines get higher quality scores and CTR |
| `brand_voice` | Tone, forbidden words, preferred language |
| `differentiators` | These ARE the value prop headlines — the reason someone picks you |
| `competitors` | Knowing who you're against sharpens positioning (without naming them in ads) |
| `seasonality` | Tells you WHEN to push urgency copy vs. evergreen, which months to bid up |
| `keyword_landscape` | High-intent terms go in headlines; competitive terms need sharper differentiation; long-tail = cheaper, more specific copy angles |
| `social_proof` | Reviews, awards, years in business — trust signal headlines and descriptions |
| `offers_or_promotions` | Time-sensitive copy angles, CTA variations |
| `landing_pages` | Copy must match the page or conversions drop — know what's there |

### Bootstrapping from existing data

Before asking the user anything, try to fill fields from what's already available:

- `mcp__adsagent__getAccountInfo` → business name, location hints
- `mcp__adsagent__listCampaigns` → service categories, geo targeting
- `mcp__adsagent__listAds` → current voice, headlines in use
- `mcp__adsagent__getKeywords` → keyword landscape
- `mcp__adsagent__getSearchTermReport` → real user language, long-tail opportunities
- `mcp__adsagent__getImpressionShare` → competitive pressure signals

Present what you found and ask the user to confirm/correct/fill gaps. This is faster and more accurate than starting from zero.

## Persona-Informed Copy

Cross-reference `~/.adsagent/personas/{accountId}.json` (created by `/ads-audit`) and `~/.adsagent/business-context.json` to ground every piece of copy in real customer data.

### How personas shape copy decisions

| Persona Field | Copy Application |
|---------------|-----------------|
| `search_terms` | Use these exact words and phrases in headlines — they're the language real customers use |
| `pain_points` | Lead descriptions with the pain point, then present the solution. Pain > features for click-through |
| `decision_trigger` | This IS your CTA angle. If the trigger is "seeing reviews mentioned", put the review count in a headline |
| `primary_goal` | Match H1 to this goal. The first headline should answer "will this page help me do X?" |
| `demographics` | Adjust register: corporate buyer gets different language than homeowner. Technical user gets specs, consumer gets benefits |

### Persona-to-headline mapping

For each ad group, identify which persona(s) it serves:
1. Look at the ad group's keywords and match to persona `search_terms`
2. Write H1 using the persona's `primary_goal` language
3. Write value prop headlines using the persona's `pain_points` (solution framing)
4. Write CTA using the persona's `decision_trigger`

If an ad group serves multiple personas (common in broad campaigns), create separate ad variants — one optimized per persona — and A/B test which performs better.

## Ad Strength vs Actual Performance

Google's ad strength score optimizes for Google's internal ad diversity goals, not your conversion rate. Treat it as a secondary signal, never a primary optimization target.

### The hierarchy (most to least important)

1. **Conversion rate** — does the ad produce customers?
2. **CTR** — does the ad get clicks from the right people?
3. **CPA** — what does each conversion cost?
4. **Ad strength** — does Google think there's enough variety?

### Specific rules

| Situation | Action |
|-----------|--------|
| "Excellent" ad strength, CTR < 2% | Ad strength is misleading. The headlines are varied but not compelling. Rewrite for relevance over diversity |
| "Good" ad strength, CTR > 5% | Do not touch this ad to chase "Excellent". The ad is working. Ad strength is a vanity metric here |
| "Poor" ad strength, CTR > industry avg | Add more headline/description variety to satisfy Google's diversity requirement, but don't change the winning headlines |
| "Poor" ad strength, CTR < industry avg | Both signals agree — the ad needs a rewrite. Start with headline relevance to keywords |
| Ad strength drops after headline edit | If CTR improved, ignore the ad strength drop. If CTR also dropped, revert |

### When ad strength IS useful

- Ensuring you have 8+ distinct headlines (not minor variations of the same message)
- Ensuring at least 1 headline per category (service, value prop, trust, CTA)
- Flagging when all descriptions say the same thing in different words
- Catching missing keyword insertion opportunities

## Competitive Differentiation

Read `~/.adsagent/business-context.json` `competitors` and `differentiators` fields. If empty, infer competitors from auction overlap (high impression share keywords where rank-lost IS is elevated suggest active competitors).

### Rules for competitive copy

| Rule | Rationale |
|------|-----------|
| NEVER name competitors in ad copy | Policy violation risk with Google Ads. Also sends brand awareness to competitors. Even "Better than [Competitor]" is dangerous |
| NEVER use "best" or "#1" without qualification | Google requires substantiation for superlative claims. "Best-Rated on Google" is OK if verifiable. "Best Plumber" is not |
| DO use specific features competitors lack | "Same-Day Service" beats "Better Service". Specificity implies superiority without claiming it |
| DO use pricing advantage if real | "Flat-Rate Pricing" or "From $99" differentiates against competitors with opaque pricing |
| DO use trust signals aggressively | "25+ Years", "4.9★ Google Rating", "500+ 5-Star Reviews" — these are verifiable and powerful |
| DO use location specificity | "Seattle's Own [Service]" or "Locally Owned Since 1998" differentiates against national chains |
| DO use speed/convenience | "Same-Day", "24/7", "Book Online in 60 Seconds" — operational advantages competitors may not match |
| DO use guarantees | "Satisfaction Guaranteed", "Free Re-Service", "No Fix, No Fee" — risk reversal converts |

### Differentiation angle selection

Based on the competitive landscape, choose the strongest angle:

| Business Situation | Best Differentiation Angle | Example Headline |
|-------------------|---------------------------|-----------------|
| Competing against national chains | Local ownership, personal service, community ties | "Family-Owned Since 2005" |
| Competing against cheaper alternatives | Quality, guarantees, reviews, expertise | "Licensed & Insured Pros" |
| Competing against premium alternatives | Value, transparent pricing, same quality for less | "Premium Service, Fair Prices" |
| Unique service offering | The specific feature itself | "Same-Day Emergency Visits" |
| Crowded market, no clear advantage | Speed, convenience, or customer experience | "Book Online — Arrive in 1hr" |

## Workflow

### 1. Understand the brief

Detect or ask:
- What product/service is this ad for?
- Target audience or segment?
- Which campaign/ad group? (pull with `mcp__adsagent__listCampaigns` → `mcp__adsagent__listAdGroups`)
- Landing page URL?
- Any geographic targeting?

Cross-reference against the business context — if the user says "write copy for boarding" and context has boarding details, you already know the angles.

### 2. Research what's working

Pull data before writing — copy should be grounded in what converts, not guesses.

**Current ad performance:**
- `mcp__adsagent__listAds` — existing headlines/descriptions and their metrics
- `mcp__adsagent__getKeywords` — active keywords
- `mcp__adsagent__getSearchTermReport` — actual user queries (reveals real language and intent)
- `mcp__adsagent__getCampaignPerformance` — CTR/conversion benchmarks to beat

**Use seasonality context.** If business context shows peak months, factor that into copy urgency. During slow months, lean on evergreen value props. During peaks, lean on scarcity and timeliness.

**Use keyword landscape context.** For competitive terms (high CPC, many bidders), copy must differentiate harder — lead with what's unique, not what everyone says. For long-tail terms, match the specific intent closely.

**If the user has a database with lead/conversion data**, query it to find which keywords and messaging actually convert. The language paying customers use is the language your ads should mirror.

### 3. Generate RSA components

Google RSA: up to **15 headlines** (30 chars max) and **4 descriptions** (90 chars max). Google's AI mixes and matches them.

**Always count characters. Flag any that exceed limits. A single character over = rejected by Google.**

#### Headline Formulas by Category

Use these formulas to generate varied, high-performing headlines. Each formula is battle-tested across thousands of accounts. Adapt the template to the specific business.

| # | Category | Formula | Template | Example | Chars |
|---|----------|---------|----------|---------|-------|
| 1 | Service+Location | [Service] in [City] | `___ in ___` | Dog Boarding in Seattle | 23 |
| 2 | Service+Location | [City] [Service] Provider | `___ ___ Provider` | Austin Plumbing Experts | 24 |
| 3 | Service+Location | [Neighborhood] [Service] | `___ ___` | Capitol Hill Dog Boarding | 26 |
| 4 | Value Prop | [Benefit] [Service] | `___ ___` | Same-Day AC Repair | 18 |
| 5 | Value Prop | [Adj] [Service] [Qualifier] | `___ ___ ___` | Affordable Pet Grooming | 24 |
| 6 | Value Prop | [Service] You Can Trust | `___ You Can Trust` | Plumbing You Can Trust | 22 |
| 7 | Trust Signal | [N]+ Years Experience | `___+ Years Experience` | 25+ Years Experience | 20 |
| 8 | Trust Signal | [Rating]★ Rated [Service] | `___★ Rated ___` | 4.9★ Rated Dog Boarding | 24 |
| 9 | Trust Signal | [N]+ [Reviews/Clients] | `___+ 5-Star Reviews` | 500+ 5-Star Reviews | 21 |
| 10 | CTA | Get [Benefit] Today | `Get ___ Today` | Get Your Free Quote Today | 25 |
| 11 | CTA | Book [Service] Now | `Book ___ Now` | Book Your Cleaning Now | 22 |
| 12 | CTA | Call Now — [Benefit] | `Call Now — ___` | Call Now — Free Estimate | 24 |
| 13 | Urgency | [Offer] — Limited Time | `___ — Limited Time` | 20% Off — Limited Time | 23 |
| 14 | Urgency | [N] Spots Left [Period] | `___ Spots Left ___` | 5 Spots Left This Week | 23 |
| 15 | Price/Offer | [Service] From $[Price] | `___ From $___` | Teeth Cleaning From $99 | 24 |
| 16 | Price/Offer | Free [Offer] Included | `Free ___ Included` | Free Consultation Included | 27 |
| 17 | Question | Need [Service]? | `Need ___?` | Need Emergency Plumbing? | 24 |
| 18 | Question | Looking for [Service]? | `Looking for ___?` | Looking for Dog Boarding? | 25 |
| 19 | Benefit | [Result] Guaranteed | `___ Guaranteed` | Satisfaction Guaranteed | 23 |
| 20 | Benefit | [Outcome] in [Timeframe] | `___ in ___` | Results in 30 Days | 19 |
| 21 | Social Proof | Trusted by [N]+ [Clients] | `Trusted by ___+ ___` | Trusted by 500+ Families | 25 |
| 22 | Social Proof | [City]'s Top-Rated [Service] | `___'s Top-Rated ___` | Seattle's Top-Rated Vet | 24 |
| 23 | Differentiator | [Unique Feature] [Service] | `___ ___` | Licensed & Insured Pros | 23 |
| 24 | Differentiator | [Guarantee] or [Refund] | `___ or ___` | On Time or It's Free | 20 |

**Headline selection rules:**
- Generate 3-4 headlines per category for a total of 12-15
- Pin 1 Service+Location headline to Position 1 (highest relevance impact)
- Pin 1 CTA headline to Position 3 (Google shows H3 less often — make it count when shown)
- Leave Position 2 unpinned to let Google test Value Prop, Trust, and Differentiator headlines
- Never pin more than 3 headlines total — over-pinning reduces Google's optimization ability

#### Description Formulas

| # | Angle | Template | Example | Chars |
|---|-------|----------|---------|-------|
| 1 | Core Value + Location | [Primary benefit] for [audience] in [location]. [Secondary benefit]. [CTA]. | Professional dog boarding for Seattle pet parents. Cage-free play all day. Book online today. | 88 |
| 2 | Differentiator + CTA | [What makes you different]. [Proof point]. [CTA with urgency]. | Family-owned since 2005 with 500+ 5-star reviews. Schedule your free estimate — limited availability. | 90 |
| 3 | Trust + Social Proof | [Trust signal]. [Social proof]. [Outcome promise]. | Licensed, bonded & insured. Rated 4.9★ by 300+ homeowners. Your satisfaction guaranteed. | 85 |
| 4 | Urgency + Offer | [Time-sensitive hook]. [Offer detail]. [CTA]. | This week only — 20% off your first visit. New clients save on [service]. Call now to claim. | 87 |
| 5 | Problem + Solution | [Pain point]? [Solution]. [Proof]. [CTA]. | Tired of unreliable contractors? We show up on time, every time. 25+ years trusted. Get a quote. | 90 |
| 6 | Feature Stack | [Feature 1]. [Feature 2]. [Feature 3]. [CTA]. | Same-day service. Transparent pricing. No hidden fees. Request your free quote online today. | 86 |
| 7 | Persona-Targeted | [Persona pain point]. [How you solve it]. [Decision trigger]. | Busy schedule? We offer evening & weekend appointments. Book online in 60 seconds. | 80 |
| 8 | Seasonal/Timely | [Seasonal hook]. [Relevant service]. [Urgency CTA]. | Spring is peak pest season — protect your home now. Licensed exterminators. Book this week. | 87 |

**Description selection rules:**
- Always generate 4 descriptions (the RSA maximum)
- D1 should be the strongest all-around description (core value + location) — it shows most often
- D2 should emphasize the primary differentiator
- D3 should lead with trust/social proof
- D4 should be seasonal or offer-based (swap this out when promotions change)
- Every description must end with a CTA verb: Call, Book, Get, Schedule, Request, Visit, Contact
- Character count is STRICT: 90 chars max. Measure before finalizing. It's better to be 85 chars and punchy than 90 chars and cramped

### 4. Present variants

Show 2-3 variants, each with a distinct messaging angle. Name the angle so it's clear what's being tested.

```
VARIANT A: "[Angle Name — e.g., Trust & Experience]"
  Target persona: [persona name from ~/.adsagent/personas/]
  H1 [Pin 1]: [Service] in [Location]       (XX chars)
  H2: [Value prop headline]                  (XX chars)
  H3: [Trust headline]                       (XX chars)
  H4: [CTA headline]                         (XX chars)
  ... (up to 15 headlines)
  D1: [Core value + location — max 90 chars] (XX chars)
  D2: [Differentiator + CTA — max 90 chars]  (XX chars)
  D3: [Trust + proof — max 90 chars]         (XX chars)
  D4: [Urgency/offer — max 90 chars]         (XX chars)

VARIANT B: "[Different Angle — e.g., Price & Value]"
  Target persona: [persona name]
  H1 [Pin 1]: ...
  ...
```

Always show character counts. Always show pin positions. Always name the target persona.

**Variant differentiation rules:**
- Each variant must test a meaningfully different angle — not minor word swaps
- Good test: "Trust & Expertise" vs "Speed & Convenience" vs "Price & Value"
- Bad test: "Call Today" vs "Call Now" vs "Call Us" (not different enough to learn from)
- If the account has multiple personas, create one variant per persona

### 5. Deploy

After user approves a variant, push it live:

- **New ad:** `mcp__adsagent__createAd` — create the RSA in the target ad group (created paused)
- **Update existing:** `mcp__adsagent__updateAdAssets` — replace headlines/descriptions on a live ad
- **Enable when ready:** `mcp__adsagent__enableAd`

Always confirm before any write operation. Note the `changeId` returned — user can undo within 7 days via `mcp__adsagent__undoChange`.

### 6. A/B test (if running one)

1. **Identify the variable** — messaging angle, CTA style, emotional vs. practical
2. **Deploy both variants** as separate ads in the same ad group (both paused, enable together)
3. **Minimum run:** 2 weeks or 100 clicks per variant, whichever comes first
4. **Success metric:** CTR for awareness campaigns, conversion rate for bottom-funnel

**Statistical significance rules:**
- Do not call a winner with <100 clicks per variant — the data isn't reliable
- A "winner" needs at least 20% relative CTR or conversion rate difference to be meaningful
- If the difference is <20% after 200+ clicks each, the variants are functionally equivalent — pick the one with better conversion rate, or run a bolder test
- If one variant has 2x+ the conversion rate, call it immediately — don't wait for click minimums

### 7. Check results

After the test period, pull results:

```
mcp__adsagent__listAds → compare metrics for each variant
```

| Variant | Impressions | Clicks | CTR | Conversions | Conv Rate | CPA | Winner? |
|---------|------------|--------|-----|-------------|-----------|-----|---------|
| A       |            |        |     |             |           |     |         |
| B       |            |        |     |             |           |     |         |

**Interpretation matrix:**

| CTR | Conv Rate | Diagnosis | Action |
|-----|-----------|-----------|--------|
| A higher | A higher | Clear winner | Pause B. Iterate on A's angle with fresh headlines |
| A higher | B higher | A attracts more clicks but B converts better | Keep B as primary. Test A's headlines on B's landing page — the click-through message may need landing page alignment. Offer `/ads-landing` |
| Similar | Similar | No meaningful difference | Need a bolder test — the variants were too similar. Change the core messaging angle, not just word choice |
| Both low | Both low | Neither variant works | The problem isn't A vs B — it's the overall approach. Check: keyword intent match, landing page quality, offer strength. May need `/ads-audit` to diagnose |

After deciding a winner: pause the loser with `mcp__adsagent__pauseAd`, keep the winner running. Then create a new variant to test against the winner — continuous improvement, never stop testing.

## Rules

1. **Business context first.** Read `~/.adsagent/business-context.json` before doing anything. If it doesn't exist, build it.
2. **Research before writing.** Always pull current performance data. Don't write copy in a vacuum.
3. **Character limits are hard.** Count every headline (<=30) and description (<=90). No exceptions. When in doubt, count again.
4. **Never deploy without confirmation.** Show the exact copy, get a yes, then create/update.
5. **Note changeIds.** Every write returns one. Tell the user they can undo within 7 days.
6. **Ground copy in conversion data.** If conversion data is available, use the language that converts. Customer language > marketing language.
7. **Seasonal awareness.** Check the business context for peak/slow months. Adjust urgency and messaging accordingly.
8. **Defer to /ads for account management.** This skill writes copy and deploys ads. For bid/budget/keyword work, use `/ads`.
9. **Personas over guesses.** If personas exist, every headline should trace back to a persona's language or triggers. If they don't exist, recommend `/ads-audit` to build them.
10. **Differentiate, don't imitate.** Read the competitors field and write copy that stands apart. Generic copy that could belong to any competitor is a waste of an ad slot.
