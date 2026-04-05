# Bid Strategy Decision Tree

Systematic framework for selecting, migrating between, and troubleshooting Google Ads bidding strategies. Every recommendation includes transition criteria based on campaign learning status and performance signals.

> **Why automated bidding is strongly preferred (2026):** Google's bidding engine is powered by an LLM-based auction system that evaluates hundreds of real-time signals per auction — device type, precise location, time of day, audience segments, query intent, competitive density, browser, OS, and more. No human bidder can access or process these signals. Manual bidding means forfeiting this advantage entirely, which is why Google's automated strategies consistently outperform manual approaches across virtually all verticals and account sizes. The recommendations below reflect this reality.

> **⚠️ eCPC Deprecation Notice:** Google deprecated Enhanced CPC (eCPC) for new Search campaigns in 2024. Existing campaigns using eCPC may still run, but Google no longer recommends it, and it cannot be selected for new campaigns. All references to eCPC below are for legacy migration purposes only. Do not adopt eCPC for any new campaign.

---

## Master Decision Tree

```
START: What is your optimization goal?
|
+-- Goal: Maximize conversions within a budget
|   |
|   +-- Campaign has exited Learning status AND stable CPA (< 20% variance)
|   |   --> Target CPA (tCPA)
|   |
|   +-- Campaign still in Learning or recently launched
|   |   --> Maximize Conversions (budget-capped) — transition to tCPA once Learning exits
|   |
|   +-- Very low volume / new campaign with no conversion history
|       --> Maximize Conversions (budget-capped) — let the algorithm gather data
|
+-- Goal: Maximize conversion value / ROAS
|   |
|   +-- Conversion value tracking in place AND campaign exited Learning with sufficient volume
|   |   --> Target ROAS (tROAS)
|   |
|   +-- Conversion value tracking in place AND still building volume
|   |   --> Maximize Conversion Value — transition to tROAS once Learning exits
|   |
|   +-- No conversion value tracking
|       --> Set up value tracking first, use tCPA in the meantime
|
+-- Goal: Drive traffic / brand awareness
|   |
|   +-- Brand campaign (own brand terms)
|   |   --> Target Impression Share (target: 95%+ top of page)
|   |
|   +-- New market / awareness play
|   |   --> Maximize Clicks (with max CPC cap)
|   |
|   +-- Competitor conquesting
|       --> Target Impression Share (with max CPC cap) or Maximize Conversions (budget-capped)
|
+-- Goal: Testing / new campaign launch
    |
    +-- Existing conversion data from other campaigns in the account
    |   --> Maximize Conversions for 2-4 weeks, then transition to tCPA
    |       (or tCPA directly if account has strong conversion history)
    |
    +-- No conversion history at all
        --> Maximize Conversions (budget-capped) for first 30 days to establish baselines
```

---

## Strategy-by-Strategy Reference

### Maximize Conversions

| Attribute | Detail |
|-----------|--------|
| **When to use** | New campaigns, budget-constrained campaigns, campaigns with some conversion history; when the goal is "spend this budget, get as many conversions as possible" |
| **Prerequisites** | Conversion tracking active; defined daily budget you are willing to fully spend |
| **Typical use case** | Campaign launch with $50-200/day budget; seasonal pushes; clearing remaining budget at end of month; replacing Manual CPC for new campaigns |
| **Pros** | Simple setup; spends full budget; good for learning what CPA is achievable; accesses Google's full real-time auction signals from day one |
| **Cons** | No CPA control — will spend entire budget regardless of CPA; can overspend early in the day; may pursue low-quality conversions |
| **Key setting** | Set daily budget carefully — the system WILL spend it all. Optionally set a max CPA bid limit |
| **Learning period** | 1-2 weeks. Do not judge results until 2 full weeks of data |
| **Exit criteria** | Campaign exits Learning status and CPA stabilizes --> move to tCPA |

### Maximize Clicks

| Attribute | Detail |
|-----------|--------|
| **When to use** | Brand awareness campaigns; new market entry; traffic-focused goals; when you have no conversion tracking yet |
| **Prerequisites** | None — works with zero conversion data |
| **Typical use case** | Brand awareness, content promotion, filling top of funnel, market research |
| **Pros** | Maximizes traffic within budget; no conversion tracking needed |
| **Cons** | No conversion optimization; attracts clicks regardless of quality; can burn budget on low-intent queries |
| **Key setting** | ALWAYS set a max CPC bid cap (start at 50% of your target CPC); without it, Google may pay $15+ per click |
| **Exit criteria** | Once conversion tracking is active and sufficient conversions accumulated --> switch to Maximize Conversions (budget-capped) |

### Target CPA (tCPA)

| Attribute | Detail |
|-----------|--------|
| **When to use** | Campaign has exited Learning status; stable CPA over recent weeks; known target CPA |
| **Prerequisites** | Conversion tracking active; campaign exited Learning status; CPA variance < 20% week-over-week |
| **Typical use case** | Mature lead gen, SaaS trials, service bookings, e-commerce with uniform AOV |
| **Pros** | Fully automated bidding optimized for conversions at your target cost; learns from auction signals you cannot access |
| **Cons** | Needs learning period (1-2 weeks); aggressive targets = zero spend; requires sufficient conversion volume |
| **Key settings** | Set target CPA at or slightly above (10-15%) your current average CPA to start |
| **Common pitfalls** | Setting tCPA 30%+ below current average --> campaign stops spending. Setting tCPA too high --> overspending on low-quality conversions |

**tCPA Setup Checklist:**
- [ ] Campaign has exited Learning status (do NOT transition while still in Learning)
- [ ] Set initial tCPA = current average CPA (do NOT set aspirational target)
- [ ] Reduce tCPA by no more than 10-15% per 2-week period
- [ ] Do not make changes during the 1-2 week learning period
- [ ] Ensure daily budget is at least 10x your tCPA target

### Target ROAS (tROAS)

| Attribute | Detail |
|-----------|--------|
| **When to use** | E-commerce with variable order values; sufficient conversion volume with value tracking; known ROAS target |
| **Prerequisites** | Conversion value tracking (revenue per conversion); campaign exited Learning status with stable ROAS; ROAS variance < 25% week-over-week |
| **Typical use case** | E-commerce, multi-product retailers, travel bookings, real estate leads with scored values |
| **Pros** | Optimizes for revenue/profit not just conversion count; smart for variable AOV businesses |
| **Cons** | Needs more data than tCPA; sensitive to conversion value accuracy; can ignore low-value but important conversions |
| **Key setting** | Set target ROAS at or slightly below (10%) your current average ROAS to start |
| **When tROAS beats tCPA** | When conversion values vary 3x+ between transactions (e.g., $50 order vs. $500 order); tCPA would treat these equally, tROAS will prioritize the $500 order |

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

### Enhanced CPC (eCPC) — DEPRECATED

> **⚠️ Legacy strategy.** eCPC was deprecated for new Search campaigns in 2024. It remains available only on existing campaigns that already use it. Do not adopt eCPC for new campaigns. Migrate existing eCPC campaigns to Maximize Conversions or Target CPA.

| Attribute | Detail |
|-----------|--------|
| **When to use** | Legacy only — existing campaigns that have not yet migrated |
| **Prerequisites** | N/A — do not adopt for new campaigns |
| **Typical use case** | Migration candidate: move to Maximize Conversions (budget-capped) or tCPA |
| **Pros** | Slightly more automation than Manual CPC while respecting base bid |
| **Cons** | Deprecated; limited optimization ceiling; Google can raise bids beyond your manual bid; far less effective than tCPA or Maximize Conversions |
| **Key setting** | N/A — focus on migration planning |
| **Exit criteria** | Migrate to Maximize Conversions (budget-capped) or directly to tCPA if conversion volume supports it |

### Manual CPC — NOT RECOMMENDED

> **⚠️ Not recommended for any new campaign.** Manual CPC forfeits access to Google's real-time LLM-based auction signals. Use Maximize Clicks (with CPC cap) for traffic goals or Maximize Conversions (budget-capped) for conversion goals instead.

| Attribute | Detail |
|-----------|--------|
| **When to use** | Extremely rare edge cases only — e.g., regulatory environments requiring fixed bids |
| **Prerequisites** | None — works with zero historical data |
| **Typical use case** | Not recommended for standard use |
| **Pros** | Full control over every keyword bid; no learning period; predictable spend |
| **Cons** | Cannot react to real-time auction signals; misses user-level optimization; time-intensive to manage; consistently underperforms automated strategies |
| **Key setting** | Set bids at keyword level; use ad schedule and device bid adjustments |
| **Exit criteria** | Migrate immediately to Maximize Conversions (budget-capped) or Maximize Clicks (with CPC cap) |

---

## Migration Paths

### Standard Migration Ladder

| Step | From | To | Transition Criteria | Timeline |
|------|------|----|---------------------|----------|
| 1 | New campaign | Maximize Conversions (budget-capped) | Conversion tracking active, budget set | Day 1 |
| 2 | Maximize Conversions | Target CPA | Campaign exits Learning status, CPA stabilizes (< 20% variance) | After 2-4+ weeks |
| 3 | Target CPA | Target ROAS | Sufficient conversion volume + value tracking active, conversion values vary 3x+ | When value optimization matters |
| Alt | New campaign (account has conversion history) | Target CPA | Account has strong conversion data from other campaigns | Day 1 (direct) |
| Legacy | eCPC (deprecated) | Maximize Conversions or tCPA | Any time — eCPC should be migrated off | Immediately |

### Migration Safety Rules

| Rule | Why |
|------|-----|
| Allow direct tCPA adoption if the account has conversion history from other campaigns | Google's algorithm can leverage cross-campaign data; rigid step-skipping rules are outdated |
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
| eCPC (legacy) | Still running on campaigns that should migrate | Underperformance vs. automated strategies | Migrate to Maximize Conversions or tCPA |
| Manual CPC (legacy) | Still in use, missing real-time signals | Losing impression share, CPA higher than automated competitors | Migrate to Maximize Conversions (budget-capped) or Maximize Clicks (with CPC cap) |
| Target IS | No max CPC cap on competitive terms | CPC spirals to 3-5x normal | Set max CPC cap; accept lower IS on expensive terms |

---

## Portfolio vs. Standard Bid Strategies

| Attribute | Standard (Campaign-level) | Portfolio (Shared across campaigns) |
|-----------|--------------------------|-------------------------------------|
| **Scope** | One campaign | Multiple campaigns share one strategy |
| **When to use** | Campaign has sufficient conversion volume on its own to exit Learning | Individual campaigns lack volume but combined total is enough to exit Learning |
| **Data pooling** | Campaign data only | Pools conversion data across all campaigns in the portfolio |
| **Budget** | Per-campaign budget | Per-campaign budgets still; strategy optimizes across them |
| **Best for** | High-volume campaigns | Low-volume campaigns that share a common goal (same CPA target, same ROAS target) |
| **Avoid when** | N/A | Campaigns have very different CPAs/ROAS targets; different business goals; different conversion types |
| **Example** | Single e-commerce campaign doing 100 conversions/month on tROAS | 5 service-area campaigns each doing 10 conversions/month, combined into a tCPA portfolio at $50 |

### Portfolio Strategy Decision Rule

```
IF single campaign has sufficient volume to exit Learning on its own
  --> Use standard (campaign-level) strategy

IF single campaign cannot exit Learning on its own
  AND multiple campaigns share the same conversion goal
  AND combined volume across those campaigns is sufficient to exit Learning
  --> Use portfolio strategy

IF total volume across all candidates is too low to exit Learning even when pooled
  --> Use Maximize Conversions (budget-capped) across campaigns until volume builds
```

---

## Bid Strategy Performance Evaluation

### What to Measure (By Strategy)

| Strategy | Primary Metric | Secondary Metric | Evaluation Window |
|----------|---------------|-----------------|-------------------|
| Maximize Conversions | CPA trend | Total conversions, budget utilization | Weekly |
| Maximize Clicks | CPC trend, traffic volume | Click quality (bounce rate, time on site) | Weekly |
| tCPA | Actual CPA vs. target CPA | Conversion volume, search impression share | 2-week rolling average |
| tROAS | Actual ROAS vs. target ROAS | Revenue, conversion value | 2-week rolling average |
| Target IS | Actual IS vs. target IS | CPC trend, budget utilization | Weekly |
| eCPC (legacy) | CPA vs. pre-eCPC baseline | Conversion volume change | Bi-weekly (migrate off) |
| Manual CPC (legacy) | CPA or ROAS | Top impression rate, impression share | Weekly (migrate off) |

### When to Intervene

| Signal | Threshold | Action |
|--------|-----------|--------|
| CPA > target by 20%+ for 2+ weeks | Sustained overshoot past learning period | Raise tCPA target by 10%; check for conversion tracking issues |
| Conversion volume drops > 30% | Algorithm may be too constrained | Raise target CPA/lower target ROAS; check for budget limits |
| "Learning" status persists > 3 weeks | Not enough conversion data | Broaden targeting; increase budget; consider less aggressive strategy |
| "Learning limited" status | Budget or targeting too restrictive | Increase budget to 10x+ tCPA; expand audience/keywords |
| CPA < target by 30%+ | Potential to scale | Decrease tCPA by 10% to improve volume; or increase budget |
| Impression share < 50% on brand terms | Competitors bidding on your brand | Switch brand campaign to Target IS at 95% |
