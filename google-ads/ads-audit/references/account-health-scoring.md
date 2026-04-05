# Account Health Scoring Framework

Structured scoring methodology for Google Ads account audits. Seven health dimensions, each scored 0-5, with weighted rollup to a 0-100 overall score.

---

## Health Dimensions Overview

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|-----------------|
| 1 | Conversion Tracking | 20% | Tracking completeness and sophistication |
| 2 | Campaign Structure | 15% | Organization, segmentation, budget logic |
| 3 | Keyword Health | 20% | Quality scores, match types, zombie keywords |
| 4 | Search Term Quality | 15% | Query relevance, negative coverage, mining |
| 5 | Ad Copy | 10% | RSA quantity, variety, and performance |
| 6 | Impression Share | 10% | Budget and rank signal interpretation |
| 7 | Spend Efficiency | 10% | Wasted spend, CPA, concentration risk |

---

## Dimension 1: Conversion Tracking (Weight: 20%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | None | No conversion tracking installed |
| 1 | Basic | Tag fires but no values assigned; only 1 conversion action |
| 2 | Partial | Multiple conversion actions with values, but gaps: missing phone calls OR form submissions OR key pages |
| 3 | Solid | All key actions tracked (form, phone, purchase); values assigned; conversion window set correctly; Consent Mode v2 implemented (mandatory for EU since March 2024) |
| 4 | Advanced | Score 3 + enhanced conversions enabled; conversion linker tag present; GCLID auto-tagging on; Consent Mode v2 verified across all regions |
| 5 | Best-in-class | Score 4 + offline conversion import OR store visit tracking; server-side tagging implemented; data-driven attribution model |

### Conversion Tracking Red Flags

| Signal | Severity | What It Means |
|--------|----------|---------------|
| 0 conversions in 30 days with spend >5x account CPA | Critical | Tracking likely broken or missing |
| Conversion rate >50% | Critical | Tag firing on page load, not actual conversions |
| All conversions = "Website" (no action names) | High | Default tracking, no meaningful segmentation |
| "Include in conversions" set to YES for micro-conversions | Medium | Inflated conversion counts, misleading CPA |
| Last-click attribution on any campaigns | High | Deprecated since 2023 — data-driven attribution (DDA) is now the only model for new conversion actions. Migrate existing conversion actions to DDA immediately |

---

## Dimension 2: Campaign Structure (Weight: 15%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | Chaotic | 1 campaign, 1 ad group, 200+ keywords of mixed intent |
| 1 | Minimal | Multiple campaigns but no logical organization; ad groups have 50+ keywords spanning unrelated themes |
| 2 | Basic | Campaigns organized by service/product line; ad groups still too broad (30-50 keywords) |
| 3 | Good | Properly themed ad groups (10-20 keywords each); logical campaign splits by service/geo; match types considered |
| 4 | Strong | Score 3 + separate brand campaign; geo-targeted campaigns where relevant; budget allocated by priority |
| 5 | Excellent | Score 4 + funnel-stage separation (brand/non-brand/competitor/remarketing); proper budget allocation ratios; campaign experiments running |

### Structure Assessment Checklist

| Check | Passing Threshold | Failing Signal |
|-------|------------------|----------------|
| Keywords per ad group | 5-15 (broad match: 5-10; exact/phrase: 10-20) | >30 per ad group |
| Ad groups per campaign | 5-15 | >25 or just 1 |
| Brand vs. non-brand separation | Separate campaigns | Mixed in same campaign |
| Campaign naming convention | Consistent pattern | No pattern (e.g., "Campaign 1", "test") |
| Budget distribution | Proportional to priority | Equal across all campaigns regardless of performance |
| Location targeting | Set per campaign need | All campaigns target same broad area |

---

## Dimension 3: Keyword Health (Weight: 20%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | Failing | Average QS <4; >50% zombie keywords; no match type strategy |
| 1 | Poor | Average QS 4-5; 30-50% zombie keywords; broad match without Smart Bidding or negatives |
| 2 | Below Average | Average QS 5-6; 20-30% zombie keywords; broad match with Smart Bidding but insufficient negatives |
| 3 | Good | Average QS 6-7; <20% zombie keywords; intentional match type strategy; negatives in place |
| 4 | Strong | Average QS 7-8; <10% zombie keywords; intentional match type strategy aligned with Smart Bidding |
| 5 | Excellent | Average QS 8+; <5% zombie keywords; tightly themed ad groups aligned to Smart Bidding signals; comprehensive negative coverage |

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

## Dimension 4: Search Term Quality (Weight: 15%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | Unmonitored | Never reviewed; no negative keywords; broad match with no controls |
| 1 | Neglected | Reviewed once; <10 negative keywords; relevance <60% |
| 2 | Basic | Quarterly review; 10-30 negatives; relevance 60-75% |
| 3 | Managed | Monthly review; 30-100 negatives; relevance 75-85%; obvious irrelevants blocked |
| 4 | Active | Bi-weekly review; 100+ negatives organized in lists; relevance 85-90%; mining opportunities captured |
| 5 | Optimized | Weekly review; comprehensive negative lists by theme; relevance >90%; all converting terms added as exact keywords; shared negative lists across campaigns |

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

## Dimension 5: Ad Copy (Weight: 10%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | Missing | Ad groups with 0 or 1 active ad; no RSAs |
| 1 | Minimal | 1 RSA per ad group; only 3-5 headlines; ad strength "Poor" |
| 2 | Basic | 1 RSA per ad group; 6-8 headlines; ad strength "Average" |
| 3 | Good | 1-2 RSAs per ad group; 8-11 headlines from 3+ angles; ad strength "Good" |
| 4 | Strong | 2 RSAs per ad group for testing; 11-15 headlines; 5+ angles; ad strength "Good" to "Excellent" |
| 5 | Excellent | Score 4 + active A/B tests running; performance data-driven pinning; CTR above position-adjusted benchmark |

### Ad Copy Sub-Metrics

| Sub-Metric | Poor | Average | Good | Excellent |
|------------|------|---------|------|-----------| 
| RSAs per ad group | 0-1 | 1 | 2 | 2+ with experiment |
| Headlines per RSA | 3-5 | 6-8 | 9-11 | 12-15 |
| Distinct headline angles | 1-2 | 3 | 4-5 | 6+ |
| Ad strength distribution | >50% Poor | >50% Average | >50% Good | >50% Excellent |
| CTR vs. position benchmark | >30% below | 10-30% below | At benchmark | Above benchmark |
| Descriptions with CTA | 0% | 25-50% | 50-75% | 75%+ |

---

## Dimension 6: Impression Share (Weight: 10%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | Invisible | Search IS <20%; losing >80% of eligible impressions |
| 1 | Struggling | Search IS 20-40%; high losses on both budget and rank |
| 2 | Below Average | Search IS 40-60%; one major loss driver (budget OR rank) |
| 3 | Competitive | Search IS 60-75%; budget-lost IS <20% and rank-lost IS <30% |
| 4 | Strong | Search IS 75-90%; budget-lost IS <10% and rank-lost IS <15% |
| 5 | Dominant | Search IS >90%; minimal losses on both dimensions |

### Budget-Lost IS Interpretation

| Budget-Lost IS | Severity | Meaning |
|---------------|----------|---------|
| >30% | Severe | Budget exhausted early in day; missing 30%+ of qualified traffic |
| 20-30% | Moderate | Noticeable budget constraint; consider increase or narrowing |
| 10-20% | Acceptable | Minor constraint; may be intentional budget cap |
| <10% | Good | Budget is not a limiting factor |

### Rank-Lost IS Interpretation

| Rank-Lost IS | Severity | Meaning |
|-------------|----------|---------|
| >50% | Crisis | Ads rarely showing in competitive positions; QS or bid fundamentally broken |
| 30-50% | Needs Work | Consistently outranked; improve QS, bids, or ad relevance |
| 15-30% | Competitive | Normal competitive loss; optimize incrementally |
| <15% | Strong | Winning most eligible auctions |

### Impression Share 2x2 Interpretation Matrix

| | Rank-Lost IS LOW (<20%) | Rank-Lost IS HIGH (>20%) |
|---|------------------------|--------------------------|
| **Budget-Lost IS LOW (<15%)** | **Healthy** -- Optimizing at the margins. Focus on bid strategy and new keyword expansion. | **QS / Bid Problem** -- Ads not competitive. Improve ad relevance, landing pages, or increase bids. Check QS components. |
| **Budget-Lost IS HIGH (>15%)** | **Pure Budget Problem** -- Ads are competitive when shown. Increase budget, narrow geo targeting, or daypart to stretch budget. | **Structural Problem** -- Wrong keywords entirely. Audience too broad, poor campaign structure. Rebuild targeting from scratch. |

---

## Dimension 7: Spend Efficiency (Weight: 10%)

| Score | Level | Criteria |
|-------|-------|----------|
| 0 | Burning | >30% wasted spend; CPA >3x industry benchmark; no conversion data |
| 1 | Poor | 20-30% wasted spend; CPA 2-3x benchmark; top spenders not converting |
| 2 | Below Average | 15-20% wasted spend; CPA 1.5-2x benchmark |
| 3 | Average | 10-15% wasted spend; CPA within 1-1.5x benchmark; top 20% keywords drive 50%+ conversions |
| 4 | Good | 5-10% wasted spend; CPA at or below benchmark; strong conversion concentration |
| 5 | Excellent | <5% wasted spend; CPA well below benchmark; top 20% keywords drive 60%+ conversions; no keyword spending >2x account CPA with 0 conversions |

### Wasted Spend Calculation

```
Wasted Spend % = (Spend on keywords with 0 conversions AND >10 clicks) / Total Spend x 100
```

| Wasted Spend % | Severity | Monthly Waste at $10k Spend |
|---------------|----------|-----------------------------|
| >30% | Critical | >$3,000/month burned |
| 20-30% | High | $2,000-$3,000/month |
| 10-20% | Medium | $1,000-$2,000/month |
| 5-10% | Low | $500-$1,000/month |
| <5% | Healthy | <$500/month |

### Spend Concentration Analysis

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Top 20% keywords' share of conversions | >50% | 30-50% | <30% |
| Top 20% keywords' share of spend | <50% | 50-70% | >70% with low conversion share |
| Single keyword share of total spend | <15% | 15-30% | >30% (concentration risk) |
| Keywords spending >1x account CPA with 0 conversions | 0-2 | 3-5 | >5 |

---

## Overall Health Score Calculation

### Formula

```
Overall Score = (D1 x 0.20 + D2 x 0.15 + D3 x 0.20 + D4 x 0.15 + D5 x 0.10 + D6 x 0.10 + D7 x 0.10) / 5 x 100
```

Where D1-D7 are the dimension scores (0-5).

### Example Calculation

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Conversion Tracking | 3 | 0.20 | 0.60 |
| Campaign Structure | 2 | 0.15 | 0.30 |
| Keyword Health | 4 | 0.20 | 0.80 |
| Search Term Quality | 3 | 0.15 | 0.45 |
| Ad Copy | 2 | 0.10 | 0.20 |
| Impression Share | 3 | 0.10 | 0.30 |
| Spend Efficiency | 3 | 0.10 | 0.30 |
| **Total** | | | **2.95** |

Overall Score = 2.95 / 5 x 100 = **59 / 100** (Needs Work)

---

## Severity Classification

| Score Range | Classification | Typical Account Profile | Urgency |
|-------------|---------------|------------------------|---------|
| 0-30 | Critical | No tracking, chaotic structure, massive waste. Money is actively burning. | Fix this week. Every day costs money. |
| 31-50 | Needs Significant Work | Basic tracking but major structural gaps. Likely 30-50% of spend is wasted. | Fix within 2 weeks. Prioritize highest-waste areas. |
| 51-70 | Needs Work | Tracking works, structure is OK, but optimization gaps. Common for unmanaged or self-managed accounts. | Fix within 30 days. Methodical improvement plan. |
| 71-85 | Good | Well-managed account with room for optimization. Typical of accounts with active management. | Ongoing optimization. Quarterly deep reviews. |
| 86-100 | Strong | Well-optimized account. Marginal gains from here. | Maintain. Focus on scaling and expansion. |

---

## Priority Action Matrix

For each dimension scored below 3, the single highest-impact fix:

| Dimension | Score 0 Fix | Score 1 Fix | Score 2 Fix |
|-----------|------------|------------|------------|
| Conversion Tracking | Install Google Tag + at least 1 conversion action | Add conversion values; track all key actions (form, phone, purchase) | Fill coverage gaps; enable enhanced conversions |
| Campaign Structure | Split into service-based campaigns with 10-20 keyword ad groups | Reorganize ad groups by theme; separate brand from non-brand | Tighten ad groups to 10-20 keywords; add geo targeting |
| Keyword Health | Pause all QS <3 keywords; add negative keywords; reduce to 10-20 per ad group | Focus on QS 4-5 keywords: improve ad relevance and landing pages | Add exact match for top converters; pause zombie keywords |
| Search Term Quality | Run first-ever search term review; add 20+ obvious negatives | Build negative keyword lists by theme; block top wasters | Set up bi-weekly review cadence; mine converting terms |
| Ad Copy | Create RSA with 8+ headlines for every ad group | Add headlines to reach 8+; ensure 3+ distinct angles | Add second RSA for A/B testing; improve headline variety |
| Impression Share | Check if budget is depleting before noon; adjust bids down or narrow targeting | Identify top budget-loss campaign; increase budget or narrow geo/schedule | Improve QS on rank-lost keywords; test bid strategies |
| Spend Efficiency | Pause all keywords with spend >1x account CPA and 0 conversions immediately | Set max CPC caps; pause keywords with >20 clicks and 0 conversions | Reallocate budget from low-efficiency to high-efficiency keywords |

---

## Quick-Reference: Audit Workflow

```
START
|
1. Check Conversion Tracking (Dimension 1)
   +-- Score 0-1? --> STOP. Fix tracking before anything else.
   |                   No point optimizing what you cannot measure.
   +-- Score 2+? --> Continue
|
2. Assess Campaign Structure (Dimension 2)
   +-- Score 0-1? --> Restructure before optimizing keywords/ads.
   +-- Score 2+? --> Continue
|
3. Evaluate Keyword Health (Dimension 3) + Search Terms (Dimension 4)
   +-- Run in parallel. These inform each other.
|
4. Review Ad Copy (Dimension 5)
   +-- Only after keywords are stable. No point writing ads for bad keywords.
|
5. Analyze Impression Share (Dimension 6) + Spend Efficiency (Dimension 7)
   +-- These are outcome metrics. Fix inputs (1-5) before worrying about outputs.
|
6. Calculate Overall Score
7. Generate Priority Action Plan (top fix per dimension scoring <3)
|
END
```

---

## Industry CPA Benchmarks

Reference benchmarks for evaluating Dimension 7 (Spend Efficiency):

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
