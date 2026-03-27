---
name: seo-analysis
description: >
  Comprehensive SEO audit and analysis skill for toprank. Use this skill whenever
  the user asks about SEO, search rankings, organic traffic, Google Search Console,
  keyword performance, why traffic dropped, which pages rank, content gaps, or
  wants to improve their site's visibility in search. Also trigger when the user
  mentions "why is my traffic down", "what keywords am I ranking for", "improve
  my rankings", "check my search console", "SEO audit", "analyze my SEO",
  "technical SEO", "meta tags", "indexing issues", "crawl errors", or any
  organic search question. If in doubt, trigger — this skill handles the full
  range from quick GSC checks to deep technical audits.
---

# SEO Analysis

A comprehensive SEO audit powered by Google Search Console data and technical
crawl analysis. Works whether you're inside a website repo or auditing any URL.

---

## Phase 1 — Confirm Access to Google Search Console

Before pulling data, confirm the user has GSC API access. Check silently:

```bash
gcloud auth application-default print-access-token 2>&1
```

**If this succeeds** (returns a token): proceed to Phase 2 — no setup needed.

**If this fails**: ask the user which situation applies:
- "I have gcloud installed but haven't set it up for GSC"
- "I don't have gcloud"
- "Skip GSC — just do a technical crawl audit of my URL"

Then guide accordingly — read `references/gsc_setup.md` for the full setup guide.

The most common case is gcloud already installed. In that case, run:
```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```
This opens a browser, the user logs in with the Google account that owns Search Console, and that's it. No service accounts, no JSON files.

---

## Phase 2 — Identify the Site

### If inside a website repo
Look for these signals to auto-detect the site URL:
- `package.json` → check `"homepage"` field or scripts for domain hints
- `next.config.js` or `next.config.ts` → look for `env.NEXT_PUBLIC_SITE_URL` or `basePath`
- `astro.config.*` → `site:` field
- `gatsby-config.js` → `siteMetadata.siteUrl`
- `.env` or `.env.local` → `NEXT_PUBLIC_SITE_URL`, `SITE_URL`, `PUBLIC_URL`
- `vercel.json` → deployment aliases

Read these files, extract the URL, confirm with the user: "I found your site at `https://example.com` — is that right?"

### If not in a website repo
Ask: "What's your website URL? (e.g. https://yoursite.com)"

### Match to GSC property
Once you have the URL, list the user's GSC properties and find the match:

```bash
python3 "$(dirname "$0")/scripts/list_gsc_sites.py"
```

GSC properties can be domain properties (`sc-domain:example.com`) or URL-prefix properties (`https://example.com/`). The script handles both. If multiple matches exist, ask the user to confirm which one to use.

---

## Phase 3 — Collect Data

Run the main analysis script with the confirmed site property:

```bash
python3 "$(dirname "$0")/scripts/analyze_gsc.py" \
  --site "sc-domain:example.com" \
  --days 90
```

This pulls:
- **Top queries** by impressions, clicks, CTR, average position
- **Top pages** by clicks + impressions
- **Position buckets** — queries in 1-3, 4-10, 11-20, 21+ (the "almost ranking" opportunities)
- **Queries losing clicks** — comparing last 28 days vs the prior 28 days
- **Pages losing traffic** — same comparison
- **Queries with high impressions but low CTR** — title/meta description optimization targets
- **Device split** — mobile vs desktop vs tablet performance

**If GSC is unavailable**, skip to Phase 4b (technical-only audit).

---

## Phase 4a — Search Console Analysis

With the data from Phase 3, analyze and surface insights:

### Traffic Overview
State: total clicks, impressions, average CTR, average position for the period. Note any dramatic changes.

### Quick Wins (highest impact, lowest effort)
1. **Position 4-10 queries** — these are ranking but not getting clicks. A title tag / meta description improvement could jump them to page 1. List top 10 with current position and impressions.
2. **High-impression, low-CTR queries** — queries where you're seen but not clicked. Often a title/snippet mismatch with search intent.
3. **Queries dropping MoM** — flag anything with >30% click decline. These need immediate investigation.

### Content Gaps
Look at queries where you rank 11-30 — you have topical authority but need a dedicated page or content expansion. Group related queries together.

### Pages to Fix
List pages with declining clicks. For each: current clicks, % change, likely cause (seasonal? algorithm update? new competitor?).

---

## Phase 4b — Technical SEO Audit

Crawl the site's key pages to check technical health. Use the firecrawl skill if available, otherwise use WebFetch.

Pages to audit: homepage, plus any pages flagged in Phase 4a.

For each page check:

**Indexability**
- Is `robots.txt` blocking important paths?
- Is there a `noindex` tag on important pages?
- Is there a canonical URL? Does it point to itself (good) or elsewhere (investigate)?

**Title & Meta**
- `<title>` present? Under 60 chars? Contains primary keyword?
- `<meta name="description">` present? 120-160 chars? Action-oriented?
- Is the title unique (not duplicated across pages)?

**Headings**
- Single `<h1>` per page? Contains primary keyword?
- Logical heading hierarchy (h1 → h2 → h3)?
- No keyword stuffing?

**Structured Data**
- JSON-LD or Schema.org markup present?
- For e-commerce: Product, Review, BreadcrumbList
- For local business: LocalBusiness, OpeningHours
- For blog: Article, BlogPosting

**Performance Signals**
- Check for render-blocking scripts in `<head>`
- Images: are they lazy-loaded? Do they have `alt` attributes?
- Is there a `<link rel="preload">` for critical resources?

**Links**
- Internal links present? Descriptive anchor text?
- Broken links (404s) on the page?

---

## Phase 5 — Report

Output a structured report. Always use this format:

---

# SEO Analysis Report — [site.com]
*Analyzed: [date range] | Data: Google Search Console + Technical Crawl*

## Executive Summary
[2-3 sentences on overall health and the single most important thing to fix]

## Traffic Snapshot
| Metric | Value | vs Prior Period |
|--------|-------|----------------|
| Total Clicks | X | ↑/↓ X% |
| Impressions | X | ↑/↓ X% |
| Avg CTR | X% | ↑/↓ |
| Avg Position | X | ↑/↓ |

## Quick Wins (Fix These First)
[Numbered list, most impactful first. Be specific: "Update title tag on /pricing from 'Pricing' to 'Pet Shipping Rates & Pricing — PawsVIP' — currently ranks #7 for 'pet shipping cost' with 2,400 monthly impressions but only 1.2% CTR"]

## Content Opportunities
[Queries you partially rank for that need dedicated pages or expanded content]

## Traffic Drops to Investigate
[Pages/queries with significant declines, with a hypothesis for each]

## Technical Issues
[Severity: Critical / High / Medium / Low]
[For each: what it is, which pages, how to fix it]

## 30-Day Action Plan
1. [Specific action — owner — expected impact]
2. ...

---

Keep recommendations specific and actionable. "Improve your meta descriptions" is useless. "Update the meta description on /products/cat-relocation to include 'door-to-door cat relocation service' and a call to action — it currently has 5,400 impressions but 0.8% CTR" is useful.
