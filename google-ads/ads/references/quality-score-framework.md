# Quality Score Diagnostics & Optimization Playbook

Systematic framework for diagnosing, prioritizing, and improving Quality Score across Google Ads accounts. Every recommendation includes concrete thresholds and specific actions.

---

## Quality Score Component Breakdown

Quality Score (QS) is a 1-10 keyword-level metric composed of three sub-components, each rated independently:

| Component | Weight (approx.) | Rating Scale | What Google Evaluates |
|-----------|------------------|--------------|----------------------|
| **Expected CTR** | ~39% | Below Average / Average / Above Average | Historical CTR of the keyword normalized for ad position, extensions, and format |
| **Ad Relevance** | ~22% | Below Average / Average / Above Average | How closely your ad copy matches the intent and language of the keyword |
| **Landing Page Experience** | ~39% | Below Average / Average / Above Average | Page load speed, mobile-friendliness, content relevance, navigation clarity, trust signals |

**Key insight**: Landing Page Experience and Expected CTR together account for ~78% of QS. Ad Relevance is the smallest factor but often the easiest to fix.

---

## QS Impact on Cost-Per-Click

Quality Score directly modifies your actual CPC through the Ad Rank formula. Below are the approximate CPC modifiers relative to QS 5 (the neutral baseline):

| Quality Score | CPC Modifier vs. QS 5 Baseline | Effective CPC at $2.00 Benchmark | Impact on Budget |
|--------------|-------------------------------|----------------------------------|-----------------|
| 10 | -50% discount | $1.00 | Budget stretches 2x |
| 9 | -44% discount | $1.12 | Significant savings |
| 8 | -37% discount | $1.26 | Strong savings |
| 7 | -28% discount | $1.44 | Moderate savings |
| 6 | -17% discount | $1.66 | Slight savings |
| **5** | **Baseline (0%)** | **$2.00** | **No modifier** |
| 4 | +25% premium | $2.50 | Noticeable waste |
| 3 | +67% premium | $3.34 | Severe waste |
| 2 | +150% premium | $5.00 | Critical — pause or fix |
| 1 | +400% premium | $10.00 | Bleeding budget — immediate action |

**Rule of thumb**: Every 1-point QS increase above 5 saves ~16% on CPC. Every 1-point decrease below 5 costs ~50% more on CPC.

---

## Diagnostic Decision Tree

```
START: Keyword Quality Score
|
+-- QS >= 7
|   Action: Monitor. Maintain current performance. Look for QS 10 opportunities.
|
+-- QS 5-6
|   Action: Identify the Below Average component and fix it.
|   |
|   +-- Expected CTR = Below Average
|   |   Go to: Expected CTR Improvement Playbook (below)
|   |
|   +-- Ad Relevance = Below Average
|   |   Go to: Ad Relevance Improvement Playbook (below)
|   |
|   +-- Landing Page Experience = Below Average
|   |   Go to: Landing Page Improvement Playbook (below)
|   |
|   +-- All components = Average
|       Action: Test new ad copy with stronger CTAs and more specific headlines.
|       Target: Move one component from Average to Above Average.
|
+-- QS 3-4
|   Action: Urgent fix. Likely 2+ components Below Average.
|   Priority: Fix Landing Page Experience first (highest weight),
|   then Expected CTR, then Ad Relevance.
|
+-- QS 1-2
    Action: Critical. Consider pausing the keyword.
    Check: Is this keyword even relevant to your business?
    If yes: Rebuild — new ad group, new ad copy, new landing page.
    If no: Pause immediately. You are paying 2-5x market rate.
```

---

## Expected CTR Improvement Playbook

Expected CTR is position-adjusted, meaning Google accounts for your average position. A "Below Average" rating means your ads get fewer clicks than competitors in similar positions.

### Position-Adjusted CTR Benchmarks (Search Network)

| Average Position | Expected CTR Floor (Below Average threshold) | Good CTR | Excellent CTR |
|-----------------|---------------------------------------------|----------|---------------|
| 1.0 - 1.5 | < 4.0% | 5.0-8.0% | > 8.0% |
| 1.5 - 2.5 | < 2.5% | 3.5-6.0% | > 6.0% |
| 2.5 - 3.5 | < 1.5% | 2.5-4.5% | > 4.5% |
| 3.5+ | < 1.0% | 1.5-3.0% | > 3.0% |

### Fix Actions (Priority Order)

| # | Action | Expected Impact | Effort |
|---|--------|----------------|--------|
| 1 | Add the keyword (or close variant) to Headline 1 or 2 | +15-30% CTR | Low |
| 2 | Add sitelink extensions (minimum 4) | +10-20% CTR | Low |
| 3 | Add callout extensions with specific benefits | +5-10% CTR | Low |
| 4 | Add structured snippet extensions | +3-8% CTR | Low |
| 5 | Include a number in the headline (price, percentage, count) | +10-20% CTR | Low |
| 6 | Add urgency or scarcity language ("Limited", "Today Only") | +5-15% CTR | Low |
| 7 | Test a question-format headline matching the search query | +5-12% CTR | Medium |
| 8 | Review search terms — if irrelevant terms are diluting CTR, add negatives | +10-40% CTR | Medium |
| 9 | Break the ad group into tighter themes (fewer keywords, more specific ads) | +15-25% CTR | High |

### Historical CTR Analysis Checklist

- [ ] Pull 90-day CTR trend — is it declining, stable, or improving?
- [ ] Compare CTR across match types — broad match often drags down CTR via irrelevant queries
- [ ] Check device-level CTR — mobile CTR is typically 15-25% lower than desktop
- [ ] Review auction insights — new competitors entering can suppress CTR
- [ ] Check if ad extensions are showing — extension eligible rate < 50% means lost CTR opportunity

---

## Ad Relevance Improvement Playbook

Ad Relevance measures how well your ad copy matches the keyword's intent and language.

### Keyword-to-Headline Alignment Rules

| Scenario | Problem | Fix |
|----------|---------|-----|
| Keyword not in any headline | Google sees weak topical match | Add keyword or close synonym to Headline 1 or 2 |
| Keyword in headline but different intent | Ad promises something the keyword doesn't seek | Rewrite headline to match the search intent (informational, commercial, transactional) |
| Ad group has 30+ keywords | Impossible for 1 ad to be relevant to all keywords | Split into ad groups of 10-20 tightly themed keywords |
| Generic ad copy across all ad groups | Same ads everywhere = low relevance for specific terms | Write unique RSAs per ad group with keyword-specific headlines |
| Using only broad match keywords | Google matches queries far from original keyword | Review search terms; add phrase/exact match for high-value terms |

### Dynamic Keyword Insertion (DKI) Guidelines

| Use DKI When | Avoid DKI When |
|-------------|---------------|
| Ad group has 5-15 closely related keywords | Keywords are long (> 25 chars) — will truncate |
| Keywords are grammatically clean in headline context | Keywords contain competitor brand names |
| You want to quickly test relevance improvement | Keywords have mixed intent within the ad group |
| Landing page is genuinely relevant to all keyword variants | Industry requires careful language (medical, legal, financial) |

**DKI syntax**: `{KeyWord:Default Headline Text}` — capitalizes each word. Use `{keyword:default}` for sentence case.

### Close Variant Handling

Google matches exact and phrase match keywords to close variants including:
- Misspellings, singular/plural, stemming
- Abbreviations, acronyms
- Implied words, paraphrases, same-intent queries

**Impact on Ad Relevance**: If Google matches your keyword "running shoes" to the query "jogging sneakers," your ad copy must also cover that intent. Write headlines and descriptions that address the broader intent, not just the literal keyword.

---

## Landing Page Experience Improvement Playbook

### Landing Page Checklist by Industry

| Factor | Target (All Industries) | E-commerce Specific | Lead Gen / Services | SaaS / B2B |
|--------|------------------------|--------------------|--------------------|------------|
| **Page Load (LCP)** | < 2.5 seconds | < 2.0 seconds (product images) | < 2.0 seconds | < 1.5 seconds |
| **Mobile Responsive** | 100% functional on mobile | Tap targets > 48px, cart accessible | Form auto-fills, click-to-call | Demo CTA visible without scroll |
| **Content Relevance** | Headline mirrors ad headline | Product matches keyword exactly | Service matches keyword exactly | Feature/benefit matches keyword |
| **Trust Signals** | HTTPS required, privacy policy visible | Reviews, ratings, security badges | Testimonials, certifications, BBB | Logos, case studies, SOC2 badge |
| **Navigation** | Clear path to conversion | Breadcrumbs, related products | Simple form (< 5 fields) | Clear pricing, FAQ section |
| **Interstitials** | No intrusive popups on mobile | Exit-intent only, delayed 30s+ | No popup before form completion | Gated content OK if value clear |
| **Above-the-fold CTA** | Primary CTA visible without scroll | "Add to Cart" or "Buy Now" | "Get Quote" or "Call Now" | "Start Free Trial" or "Book Demo" |
| **Unique Content** | Original, substantial content on page | Unique product descriptions (not mfr copy) | Unique service descriptions | Feature explanations, not just bullets |

### Page Speed Quick Wins

| Fix | Typical LCP Improvement | Effort |
|-----|------------------------|--------|
| Compress images to WebP/AVIF | -0.5 to -2.0 seconds | Low |
| Lazy-load below-fold images | -0.3 to -1.0 seconds | Low |
| Remove unused CSS/JS | -0.2 to -0.5 seconds | Medium |
| Add CDN for static assets | -0.3 to -1.5 seconds | Medium |
| Server-side render above-fold content | -0.5 to -2.0 seconds | High |
| Upgrade hosting (shared → dedicated/cloud) | -0.5 to -3.0 seconds | High |

### Landing Page Relevance Scoring

Score your landing page 1-5 on each factor. Total < 15 = immediate rebuild needed.

| Factor | Score 1 (Poor) | Score 3 (Acceptable) | Score 5 (Excellent) |
|--------|---------------|---------------------|-------------------|
| **Headline Match** | No relation to ad/keyword | Contains keyword in subhead | Exact keyword/intent in H1 |
| **Content Depth** | Thin page (< 200 words) | Adequate content (300-500 words) | Comprehensive (500+ words, structured) |
| **CTA Clarity** | No clear next step | CTA exists but buried | Above-fold CTA with clear value prop |
| **Trust Elements** | No trust signals | Basic (HTTPS only) | Reviews + certifications + guarantees |
| **Mobile UX** | Broken on mobile | Functional but clunky | Fast, thumb-friendly, optimized forms |

---

## QS Optimization Priority Matrix

When you have limited time, prioritize fixes by impact and effort:

| Priority | Component | Condition | Action | Expected QS Impact |
|----------|-----------|-----------|--------|-------------------|
| P0 | Landing Page | LCP > 4 seconds | Fix page speed immediately | +1 to +3 QS points |
| P0 | Ad Relevance | Keyword not in any headline | Add keyword to Headline 1 | +1 to +2 QS points |
| P1 | Expected CTR | CTR < position-adjusted floor | Rewrite headlines, add extensions | +1 to +2 QS points |
| P1 | Landing Page | No HTTPS or broken mobile layout | Fix technical issues | +1 to +2 QS points |
| P2 | Ad Relevance | Ad group has 30+ keywords | Split into tighter ad groups | +1 to +2 QS points |
| P2 | Expected CTR | Broad match diluting CTR | Add negative keywords from search terms | +1 QS point |
| P3 | Landing Page | Generic trust signals | Add reviews, certifications, guarantees | +0.5 to +1 QS point |
| P3 | Expected CTR | Ad extensions not showing | Enable all relevant extension types | +0.5 to +1 QS point |

---

## QS Monitoring Cadence

| Frequency | Action | Tool |
|-----------|--------|------|
| Weekly | Review keywords with QS < 5 (sorted by spend) | Keyword report, QS column |
| Bi-weekly | Check component-level ratings for top 50 keywords by spend | Keyword report with QS sub-columns |
| Monthly | Audit landing page speeds for all active landing pages | Google PageSpeed Insights or Lighthouse |
| Monthly | Review search term report for irrelevant queries diluting CTR | Search terms report |
| Quarterly | Full QS distribution analysis (% of keywords at each QS level) | Custom report or script |

### QS Distribution Health Benchmarks

| QS Range | Healthy Account | Needs Work | Critical |
|----------|----------------|------------|----------|
| QS 8-10 | > 30% of keywords | 15-30% | < 15% |
| QS 5-7 | 50-60% of keywords | 40-50% | < 40% |
| QS 1-4 | < 10% of keywords | 10-25% | > 25% |

**Target**: A well-managed account should have 30%+ of keywords (by impression volume) at QS 7+, and fewer than 10% at QS 4 or below.
