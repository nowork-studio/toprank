# Landing Page Measurement Rubric

Five dimensions, each measured against real evidence. The dimension scores are observations (real PageSpeed Insights numbers, word-for-word ad-to-page comparison, form field counts) — not artificial ratings.

There is no letter grade. The report surfaces each dimension's measurement and the top finding, plus a dollar-denominated lift estimate. Internally, the skill computes a weighted composite only to feed the lift formula:

```
internal_composite = 0.25 × Message Match
                   + 0.25 × Page Speed
                   + 0.20 × Mobile Experience
                   + 0.15 × Trust Signals
                   + 0.15 × Form & CTA
```

The two 25% dimensions (Message Match, Page Speed) are deliberately weighted equally — Google's Landing Page Experience QS component considers both, and real-world CVR correlates strongly with both. Everything else is secondary. The 0-100 scores per dimension are kept as internal numbers for history tracking and the lift formula; the user-facing report cites the underlying measurement (LCP seconds, field count, H1 word match) rather than the score.

---

## 1. Message Match (25%)

*"Did the user arrive where they expected?"*

The ad promises something. The page must deliver it within 3 seconds of scroll-free viewing. This is the single strongest predictor of CVR lift.

### Scoring

| Score | Rubric |
|-------|--------|
| 90-100 | Page H1 contains the ad's promise word-for-word or a tight synonym. Subhead reinforces. CTA matches the ad's action verb. Offer in ad (if any) is front-and-center on the page |
| 75-89 | H1 clearly relates to the ad's service and location. Primary CTA matches ad intent. Minor drift in tone or offer language |
| 60-74 | Page is on-topic but generic — H1 says "Quality Roofing Services" when the ad said "Emergency Roof Repair in Tukwila". User has to infer the connection |
| 45-59 | Page is about the business but not about the ad's specific angle. Ad pushed urgency, page is evergreen. Ad pushed a specific service, page is a services overview |
| <45 | Homepage, category page, or completely mismatched content. Ad said "free quote", page has no quote CTA. Ad said "24/7", page shows business hours |

### Evidence to capture

- **Ad headline 1** (the one most users see) vs. **Page H1** — quote both verbatim in the report
- **Ad CTA verb** (Get, Book, Call, Shop) vs. **Primary page button text**
- **Offer in ad** (if any) vs. **offer visible above the fold**
- **Location from ad** (if geo-targeted) vs. **location shown on page**
- **Keyword from search query** (pull top search term for the ad group) — does it appear on the page at all?

### Common failure patterns

| Pattern | Fix |
|---------|-----|
| Ad points to homepage | Build a service-specific landing page or change final URL |
| Ad headline promises a discount, page has no mention | Either remove the discount from ad or add it to page hero |
| Ad pushes one service, page lists 15 | Send traffic to a single-service page |
| Ad says "free estimate", page says "call for pricing" | Align the CTA or expand the pricing page |

---

## 2. Page Speed (25%)

*"Can the user even see the page before bouncing?"*

Measured via PageSpeed Insights API on mobile (Google's default crawl profile for ads since 2019). Desktop is secondary.

### Scoring (based on mobile Core Web Vitals)

| Score | LCP | INP | CLS | Notes |
|-------|-----|-----|-----|-------|
| 90-100 | <2.0s | <100ms | <0.05 | All three in green. Page feels instant |
| 75-89 | 2.0-2.5s | 100-200ms | 0.05-0.10 | Mostly green, one metric in yellow |
| 60-74 | 2.5-4.0s | 200-500ms | 0.10-0.25 | All yellow, or one metric in red |
| 45-59 | 4.0-6.0s | 500-1000ms | 0.25-0.40 | Two metrics in red |
| <45 | >6.0s | >1000ms | >0.40 | All three red. User bounced before LCP fired |

If PSI returns a performance score directly, use that as a tiebreaker within the band the vitals place you in.

### Evidence to capture

- LCP (s), INP (ms), CLS (unitless), Performance Score (0-100) — all from mobile strategy
- Top 3 `lighthouseResult.audits` with `score < 0.5` and `details.overallSavingsMs > 200` — these are the biggest levers
- Total page weight (kB), number of blocking scripts, number of image requests

### Common failure patterns

| Audit | Typical fix |
|-------|------------|
| `uses-optimized-images` | Serve WebP/AVIF, compress hero image |
| `render-blocking-resources` | Defer or async third-party scripts (analytics, chat widgets, tag managers) |
| `unused-javascript` | Remove marketing tags that aren't being read (Facebook Pixel on a B2B page, etc.) |
| `largest-contentful-paint-element` points to a hero image | Preload the hero image, set explicit dimensions to prevent CLS |
| `uses-long-cache-ttl` | Configure CDN cache headers |

---

## 3. Mobile Experience (20%)

*"Does the page work with a thumb?"*

70%+ of Google Ads traffic is mobile. A page that renders but is unusable on a 375px viewport is worse than a slow page — users rage-quit.

### Scoring

| Score | Rubric |
|-------|--------|
| 90-100 | Tap targets >48px. Text >=16px body. Sticky CTA or phone number in mobile viewport. Form fits without horizontal scroll. No popups that cover content. PSI accessibility >95 |
| 75-89 | Tap targets adequate, text readable. One minor issue (e.g., hero text partially cropped, footer form below fold) |
| 60-74 | 2+ mobile issues: small tap targets, zoomed-out default viewport, form requires zoom to complete, CTA below fold |
| 45-59 | Unusable without pinch-zoom. Content overflows. Multiple popups. PSI accessibility <75 |
| <45 | Desktop-only site. No mobile viewport meta. Broken rendering |

### Evidence to capture

- `viewport` meta tag present and correct (`width=device-width, initial-scale=1`)
- PSI mobile accessibility score
- Visible above-the-fold content on mobile (from WebFetch rendered markup)
- Presence of click-to-call link (`tel:` anchor) — critical for service businesses
- Presence of sticky mobile CTA
- Popup/interstitial detection — any element with `position: fixed` and `z-index > 1000` covering content

### Common failure patterns

| Pattern | Fix |
|---------|-----|
| Phone number not click-to-call | Wrap in `<a href="tel:...">` |
| No sticky mobile CTA | Add bottom-fixed button bar with primary action |
| Hero image dominates viewport, pushes headline below fold | Reduce hero size, move headline up |
| Popup appears on load | Delay to 30s scroll or remove entirely on paid-traffic pages |

---

## 4. Trust Signals (15%)

*"Would a stranger give this page their credit card or phone number?"*

Trust is the invisible conversion tax. Even a perfect ad-to-page match with blazing speed will lose conversions if the page feels sketchy.

### Scoring

| Score | Rubric |
|-------|--------|
| 90-100 | All of: real reviews/testimonials with names, star rating visible, trust badges (BBB, industry certs), years in business, physical address, phone number, photos of real people/work |
| 75-89 | Most of the above. One category missing (e.g., no certs but strong reviews) |
| 60-74 | Generic trust signals only: stock-photo testimonials, no names, no specifics |
| 45-59 | No reviews, no address, no photos. Just marketing copy |
| <45 | Active distrust signals: broken links, copyright year 3 years old, typos, contact form only (no phone) |

### Evidence to capture

- Review count and star rating (visible on page)
- Named testimonials (first name + last initial minimum)
- Physical address
- Phone number (ideally click-to-call)
- HTTPS + valid certificate
- Copyright year — must be current or last year
- Privacy policy link (critical for lead-gen compliance)

### Common failure patterns

| Pattern | Fix |
|---------|-----|
| No reviews on page | Pull from `business-context.json.social_proof` and add a reviews section |
| Copyright 2023 in 2026 | Update footer — tiny fix, surprisingly high impact on trust perception |
| No phone number on a service page | Add one, use click-to-call |
| Stock photos of "our team" | Replace with real photos, even phone-quality beats stock |

---

## 5. Form & CTA (15%)

*"Can the user actually convert?"*

The page can be perfect, but if the form has 11 fields or the button says "Submit", conversions leak out here.

### Scoring

| Score | Rubric |
|-------|--------|
| 90-100 | Primary CTA above fold, action-oriented ("Get My Free Quote", not "Submit"). Form has 3-4 fields max for lead gen. Clear value prop next to form ("We'll respond within 24h"). No dark patterns |
| 75-89 | CTA visible, form reasonable (5-6 fields), button copy active. One friction point |
| 60-74 | CTA below fold OR form has 7-8 fields OR button is generic ("Submit", "Send") |
| 45-59 | Multiple friction: 9+ field form, generic CTA, no value prop near form, unclear what happens after submit |
| <45 | No clear CTA, form broken, or form requires login/account creation before conversion |

### Evidence to capture

- Number of form fields (required vs. optional)
- Button text verbatim
- Above-fold CTA presence (from WebFetch'd markup, estimate using viewport-sized window)
- Secondary CTAs that might compete with the primary (too many CTAs = analysis paralysis)
- Trust reinforcement next to form (privacy note, response time, guarantee)

### Common failure patterns

| Pattern | Fix |
|---------|-----|
| Form has 10 fields for a "free estimate" | Reduce to name, phone, service type — everything else can wait for the follow-up call |
| Button says "Submit" or "Send" | Change to the action ("Get My Free Quote", "Book My Consultation") |
| Primary CTA below fold | Move above fold or add a sticky header CTA |
| Phone number hidden in footer | Put it in the header AND next to the form |

---

## Calibration notes

- **Don't over-weight speed for non-e-commerce.** A lead-gen page with LCP 3.5s and message-match 95 will convert better than LCP 1.5s with message-match 60. The weighted formula handles this correctly — don't override it.
- **Mobile accessibility floors the grade.** If PSI mobile accessibility < 60, cap Mobile Experience at 59 regardless of other factors. Broken accessibility is a trust/legal issue.
- **Don't trust average CVR as a benchmark without context.** A legal services page at 2% CVR is healthy; an e-commerce page at 2% CVR is broken. Use `industry-templates.json` → `typical_cvr` as the baseline.
- **Confidence decays with missing data.** If PSI didn't run, cap the final score at 85 (can't grade A without speed data). If `business-context.json` is missing, cap Message Match at 80 (can't validate brand voice).
