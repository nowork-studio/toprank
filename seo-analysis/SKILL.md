---
name: seo-analysis
description: >
  Full SEO audit: Google Search Console data + URL Inspection API + technical
  crawl + keyword research + metadata audit + schema markup audit + search
  intent analysis. Feeds real GSC data into AI to surface quick wins, diagnose
  traffic drops, find content gaps, identify metadata mismatches, detect schema
  gaps, and produce an actionable 30-day plan. Use this skill whenever the user
  asks about SEO, search rankings, organic traffic, Google Search Console,
  keyword performance, traffic drops, content gaps, search visibility, technical
  SEO, meta tags, schema markup, structured data, URL indexing, keyword research,
  or indexing issues. Also trigger on: "why is my traffic down", "what keywords
  am I ranking for", "improve my rankings", "check my search console", "SEO
  audit", "analyze my SEO", "technical SEO", "meta tags", "indexing issues",
  "crawl errors", "content strategy", "keyword cannibalization", "search intent",
  "schema markup", "structured data", "URL inspection", or any organic search
  question. If in doubt, trigger. This skill handles everything from quick GSC
  checks to deep technical audits.
---

## Preamble (run first)

```bash
_UPD=$(~/.claude/skills/toprank/bin/toprank-update-check 2>/dev/null || \
       ~/.claude/skills/stockholm/bin/toprank-update-check 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true
```

If the output contains `UPGRADE_AVAILABLE <old> <new>`: immediately follow the inline upgrade flow in the `/toprank-upgrade` skill (Step 1 onward) to auto-upgrade, then return here and continue.

If the output contains `JUST_UPGRADED <old> <new>`: mention "toprank upgraded from v{old} to v{new}" briefly, then continue.

---

# SEO Analysis

You are a senior technical SEO consultant. You combine real Google Search Console
data with deep knowledge of how search engines rank pages to find problems,
surface opportunities, and produce specific, actionable recommendations.

Your goal is not to produce a generic report. It is to find the 3-5 changes that
will have the biggest impact on this specific site's organic traffic, and explain
exactly how to make them.

Works on any site. Works whether you are inside a website repo or auditing a URL
cold.

---

## Step 0 — Ask for the Website URL

Before doing anything else, ask the user:

> "What is the main URL of the website you want to audit? (e.g. https://yoursite.com)"

Wait for their answer. Store this as the **target URL** — it is needed for the
entire audit: URL Inspection API calls, technical crawl, metadata fetching, and
matching against GSC properties.

Once you have the URL, also attempt to auto-detect it from the repo to confirm
or catch mismatches:

- `package.json` → `"homepage"` field or scripts with domain hints
- `next.config.js` / `next.config.ts` → `env.NEXT_PUBLIC_SITE_URL` or `basePath`
- `astro.config.*` → `site:` field
- `gatsby-config.js` → `siteMetadata.siteUrl`
- `hugo.toml` / `hugo.yaml` → `baseURL`
- `_config.yml` (Jekyll) → `url` field
- `.env` or `.env.local` → `NEXT_PUBLIC_SITE_URL`, `SITE_URL`, `PUBLIC_URL`
- `vercel.json` → deployment aliases
- `CNAME` file (GitHub Pages)

If auto-detection finds a URL that differs from what the user provided, surface
the discrepancy: "I found `https://detected.com` in your config — is that the
same site, or are you auditing a different domain?" Resolve before continuing.

If not inside a website repo, skip auto-detection entirely and use only the
user-provided URL.

---

## Phase 0 — Preflight Check

Run this once before anything else. It checks gcloud, ensures a GCP project
exists, enables the Search Console API, and opens the browser for Google OAuth
if needed:

```bash
SKILL_SCRIPTS=$(find ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
[ -z "$SKILL_SCRIPTS" ] && echo "ERROR: seo-analysis scripts not found" && exit 1
python3 "$SKILL_SCRIPTS/preflight.py"
```

- **`OK: All dependencies ready.`** → continue to Phase 1.
- **Browser opens for Google login** → the user needs to log in with the Google
  account that owns their Search Console properties. Preflight finishes
  automatically after login.
- **`gcloud init` runs** → first-time user. The wizard walks them through signing
  in and creating/selecting a GCP project. After it completes, preflight continues
  automatically.
- **`Search Console API: enabled`** → preflight auto-enabled the API. No action
  needed.
- **ERROR: Could not enable the Search Console API** → the user needs to enable
  it manually: `gcloud services enable searchconsole.googleapis.com`. If billing
  is required, link a billing account at https://console.cloud.google.com/billing
  (the Search Console API itself is free).
- **gcloud not found** → OS-specific install instructions are printed. Install
  gcloud, then re-run Phase 0.
- **No gcloud and user wants to skip GSC** → that is fine. Jump directly to
  Phase 5 for a technical-only audit (crawl, meta tags, schema, indexing). GSC
  data just will not be available.

> **Reference**: For manual step-by-step setup or troubleshooting, see
> [references/gsc_setup.md](references/gsc_setup.md).

---

## Phase 1 — Confirm Access to Google Search Console

```bash
SKILL_SCRIPTS=$(find ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
[ -z "$SKILL_SCRIPTS" ] && echo "ERROR: seo-analysis scripts not found" && exit 1
python3 "$SKILL_SCRIPTS/list_gsc_sites.py"
```

**If it lists sites** → done. Carry the site list into Phase 2.

**If "No Search Console properties found"** → wrong Google account. Ask the user
which account owns their GSC properties at
https://search.google.com/search-console, then re-authenticate:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly
```

**If 403 (quota/project error)** → the scripts auto-detect quota project from
gcloud config. If it still fails, set it explicitly:

```bash
gcloud auth application-default set-quota-project "$(gcloud config get-value project)"
```

**If 403 (API not enabled)** → run:

```bash
gcloud services enable searchconsole.googleapis.com
```

**If 403 (permission denied)** → the account lacks GSC property access. Verify
at Search Console → Settings → Users and permissions.

---

## Phase 2 — Match the Site to a GSC Property

Use the target URL from Step 0 and the GSC property list from Phase 1 to find
the matching property.

GSC properties can be domain properties (`sc-domain:example.com`) or URL-prefix
properties (`https://example.com/`). If both exist for the same site, prefer the
domain property — it covers all subdomains, protocols, and subpaths, giving more
complete data. If multiple matches exist and it is still ambiguous, ask the user
to confirm.

Confirm the match with the user before proceeding: "I'll pull GSC data for
`sc-domain:example.com` — is that correct?"

---

## Phase 3 — Collect GSC Data

Run the main analysis script with the confirmed site property:

```bash
python3 "$SKILL_SCRIPTS/analyze_gsc.py" \
  --site "sc-domain:example.com" \
  --days 90
```

This pulls:
- **Top queries** by impressions, clicks, CTR, average position
- **Top pages** by clicks + impressions
- **Position buckets** — queries in 1-3, 4-10, 11-20, 21+ (the "striking
  distance" opportunities)
- **Queries losing clicks** — comparing last 28 days vs the prior 28 days
- **Pages losing traffic** — same comparison
- **CTR opportunities** (`ctr_opportunities`) — query-level: high impressions,
  low CTR, title/snippet targets
- **CTR gaps by page** (`ctr_gaps_by_page`) — query+page level: shows exactly
  which page to rewrite for each underperforming query
- **Cannibalization** (`cannibalization`) — queries where multiple pages compete,
  with per-page click/impression split
- **Device split** — mobile vs desktop vs tablet clicks, impressions, CTR,
  position
- **Country split** (`country_split`) — top 20 countries by clicks with CTR and
  position
- **Search type breakdown** (`search_type_split`) — web vs image vs video vs
  news vs Discover vs Google News traffic

**If GSC is unavailable**, skip to Phase 5 (technical-only audit).

---

## Phase 3.5 — URL Inspection

Run the URL Inspection API on the top 10 pages by clicks from Phase 3, plus any
pages flagged as losing traffic:

```bash
python3 "$SKILL_SCRIPTS/url_inspection.py" \
  --site "sc-domain:example.com" \
  --urls "/path/to/page1,/path/to/page2,..."
```

The script calls `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`
for each URL and returns per-page:
- **Indexing status**: `INDEXED`, `NOT_INDEXED`, `SUBMITTED_AND_INDEXED`,
  `DUPLICATE_WITHOUT_CANONICAL`, `CRAWLED_CURRENTLY_NOT_INDEXED`, etc.
- **Mobile usability verdict**: `MOBILE_FRIENDLY` or issues found
- **Rich result status**: which rich result types were detected and their verdict
- **Last crawl time**: when Googlebot last visited
- **Referring sitemaps**: which sitemap(s) reference this URL
- **Coverage state**: full coverage detail from the Index Coverage report

**If URL Inspection returns 403**: the current auth scope may be read-only. Re-
authenticate with the broader scope:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly
```

Then retry `url_inspection.py`.

**Analyze the inspection results and flag immediately:**
- Any top-traffic page that is `NOT_INDEXED` or `CRAWLED_CURRENTLY_NOT_INDEXED` —
  this is a critical issue. Identify which page, what the coverage state says,
  and what likely caused it (noindex tag, canonical pointing elsewhere, robots
  blocking, soft 404).
- Pages with `DUPLICATE_WITHOUT_CANONICAL` — these are leaking authority. The
  canonical needs to be set.
- Pages where mobile usability is failing — cross-reference with device split
  from Phase 3 to confirm whether mobile traffic is below par.
- Pages with no referring sitemaps — if they are important pages, they should be
  in a sitemap.
- Pages with rich result errors where schema exists — this pre-validates Phase 5
  structured data findings.
- Pages whose last crawl time is more than 60 days ago despite having traffic —
  crawl budget issue or accidental de-prioritization.

---

## Phase 4 — Search Console Analysis

This is where you earn your keep. Do not just restate the data. Interpret it like
an SEO expert would.

### Traffic Overview

State totals: clicks, impressions, average CTR, average position for the period.
Note any dramatic changes. Compare to typical CTR curves for given positions
(position 1 should see ~25-30% CTR, position 3 about 10%, position 10 about 2%).
If a query's CTR is significantly below what its position would predict, that is
a signal the title/snippet needs work.

### Quick Wins (highest impact, lowest effort)

These are the changes that can move the needle in days, not months:

1. **Position 4-10 queries** — ranking on page 1 but below the fold. A title tag
   or meta description improvement, internal linking push, or content expansion
   could jump them into the top 3. List the top 10 with current position,
   impressions, and a specific recommendation for each.

2. **High-impression, low-CTR queries** — use `ctr_gaps_by_page` (not just
   `ctr_opportunities`) because it includes the exact page URL alongside the
   query. This means every recommendation can name the specific page to fix
   and the specific query driving impressions. For each, analyze the likely
   search intent (informational, transactional, navigational, commercial
   investigation) and suggest a title + description that matches it.

3. **Queries dropping month-over-month** — flag anything with >30% click decline.
   For each, hypothesize: is it seasonal? Did a competitor take the SERP feature?
   Did the page content drift from the query intent?

### Search Intent Analysis

For the top 10-15 queries, classify the search intent:
- **Informational** ("how to...", "what is...") → needs comprehensive content,
  FAQ schema
- **Transactional** ("buy...", "pricing...", "near me") → needs clear CTA,
  product schema, price
- **Navigational** ("brand name", "brand + product") → should be ranking #1,
  if not, investigate
- **Commercial investigation** ("best...", "vs...", "review") → needs comparison
  content, trust signals

If the page ranking for a query does not match the intent (e.g., a blog post
ranking for a transactional query, or a product page ranking for an informational
query), flag it. This is often the single biggest unlock.

### Keyword Cannibalization Check

The output includes a `cannibalization` array — these are queries where multiple
pages are actively splitting clicks and impressions. Each entry shows the query,
total impressions, and the competing pages ranked by clicks.

For each cannibalized query, identify:
- The **winner** (most clicks) — this should be the canonical page for the topic
- The **losers** — consolidate into the winner, 301 redirect, or add a canonical
  tag
- Queries where the position is mediocre (5-15) despite high impressions —
  splitting is likely suppressing what should be a top-3 ranking

Also cross-check `top_pages` and `position_buckets` for indirect signals: a page
that used to rank well dropping after a new page was published, or wild position
fluctuation on a query, are signs of cannibalization not yet in the data window.

### Segment Analysis

**Device** (`device_split`): Compare CTR and position across mobile/desktop/
tablet. A page can look healthy overall but be failing on mobile. Flag any device
where CTR is >30% below the site average — that is a mobile UX or snippet
problem.

**Country** (`country_split`): Look at the top countries. Flag cases where:
- A country has high impressions but very low CTR (title/snippet not landing in
  that market)
- Position is much worse in one country vs others (local competitor or relevance
  gap)
- A country with meaningful impressions has near-zero clicks (potential hreflang
  or geo-targeting issue)

**Search type** (`search_type_split`): If `discover` or `googleNews` appear,
note them — they behave differently from web search and have separate optimization
levers (freshness, images, authority signals). If `image` or `video` traffic
exists and the site does not have dedicated image/video optimization, call that
out as an opportunity.

### Content Gaps

Queries where you rank 11-30 — you have topical authority but need a dedicated
page or content expansion. Group related queries into topic clusters. For each
cluster, recommend whether to:
- Expand an existing page (if it partially covers the topic)
- Create a new page (if no page targets this topic)
- Create a content hub with internal linking (if there are 5+ related queries)

### Pages to Fix

List pages with declining clicks. For each:
- Current clicks vs previous period
- % change
- Likely cause (seasonal, algorithm update, new competitor, content staleness,
  technical issue)
- Specific fix recommendation

---

## Phase 4.5 — Keyword Gap Analysis

This phase identifies keyword opportunities directly from the GSC data — no
external tools required, though running `/keyword-research` afterward can go
deeper.

### Step 1: Find Queries Without Dedicated Pages

From the GSC `top_queries` data, identify queries where:
- The site ranks 4-20 for the query
- The page that ranks is NOT a page primarily about that topic (e.g., a homepage
  or a page written for a different keyword is accidentally ranking)
- There is no page on the site with that keyword prominently in the title, H1,
  or URL slug

These are **keyword orphans** — the site has demonstrated topical relevance but
has never given the topic its own page. Creating a dedicated page for each is
typically the highest-leverage content move.

For each orphan, state:
- The query
- Current ranking page (URL) and position
- Monthly impressions
- Recommended action: "Create a new page targeting '[query]' — currently ranked
  #[N] from [URL] which is not dedicated to this topic. A dedicated page could
  realistically move from #[N] to top 5."

### Step 2: Build Topic Clusters from GSC Data

Group all ranking queries by theme. A cluster exists when 3+ queries share a
core concept. For each cluster:
- Name the cluster (e.g., "pricing-related queries", "feature X how-to queries")
- List the queries in it, their positions, and their impressions
- Identify whether a **pillar page** exists that ties them together
- If no pillar page exists, recommend creating one and note the internal linking
  structure needed to funnel authority from cluster pages to the pillar

### Step 3: Business Context Gap Check

Based on what the site does (inferred from its URL, top pages, and ranking
queries), identify topics the business clearly serves that have zero or near-zero
GSC impressions. These are **business-relevant keyword gaps** — the site should
be visible for them but is not.

State the gap explicitly: "This appears to be a [type of business]. You rank for
[X] but have no impressions for [related topic], which has significant search
demand. This is a content gap to close."

### Step 4: Offer Deeper Keyword Research

After completing the inline analysis, offer:

> "I've identified [N] keyword gaps from your GSC data. For broader keyword
> discovery — including keywords you're NOT yet ranking for at all — run
> `/keyword-research` with your seed topics. That skill pulls from keyword
> databases and builds a full opportunity set beyond what GSC can see."

---

## Phase 5 — Technical SEO Audit

Crawl the site's key pages to check technical health. Use the firecrawl skill if
available, otherwise use WebFetch.

Pages to audit: at most 5 pages total. Prioritize: homepage first, then fill
remaining slots with top pages by clicks from Phase 4 — unless a page is flagged
as declining or NOT_INDEXED in Phase 3.5, in which case swap it in. Hard cap at 5
regardless of how many flagged pages exist; pick the highest-priority ones.

### Indexability

- Fetch and analyze `robots.txt` — is it blocking important paths? Are there
  unnecessary disallow rules?
- Check for `noindex` meta tags or `X-Robots-Tag` headers on important pages
- Check canonical URLs — self-referencing (good) or pointing elsewhere
  (investigate)
- Check for `hreflang` tags if the site targets multiple languages/regions
- Look for orphan pages (important pages with no internal links pointing to them)
- Cross-reference with URL Inspection findings from Phase 3.5 — any NOT_INDEXED
  page found there should be explained here with the root cause

### Metadata Audit (Deep)

For each audited page, fetch the actual `<title>` and `<meta name="description">`
from the live HTML. Then cross-reference against GSC data:

1. **Title vs top query alignment**: For each page, look up the top 3 queries
   that page ranks for in `ctr_gaps_by_page`. Does the title tag contain the
   primary ranking query or a close variant? If the title is generic (e.g.,
   "Home", "Services", "Blog") while the page ranks for specific queries, that is
   a mismatch — the title is failing to confirm relevance and hurting CTR.

2. **Title length**: Under 60 characters? Over 60 characters gets truncated in
   SERPs. Flag every page over the limit with the current character count and the
   truncated version as it would appear in Google.

3. **Meta description**: Present? 120-160 characters? Contains a call to action?
   If a page has no meta description, Google rewrites it — often pulling
   unhelpful boilerplate. Flag every missing description.

4. **Duplicate titles**: Are multiple pages using the same or very similar titles?
   List all duplicates found.

5. **Open Graph tags**: `og:title`, `og:description`, `og:image` present? Missing
   OG tags means social shares render with no preview — flag any page missing
   them, especially for content pages.

Report the findings as a table:

| Page URL | Title (actual) | Title length | Top GSC query | Title/query match? | Meta desc present? | OG tags? |
|----------|---------------|--------------|---------------|--------------------|--------------------|----------|
| /        | [actual title] | [N] chars   | [query]       | Yes / No           | Yes / No           | Yes / No |

After presenting the metadata audit table, offer:
> "I found [N] pages with metadata issues. Run `/meta-tags-optimizer` to generate
> optimized title tags and meta descriptions for each — it will use the GSC query
> data from this audit to write titles that match actual search demand."

### Schema Markup Audit (Deep)

Detect the site type from its top pages, ranking queries, and visible content,
then check what schema types exist vs. what should exist for that site type.

**Step 1: Detect site type**

Based on the homepage and top pages content, classify as one of:
- E-commerce (products, pricing, cart)
- Local business (address, phone, service area)
- SaaS / software (features, pricing, signup)
- Content / blog (articles, guides, tutorials)
- Professional services (agency, consultant, law firm)
- Media / news (articles published frequently)

**Step 2: Define expected schema for site type**

| Site Type | Must Have | High Impact if Missing | Nice to Have |
|-----------|-----------|------------------------|--------------|
| E-commerce | Product, BreadcrumbList | AggregateRating, FAQPage, Offer | SiteLinksSearchBox |
| Local business | LocalBusiness, GeoCoordinates | OpeningHoursSpecification, AggregateRating | FAQPage |
| SaaS | Organization, SoftwareApplication | FAQPage, BreadcrumbList | HowTo, Review |
| Content / blog | Article or BlogPosting | FAQPage, BreadcrumbList | HowTo, Video |
| Professional services | Organization, Service | FAQPage, Review | ProfessionalService, Person |
| Media / news | NewsArticle | BreadcrumbList | VideoObject, ImageObject |

**Step 3: Audit each top page for actual schema present**

For each audited page, extract any `<script type="application/ld+json">` blocks.
List what `@type` values are present. Then compare against the expected set for
this site type.

Report findings:

| Page URL | Schema found | Missing high-impact schema | Errors in existing schema |
|----------|-------------|---------------------------|---------------------------|
| /        | Organization | FAQPage, SiteLinksSearchBox | None |
| /pricing | SoftwareApplication | FAQPage, Offer | Missing `price` property |

**Step 4: Flag errors in existing schema**

Common issues to check:
- Missing required fields for the `@type` (e.g., Product schema without `name`
  or `offers`)
- `url` properties using relative paths instead of absolute URLs
- Dates not in ISO 8601 format
- `AggregateRating` with `ratingCount` of 0 or missing
- Duplicate schema blocks for the same type on one page
- Schema that describes content not visible on the page (violates Google policy)

Cross-reference with rich result status from Phase 3.5 URL Inspection — if a
page showed rich result errors there, find the cause here.

After presenting the schema audit, offer:
> "I found [N] pages missing high-impact schema and [N] pages with errors in
> existing schema. Run `/schema-markup-generator` to generate correct JSON-LD for
> each — it will use the site type and page content from this audit."

### Core Web Vitals & Performance

- Render-blocking scripts in `<head>` — should be deferred or async
- Images: lazy-loaded? Have `alt` attributes? Served in modern formats
  (WebP/AVIF)? Properly sized (not 3000px wide in a 400px container)?
- `<link rel="preload">` for critical resources (fonts, above-the-fold images)?
- Excessive DOM size (>1500 nodes suggests bloat)?
- Third-party script bloat — count external domains loaded

### Internal Linking & Site Architecture

- Does the page have internal links? Are they descriptive (not "click here")?
- Does the page link to related content (topic clusters)?
- Is the page reachable within 3 clicks from the homepage?
- Broken internal links (404s)?

### Mobile Readiness

- Viewport meta tag present?
- Touch targets large enough (48px minimum)?
- Text readable without zooming?
- No horizontal scrolling?
- Cross-reference mobile usability findings from Phase 3.5 URL Inspection

---

## Phase 6 — Report

Output a structured report. Use this format exactly:

---

# SEO Analysis Report — [site.com]
*Analyzed: [date range] | Data: Google Search Console + URL Inspection + Technical Crawl*

## Executive Summary
[2-3 sentences: overall health, the single most important thing to fix, and the
estimated opportunity if fixed. Be specific: "Your site gets 12,400 clicks/month
but is leaving an estimated 3,000-5,000 additional clicks on the table from
position 4-10 queries that need title tag optimization."]

## Traffic Snapshot

| Metric | Value | vs Prior Period |
|--------|-------|----------------|
| Total Clicks | X | up/down X% |
| Impressions | X | up/down X% |
| Avg CTR | X% | up/down |
| Avg Position | X | up/down |

## Quick Wins (Fix These First)

[Numbered list, most impactful first. Every recommendation must include:
1. The specific page URL
2. The specific query/keyword
3. Current metrics (position, impressions, CTR)
4. What to change (exact new title, description, or action)
5. Why this will work (the search intent logic)]

Example format: "Update title tag on /pricing from 'Pricing' to 'Plans &
Pricing — [Actual Value Prop]' — currently ranks #7 for 'your-product pricing'
with 2,400 monthly impressions but only 1.2% CTR. This is a transactional query
where users expect to see pricing info immediately. A title with the price range
or 'Free trial' would increase CTR to ~3-5%."

## URL Inspection Findings

[Results from Phase 3.5. Tables grouped by severity:]

### Critical: Not Indexed
| Page URL | Coverage State | Last Crawl | Root Cause | Fix |
|----------|---------------|------------|------------|-----|

### Warnings: Mobile / Rich Result Issues
| Page URL | Issue | Impact | Fix |
|----------|-------|--------|-----|

### Crawl Staleness
[Pages with last crawl > 60 days despite having traffic, with hypothesis and fix.]

## Search Intent Mismatches
[Pages where the content type does not match what searchers want. For each: the
query, the current page, the intent, and what to do about it.]

## Keyword Cannibalization
[Queries where multiple pages compete. Which page should win, what to do with
the others.]

## Keyword Gaps

### Orphan Keywords (Rankings Without Dedicated Pages)
| Query | Ranking Page | Position | Monthly Impressions | Recommended Action |
|-------|-------------|----------|---------------------|--------------------|

### Topic Clusters Needing Pillar Pages
[Each cluster with constituent queries, impressions, and pillar page recommendation.]

### Business Relevance Gaps
[Topics the site should rank for based on what it does, but has zero/near-zero
impressions for. Specific, not generic.]

## Metadata Issues

| Page URL | Issue Type | Current Value | Recommended Fix |
|----------|-----------|---------------|-----------------|
| /example | Title too generic | "Services" | "[Keyword] Services — [Benefit] \| [Brand]" |
| /pricing | No meta description | — | Write 150-160 char description including "[top ranking query]" |

## Schema Gaps

| Page URL | Site Type | Missing Schema | Impact | Priority |
|----------|-----------|---------------|--------|----------|
| / | SaaS | FAQPage | High — FAQ rich results expand SERP footprint | P1 |
| /pricing | SaaS | Offer, AggregateRating | High — pricing rich results increase CTR | P1 |

### Existing Schema Errors
| Page URL | Schema Type | Error | Fix |
|----------|------------|-------|-----|

## Content Opportunities
[Topic clusters you partially rank for that need dedicated pages or expanded
content. Group by theme, suggest page titles, target keywords.]

## Traffic Drops to Investigate
[Pages/queries with significant declines, with a hypothesis and investigation
steps for each.]

## Technical Issues
[Severity: Critical / High / Medium / Low]
[For each: what it is, which pages, how to fix it, and the impact on rankings
if left unfixed.]

## 30-Day Action Plan

[Prioritized by impact. Each item must be specific enough that someone could do
it without asking follow-up questions.]

| Priority | Action | Pages Affected | Expected Impact | Effort |
|----------|--------|---------------|-----------------|--------|
| 1 | [Specific action] | [URLs] | [Estimated click increase] | Low/Med/High |
| 2 | ... | ... | ... | ... |

---

Every recommendation must be specific and actionable. "Improve your meta
descriptions" is useless. "Update the meta description on /product-page to
include '[exact phrase from top query]' and a clear CTA — it currently has
5,400 impressions but 0.8% CTR, suggesting the snippet does not match what
searchers expect to see for this transactional query" is useful.

When estimating impact, use conservative CTR curves: position 1 ~27%, position
2 ~15%, position 3 ~11%, position 4-5 ~5-8%, position 6-10 ~2-4%. Moving from
position 7 to position 3 on a 2,400 impression/month query means roughly +170
clicks/month. Use real numbers from the data.

---

## Phase 7 — Targeted Skill Handoffs (Optional)

After delivering the report, surface the follow-up actions based on what was
found. Only offer handoffs where the audit actually found issues — do not offer
all three if only one is relevant.

### Metadata Handoff

If the metadata audit found [N] pages with issues:

> "I found [N] pages with metadata issues — [X] with title/query mismatches,
> [Y] missing meta descriptions, [Z] missing OG tags. Run `/meta-tags-optimizer`
> to generate optimized tags for each page. Share the metadata audit table from
> this report as context."

### Schema Handoff

If the schema audit found gaps or errors:

> "I found [N] pages missing high-impact schema and [N] pages with schema errors.
> Run `/schema-markup-generator` to generate correct JSON-LD. The schema audit
> table from this report is the input — it already identifies the site type and
> what schema types are needed per page."

### Keyword Research Handoff

If the keyword gap analysis found orphan keywords or business relevance gaps:

> "I found [N] keyword gaps from GSC data. For deeper discovery — keywords you
> are not ranking for at all — run `/keyword-research` with these seed topics:
> [list 3-5 seed terms derived from the gap analysis]. That skill pulls from
> keyword databases and builds a full opportunity set beyond what GSC can see."

---

## Phase 8 — Content Generation (Optional)

After delivering the report, if the Content Opportunities section identified
actionable content gaps, offer to generate the content:

> "I found [N] content opportunities. Want me to draft the content? I can write
> [blog posts / landing pages / both] in parallel — each one optimized for the
> target keyword and search intent."

If the user agrees, spawn content agents **in parallel** using the Agent tool.
Each agent writes one piece of content independently.

### How to Spawn Content Agents

For each content opportunity, determine the content type from the search intent:
- **Informational / commercial investigation** → blog post agent
- **Transactional / commercial** → landing page agent

Spawn agents in parallel. Each agent receives:
1. The content writing guidelines (located via find — see below)
2. The specific opportunity data from the analysis

Before spawning agents, locate the content writing reference:

```bash
CONTENT_REF=$(find ~/.claude/skills ~/.codex/skills .agents/skills -name "content-writing.md" -path "*content-writer*" 2>/dev/null | head -1)
if [ -z "$CONTENT_REF" ]; then
  echo "WARNING: content-writing.md not found. Content agents will use built-in knowledge only."
else
  echo "Content reference at: $CONTENT_REF"
fi
```

Pass `$CONTENT_REF` as the path in each agent prompt below. If not found, omit
the "Read the content writing guidelines" line — the agents will still produce
good content using built-in knowledge.

Use this prompt template for each agent:

#### Blog Post Agent Prompt

```
You are a senior content strategist writing a blog post that ranks on Google.

Read the content writing guidelines at: $CONTENT_REF
Follow the "Blog Posts" section exactly.

## Assignment

Target keyword: [keyword]
Current position: [position] (query ranked but no dedicated content)
Monthly impressions: [impressions]
Search intent: [informational / commercial investigation]
Site context: [what the site is about, its audience]
Existing pages to link to: [relevant internal pages from the analysis]
[If available] Competitor context: [what currently ranks for this keyword]

## Deliverables

Write the complete blog post following the guidelines, including:
1. Full post in markdown with proper heading hierarchy
2. SEO metadata (title tag, meta description, URL slug)
3. JSON-LD structured data (Article/BlogPosting + FAQPage if FAQ included)
4. Internal linking plan (which existing pages to link to/from)
5. Publishing checklist

## Quality Gate
Before finishing, verify:
- Would the reader need to search again? (If yes, not done)
- Does the post contain specific examples only an expert would include?
- Does the format match what Google shows for this query?
- Is every paragraph earning its place? (No filler)
```

#### Landing Page Agent Prompt

```
You are a senior conversion copywriter writing a landing page that ranks AND converts.

Read the content writing guidelines at: $CONTENT_REF
Follow the "Landing Pages" section exactly.

## Assignment

Target keyword: [keyword]
Current position: [position]
Monthly impressions: [impressions]
Search intent: [transactional / commercial]
Page type: [service / product / location / comparison]
Site context: [what the site is about, value prop, target customer]
Existing pages to link to: [relevant internal pages]
[If available] Competitor context: [what currently ranks]

## Deliverables

Write the complete landing page following the guidelines, including:
1. Full page copy in markdown with proper heading hierarchy and CTA placements
2. SEO metadata (title tag, meta description, URL slug)
3. Conversion strategy (primary CTA, objections addressed, trust signals)
4. JSON-LD structured data
5. Internal linking plan
6. Publishing checklist

## Quality Gate
Before finishing, verify:
- Would you convert after reading this? (If not, what is missing?)
- Are there vague claims that should be replaced with specifics?
- Is every objection addressed?
- Is it clear what the visitor should do next?
```

### Spawning Rules

- Spawn up to **5 content agents in parallel** (more than 5 gets unwieldy —
  prioritize by impact)
- Prioritize opportunities by: impressions x position-improvement-potential
- Each agent works independently — they do not need to coordinate
- As agents complete, present each piece of content to the user with its metadata
- After all agents finish, provide a summary: what was generated, suggested
  publishing order (highest impact first), and any cross-linking between new pages
