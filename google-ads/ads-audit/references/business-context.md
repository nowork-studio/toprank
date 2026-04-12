# Business Context — Website Crawl & Data Collection

This reference covers the website crawl procedure and business context JSON schema used by the `/ads-audit` skill.

## Website Crawl

### Step 1: Resolve the website URL

Find the website URL from Phase 1 data, in priority order:
1. Ad final URLs from `listAds` — extract the root domain (e.g., `https://example.com`). Normalize to the apex domain (strip `www.` and subdomain prefixes) before frequency-counting across all ads. Use the most common domain.
2. If no URL found in ad data, ask the user: "What's your website URL?"

### Step 2: Crawl the website

Issue all `WebFetch` calls in a single tool-use turn so they run in parallel. If any individual fetch fails (404, timeout, blocked), skip that page and continue.

| Page | URL pattern | Why |
|------|-------------|-----|
| Homepage | `{root_url}` | Services overview, hero messaging, trust signals, brand voice |
| About page | `{root_url}/about` | Differentiators, history, team, social proof |
| Services page | `{root_url}/services` | Full service list, service descriptions |
| Top ad landing pages | Up to 3 unique final URLs from ads, **excluding any URL that matches the homepage, about, or services pages already being fetched** | What the ads actually link to — offers, CTAs, messaging |

**Fallback if `/about` or `/services` return 404:** Try one fallback each:
- About: try `/about-us` (most common variant)
- Services: try `/our-services` (most common variant)

If the fallback also 404s, move on — don't spider the site.

**Detecting unusable pages:** If a fetched page has fewer than 50 words of visible text (excluding HTML tags, scripts, and navigation), or if the primary content is a login/auth form (email/password fields, "Sign In" as the main heading), treat it as a failed fetch and skip it for extraction.

### Step 3: Extract business context from crawled pages

Scan the fetched page content for these signals. Merge with what you already inferred from account data — website data fills gaps, account data confirms what's active.

| Field | What to look for on the website |
|-------|-------------------------------|
| `services` | Service names from navigation, headings, service cards. **Merge** with services inferred from campaigns — the website may list services not yet advertised |
| `differentiators` | "Why choose us" sections, hero subheadings, unique value claims (e.g., "Family-owned since 1998", "Same-day service guaranteed") |
| `social_proof` | Review counts, star ratings, award badges, "As seen in" logos, certifications, years in business, number of customers served |
| `offers_or_promotions` | Banner offers, hero CTAs with discounts, seasonal promotions, "Free estimate" or "X% off" |
| `brand_voice` | Tone of headlines and body copy — professional vs casual, technical vs approachable. Capture 3-5 literal phrases from the site that exemplify the tone |
| `target_audience` | Who the site speaks to — homeowners vs businesses, specific industries, demographic cues |
| `locations` | Footer addresses, "Areas we serve" pages, location-specific content |
| `landing_pages` | Map each ad final URL to a summary of what's on that page (headline, primary CTA, offer if any) |
| `industry` | What the business clearly does — confirm or refine what campaign names suggest |
| `competitors` | Look for comparison tables or "vs" pages linked from the nav |

**Important:** Only extract from pages you actually retrieved with usable content. If the homepage is all you got, that's fine — it usually has the most signal. Extract in the site's original language — downstream skills handle translation when generating English ad copy.

**If all pages failed or returned no usable content**, skip website extraction entirely and proceed to the full question set (do not skip any questions).

## Business Context JSON Schema

Write the complete business context to `{data_dir}/business-context.json`:

```json
{
  "business_name": "",
  "industry": "",
  "website": "",
  "services": [],
  "locations": [],
  "target_audience": "",
  "brand_voice": {
    "tone": "",
    "words_to_avoid": [],
    "words_to_use": []
  },
  "differentiators": [],
  "competitors": [],
  "seasonality": {
    "peak_months": [],
    "slow_months": [],
    "seasonal_hooks": []
  },
  "keyword_landscape": {
    "high_intent_terms": [],
    "competitive_terms": [],
    "long_tail_opportunities": []
  },
  "social_proof": [],
  "offers_or_promotions": [],
  "landing_pages": {},
  "notes": "",
  "audit_date": "",
  "account_id": ""
}
```

Include `audit_date` (today's date) and `account_id` so future skills know when this was last refreshed.
