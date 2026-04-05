# RSA Best Practices Reference

Expert knowledge for writing, testing, and optimizing Responsive Search Ads. Specific character limits, formula tables, pinning strategies, and performance benchmarks.

> **PMax cross-reference:** For accounts running Performance Max campaigns alongside Search, coordinate RSA messaging with PMax asset groups. PMax may serve text ads on Search inventory — ensure your RSA headlines and descriptions complement (not duplicate) PMax asset group text assets. See PMax documentation for asset group best practices.

---

## Character Limits

| Component | Max Characters | Notes |
|-----------|---------------|-------|
| Headline | 30 | Up to 15 headlines per RSA |
| Description | 90 | Up to 4 descriptions per RSA |
| Display Path 1 | 15 | Appears after domain in display URL |
| Display Path 2 | 15 | Second segment after slash |
| Final URL | 2048 | Landing page URL |
| Business Name | 25 | Shown in some ad formats |

### Minimum Asset Requirements

| Asset | Minimum Required | Recommended | Maximum |
|-------|-----------------|-------------|---------|
| Headlines | 3 | 11-15 | 15 |
| Descriptions | 2 | 3-4 | 4 |
| Unique headline angles | 3 | 5+ | -- |

---

## Headline Formula Table

### Service + Location Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 1 | Service in City | [Service] in [City] | Plumbing in Austin | 18 |
| 2 | City + Service | [City] [Service] Experts | Denver Roofing Experts | 22 |
| 3 | Near You | [Service] Near You | AC Repair Near You | 18 |
| 4 | Local + Service | Local [Service] in [City] | Local HVAC in Dallas | 20 |

### Value Proposition Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 5 | Differentiator | [Unique Benefit] [Service] | Same-Day Emergency Repair | 25 |
| 6 | Result Promise | Get [Result] [Timeframe] | Get More Leads in 30 Days | 26 |
| 7 | Save + Metric | Save [Amount] on [Service] | Save 40% on Insurance | 22 |
| 8 | Award/Rank | #1 Rated [Service] in [City] | #1 Rated Dentist in Miami | 25 |

### Trust Signal Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 9 | Years in Business | [N]+ Years of Experience | 25+ Years of Experience | 23 |
| 10 | Reviews | [N]-Star Rated on Google | 5-Star Rated on Google | 22 |
| 11 | Customers Served | [N]+ Satisfied Customers | 10,000+ Happy Customers | 24 |
| 12 | Licensed/Certified | Licensed & Insured [Trade] | Licensed & Insured HVAC | 24 |

### CTA Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 13 | Get + Offer | Get Your Free [Offer] | Get Your Free Estimate | 22 |
| 14 | Action + Today | [Action] Today | Book a Consultation Today | 26 |
| 15 | Call Now | Call Now for [Benefit] | Call Now for Free Quote | 22 |
| 16 | Start + Action | Start [Action] Today | Start Saving Today | 18 |

### Urgency / Scarcity Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 17 | Limited Time | Limited Time: [Offer] | Limited Time: 20% Off | 22 |
| 18 | Ending Soon | [Offer] Ends [Date] | Spring Sale Ends Friday | 23 |
| 19 | Spots Left | Only [N] Spots Left | Only 5 Spots Left | 18 |

### Price / Offer Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 20 | Starting At | [Service] From $[Price] | Websites From $499 | 18 |
| 21 | Discount | [N]% Off [Service] | 30% Off First Month | 20 |
| 22 | Free Offer | Free [Deliverable] | Free Roof Inspection | 20 |

### Question Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 23 | Need + Service? | Need [Service]? | Need a New Roof? | 16 |
| 24 | Looking for? | Looking for [Solution]? | Looking for Fast WiFi? | 22 |

### Benefit Headlines

| # | Formula | Template | Example | Chars |
|---|---------|----------|---------|-------|
| 25 | Adjective + Benefit | [Adjective] [Service] | Affordable Web Design | 21 |
| 26 | No + Pain Point | No [Pain Point] | No Hidden Fees Ever | 19 |
| 27 | Fast + Outcome | Fast [Outcome] Guaranteed | Fast Turnaround Guaranteed | 27 |

---

## Description Formula Table

| # | Category | Formula | Template | Example | Chars |
|---|----------|---------|----------|---------|-------|
| 1 | Core Benefit + Location | [Benefit] for [audience] in [City]. [CTA]. | Professional plumbing services for homes in Austin. Call today for a free estimate. | 82 |
| 2 | Differentiator + CTA | [What makes you different]. [Proof]. [CTA]. | Same-day service with no overtime charges. Serving 10,000+ homes. Book online now. | 85 |
| 3 | Trust + Social Proof | [Trust signal]. [Social proof]. [CTA]. | Licensed & insured since 1998. Rated 4.9/5 on Google. Schedule your free consultation. | 89 |
| 4 | Urgency + Offer | [Time limit]. [Offer details]. [CTA]. | Spring special ends March 31st. Save 25% on all AC installations. Call now to lock in rates. | 90 |
| 5 | Problem + Solution | [Pain point]? [Your solution]. [CTA]. | Tired of slow WiFi? We install enterprise-grade networks for homes. Get a free site survey. | 90 |
| 6 | Feature + Benefit | [Feature] so you [benefit]. [CTA]. | 24/7 emergency support so you never wait for help. Request service online in 60 seconds. | 88 |
| 7 | Comparison + Advantage | Unlike [alternative], we [advantage]. [CTA]. | Unlike big-box stores, we custom-build every cabinet. Visit our showroom or request a quote. | 90 |
| 8 | Risk Reversal + Guarantee | [Guarantee]. [Risk removal]. [CTA]. | 100% satisfaction guarantee or your money back. No contracts, cancel anytime. Start free today. | 90 |
| 9 | Credentials + Expertise | [Credential]. [Years/experience]. [CTA]. | Board-certified surgeons with 15,000+ procedures performed. Book your consultation today. | 88 |
| 10 | Process + Ease | [How it works in N steps]. [CTA]. | 3 simple steps: request a quote, approve the plan, we handle the rest. Get started in minutes. | 90 |

---

## Pinning Strategy Decision Tree

```
Should I pin this headline?
|
+-- Is it a legal/compliance requirement?
|   +-- YES --> Pin to Position 1 or 2 (mandatory)
|   +-- NO --> Continue
|
+-- Is it a brand name headline?
|   +-- YES --> Pin to Position 1 (brand consistency)
|   +-- NO --> Continue
|
+-- Is it a price/offer that MUST appear?
|   +-- YES --> Pin to Position 1 or 2
|   +-- NO --> Continue
|
+-- Does the ad group have a single clear intent?
|   +-- YES --> Leave unpinned (let Google optimize)
|   +-- NO --> Continue
|
+-- Do you have 50+ conversions/month at the campaign level?
|   +-- YES --> Leave unpinned (enough data for Google to optimize)
|   +-- NO --> Consider pinning your best 2-3 headlines to Positions 1-2
|
DEFAULT --> Leave unpinned. Google's ML needs freedom to test combinations.
```

### Pinning Impact on Ad Strength

| Pins Used | Impact on Ad Strength | Impact on Impressions |
|-----------|----------------------|----------------------|
| 0 pins | Neutral to positive | Maximum reach |
| 1-2 pins | Minor reduction | Minimal impact |
| 3-5 pins | Moderate reduction | Noticeable impression reduction (Google has not published exact figures) |
| 6+ pins | Significant reduction | Substantial impression reduction — diminishes RSA's optimization ability |
| All pinned | Severe; ad strength drops to "Poor" | Major impression reduction — effectively negates the RSA format's advantages |

### Pinning Rules

| Rule | Rationale |
|------|-----------|
| Never pin more than 2 headlines to the same position | Gives Google at least 2 options per slot |
| If you pin Position 1, provide 3+ headlines pinned there | Ensures variety even with pinning |
| Never pin all 15 headlines | Defeats the purpose of RSA entirely |
| Pin descriptions less often than headlines | Descriptions have less positional impact |

---

## Ad Strength Scoring

### What Google's Ad Strength Actually Measures

| Ad Strength | What It Means | What It Does NOT Mean |
|-------------|---------------|----------------------|
| Poor | Too few assets or too similar | Your ads will not convert |
| Average | Minimum diversity met | Adequate for conversions |
| Good | Solid headline/description variety | You are optimized |
| Excellent | Maximum asset diversity | Maximum conversion rate |

### Ad Strength vs. Performance Reality

| Scenario | Ad Strength | CTR | Conv. Rate | Verdict |
|----------|------------|-----|------------|---------|
| Highly targeted ad group, 5 specific headlines | Average | High | High | Keep it. Ad strength is wrong. |
| Broad ad group, 15 generic headlines | Excellent | Low | Low | Ad strength is misleading. Fix targeting. |
| Brand campaign, 3 pinned headlines | Poor | Very High | Very High | Ignore ad strength for brand. |

**When to ignore Ad Strength**: Brand campaigns, single-product ad groups with very specific intent, accounts with <50 conversions/month where Google's ML has insufficient data.

**When to respect Ad Strength**: Broad campaigns with mixed intent, new campaigns with no performance data, campaigns spending >$5k/month where impressions matter.

---

## CTR Benchmarks by Ad Position

| Ad Position | Avg CTR (Search) | Top Quartile CTR | Bottom Quartile CTR |
|-------------|-----------------|-------------------|---------------------|
| Position 1 (top) | 6-7% | 10-12% | 3-4% |
| Position 2 | 4-5% | 7-8% | 2-3% |
| Position 3 | 2-3% | 4-5% | 1-2% |
| Position 4+ (bottom of page) | 1-2% | 2-3% | <1% |

### CTR Benchmarks by Industry (Position 1)

| Industry | Avg CTR | Good CTR | Excellent CTR |
|----------|---------|----------|---------------|
| Legal | 4.4% | 6% | 8%+ |
| Home Services | 5.2% | 7% | 10%+ |
| Healthcare | 3.6% | 5% | 7%+ |
| B2B / SaaS | 3.2% | 5% | 7%+ |
| E-commerce | 2.8% | 4% | 6%+ |
| Finance / Insurance | 3.8% | 5.5% | 8%+ |
| Real Estate | 3.7% | 5% | 7%+ |
| Education | 4.1% | 6% | 8%+ |
| Travel | 4.7% | 6.5% | 9%+ |
| Automotive | 4.0% | 5.5% | 7%+ |

---

## A/B Testing Methodology

### Minimum Sample Requirements

| Metric | Minimum Threshold | Ideal Threshold |
|--------|------------------|-----------------|
| Clicks per variant | 200 | 500+ |
| Duration | 14 days | 30 days |
| Conversions per variant | 50 | 100+ |
| Impressions per variant | 1,000 | 5,000+ |

### When to Call a Winner Early

| Condition | Can Call Early? | Confidence |
|-----------|---------------|------------|
| 3x CTR difference, 50+ clicks each | Yes | High |
| 2x CTR difference, 100+ clicks each | Yes | High |
| Stat sig >99%, 75+ clicks each | Yes | High |
| <20% CTR difference, <200 clicks | No | Wait |
| Conv. rate difference <10%, <50 conversions | No | Wait |

### What to Test (Priority Order)

| Priority | Test Variable | Expected CTR Impact | Min. Test Duration |
|----------|--------------|--------------------|--------------------|
| 1 | Headline angle (benefit vs. feature) | 15-30% | 14 days |
| 2 | CTA phrasing (Get vs. Book vs. Call) | 10-20% | 14 days |
| 3 | Price/offer inclusion vs. exclusion | 10-25% | 14 days |
| 4 | Urgency language vs. none | 5-15% | 21 days |
| 5 | Question vs. statement headline | 5-15% | 21 days |
| 6 | Description CTA variation | 5-10% | 21 days |
| 7 | Display path text | 3-8% | 14 days |

### Interpreting Test Results

| Result | Interpretation | Action |
|--------|---------------|--------|
| CTR up, Conv. Rate up | Clear winner | Adopt immediately |
| CTR up, Conv. Rate flat | More clicks, same quality | Adopt if CPA is acceptable |
| CTR up, Conv. Rate down | Attracting wrong clicks | Revert; tighten targeting |
| CTR down, Conv. Rate up | Fewer but better clicks | Keep if total conversions increase |
| CTR flat, Conv. Rate flat | No meaningful difference | Test a bolder variation |

---

## Headline Variation Requirements

### Minimum Diversity Rules

| Rule | Minimum | Recommended |
|------|---------|-------------|
| Total unique headlines | 8 | 11-15 |
| Distinct angles/themes | 3 | 5+ |
| Headlines with CTA | 2 | 3 |
| Headlines with location | 1-2 | 2-3 (if local) |
| Headlines with numbers | 2 | 3-4 |
| Character length spread | 3 different lengths | Mix of 15-20, 21-25, 26-30 |

### Angle Distribution for 12-Headline RSA

| Angle | Count | Examples |
|-------|-------|---------|
| Service/Product | 2-3 | "Professional Roof Repair", "Complete Roofing Solutions" |
| Value Proposition | 2-3 | "Same-Day Service Available", "No Hidden Fees" |
| Trust/Proof | 2 | "25+ Years Experience", "4.9-Star Google Rating" |
| CTA | 2 | "Get a Free Quote Today", "Book Online in Minutes" |
| Offer/Price | 1-2 | "Spring Sale: 20% Off", "Free Inspection Included" |
| Location | 1-2 | "Serving All of Austin", "Dallas Roofing Experts" |

---

## Common RSA Mistakes

| Mistake | Why It Hurts | Fix |
|---------|-------------|-----|
| Too many similar headlines | Google shows redundant combinations; wastes ad slots | Write from 5+ distinct angles |
| All headlines same length | Looks repetitive; Google prefers mixing short + long | Vary between 15-30 chars |
| No CTA headlines | Misses click intent when Google picks non-CTA combination | Include 2-3 CTA headlines |
| Pinning everything | Substantially reduces Google's optimization ability | Pin only what is legally or brand-required |
| Ignoring ad strength entirely | Missing easy wins from insufficient asset diversity | Aim for "Good" minimum unless justified |
| Only 3 headlines provided | Minimum assets = minimum reach and no testing | Always provide 8+ headlines |
| Duplicate keywords in headlines | Wastes headline slots repeating same keyword | Each headline should add new info |
| No description CTA | Descriptions without CTA have 10-15% lower CTR | End every description with an action verb |
| Display paths left empty | Wastes free keyword real estate in ad | Always fill both display path segments |
| Same ad copy across all ad groups | Ignores intent differences between ad groups | Tailor headlines to each ad group's keyword theme |
| Testing too many variables at once | Cannot isolate what caused improvement | Change one angle per test cycle |
| Not reviewing Search Terms Report | Ad copy may not match actual queries | Check STR monthly; adapt headlines to real queries |
