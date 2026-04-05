# Bid Strategy Decision Tree

Systematic framework for selecting, migrating between, and troubleshooting Google Ads bidding strategies. Every recommendation includes data thresholds and concrete transition criteria.

---

## Master Decision Tree

```
START: What is your optimization goal?
|
+-- Goal: Maximize conversions within a budget
|   |
|   +-- Conversion volume >= 50/month AND stable CPA (< 20% variance)
|   |   --> Target CPA (tCPA)
|   |
|   +-- Conversion volume 30-49/month
|   |   --> Maximize Conversions (budget-capped) — transition to tCPA once 50+/mo
|   |
|   +-- Conversion volume 15-29/month
|   |   --> Enhanced CPC (eCPC) — build conversion history
|   |
|   +-- Conversion volume < 15/month
|       --> Manual CPC — gather data before automating
|
+-- Goal: Maximize conversion value / ROAS
|   |
|   +-- Conversion value tracking in place AND 50+ conv/month
|   |   --> Target ROAS (tROAS)
|   |
|   +-- Conversion value tracking in place AND 30-49 conv/month
|   |   --> Maximize Conversion Value — transition to tROAS once 50+/mo
|   |
|   +-- No conversion value tracking
|       --> Set up value tracking first, use tCPA in the meantime
|
+-- Goal: Drive traffic / brand awareness
|   |
|   +-- Brand campaign (own brand terms)
|   |   --> Manual CPC or Target Impression Share (target: 95%+ top of page)
|   |
|   +-- New market / awareness play
|   |   --> Maximize Clicks (with max CPC cap)
|   |
|   +-- Competitor conquesting
|       --> Manual CPC (tight control on spend) or Target Impression Share
|
+-- Goal: Testing / new campaign launch
    |
    +-- Existing conversion data from other campaigns
    |   --> Maximize Conversions for 2-4 weeks, then transition
    |
    +-- No conversion history at all
        --> Manual CPC for first 30 days to establish baselines
```

---

## Strategy-by-Strategy Reference

### Manual CPC

| Attribute | Detail |
|-----------|--------|
| **When to use** | New campaigns, < 15 conversions/month, testing keyword viability, competitor campaigns needing tight spend control |
| **Prerequisites** | None — works with zero historical data |
| **Typical use case** | Campaign launch, niche B2B with low volume, brand defense |
| **Pros** | Full control over every keyword bid; no learning period; predictable spend |
| **Cons** | Time-intensive to manage; cannot react to real-time auction signals; misses user-level optimization |
| **Key setting** | Set bids at keyword level; use ad schedule and device bid adjustments |
| **Exit criteria** | 15+ conversions/month accumulated over 30 days --> move to eCPC |

### Enhanced CPC (eCPC)

| Attribute | Detail |
|-----------|--------|
| **When to use** | 15-29 conversions/month; transitioning from Manual CPC; want some automation with guardrails |
| **Prerequisites** | Conversion tracking active; 15+ conversions in last 30 days |
| **Typical use case** | Mid-volume lead gen, local services, building toward full automation |
| **Pros** | Adjusts bids up/down based on conversion likelihood while respecting your base bid; lower risk than full automation |
| **Cons** | Limited optimization ceiling; Google can raise bids beyond your manual bid; less effective than tCPA at scale |
| **Key setting** | Set a manual base bid; Google adjusts up or down at auction time |
| **Exit criteria** | 30+ conversions/month sustained for 60 days --> move to tCPA |

### Target CPA (tCPA)

| Attribute | Detail |
|-----------|--------|
| **When to use** | 30+ conversions/month (Google recommendation: 50+ for best results); stable CPA over 60 days; known target CPA |
| **Prerequisites** | Conversion tracking active; 30+ conversions in last 30 days; CPA variance < 20% week-over-week |
| **Typical use case** | Mature lead gen, SaaS trials, service bookings, e-commerce with uniform AOV |
| **Pros** | Fully automated bidding optimized for conversions at your target cost; learns from auction signals you cannot access |
| **Cons** | Needs learning period (1-2 weeks); aggressive targets = zero spend; requires sufficient conversion volume |
| **Key settings** | Set target CPA at or slightly above (10-15%) your current average CPA to start |
| **Common pitfalls** | Setting tCPA 30%+ below current average --> campaign stops spending. Setting tCPA too high --> overspending on low-quality conversions |

**tCPA Setup Checklist:**
- [ ] Minimum 30 conversions in last 30 days
- [ ] Set initial tCPA = current average CPA (do NOT set aspirational target)
- [ ] Reduce tCPA by no more than 10-15% per 2-week period
- [ ] Do not make changes during the 1-2 week learning period
- [ ] Ensure daily budget is at least 10x your tCPA target

### Target ROAS (tROAS)

| Attribute | Detail |
|-----------|--------|
| **When to use** | E-commerce with variable order values; 50+ conversions/month with value tracking; known ROAS target |
| **Prerequisites** | Conversion value tracking (revenue per conversion); 50+ conversions in last 30 days; ROAS variance < 25% week-over-week |
| **Typical use case** | E-commerce, multi-product retailers, travel bookings, real estate leads with scored values |
| **Pros** | Optimizes for revenue/profit not just conversion count; smart for variable AOV businesses |
| **Cons** | Needs more data than tCPA; sensitive to conversion value accuracy; can ignore low-value but important conversions |
| **Key setting** | Set target ROAS at or slightly below (10%) your current average ROAS to start |
| **When tROAS beats tCPA** | When conversion values vary 3x+ between transactions (e.g., $50 order vs. $500 order); tCPA would treat these equally, tROAS will prioritize the $500 order |

### Maximize Conversions

| Attribute | Detail |
|-----------|--------|
| **When to use** | Budget-constrained campaigns; new campaigns with some conversion history; when the goal is "spend this budget, get as many conversions as possible" |
| **Prerequisites** | Conversion tracking active; defined daily budget you are willing to fully spend |
| **Typical use case** | Campaign launch with $50-200/day budget; seasonal pushes; clearing remaining budget at end of month |
| **Pros** | Simple setup; spends full budget; good for learning what CPA is achievable |
| **Cons** | No CPA control — will spend entire budget regardless of CPA; can overspend early in the day; may pursue low-quality conversions |
| **Key setting** | Set daily budget carefully — the system WILL spend it all. Optionally set a max CPA bid limit |
| **Learning period** | 1-2 weeks. Do not judge results until 2 full weeks of data |

### Maximize Clicks

| Attribute | Detail |
|-----------|--------|
| **When to use** | Brand awareness campaigns; new market entry; traffic-focused goals; when you have no conversion tracking yet |
| **Prerequisites** | None — works with zero conversion data |
| **Typical use case** | Brand awareness, content promotion, filling top of funnel, market research |
| **Pros** | Maximizes traffic within budget; no conversion tracking needed |
| **Cons** | No conversion optimization; attracts clicks regardless of quality; can burn budget on low-intent queries |
| **Key setting** | ALWAYS set a max CPC bid cap (start at 50% of your target CPC); without it, Google may pay $15+ per click |
| **Exit criteria** | Once conversion tracking is active and 15+ conversions accumulated --> switch to Manual CPC or eCPC |

### Target Impression Share

| Attribute | Detail |
|-----------|--------|
| **When to use** | Brand campaigns (target 95%+ IS); competitive positioning; when visibility matters more than CPA |
| **Prerequisites** | None, but works best with known competitive landscape |
| **Typical use case** | Brand defense, competitor conquesting, product launches |
| **Placement options** | Anywhere on page / Top of page / Absolute top of page |
| **Pros** | Guarantees visibility; protects brand terms from competitors |
| **Cons** | Expensive if targeting high IS on competitive terms; no conversion optimization |
| **Key setting** | Set max CPC cap to prevent runaway costs; target IS: 95% for brand, 50-70% for competitive |

---

## Migration Paths

### Standard Migration Ladder

| Step | From | To | Minimum Data Threshold | Timeline |
|------|------|----|----------------------|----------|
| 1 | Manual CPC | Enhanced CPC | 15+ conversions in 30 days | After 30-60 days of data |
| 2 | Enhanced CPC | Target CPA | 30+ conversions in 30 days, CPA variance < 20% | After 60 days on eCPC |
| 3 | Target CPA | Target ROAS | 50+ conversions in 30 days + value tracking active | When conversion values vary 3x+ |
| Alt | Manual CPC | Maximize Conversions | Conversion tracking active, fixed budget | When budget is set and you want to skip eCPC |
| Alt | Maximize Conversions | Target CPA | 30+ conversions in 30 days from Max Conv data | After 2-4 weeks of Max Conv data |

### Migration Safety Rules

| Rule | Why |
|------|-----|
| Never skip more than one step in the ladder (e.g., Manual --> tROAS) | Insufficient data leads to erratic bidding and wasted spend |
| Never change bid strategy AND campaign settings simultaneously | Impossible to diagnose what caused performance change |
| Allow 2 full weeks after any strategy change before evaluating | Learning period needs time; early data is unreliable |
| Never change bid strategy during seasonal peaks (Black Friday, etc.) | Algorithm relearns during your highest-value period |
| Set initial automated targets at or above current performance | Aggressive targets cause campaigns to stop serving |
| Keep daily budget >= 10x target CPA when using tCPA | Insufficient budget constrains the algorithm and hurts performance |

---

## Common Pitfalls by Strategy

| Strategy | Pitfall | Symptom | Fix |
|----------|---------|---------|-----|
| tCPA | Target set 30%+ below current CPA | Spend drops to near zero; few impressions | Raise tCPA to current average CPA, then decrease 10% per 2 weeks |
| tCPA | Daily budget < 5x tCPA target | Inconsistent daily spend; algorithm cannot optimize | Increase budget to 10-15x tCPA target |
| tROAS | Inaccurate conversion values | ROAS looks great but revenue doesn't match | Audit conversion tracking; verify values match actual revenue |
| tROAS | Target set 50%+ above current ROAS | Zero spend, similar to tCPA with too-low target | Set tROAS at 90% of current average, increase 10% per 2 weeks |
| Max Conversions | No budget cap awareness | Entire monthly budget spent in first week | Set daily budget = monthly budget / 30; monitor daily spend |
| Max Conversions | Low-quality conversions | High conversion count but poor lead quality | Add a max CPA bid limit; consider switching to tCPA |
| Max Clicks | No max CPC cap set | Single clicks costing $10-20+ | Always set max CPC cap at 50-75% of target CPC |
| eCPC | Ad groups with mixed intent keywords | Google overbids on irrelevant close variants | Tighten ad groups; add negative keywords |
| Manual CPC | Bids not updated in 30+ days | Missing auction changes, losing impression share | Review bids weekly or switch to automated strategy |
| Target IS | No max CPC cap on competitive terms | CPC spirals to 3-5x normal | Set max CPC cap; accept lower IS on expensive terms |

---

## Portfolio vs. Standard Bid Strategies

| Attribute | Standard (Campaign-level) | Portfolio (Shared across campaigns) |
|-----------|--------------------------|-------------------------------------|
| **Scope** | One campaign | Multiple campaigns share one strategy |
| **When to use** | Campaign has 50+ conversions/month alone | Individual campaigns have < 30 conversions/month but combined total is 50+ |
| **Data pooling** | Campaign data only | Pools conversion data across all campaigns in the portfolio |
| **Budget** | Per-campaign budget | Per-campaign budgets still; strategy optimizes across them |
| **Best for** | High-volume campaigns | Low-volume campaigns that share a common goal (same CPA target, same ROAS target) |
| **Avoid when** | N/A | Campaigns have very different CPAs/ROAS targets; different business goals; different conversion types |
| **Example** | Single e-commerce campaign doing 100 conversions/month on tROAS | 5 service-area campaigns each doing 10 conversions/month, combined into a tCPA portfolio at $50 |

### Portfolio Strategy Decision Rule

```
IF single campaign conversions >= 50/month
  --> Use standard (campaign-level) strategy

IF single campaign conversions < 30/month
  AND multiple campaigns share the same conversion goal
  AND combined conversions across those campaigns >= 50/month
  --> Use portfolio strategy

IF total conversions across all candidates < 30/month
  --> Use Manual CPC or eCPC until volume builds
```

---

## Bid Strategy Performance Evaluation

### What to Measure (By Strategy)

| Strategy | Primary Metric | Secondary Metric | Evaluation Window |
|----------|---------------|-----------------|-------------------|
| Manual CPC | CPA or ROAS | Impression share, avg. position | Weekly |
| eCPC | CPA vs. pre-eCPC baseline | Conversion volume change | Bi-weekly |
| tCPA | Actual CPA vs. target CPA | Conversion volume, search IS | 2-week rolling average |
| tROAS | Actual ROAS vs. target ROAS | Revenue, conversion value | 2-week rolling average |
| Max Conversions | CPA trend | Total conversions, budget utilization | Weekly |
| Max Clicks | CPC trend, traffic volume | Click quality (bounce rate, time on site) | Weekly |
| Target IS | Actual IS vs. target IS | CPC trend, budget utilization | Weekly |

### When to Intervene

| Signal | Threshold | Action |
|--------|-----------|--------|
| CPA > target by 20%+ for 2+ weeks | Sustained overshoot past learning period | Raise tCPA target by 10%; check for conversion tracking issues |
| Conversion volume drops > 30% | Algorithm may be too constrained | Raise target CPA/lower target ROAS; check for budget limits |
| "Learning" status persists > 3 weeks | Not enough conversion data | Broaden targeting; increase budget; consider less aggressive strategy |
| "Learning limited" status | Budget or targeting too restrictive | Increase budget to 10x+ tCPA; expand audience/keywords |
| CPA < target by 30%+ | Potential to scale | Decrease tCPA by 10% to improve volume; or increase budget |
| Impression share < 50% on brand terms | Competitors bidding on your brand | Switch brand campaign to Target IS at 95% |
