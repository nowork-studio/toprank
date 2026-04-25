---
name: ads-copy
description: Generate and A/B test Google Ads copy. Use when asked to write ad copy, headlines, descriptions, create ad variants, test ad messaging, improve CTR, or generate RSA (Responsive Search Ad) components. Trigger on "ad copy", "write ads", "headlines", "descriptions", "RSA", "responsive search ad", "ad text", "ad creative", "improve CTR", "ad A/B test", "ad variants", "write me an ad", or when the user wants to improve click-through rate on existing ads.
argument-hint: "<ad group name, keyword theme, or 'write new ads'>"
---

## Setup

Read and follow `../shared/preamble.md` — it handles MCP detection, token, and account selection. If config is already cached, this is instant.

# Ad Copy Generator + A/B Tester

Write Google Ads RSA copy and run structured A/B tests to find winning messaging.

## Reference Documents

Before generating any copy, read these reference documents for expert-level context:

- `references/rsa-best-practices.md` — Character limits, headline formulas, pinning strategy, A/B methodology, common mistakes
- Read from ads skill: `../ads/references/industry-benchmarks.md` — Industry-specific CTR benchmarks to beat
- Read from ads skill: `../ads/references/quality-score-framework.md` — How ad copy impacts Quality Score components

These contain the specific formulas, character counts, and patterns that separate amateur ad copy from expert-level RSAs.

## Business Context — Read First, Ask Once

Every ad copy decision depends on understanding the business. Business context is stored in `{data_dir}/business-context.json`.

### On every invocation:

1. **Read `{data_dir}/business-context.json`**. If it exists and has content, use it — skip to the next section.
2. **If missing or empty**, follow the full intake procedure in `../ads-audit/references/business-context.md` (website crawl, data bootstrapping, JSON schema). That document is the single source of truth for gathering business context.
3. **If the user volunteers new info** (new service, changed positioning, seasonal update), merge it into the existing file.

### How business context shapes copy

| Field | Copy application |
|-------|-----------------|
| `services` | Determines headline categories and description angles |
| `locations` | Geo-specific headlines get higher quality scores and CTR |
| `brand_voice` | Tone, forbidden words, preferred language |
| `differentiators` | These ARE the value prop headlines — the reason someone picks you |
| `competitors` | Sharpens positioning (without naming them in ads) |
| `seasonality` | When to push urgency copy vs. evergreen |
| `social_proof` | Trust signal headlines and descriptions |
| `offers_or_promotions` | Time-sensitive copy angles, CTA variations |
| `landing_pages` | Copy must match the page or conversions drop |

## Persona-Informed Copy

Cross-reference `{data_dir}/personas/{accountId}.json` (created by `/ads-audit`) and `{data_dir}/business-context.json` to ground every piece of copy in real customer data.

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

Read `{data_dir}/business-context.json` `competitors` and `differentiators` fields. If empty, infer competitors from auction overlap (high impression share keywords where rank-lost IS is elevated suggest active competitors).

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

## What to pull before writing

Copy should be grounded in what converts, not guesses. One `runScript` call with `ads.gaqlParallel` covers everything you need for almost any copy job — fan out the surfaces below in parallel:

- **Existing ads** (`ad_group_ad`) — current headlines, descriptions, ad-strength, per-ad clicks / CTR / conversions. The baseline to beat.
- **Keywords with quality info** (`keyword_view`) — what's already converting and which QS components are hurting.
- **Search terms** (`search_term_view`) — the actual phrases real customers are typing. The single best source of language for headlines.
- **Campaign-level CTR / CVR** (`campaign`) — the benchmark each variant has to beat.

For brand-wide rewrites, correlate everything in one fan-out. For a single ad group, add `WHERE ad_group.id = …` to each query — the marginal cost is zero. If the user has a database with lead / conversion outcome data, mine it: customer language > marketing language.

Layer on the seasonality and keyword-landscape context from `business-context.json`. Peak months call for urgency, slow months for evergreen value props. Highly competitive heads need sharper differentiation; long-tail tails need closer intent match.

## RSA mechanics

Google RSA: up to **15 headlines (30 chars max)** and **4 descriptions (90 chars max)**. A single character over = rejected. Always count.

The headline formula table (27 formulas across 8 categories) and description formula table (5 formulas) live in `references/rsa-best-practices.md` — that file is the source of truth for what to actually write.

**Pinning strategy:**

- Pin 1 Service+Location headline to Position 1 (highest relevance impact)
- Pin 1 CTA headline to Position 3 (Google shows H3 less often — make it count)
- Leave Position 2 unpinned for Google to test value-prop, trust, and differentiator headlines
- Never pin more than 3 total — over-pinning kneecaps Google's optimization

**Description ordering:**

- D1 = strongest all-around (core value + location). Shows most often.
- D2 = primary differentiator
- D3 = trust / social proof
- D4 = seasonal or offer-based (the slot you swap out when promotions change)
- Every description ends with a CTA verb: Call, Book, Get, Schedule, Request, Visit, Contact
- Punchy at 85 chars beats cramped at 90

## A/B testing

When the user wants to test, deploy variants as separate ads in the same ad group (paused, then enabled together). Each variant must test a **meaningfully different angle** — not word swaps. "Trust & Expertise" vs. "Speed & Convenience" vs. "Price & Value" is a real test; "Call Today" vs. "Call Now" is noise. If the account has multiple personas, create one variant per persona.

**Statistical significance thresholds (apply when calling winners):**

- <100 clicks per variant → too early to call. Wait.
- 100–200 clicks per variant, <20% relative CTR/CVR difference → functionally equivalent; pick on conversion rate or run a bolder test
- ≥20% relative CTR or CVR delta → real winner
- Either variant with 2× the other's conversion rate → call it immediately, don't wait

**Result interpretation matrix:**

| CTR | Conv rate | Diagnosis | Action |
|-----|-----------|-----------|--------|
| A higher | A higher | Clear winner | Pause B. Iterate on A's angle with fresh headlines |
| A higher | B higher | A pulls clicks, B converts | Keep B; test A's headlines on B's landing page — message-match may need work. Offer `/ads-landing` |
| Similar | Similar | No meaningful difference | Variants too similar — change the core angle, not the wording |
| Both low | Both low | Neither works | Problem isn't A vs B — keyword intent, landing page, or offer is broken. Suggest `/ads-audit` |

After a winner is called: pause the loser, then create a new variant to test against the winner. Never stop testing.

## Operating principles

1. **Business context is non-negotiable.** Read `{data_dir}/business-context.json` and `{data_dir}/personas/{accountId}.json` first. If they don't exist or are stale, recommend `/ads-audit` before writing anything generic.
2. **Confirm before deploying.** Show the exact copy, character counts per asset, and pin positions. Get a yes, then push.
3. **Every write returns a `changeId`.** Tell the user it's undoable within 7 days via `undoChange` (assuming the entity hasn't been modified since).
4. **Differentiate, don't imitate.** Read the `competitors` field. Generic copy that could belong to any competitor is a wasted ad slot.
5. **Defer to `/ads` for account management.** This skill writes copy and deploys RSAs; bid / budget / keyword work belongs in `/ads`.
