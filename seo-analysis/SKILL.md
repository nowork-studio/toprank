---
name: seo-analysis
description: >
  Full SEO audit: Google Search Console data + technical crawl + search intent
  analysis. Feeds real GSC data into AI to surface quick wins, diagnose traffic
  drops, find content gaps, and produce an actionable 30-day plan. Use this skill
  whenever the user asks about SEO, search rankings, organic traffic, Google
  Search Console, keyword performance, traffic drops, content gaps, search
  visibility, or technical SEO. Also trigger on: "why is my traffic down",
  "what keywords am I ranking for", "improve my rankings", "check my search
  console", "SEO audit", "analyze my SEO", "technical SEO", "meta tags",
  "indexing issues", "crawl errors", "content strategy", "keyword cannibalization",
  "search intent", or any organic search question. If in doubt, trigger. This
  skill handles everything from quick GSC checks to deep technical audits.
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

Your goal is not to produce a generic report. It's to find the 3-5 changes that
will have the biggest impact on this specific site's organic traffic, and explain
exactly how to make them.

Works on any site. Works whether you're inside a website repo or auditing a URL
cold.

---

## Phase 0 — Preflight Check

Run this once before anything else. It checks gcloud, ensures a GCP project exists,
enables the Search Console API, and opens the browser for Google OAuth if needed:

```bash
SKILL_SCRIPTS=$(find ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
[ -z "$SKILL_SCRIPTS" ] && echo "ERROR: seo-analysis scripts not found" && exit 1
python3 "$SKILL_SCRIPTS/preflight.py"
```

- **`OK: All dependencies ready.`** → continue to Phase 1.
- **Browser opens for Google login** → the user needs to log in with the Google
  account that owns their Search Console properties. Preflight finishes automatically
  after login.
- **`gcloud init` runs** → first-time user. The wizard walks them through signing in
  and creating/selecting a GCP project. After it completes, preflight continues
  automatically.
- **`Search Console API: enabled`** → preflight auto-enabled the API. No action needed.
- **ERROR: Could not enable the Search Console API** → the user needs to enable it
  manually: `gcloud services enable searchconsole.googleapis.com`. If billing is
  required, link a billing account at https://console.cloud.google.com/billing
  (the Search Console API itself is free).
- **gcloud not found** → OS-specific install instructions are printed. Install
  gcloud, then re-run Phase 0.
- **No gcloud and user wants to skip GSC** → that's fine. Jump directly to Phase 5
  for a technical-only audit (crawl, meta tags, indexing). GSC data just won't be
  available.

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
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
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

**If 403 (permission denied)** → the account lacks GSC property access. Verify at
Search Console → Settings → Users and permissions.

---

## Phase 2 — Identify the Site

### If inside a website repo
Auto-detect the site URL from config files:
- `package.json` → `"homepage"` field or scripts with domain hints
- `next.config.js` / `next.config.ts` → `env.NEXT_PUBLIC_SITE_URL` or `basePath`
- `astro.config.*` → `site:` field
- `gatsby-config.js` → `siteMetadata.siteUrl`
- `hugo.toml` / `hugo.yaml` → `baseURL`
- `_config.yml` (Jekyll) → `url` field
- `.env` or `.env.local` → `NEXT_PUBLIC_SITE_URL`, `SITE_URL`, `PUBLIC_URL`
- `vercel.json` → deployment aliases
- `CNAME` file (GitHub Pages)

Confirm with the user: "I found your site at `https://example.com` — is that right?"

### If not in a website repo
Ask: "What's your website URL? (e.g. https://yoursite.com)"

### Match to GSC property
If Phase 1 already listed the user's GSC properties, use that output. Otherwise
re-run (e.g., if GSC was skipped and the user has since authenticated):

```bash
python3 "$SKILL_SCRIPTS/list_gsc_sites.py"
```

GSC properties can be domain properties (`sc-domain:example.com`) or URL-prefix
properties (`https://example.com/`). The script handles both. If both a domain
property and a URL-prefix property exist for the same site, prefer the domain
property — it covers all subdomains, protocols, and subpaths, giving more complete
data. If multiple matches exist and it's still ambiguous, ask the user to confirm.

---

## Phase 3 — Collect Data

Run the main analysis script with the confirmed site property:

```bash
python3 "$SKILL_SCRIPTS/analyze_gsc.py" \
  --site "sc-domain:example.com" \
  --days 90
```

This pulls:
- **Top queries** by impressions, clicks, CTR, average position
- **Top pages** by clicks + impressions
- **Position buckets** — queries in 1-3, 4-10, 11-20, 21+ (the "striking distance" opportunities)
- **Queries losing clicks** — comparing last 28 days vs the prior 28 days
- **Pages losing traffic** — same comparison
- **Queries with high impressions but low CTR** — title/snippet optimization targets
- **Device split** — mobile vs desktop vs tablet performance

**If GSC is unavailable**, skip to Phase 5 (technical-only audit).

---

## Phase 4 — Search Console Analysis

This is where you earn your keep. Don't just restate the data. Interpret it like
an SEO expert would.

### Traffic Overview
State totals: clicks, impressions, average CTR, average position for the period.
Note any dramatic changes. Compare to typical CTR curves for given positions
(position 1 should see ~25-30% CTR, position 3 about 10%, position 10 about 2%).
If a query's CTR is significantly below what its position would predict, that's a
signal the title/snippet needs work.

### Quick Wins (highest impact, lowest effort)

These are the changes that can move the needle in days, not months:

1. **Position 4-10 queries** — ranking on page 1 but below the fold. A title tag
   or meta description improvement, internal linking push, or content expansion
   could jump them into the top 3. List the top 10 with current position,
   impressions, and a specific recommendation for each.

2. **High-impression, low-CTR queries** — you're being shown but not clicked.
   This is almost always a title/snippet mismatch with search intent. For each
   one, analyze the likely search intent (informational, transactional,
   navigational, commercial investigation) and suggest a title + description
   that matches it.

3. **Queries dropping month-over-month** — flag anything with >30% click decline.
   For each, hypothesize: is it seasonal? Did a competitor take the SERP feature?
   Did the page content drift from the query intent?

### Search Intent Analysis

For the top 10-15 queries, classify the search intent:
- **Informational** ("how to...", "what is...") → needs comprehensive content, FAQ schema
- **Transactional** ("buy...", "pricing...", "near me") → needs clear CTA, product schema, price
- **Navigational** ("brand name", "brand + product") → should be ranking #1, if not, investigate
- **Commercial investigation** ("best...", "vs...", "review") → needs comparison content, trust signals

If the page ranking for a query doesn't match the intent (e.g., a blog post
ranking for a transactional query, or a product page ranking for an informational
query), flag it. This is often the single biggest unlock.

### Keyword Cannibalization Check

Look for queries where multiple pages from the same site rank. Signs:
- The same query appears for two or more pages in the top pages data
- A page that used to rank well for a query dropped after a new page was published
- Position fluctuates wildly for a query (Google is confused about which page to show)

If found, recommend: consolidate into one authoritative page, 301 redirect the
weaker one, or add canonical tags.

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
- Likely cause (seasonal, algorithm update, new competitor, content staleness, technical issue)
- Specific fix recommendation

---

## Phase 5 — Technical SEO Audit

Crawl the site's key pages to check technical health. Use the firecrawl skill if
available, otherwise use WebFetch.

Pages to audit: homepage, top 3-5 traffic pages from Phase 4, plus any pages
flagged as declining.

### Indexability
- Fetch and analyze `robots.txt` — is it blocking important paths? Are there
  unnecessary disallow rules?
- Check for `noindex` meta tags or `X-Robots-Tag` headers on important pages
- Check canonical URLs — self-referencing (good) or pointing elsewhere (investigate)
- Check for `hreflang` tags if the site targets multiple languages/regions
- Look for orphan pages (important pages with no internal links pointing to them)

### Title & Meta
- `<title>` present? Under 60 characters? Contains primary keyword near the front?
- `<meta name="description">` present? 120-160 characters? Includes a call to action?
- Title uniqueness — are multiple pages using the same or very similar titles?
- Open Graph and Twitter Card tags present for social sharing?

### Headings & Content Structure
- Single `<h1>` per page? Contains primary keyword naturally (not stuffed)?
- Logical heading hierarchy (h1 → h2 → h3, no skipped levels)?
- Content depth — is the page thin (under 300 words for a page trying to rank)?
- Content freshness — when was it last updated? Stale content loses rankings.

### Structured Data
Detect the site type and check for appropriate schema:
- **E-commerce**: Product, AggregateRating, BreadcrumbList, FAQPage, Offer
- **Local business**: LocalBusiness, OpeningHoursSpecification, GeoCoordinates
- **Blog/content**: Article, BlogPosting, HowTo, FAQPage
- **SaaS/services**: Organization, Service, FAQPage, SoftwareApplication
- **Professional services**: ProfessionalService, Review, Person

Validate any existing JSON-LD — common issues: missing required fields, wrong
@type, invalid dates, duplicate markup.

### Core Web Vitals & Performance
- Render-blocking scripts in `<head>` — should be deferred or async
- Images: lazy-loaded? Have `alt` attributes? Served in modern formats (WebP/AVIF)?
  Properly sized (not 3000px wide in a 400px container)?
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

---

## Phase 6 — Report

Output a structured report. Use this format:

---

# SEO Analysis Report — [site.com]
*Analyzed: [date range] | Data: Google Search Console + Technical Crawl*

## Executive Summary
[2-3 sentences: overall health, the single most important thing to fix, and the
estimated opportunity if fixed. Be specific: "Your site gets 12,400 clicks/month
but is leaving an estimated 3,000-5,000 additional clicks on the table from
position 4-10 queries that need title tag optimization."]

## Traffic Snapshot
| Metric | Value | vs Prior Period |
|--------|-------|----------------|
| Total Clicks | X | ↑/↓ X% |
| Impressions | X | ↑/↓ X% |
| Avg CTR | X% | ↑/↓ |
| Avg Position | X | ↑/↓ |

## Quick Wins (Fix These First)
[Numbered list, most impactful first. Every recommendation must include:
1. The specific page URL
2. The specific query/keyword
3. Current metrics (position, impressions, CTR)
4. What to change (exact new title, description, or action)
5. Why this will work (the search intent logic)

Example: "Update title tag on /pricing from 'Pricing' to 'Plans & Pricing —
[Actual Value Prop]' — currently ranks #7 for 'your-product pricing' with
2,400 monthly impressions but only 1.2% CTR. This is a transactional query
where users expect to see pricing info immediately. A title with the price
range or 'Free trial' would increase CTR to ~3-5%."]

## Search Intent Mismatches
[Pages where the content type doesn't match what searchers want. For each:
the query, the current page, the intent, and what to do about it.]

## Keyword Cannibalization
[Queries where multiple pages compete. Which page should win, what to do with
the others.]

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
[Prioritized by impact. Each item must be specific enough that someone could
do it without asking follow-up questions.]

| Priority | Action | Pages Affected | Expected Impact | Effort |
|----------|--------|---------------|-----------------|--------|
| 1 | [Specific action] | [URLs] | [Estimated click increase] | [Low/Med/High] |
| 2 | ... | ... | ... | ... |

---

Every recommendation must be specific and actionable. "Improve your meta
descriptions" is useless. "Update the meta description on /product-page to
include '[exact phrase from top query]' and a clear CTA — it currently has
5,400 impressions but 0.8% CTR, suggesting the snippet doesn't match what
searchers expect to see for this transactional query" is useful.

When estimating impact, use conservative CTR curves: position 1 ~27%, position
2 ~15%, position 3 ~11%, position 4-5 ~5-8%, position 6-10 ~2-4%. Moving from
position 7 to position 3 on a 2,400 impression/month query means roughly
+170 clicks/month. Use real numbers from the data.

---

## Phase 7 — Content Generation (Optional)

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
- Would you convert after reading this? (If not, what's missing?)
- Are there vague claims that should be replaced with specifics?
- Is every objection addressed?
- Is it clear what the visitor should do next?
```

### Spawning Rules

- Spawn up to **5 content agents in parallel** (more than 5 gets unwieldy — prioritize by impact)
- Prioritize opportunities by: impressions × position-improvement-potential
- Each agent works independently — they don't need to coordinate
- As agents complete, present each piece of content to the user with its metadata
- After all agents finish, provide a summary: what was generated, suggested
  publishing order (highest impact first), and any cross-linking between new pages
