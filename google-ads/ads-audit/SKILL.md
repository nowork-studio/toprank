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
| No arguments / "audit my ads" | **Full account** | Audit all campaigns, all passes |
| "focus on grooming" / "grooming campaigns" | **Service-scoped** | Filter to campaigns matching the service keyword. Still pull account-level data for context (conversion tracking, account settings), but deep-dive analysis and recommendations focus on the matched campaigns only |
| "campaign X" / specific campaign name | **Campaign-scoped** | Same as service-scoped but matched to exact campaign(s) |
| "just check wasted spend" / "impression share" | **Focus-scoped** | Full data pull but report only the requested area in depth. All 3 passes still run for context, but detailed findings and actions focus on the requested area |

### Scope threading rules

1. **Always pull `listCampaigns` unfiltered first** — you need the full picture to identify which campaigns match the scope and to calculate account-wide metrics like total spend (needed for waste percentages)
2. **Filter deep-dive data to scoped campaigns** — In Phase 1B, only pull per-campaign data (`getCampaignSettings`, `getKeywords`, `getSearchTermReport`, `listAds`) for campaigns matching the scope. This saves API calls and keeps the analysis focused
3. **Analyze relative to scope** — If scoped to grooming campaigns, waste calculations and keyword analysis reflect grooming keywords only, not the whole account. Make this explicit in the report header: "Scoped to: [Grooming campaigns]"
4. **Account-wide checks still run** — Signal quality, tracking, and account settings are account-level regardless of scope. Check them normally but note when issues affect the scoped campaigns specifically
5. **Persona discovery uses scoped data** — Build personas from search terms within the scoped campaigns only
6. **Business context is always full-account** — `business-context.json` captures the whole business, not just the scoped segment. Don't narrow business context to the scope

### Scope matching

Match campaign names, ad group names, and keyword themes using case-insensitive substring matching. For example, "grooming" matches campaigns named "Tukwila Grooming Search", "Grooming Test", etc. If no campaigns match, tell the user what campaigns exist and ask them to clarify.

## Reference Documents

**Always read before Phase 2:**
- `references/account-health-scoring.md` — Diagnostic thresholds, red flags, interpretation matrices, pulse metric annotation rules, and the dollar-driven Quick Wins filter
- `../shared/industry-templates.json` — Industry presets (margin, AOV, target CPA, red flags, quick-start negatives). Cache in memory for the session
- `../shared/ppc-math.md` — Break-even CPA, headroom, LTV:CAC, IS opportunity, budget forecasting. Read before computing any dollar-denominated finding

**Read during Phase 2.5 / Phase 3:**
- `references/persona-discovery.md` — Persona template, derivation rules, and JSON schema (read during Phase 2.5)
- `references/business-context.md` — Website crawl procedure, business-context.json schema, and unit economics population rules (read during Phase 3)

**Read on demand** — only load these when the analysis surfaces a relevant issue. Loading all of them upfront wastes ~1,000 lines of context:
- `../ads/references/quality-score-framework.md` — Read only if avg QS < 6 or high-spend keywords have QS < 5
- `../ads/references/search-term-analysis-guide.md` — Read only during Layer 2 search term quality analysis
- `../ads/references/industry-benchmarks.md` — Read only during Layer 3 efficiency analysis for CPA comparison
- `../ads/references/campaign-structure-guide.md` — Read only if structural issues detected (>30 keywords per ad group, brand/non-brand mixed, poor naming)

## Step 0: Policy Freshness Check (runs in parallel with Phase 1A)

Verify policy assumptions are current — but don't block data collection on it. Run this check in parallel with Phase 1A since they're independent.

1. Read `../shared/policy-registry.json` and check each entry: if `last_verified` + `stale_after_days` < today's date, the entry is stale.
2. **High-volatility stale entries:** Use WebSearch to check for recent Google Ads changes related to each stale entry's `area` (e.g., "Google Ads broad match behavior changes 2026"). Compare findings against the `assumption` field. If discrepancies are found:
   - Display a warning banner at the top of the audit: `⚠️ Policy drift detected: [area] — [brief description of what changed]. Recommendations in this area may need manual verification.`
   - Suggest updating `policy-registry.json` with corrected assumptions and today's date.
3. **Moderate-volatility stale entries:** Note them in the audit output as an informational line (e.g., "ℹ️ [area] last verified [date] — may warrant a check") but do not block the audit.
4. **Stable stale entries:** Skip — these rarely change.

## Phase 1: Pull Account Data

Gather everything in parallel before asking the user a single question. The goal is to show up informed.

**Date range:** Default to `LAST_30_DAYS` for a full audit — 30 days gives enough signal for meaningful waste calculations, impression share trends, and bid strategy assessment. Use `LAST_7_DAYS` only for daily campaign performance queries on accounts with 3+ campaigns (to stay within GAQL's 50-row limit).

**Use the adaptive data fetching algorithm from `../shared/gaql-cookbook.md`.** The approach varies by account size — read the cookbook's "Adaptive data fetching algorithm" section. Here's the summary:

### Phase 1A: Account basics + sizing probe (parallel)

Pull these simultaneously — they don't require campaign IDs and they tell you the account size:

- `getAccountInfo` — business name, currency, timezone
- `getAccountSettings` — auto-tagging, tracking template, conversion setup
- `listCampaigns` — all campaigns with spend, clicks, conversions **(also serves as the sizing probe — default limit is 100)**
- `getConversionActions` — what conversions are set up
- `getRecommendations` — Google's optimization suggestions

**After Phase 1A, apply scope filtering:** If the user specified a scope (see Scope Detection above), identify which campaigns match. Log the matched campaigns and their IDs. If no campaigns match, stop and ask the user to clarify. For the rest of the audit, "active campaigns" means scope-matched campaigns (or all campaigns if no scope was specified).

**After Phase 1B: kick off the website crawl.** Once `listAds` data is available (pulled in Phase 1B), resolve the website URL and start the website crawl (see `references/business-context.md`) immediately. The crawl results aren't needed until Phase 3's user questions, so it runs in the background while you finish analysis.

### Phase 1B: Adaptive data pull (depends on account size)

Count the **in-scope** enabled campaigns with spend from Phase 1A, then follow the cookbook's adaptive algorithm. When scoped, only pull per-campaign data for in-scope campaigns — but still run account-wide GAQL queries (they're cheap and provide context).

**In addition to the cookbook's strategy**, always pull `getCampaignSettings(campaignId)` and `listAds(campaignId)` for each in-scope campaign (needed for Display Network detection, bidding strategy assessment, and ad copy analysis).

### PMax data pull

For each in-scope PMax campaign (identified from `listCampaigns` by campaign type), pull in parallel:
- `getPmaxAssetGroups(campaignId)` — asset group status and performance
- `getPmaxAssets(assetGroupId)` for each asset group — completeness check (headlines, images, video)

### Audience segment pull

Pull audience data for Search campaigns via GAQL — needed for the Layer 2 audience signals check. PMax audience signals come from `getPmaxAssetGroups` (already pulled above).

Search campaign audiences are typically set at the **ad group level** (observation mode), not at campaign level. Query both levels — finding audiences at either level means the check passes:

```
SELECT campaign.id, campaign.name,
       ad_group.id, ad_group.name,
       ad_group_criterion.type,
       ad_group_criterion.user_list.user_list
FROM ad_group_criterion
WHERE campaign.id IN (<in-scope campaign IDs>)
  AND ad_group_criterion.type IN ('USER_LIST', 'CUSTOM_AUDIENCE', 'COMBINED_AUDIENCE')
  AND campaign.status = 'ENABLED'
```

If this returns zero rows, also check campaign-level criteria (less common but possible):

```
SELECT campaign.id, campaign.name,
       campaign_criterion.type,
       campaign_criterion.user_list.user_list
FROM campaign_criterion
WHERE campaign.id IN (<in-scope campaign IDs>)
  AND campaign_criterion.type IN ('USER_LIST', 'CUSTOM_AUDIENCE', 'COMBINED_AUDIENCE')
```

If both queries return zero rows for all Search campaigns, flag "no audience segments" in Layer 2.

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

`radius_units` enum: `UNSPECIFIED` = 0, `UNKNOWN` = 1, `MILES` = 2, `KILOMETERS` = 3. There is no "meters" value — Google Ads only supports miles and kilometers for proximity targeting. Do NOT claim "no geo-targeting" based solely on `getCampaignSettings` — the GAQL query is authoritative.

### Fallback

If `runGaqlQuery` errors or is unavailable, fall back to per-campaign helper tools for each active campaign, run in parallel.

**Minimum data for a meaningful audit:** Campaign list, keyword data, impression share, and conversion actions must return data. If the account has zero campaigns or zero spend, skip to Phase 3 (business context).

**Launch mode (small/new account gate):** If total spend < $500 or total conversions < 10 in the date range, the account doesn't have enough data for meaningful waste rate, demand captured, or CPA metrics. Switch to **Launch mode**:

1. Layer 1 (tracking check) — still critical, catch setup problems early
2. Layer 2 (structure check only) — campaign organization, keyword themes, ad copy completeness, industry-template red-flag checks
3. Skip Layers 3-5 — they'd be statistically meaningless. Still compute and persist pulse metrics (with `"low_data": true`) so re-audits have a baseline
4. Report format: use the launch-mode template — no pulse metrics (too little data to compute waste or headroom in dollars), no dollar-impact claims. Instead surface a **Readiness checklist** scored `ready | needs fix | blocker` and a **Next milestone** trigger
5. **Set the next milestone** in `audit-history.json`:
   ```json
   "next_milestone": { "conversions": 30, "spend_usd": 1000, "check_after": "2026-05-14" }
   ```
   The thresholds are `max(30, industry_template.smart_bidding_min_conv_month)` for conversions, `$1,000` for spend, and 30 days out for the date. Whichever hits first triggers the next full audit.
6. Still run Phase 2.5 (personas) and Phase 3 (business context) — these are valuable regardless of data volume. Use `industry_template.recommended_conversion_actions` to recommend missing conversion actions.

**Milestone check on subsequent runs:** If `audit-history.json.next_milestone` exists and any threshold has been crossed, graduate to a full audit and clear the milestone. Otherwise repeat launch-mode with a brief "tracking toward milestone" update.

## Phase 2: Analyze

The audit analyzes the account in **5 layers** (each depends on the one below), then presents findings as **3 actionable passes** (organized by what the user should do). The layers determine analysis order — the passes determine report order.

```
Analysis layers (work through in order):
  Layer 1: Signals    → "Can I trust the data?"
  Layer 2: Relevance  → "Am I in the right auctions?"
  Layer 3: Efficiency → "Am I spending wisely?"
  Layer 4: Scale      → "How do I get more?"
  Layer 5: Growth     → "What's next?"

Report passes (organized by action type):
  Pass 1: Stop Wasting    → findings that represent money being burned
  Pass 2: Capture More    → missed opportunities to get more conversions
  Pass 3: Fix Fundamentals → structural issues that compound over time
```

**Scope-aware analysis:** When the audit is scoped, analyze campaign-level data using only in-scope campaigns. Account-level checks (tracking, settings) run account-wide but note how issues affect the scoped campaigns.

Read `references/account-health-scoring.md` for diagnostic thresholds, red flags, and interpretation matrices. The threshold bands tell you what's "bad enough to flag" vs. "acceptable" — use them to decide whether a finding makes it into the report at all.

---

### Layer 1: Signals — "Can I trust the data?"

If signals are broken, every insight downstream is built on lies — and Smart Bidding can't optimize what it can't measure.

**Hard stop conditions** (→ Pass 1, top priority):
- Zero conversion actions set up → "Stop spending. Set up conversion tracking first."
- Conversion actions exist but 0 conversions recorded despite 50+ clicks → "Tracking is broken. Fix it before spending another dollar."
- Only micro-conversions (page views, button clicks) as primary actions → "You're optimizing for the wrong thing. Set up a real conversion action (form submit, phone call, purchase)."

If any hard stop triggers, skip to Phase 4 with the tracking fix as the only recommendation. No point analyzing what you can't measure.

**Checks** (flag issues, assign to appropriate pass):
- Auto-tagging: is it enabled? If not, Google Analytics integration breaks (→ Pass 3)
- Counting method: "Every" vs "One"? Lead gen should use "One", e-commerce should use "Every" (→ Pass 1 if inflating conversion count)
- **Enhanced Conversions:** Is hashed first-party data being sent? Without it, cross-device and cross-browser journeys are invisible to Smart Bidding (→ Pass 3)
- **Consent Mode v2:** Mandatory for EU since March 2024. Without it, bid strategies are flying blind in privacy-regulated markets (→ Pass 3)
- **Data density:** Smart Bidding needs 30+ conversions/month per campaign for tCPA, 50+ for tROAS. If a campaign uses automated bidding but has <15 conversions/month, the algorithm doesn't have enough signal to learn (→ Pass 3)
- **Attribution model:** Last-click attribution is deprecated — data-driven attribution (DDA) is the only model for new conversion actions. Flag any existing actions still on last-click (→ Pass 3)

---

### Layer 2: Relevance — "Am I in the right auctions?"

Before asking "am I getting enough impressions?", ask "are these the right impressions?" and "am I competitive in the auctions I'm entering?"

#### Pre-checks (settings that silently burn money) → Pass 1

These are checked first because they affect every dollar spent:

**Location targeting intent:** Check `getCampaignSettings` for each active campaign. The field is `campaign.geo_target_type_setting.positive_geo_target_type`. Verify it's set to **`PRESENCE`** — NOT `PRESENCE_OR_INTEREST` (Google's default, which shows ads to anyone *searching about* your location from anywhere in the world). For a local business, this can waste 20-30% of budget.

**Search Partners:** Check if Search Partners is enabled. If search partner clicks are high but conversions are zero → recommend turning it off.

**Display Network leakage:** Check `networkDisplayEnabled` on Search campaigns. If any Search campaign has Display Network on with display clicks > 20 and 0 display conversions → turn off Display Network.

#### Campaign structure analysis

- Are brand and non-brand keywords in separate campaigns? Mixing them inflates brand CTR and hides non-brand problems (→ Pass 3)
- For multi-location businesses, is there geo-specific structure? (→ Pass 3)
- One ad group with 200 keywords = poor relevance, QS will suffer (→ Pass 3)
- **PMax cannibalization:** If PMax campaigns exist alongside Search campaigns, check whether PMax is eating high-intent brand search traffic. Compare brand Search campaign IS — if it's below 90% with PMax running, PMax may be cannibalizing. Recommend adding brand terms as negative keywords in PMax (→ Pass 1 if significant spend, Pass 3 if structural)
- Reference `../ads/references/campaign-structure-guide.md`

#### Keyword health analysis

- Calculate keyword waste: spend on keywords where `conversions = 0 AND spend > 2x account average CPA`. The 2x CPA threshold respects Smart Bidding's learning curve — a keyword that's spent double your typical conversion cost with nothing to show has had a fair shot (→ Pass 1)
- Before killing any keyword with $50+ spend, check assisted conversions. If it has assists, investigate before pausing
- Average QS weighted by spend (not by keyword count) — a QS-3 keyword spending $2,000/month matters more than a QS-3 keyword spending $5/month (→ Pass 3 if QS < 5 on high-spend keywords)
- Zombie keywords: 0 impressions for 30+ days → pause (→ Pass 1)
- Reference `../ads/references/quality-score-framework.md`

#### Search term quality analysis

- Score search term relevance using `../ads/references/search-term-analysis-guide.md`
- Flag irrelevant search terms by category: wrong service, wrong location, wrong intent, competitor names, brand terms in non-brand campaigns (→ Pass 1)
- **Negative conflict cross-check:** Before recommending new negatives, cross-reference them against converting keywords and converting search terms. If a proposed negative would block a converting term, don't add it
- Flag converting search terms (2+ conversions) not yet added as keywords (→ Pass 2)
- Flag obvious negative keyword gaps: "free" variants, "jobs"/"careers" variants, wrong service types (→ Pass 1)

#### Ad copy & creative health

- RSA count per ad group: <2 means no testing is possible (→ Pass 3)
- Headline diversity: are the 15 headlines actually different? Check if keywords appear in headlines
- Ad extensions/assets: sitelinks, callouts, structured snippets, image extensions. Missing assets reduce Ad Rank (→ Pass 3)
- **PMax asset groups:** For each PMax campaign, check asset group completeness via `getPmaxAssets`:
  - Headlines: at least 5 (max 15)
  - Long headlines: at least 1
  - Descriptions: at least 2
  - Marketing images: at least 1 landscape + 1 square
  - Logo: at least 1
  - Video: at least 1. If missing, Google auto-generates low-quality video — flag it (→ Pass 3)

#### Audience signals check

Google's algorithms lean heavily on audience signals — campaigns without them are competing with less data than competitors.

- **PMax asset groups:** Check if audience signals are configured (custom segments, your data segments, interests). PMax without audience signals forces Google to start cold — it'll spend more during the learning phase finding the right audience (→ Pass 3)
- **Search campaigns:** Check for audience segments (observation or targeting mode). If no audiences are attached, the account is missing bid signal data that could improve Smart Bidding performance (→ Pass 3)
- **Remarketing/customer match:** If no remarketing lists or customer match audiences exist in the account, flag as a coverage gap — these are the highest-ROAS audiences available (→ Pass 2)

#### Auction fitness (Lost IS — Rank) → Pass 3

Lost IS (Rank) is a *relevance* signal, not a scale signal. High rank-lost IS means your Ad Rank is insufficient.

- Isolate Lost IS (Rank) from impression share data. If rank-lost IS > 30%, diagnose via QS components:
  - Expected CTR below average → ad copy needs rewriting
  - Ad relevance below average → ad group themes too broad
  - Landing page experience below average → page speed, mobile UX, content mismatch
- **Do not recommend "spend more" for rank-lost IS.** The fix is improving relevance, not more budget

---

### Layer 3: Efficiency — "Am I spending wisely?"

#### Impression share interpretation

Use the **Impression Share 2x2 Interpretation Matrix** from `references/account-health-scoring.md` to classify each campaign as healthy, relevance problem, capital problem, or structural problem. The matrix determines whether the fix is "improve ads/QS" vs. "increase budget" — getting this wrong gives exactly the wrong advice.

#### Spend efficiency

- Calculate: per-campaign CPA and compare to account average. Flag any campaign with CPA > 150% of account avg (→ Pass 1)
- Calculate: budget allocation efficiency — does each campaign's % of total budget match its % of total conversions? If one campaign gets 60% of budget but delivers only 30% of conversions, that's a reallocation opportunity (→ Pass 1)
- **PMax efficiency:** If PMax CPA is dramatically worse than Search CPA (>2x) for the same services, PMax may be spending on low-intent display/video traffic (→ Pass 1)

#### Brand vs. Non-Brand segmentation

Many accounts show great ROAS, but 80% comes from brand traffic — paying Google a tax on existing customers.

- Calculate brand vs. non-brand split: what % of conversions and spend comes from brand terms?
- If brand represents >60% of conversions: "Account ROAS is inflated by brand traffic. Non-brand CPA is $X vs. brand CPA of $Y — this is the true acquisition cost"
- If brand and non-brand are mixed in the same campaigns, flag as a structural issue (→ Pass 3)

#### Bid strategy fitness → Pass 3

- Does the bid strategy match the campaign goal and data volume?
- Learning phase stability: are campaigns stuck in "Learning" or "Learning (limited)"?
- For tCPA/tROAS: is the target realistic given historical data? (>50% gap = choking volume or burning money)
- Manual bid adjustments (device, location, schedule) fighting Smart Bidding → remove conflicting adjustments
- **PMax bid strategy:** PMax only supports MAXIMIZE_CONVERSIONS (with optional tCPA) and MAXIMIZE_CONVERSION_VALUE (with optional tROAS). If PMax is on MAXIMIZE_CONVERSIONS with no tCPA cap and CPA is climbing, recommend adding a cap based on historical data

#### Conversion value sanity check → Pass 1

For accounts with mixed-value services, check whether CPA exceeds the likely service value. A $50 CPA on a Board & Train lead (worth $2,000+) is excellent. A $50 CPA on a nail trim (worth $25) is negative ROI — even though it "converted." Read `{data_dir}/business-context.json` if it exists for service value context.

#### Wasted spend calculation

Use the **Wasted Spend Calculation** formula from `references/account-health-scoring.md` — it covers all three waste components (keyword, search term, structural) and includes de-duplication rules to avoid double-counting.

---

### Layer 4: Scale — "How do I get more?" → Pass 2

Only reach this layer after Layers 1-3 are addressed. Scaling broken foundations amplifies waste.

**Budget-constrained winners (Lost IS — Budget):**

Lost IS (Budget) is a capital problem, not a relevance problem: "You're winning auctions but running out of gas."

- For each campaign with budget-lost IS > 20% AND CPA at/below account average → this is the #1 scaling lever. The auction already validates your ads
- **Do not recommend increasing budget on campaigns with rank-lost IS > 30%.** Fix relevance first
- Quantify: "Campaign X has 35% budget-lost IS at $45 CPA. Increasing daily budget by $X could capture ~Y additional conversions/month"

**Coverage gaps:**
- Geographic: locations the business serves but isn't targeting?
- Dayparting: ads dark during hours customers convert? Only flag if >2x conversion rate difference between best and worst periods
- Device: segments accidentally excluded or severely underperforming?
- Audiences: no remarketing lists or customer match segments? These are typically the highest-ROAS audiences — missing them means leaving the easiest conversions on the table

**High-CTR, low-conversion ad groups:**

If an ad group has CTR above campaign average but conversion rate below average, the problem is likely the landing page. Check: does the landing page match intent? Is there a clear CTA?

---

### Layer 5: Growth — "What's next?" → Pass 2 / forward-looking

**Incrementality:**
- If brand campaigns represent >70% of conversions and non-brand CPA is 3x+ brand CPA, the account is over-dependent on brand traffic. Growth requires making non-brand work, not scaling brand
- Flag if the account has never tested pausing brand campaigns to measure organic lift

**Channel expansion:**
- New campaign types: PMax (if not already running), Demand Gen, video
- New keyword territories / adjacent service areas
- Competitor conquesting opportunities

Note these as forward-looking recommendations — they give the user a roadmap after fixing the urgent issues

## Phase 2.5: Persona Discovery

Discover 2-3 customer personas from the ad data. This runs in parallel with Phase 3 — it uses only the data already pulled in Phase 1. Read `references/persona-discovery.md` for the full template, derivation rules, and JSON schema.

Key rules:
- Each persona must be grounded in 5+ actual search terms from the data — no speculative personas
- Name by behavior ("The Emergency Caller"), not demographics
- If all search terms look the same, 1-2 personas max. Don't force 3
- Save to `{data_dir}/personas/{accountId}.json` for downstream skills

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

### Website crawl + extraction

Read `references/business-context.md` for the full crawl procedure (URL resolution, page list, fallbacks, extraction fields). The crawl was kicked off after Phase 1B — results should be ready by now.

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

Write to `{data_dir}/business-context.json` using the schema in `references/business-context.md`. Include `audit_date` (today's date) and `account_id` so future skills know when this was last refreshed.

## Phase 4: Deliver the Audit Report

The report uses the **3-pass structure** — organized by what the user should do, not by what dimension was analyzed. Lead with the three pulse metrics (each self-narrating), then the three passes, then Quick Wins, personas, and questions.

**The #1 rule: no duplication.** Each finding appears in exactly one place.
**The #2 rule: no artificial ratings.** No letter grades. No emoji verdict labels. No severity buckets. Every finding carries its dollar impact and `time_to_fix`; the pulse metrics carry their top contributor and a pass pointer. That's all the prioritization signal the user needs — and it can't invert on dollars.

### Annotating every finding

Each Pass 1/2/3 finding must carry two fields (and only two):

- `dollar_impact_usd`: the monthly dollar value of the waste / opportunity. Use margin-aware framing when `business-context.json.unit_economics.aov_usd` and `profit_margin` are available (see `../shared/ppc-math.md`); fall back to account-average heuristics otherwise. Never mix framings in one report.
- `time_to_fix`: descriptive only — `<5min` | `<15min` | `<30min` | `<2h` | `>2h`. How long the fix takes, not how important it is.

Findings that can't be dollar-denominated (tracking broken, policy risk, missing consent mode) use `dollar_impact_usd: "blocker"` instead of a number. Blockers always float to the top of their pass and always qualify for Quick Wins regardless of fix time.

Sort findings within each pass by `dollar_impact_usd` descending. Blockers first. No severity label, no priority label — the dollar number IS the priority.

### Annotating the pulse metrics

Each pulse metric line is a self-contained finding. It states the raw number, names the single biggest contributor, and points to the pass that fixes it. Rules in `references/account-health-scoring.md` → "Pulse Metrics — The Only Scoreboard":

1. **Waste** — `$X/mo (Y% of spend) · top: "[keyword/term/campaign]" $Z/mo · → Pass 1`
   Signal override: if conversion tracking is broken, replace `$X/mo (Y%)` with `⚠️ Cannot compute — conversion tracking broken` and point to the tracking fix.
2. **Demand captured** — `X% · top opportunity: "[campaign]" ~$Y/mo headroom · → Pass 2`
   Relevance override: if rank-lost IS > 30% on a campaign, point to Pass 3 and explicitly say "fix relevance first — more budget won't help."
3. **CPA** — `$X · vs [industry $Y–$Z OR break-even $Y] · [trend or top structural driver] · → Pass 3 or "healthy — no action"`

**On re-audits**, diff each metric line against the previous `audit-history.json` entry and append `_(was $Y/mo — [what changed])_` when the delta is >5%. When the delta is <5%, say `_(unchanged)_`. No bucket-flipping, no emoji verdict swaps — just three numbers moving (or not).

### Pulse Metrics

Track 3 objective metrics — one per pass. Each has a clear "better" direction and is denominated in something the user already understands.

| Metric | What it measures | Maps to | Better = | How to calculate |
|--------|-----------------|---------|----------|-----------------|
| **Waste rate** | % of spend on zero-conversion entities | Pass 1 | Lower | See **Wasted Spend Calculation** in `references/account-health-scoring.md` (3-component formula: keyword + search term + structural waste) |
| **Demand captured** | Weighted avg impression share on profitable campaigns | Pass 2 | Higher | `avg(search_impression_share)` across campaigns with at least 1 conversion in the period, weighted by spend. If the account has explicit CPA/ROAS targets (from business-context.json), use CPA <= 1.5x target as the profitability filter instead |
| **CPA** | Cost per conversion | Pass 3 | Lower or stable | `total spend / total conversions` for the period |

Each number means something specific. "Waste dropped from 18% to 11%" tells you Pass 1 actions worked. Each number points to a pass. They're in the user's language — dollars and percentages, not arbitrary scales.

### History persistence

After each audit, append a snapshot to `{data_dir}/audit-history.json`:

```json
{
  "history": [
    {
      "date": "2026-04-11",
      "date_range": "2026-03-12 to 2026-04-11",
      "account_id": "7521406707",
      "mode": "full",
      "total_spend": 14320.00,
      "total_conversions": 72,
      "metrics": {
        "waste": {
          "usd_per_month": 1240,
          "pct_of_spend": 8.7,
          "top_contributor": "keyword 'free dog food' — $340/mo",
          "tracking_blocker": false
        },
        "demand_captured": {
          "pct": 42.7,
          "top_opportunity": "Tukwila Search — ~$2,100/mo headroom at 35% budget-lost IS",
          "rank_lost_blocker": false
        },
        "cpa": {
          "usd": 19.88,
          "benchmark_low": 25,
          "benchmark_high": 65,
          "break_even": 72,
          "trend_vs_last": -2.14
        }
      },
      "top_actions": [
        "Paused 'free dog food' keyword ($120 waste)",
        "Budget-lost IS 40% on Tukwila Search at $14 CPA"
      ],
      "next_milestone": null
    }
  ]
}
```

For launch-mode audits, set `"mode": "launch"`, mark each metric with `"low_data": true`, and populate `next_milestone` with the conversion/spend/date thresholds that graduate the next audit to full mode.

**On first audit:** Create the file. Show raw values with no comparison.

**On subsequent audits:** Load the previous entry and compute trends:
- Improved (moved in "better" direction by >5% relative) = show improvement with previous value
- Unchanged (moved <5% either way) = stable
- Worsened (moved in wrong direction by >5%) = flag with warning

### Report structure

```
# [Business Name] — Ads Audit
[Date range] · $X,XXX spent · XX conversions · Last 30 days
[If scoped] Scoped to: [description]
[If unit_economics.source == "inferred_from_template"]
_Profitability estimates use industry defaults — confirm your actual AOV and margin for sharper recommendations._

**Waste: $X/mo (Y% of spend)** — top: "[keyword/term/campaign]" $Z/mo · → Pass 1
[if re-audit] _(was $A/mo — [what changed])_ or _(unchanged)_

**Demand captured: X%** — top opportunity: "[campaign]" ~$Y/mo headroom · → Pass 2
[if rank-lost IS > 30% on a campaign: "Rank-lost IS X% on [campaign] — fix relevance first, more budget won't help · → Pass 3"]
[if re-audit] _(was Y% — [what changed])_ or _(unchanged)_

**CPA: $X** — vs [industry $Y–$Z OR break-even $Y] · [trend or top driver] · → Pass 3 or "healthy — no action"
[if re-audit] _(was $Y — [what changed])_ or _(unchanged)_

[If conversion tracking is broken, the Waste line is replaced with:]
**Waste: ⚠️ Cannot compute — conversion tracking broken** · → Pass 1 (fix tracking first)

## Stop Wasting (Pass 1)
1. **[Action]** — saves $X/mo · `<15min`
2. **[Action]** — saves $X/mo · `<30min`
3. **[Action]** — saves $X/mo · `<2h`

## Capture More (Pass 2)
1. **[Action]** — est. +$X/mo revenue (+Y conv at $Z CPA) · `<30min`
2. **[Action]** — est. +$X/mo · `<2h`
3. **[Action]** — est. +$X/mo · `<2h`

## Fix Fundamentals (Pass 3)
1. **[Action]** — est. $X/mo CPC savings on $Y/mo spend · `>2h`
2. **[Action]** — [impact in $/mo] · `<2h`
3. **[Action]** — [impact in $/mo] · `<30min`

Findings are sorted by dollar impact within each pass. Blockers (tracking,
policy, consent) appear at the top of their pass regardless of dollar value
because they unblock measurement.

## Quick Wins
[Auto-generated: findings where dollar_impact_usd >= 200 AND
time_to_fix IN ('<5min','<15min'), sorted by $ impact desc, max 5.
Blockers (tracking/policy fixes) are pinned at the top regardless of
dollar figure. Each item must include the exact /ads command where
applicable. If none qualify, omit this section entirely — don't fabricate.]

1. [Action] — saves ~$X/mo (`<5min`) · `/ads [command]`
2. [Action] — saves ~$X/mo (`<15min`) · `/ads [command]`

Run `/ads` to execute any of these.

## Personas

| Persona | Example searches | Value |
|---------|-----------------|-------|
| [name] | [2-3 terms] | [why they matter] |

## Questions for You

[Only if business context has gaps that matter for the recommendations.
Max 2-3 questions. Don't ask what you can infer from the data.]
```

**Launch-mode report variant** (total spend < $500 OR total conversions < 10):

```
# [Business Name] — Ads Launch Check
**Launch mode** · [Date range] · $XXX spent · X conversions
_Too little data to compute waste or headroom in dollars — come back after the milestone below._
[If scoped] Scoped to: [description]

[2-3 sentences describing setup quality and readiness — what's configured,
what's missing, what should happen before the next milestone. No optimization
claims, no dollar impact, no score.]

## Readiness Checklist
- ✅ / ⚠️ / 🚫 Conversion tracking — [what's set up or missing]
- ✅ / ⚠️ / 🚫 Campaign structure — [organization quality]
- ✅ / ⚠️ / 🚫 Ad copy completeness — [RSA count, asset coverage]
- ✅ / ⚠️ / 🚫 Targeting — [geo, network, language]
- ✅ / ⚠️ / 🚫 Industry red flags — [from industry-templates.json]

## Fix Before Next Milestone
1. [Blocker or needs-fix item] — `/ads` command or manual step
2. ...

## Next Milestone
Come back for a full audit when **any** of these hits:
- 📈 **XX conversions** (currently X)
- 💵 **$X,000 spent** (currently $XXX)
- 📅 **[date 30 days out]**

I'll remember the milestone — next `/ads-audit` run will auto-upgrade to a full audit.
```

### What makes a good action item

- **Specific:** "Pause keyword 'free dog food' — $847 spent, 0 conversions" not "Review underperforming keywords"
- **Quantified:** Include the spend, impressions, or conversions at stake
- **Dollar-denominated:** Express impact as "save $X/month" or "gain X conversions/month at $Y CPA"
- **Actionable with /ads:** Every recommendation should be executable via `/ads`

### Output discipline

1. **Empty passes are fine.** If a pass finds no issues, show "No issues found" and move on. Don't fabricate findings.
2. **Max 3 items per pass.** If you found 10 things, pick the top 3 by dollar impact. The user can re-audit after fixing those.
3. **Max 3 examples per finding.** Show the top 3 by spend, not an exhaustive list.
4. **No standalone analysis sections.** Don't create separate "Wasted Spend Analysis" or "Impression Share Analysis" sections. Findings belong in their pass.
5. **The entire report should fit in ~60-80 lines of markdown.** If you're over 100 lines, you're duplicating or over-explaining.

### Conditional handoff (pick the single most relevant one)

After the report, add ONE handoff based on the biggest issue found:

| Condition | Handoff |
|-----------|---------|
| Ad copy issues dominate Pass 3 | Suggest `/ads-copy` for RSA variants |
| Rank-lost IS > 30% | Suggest `/ads` for QS and relevance improvements (not budget) |
| Budget-lost IS > 20% on profitable campaigns | Suggest `/ads` for budget optimization |
| 3+ converting search terms not yet keywords | Offer to add them via `/ads` |
| Waste rate > 15% | Offer to pause/negative via `/ads` |
| Brand >60% of conversions | Flag brand dependency risk; suggest non-brand strategy |
| High CTR but low conversion rate | Suggest `/ads-landing` to score the landing page |
| Any ad group with CTR > account avg AND CVR < 50% of account avg | Suggest `/ads-landing` for that landing page |

Don't list all possible handoffs — pick the one that matches the #1 action item.

## Rules

1. **Data first, questions second.** Pull all account data before asking the user anything. Show up informed.
2. **Infer before asking.** Don't ask "what industry are you in?" if the campaigns clearly say "plumbing services."
3. **Be specific.** Name the campaigns, keywords, and dollar amounts. Vague advice is useless.
4. **Prioritize by money.** The biggest waste or biggest opportunity comes first.
5. **Save the context.** Always write `business-context.json` — this is the handoff to every other ads skill.
6. **Don't fix things here.** This skill diagnoses and recommends. The user executes fixes with `/ads`. Offer to switch to `/ads` for implementation.
7. **Track progress.** Always compute and persist pulse metrics. On re-audits, show trends.
8. **Name names.** Every finding should reference specific campaigns, keywords, ad groups, or search terms. "Some keywords are underperforming" is not an audit finding — "$423 spent on 'free plumbing advice' with 0 conversions" is.
