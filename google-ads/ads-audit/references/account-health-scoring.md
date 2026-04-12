# Account Health — Diagnostic Reference

Thresholds, red flags, interpretation matrices, and benchmarks for Google Ads account audits. Use these to determine severity of findings and assign them to the right pass (Stop Wasting, Capture More, or Fix Fundamentals).

---

## Audit Areas Overview

| Area | Layer | What to Check |
|------|-------|---------------|
| Signal Quality | 1: Signals | Tracking completeness, enhanced conversions, consent mode, data density for Smart Bidding |
| Campaign Structure | 2: Relevance | Organization, segmentation, budget logic, PMax cannibalization |
| Keyword Health | 2: Relevance | Quality scores, match types, zombie keywords, wasted spend |
| Search Term Quality | 2: Relevance | Query relevance, negative coverage, mining opportunities |
| Ad Copy & Creative | 2: Relevance | RSA quantity, variety, asset health, extensions, PMax completeness |
| Impression Share | 2/4: Relevance/Scale | Rank-lost IS = Layer 2 relevance problem; Budget-lost IS = Layer 4 scaling opportunity — different problems, different fixes |
| Spend Efficiency | 3: Efficiency | Wasted spend, CPA, brand vs non-brand split, concentration risk |

---

## Signal Quality

*Layer 1 — "Can I trust the data?"*

If signals are broken, every decision downstream is built on lies — and Smart Bidding can't optimize what it can't measure.

### Red Flags

| Signal | Severity | What It Means |
|--------|----------|---------------|
| 0 conversions in 30 days with spend >5x account CPA | Critical | Tracking likely broken or missing |
| Conversion rate >50% | Critical | Tag firing on page load, not actual conversions |
| All conversions = "Website" (no action names) | High | Default tracking, no meaningful segmentation |
| "Include in conversions" set to YES for micro-conversions | Medium | Inflated conversion counts, misleading CPA |
| Last-click attribution on any campaigns | High | Deprecated since 2023 — data-driven attribution (DDA) is now the only model for new conversion actions. Migrate existing conversion actions to DDA immediately |
| Campaign using tCPA/tROAS with <15 conversions/month | High | Insufficient data density — Smart Bidding can't learn. Need 30+ for tCPA, 50+ for tROAS |
| No Consent Mode v2 with EU traffic | High | Degraded conversion modeling in privacy-regulated markets. Bid strategies underperform |
| Enhanced conversions not enabled | Medium | Cross-device and cross-browser attribution gaps. Smart Bidding missing signal |

---

## Campaign Structure

*Layer 2 — "Am I in the right auctions?"*

### Structure Assessment Checklist

| Check | Passing Threshold | Failing Signal |
|-------|------------------|----------------|
| Keywords per ad group | 5-15 (broad match: 5-10; exact/phrase: 10-20) | >30 per ad group |
| Ad groups per campaign | 5-15 | >25 or just 1 |
| Brand vs. non-brand separation | Separate campaigns | Mixed in same campaign |
| Campaign naming convention | Consistent pattern | No pattern (e.g., "Campaign 1", "test") |
| Budget distribution | Proportional to priority | Equal across all campaigns regardless of performance |
| Location targeting | Set per campaign need | All campaigns target same broad area |
| PMax cannibalization | PMax excluded from brand terms or brand IS stable | PMax running alongside Search with declining brand IS |

---

## Keyword Health

*Layer 2 — "Am I in the right auctions?"*

### Keyword Sub-Metric Thresholds

| Sub-Metric | Critical | Needs Work | OK | Strong |
|------------|----------|------------|----|---------| 
| Average Quality Score | <4 | 4-5 | 6-7 | 8+ |
| Zombie keywords (0 impressions, 90 days) | >50% | 30-50% | 10-30% | <10% |
| Match type intentionality | No strategy | Single match type only | Some match type variation | Deliberate match type strategy aligned with campaign goals and Smart Bidding |
| % Keywords with QS <5 | >40% | 25-40% | 10-25% | <10% |
| Negative keyword count vs. active keywords | 0 negatives | <10% ratio | 10-30% ratio | 30%+ ratio |

### Quality Score Component Diagnosis

| QS Component | Below Average Fix | Average Fix |
|-------------|-------------------|-------------|
| Expected CTR | Rewrite ad copy; test new headlines | Minor headline tweaks; add extensions |
| Ad Relevance | Tighten ad group themes; match headlines to keywords | Ensure primary keyword appears in headline |
| Landing Page Experience | Improve page speed, mobile UX, content relevance | Minor content alignment to ad group theme |

---

## Search Term Quality

*Layer 2 — "Am I in the right auctions?"*

### Search Term Relevance Thresholds

| Relevance % | Severity | Interpretation |
|-------------|----------|---------------|
| <60% | Critical | More than 40% of spend going to irrelevant queries |
| 60-75% | Needs Work | Significant waste; negative keyword gaps |
| 75-85% | OK | Normal for phrase/broad match campaigns |
| 85-90% | Good | Well-managed negative keyword strategy |
| >90% | Strong | Tight keyword control; mostly exact match or excellent negatives |

### Mining Opportunity Assessment

| Signal | Action |
|--------|--------|
| Search term converting at >2x avg. conversion rate, not added as keyword | Add as exact match keyword immediately |
| Search term with 10+ clicks and 0 conversions | Add as negative keyword |
| Search term cluster (3+ related terms) with good performance | Create new ad group targeting this theme |
| Search term revealing new intent angle | Research and potentially create new campaign |

---

## Ad Copy & Creative

*Layer 2 — "Am I fit to compete in the auctions I'm entering?"*

In the RSA + Smart Bidding era, creative variety is how Google's ML finds the right audience segments. Missing assets reduce Ad Rank and limit the algorithm's ability to optimize.

### Ad Copy & Creative Sub-Metrics

| Sub-Metric | Poor | Average | Good | Excellent |
|------------|------|---------|------|-----------| 
| RSAs per ad group | 0-1 | 1 | 2 | 2+ with experiment |
| Headlines per RSA | 3-5 | 6-8 | 9-11 | 12-15 |
| Distinct headline angles | 1-2 | 3 | 4-5 | 6+ |
| Ad strength distribution | >50% Poor | >50% Average | >50% Good | >50% Excellent |
| CTR vs. position benchmark | >30% below | 10-30% below | At benchmark | Above benchmark |
| Descriptions with CTA | 0% | 25-50% | 50-75% | 75%+ |
| Extension coverage | None | 1-2 types | 3-4 types | Full suite |
| PMax asset completeness | Missing asset types | Partial | Most types | All types with variety |

---

## Impression Share

**Data limit:** `getImpressionShare` supports max 90 days (not 365 like other tools). For GAQL impression share queries, the same 90-day practical limit applies. Do not use `LAST_365_DAYS` for impression share data.

*Diagnosed across two layers:*
- **Lost IS (Rank)** = Layer 2 relevance problem. The auction is telling you your Ad Rank is low. Fix with better ads, tighter themes, better landing pages — not more money.
- **Lost IS (Budget)** = Layer 4 scaling opportunity. You're winning auctions but running out of gas. Fix with more budget or narrower targeting.

This split is the most important insight in the audit. Treating both as a single "impression share problem" gives bad advice — telling someone with a relevance problem to spend more money just burns money faster.

### Budget-Lost IS Interpretation (Layer 4 — Scale)

| Budget-Lost IS | Severity | Meaning |
|---------------|----------|---------|
| >30% | Severe | Budget exhausted early in day; missing 30%+ of qualified traffic |
| 20-30% | Moderate | Noticeable budget constraint; consider increase or narrowing |
| 10-20% | Acceptable | Minor constraint; may be intentional budget cap |
| <10% | Good | Budget is not a limiting factor |

### Rank-Lost IS Interpretation (Layer 2 — Relevance)

| Rank-Lost IS | Severity | Meaning |
|-------------|----------|---------|
| >50% | Crisis | Ads rarely showing in competitive positions; QS or bid fundamentally broken. Do NOT spend more — fix relevance first |
| 30-50% | Needs Work | Consistently outranked; improve QS, ad relevance, or landing page experience |
| 15-30% | Competitive | Normal competitive loss; optimize incrementally |
| <15% | Strong | Winning most eligible auctions |

### Impression Share 2x2 Interpretation Matrix

| | Rank-Lost IS LOW (<20%) | Rank-Lost IS HIGH (>20%) |
|---|------------------------|--------------------------|
| **Budget-Lost IS LOW (<15%)** | **Healthy** -- Optimizing at the margins. Focus on bid strategy and new keyword expansion. | **Relevance Problem (Layer 2 fix)** -- Ads not competitive. Improve ad relevance, landing pages, or check QS components. Do not increase budget. |
| **Budget-Lost IS HIGH (>15%)** | **Capital Problem (Layer 4 fix)** -- Ads are competitive when shown. Increase budget, narrow geo targeting, or daypart to stretch budget. | **Structural Problem (Layer 2 fix)** -- Wrong keywords entirely. Audience too broad, poor campaign structure. Rebuild targeting from scratch. |

---

## Spend Efficiency

*Layer 3 — "Am I spending wisely?"*

### Wasted Spend Calculation

Wasted spend is the sum of three components:

```
Keyword waste    = Spend on keywords with 0 conversions AND spend > 2x account avg CPA
Search term waste = Spend on search terms with 10+ clicks AND 0 conversions (data-only filter — no subjective scoring)
Structural waste  = Spend on Display Network clicks in Search campaigns where display clicks > 20 AND 0 display conversions

Wasted Spend % = (keyword waste + search term waste + structural waste) / Total Spend x 100
```

**De-duplication:** Search term waste and keyword waste can overlap (a wasted keyword triggers wasted search terms). To avoid double-counting, calculate keyword waste first, then only count search term waste from search terms that don't map to already-counted wasted keywords.

| Wasted Spend % | Severity | Monthly Waste at $10k Spend |
|---------------|----------|-----------------------------|
| >30% | Critical | >$3,000/month burned |
| 20-30% | High | $2,000-$3,000/month |
| 10-20% | Medium | $1,000-$2,000/month |
| 5-10% | Low | $500-$1,000/month |
| <5% | Healthy | <$500/month |

### Brand vs. Non-Brand Segmentation

Many accounts show great overall ROAS, but the majority comes from brand traffic — you're paying Google a tax on existing customers, not acquiring new ones. This analysis is critical for understanding true acquisition efficiency.

| Brand % of Conversions | Interpretation |
|------------------------|---------------|
| >80% | Over-dependent on brand. Account ROAS is misleading — non-brand performance is likely poor. Growth requires making non-brand work |
| 60-80% | Brand-heavy. Report non-brand CPA separately — this is the true acquisition cost |
| 40-60% | Healthy mix. Both channels contributing meaningfully |
| <40% | Non-brand dominant. Verify brand isn't being cannibalized by PMax or competitors |

Always report: "Overall CPA is $X, but brand CPA is $Y and non-brand CPA is $Z." If brand and non-brand aren't in separate campaigns, flag as a structural issue (→ Pass 3).

### Spend Concentration Analysis

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Top 20% keywords' share of conversions | >50% | 30-50% | <30% |
| Top 20% keywords' share of spend | <50% | 50-70% | >70% with low conversion share |
| Single keyword share of total spend | <15% | 15-30% | >30% (concentration risk) |
| Keywords spending >2x account CPA with 0 conversions | 0-2 | 3-5 | >5 |

---

## Pulse Metrics — What to Track

Instead of a composite score, the audit tracks 3 objective metrics:

| Metric | What it measures | Better = | Severity thresholds |
|--------|-----------------|----------|---------------------|
| **Waste rate** | % of spend on zero-conversion entities | Lower | >20% critical, 10-20% needs work, 5-10% OK, <5% healthy |
| **Demand captured** | Weighted avg IS on profitable campaigns | Higher | <30% critical, 30-50% needs work, 50-70% OK, >70% strong |
| **CPA** | Cost per conversion | Lower/stable | Compare to industry benchmarks below |

---

## Quick-Reference: Audit Workflow

```
START
|
LAYER 1: SIGNALS
|
1. Gate check: Is tracking working?
   +-- Hard stop? --> STOP. Fix tracking before anything else.
   +-- Flags? --> Note them, continue
|
LAYER 2: RELEVANCE
|
2. Pre-checks (location intent, search partners, display network) --> Pass 1
3. Campaign structure, keyword health, search terms, ad copy
   +-- Waste findings --> Pass 1 (stop the bleeding)
   +-- Structural fixes --> Pass 3 (fix fundamentals)
   +-- PMax running? --> Check cannibalization, asset completeness
   +-- Rank-lost IS > 30%? --> Pass 3, do NOT recommend more budget
|
LAYER 3: EFFICIENCY
|
4. Impression share interpretation + spend efficiency
   +-- Brand vs non-brand segmentation
   +-- Bid strategy fitness
   +-- Conversion value sanity check
|
LAYER 4: SCALE
|
5. Budget-constrained winners (budget-lost IS on profitable campaigns) --> Pass 2
   +-- Coverage gaps (geo, dayparting, device) --> Pass 2
   +-- High-CTR low-conversion ad groups --> Pass 2
|
LAYER 5: GROWTH
|
6. Incrementality + expansion opportunities --> Pass 2 / forward-looking
|
7. Compute pulse metrics (waste rate, demand captured, CPA)
8. Persist to audit-history.json
9. Generate 3-pass report (max 3 items per pass)
|
END
```

---

## Industry CPA Benchmarks

Reference benchmarks for evaluating spend efficiency:

| Industry | Avg CPA (Search) | Good CPA | Excellent CPA |
|----------|-----------------|----------|---------------|
| Legal | $85-$120 | <$70 | <$50 |
| Home Services | $40-$65 | <$35 | <$25 |
| Healthcare | $55-$85 | <$50 | <$35 |
| B2B / SaaS | $75-$120 | <$65 | <$45 |
| E-commerce | $30-$50 | <$25 | <$15 |
| Finance / Insurance | $70-$110 | <$60 | <$40 |
| Real Estate | $50-$80 | <$45 | <$30 |
| Education | $45-$75 | <$40 | <$25 |
| Travel | $35-$60 | <$30 | <$20 |
| Automotive | $40-$65 | <$35 | <$25 |

**Note**: These are directional benchmarks. Actual CPA varies by market, geography, competition, and offer. Use as a reference point, not an absolute target.
