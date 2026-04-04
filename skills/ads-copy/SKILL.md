---
name: ads-copy
description: Generate and A/B test Google Ads copy. Use when asked to write ad copy, headlines, descriptions, create ad variants, test ad messaging, improve CTR, or generate RSA (Responsive Search Ad) components. Trigger on "ad copy", "write ads", "headlines", "descriptions", "RSA", "responsive search ad", "ad text", "ad creative", "improve CTR", "ad A/B test", "ad variants", "write me an ad", or when the user wants to improve click-through rate on existing ads.
---

# Ad Copy Generator + A/B Tester

Write Google Ads RSA copy and run structured A/B tests to find winning messaging.

## Setup

This skill requires the AdsAgent MCP server. Try calling `mcp__adsagent__listConnectedAccounts` to verify it's connected.

- **If the tool doesn't exist** → the MCP server isn't configured. Run `/ads-audit` which walks the user through full setup (MCP server, token, account selection, and business context).
- **If the tool works** → read `~/.adsagent/config.json` for `apiKey` and `accountId`. If missing, run `/ads-audit` for onboarding.

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

**Always count characters. Flag any that exceed limits.**

Generate 3-4 headlines per category:

| Category | Purpose | Pin guidance |
|----------|---------|-------------|
| Product/Service + Location | Relevance, match search intent | **Pin to position 1** |
| Value proposition | Why this business over competitors | Position 2 candidate |
| Trust signals | Credibility (ratings, years, locations) | Any position |
| Call to action | Drive the click | Position 3 candidate |

Descriptions (one per angle):
1. **Core value prop** + location specificity
2. **Differentiator** + CTA
3. **Trust signal** + social proof
4. **Urgency** or seasonal angle

### 4. Present variants

Show 2-3 variants, each with a distinct messaging angle. Name the angle so it's clear what's being tested.

```
VARIANT A: "[Angle Name]"
  H1 [Pin 1]: [Service] in [Location]       (XX chars)
  H2: [Value prop headline]                  (XX chars)
  H3: [CTA headline]                         (XX chars)
  D1: [Value prop description — max 90 chars]
  D2: [Trust/CTA description — max 90 chars]

VARIANT B: "[Different Angle]"
  H1 [Pin 1]: ...
  ...
```

Always show character counts. Always show pin positions.

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

### 7. Check results

After the test period, pull results:

```
mcp__adsagent__listAds → compare metrics for each variant
```

| Variant | Impressions | Clicks | CTR | Conversions | Conv Rate | Winner? |
|---------|------------|--------|-----|-------------|-----------|---------|
| A       |            |        |     |             |           |         |
| B       |            |        |     |             |           |         |

**Interpret:**
- Higher CTR + higher conversion rate → clear winner, pause the loser
- Higher CTR + lower conversion rate → ad attracts clicks but landing page doesn't match the promise. Suggest `/ads-landing` to fix alignment
- No statistical difference → need more volume or a bolder variant

After deciding a winner: pause the loser with `mcp__adsagent__pauseAd`, keep the winner running.

## Rules

1. **Business context first.** Read `~/.adsagent/business-context.json` before doing anything. If it doesn't exist, build it.
2. **Research before writing.** Always pull current performance data. Don't write copy in a vacuum.
3. **Character limits are hard.** Count every headline (≤30) and description (≤90). No exceptions.
4. **Never deploy without confirmation.** Show the exact copy, get a yes, then create/update.
5. **Note changeIds.** Every write returns one. Tell the user they can undo within 7 days.
6. **Ground copy in conversion data.** If conversion data is available, use the language that converts.
7. **Seasonal awareness.** Check the business context for peak/slow months. Adjust urgency and messaging accordingly.
8. **Defer to /ads for account management.** This skill writes copy and deploys ads. For bid/budget/keyword work, use `/ads`.
