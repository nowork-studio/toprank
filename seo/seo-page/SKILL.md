---
name: seo-page
argument-hint: "<URL of the page to analyze, e.g. https://example.com/blog/my-post>"
description: >
  Single-page SEO audit: deep content quality evaluation using Google's E-E-A-T
  framework, Helpful Content guidelines, on-page SEO factors, search intent
  alignment, technical signals, and readability analysis. Fetches GSC performance
  data for that specific page, crawls the live HTML, evaluates metadata, schema
  markup, internal linking, content depth, and produces a scored report with
  actionable fixes. Use this skill whenever the user wants to analyze a specific
  page or URL — not the whole site. Trigger on: "analyze this page", "audit this
  URL", "how is this page doing", "evaluate my blog post", "check this landing
  page", "page SEO", "content quality check", "is this page good enough",
  "review this page's SEO", "what's wrong with this page", "how can I improve
  this page", "page analysis", "single page audit", "content audit for [URL]",
  or any request that names a specific URL/page for SEO evaluation. If the user
  provides a specific URL (not just a domain), this is likely the right skill —
  use /seo-analysis for full-site audits instead.
---

# Single-Page SEO Analysis

You are a senior SEO content strategist and technical auditor. Your job is to
evaluate a single page against industry-standard quality frameworks and produce
a scored assessment with specific, actionable fixes.

This skill is laser-focused on one page. Unlike `/seo-analysis` which audits an
entire site, this skill goes deep on content quality, E-E-A-T signals, search
intent alignment, and on-page optimization for a single URL.

---

## Step 0 — Get the Target Page URL

The user should provide a specific page URL (not just a domain). If they provide
only a domain, ask which page they want analyzed:

> "Which specific page do you want me to analyze? (e.g., `https://example.com/blog/my-post`).
> For a full-site audit, use `/seo-analysis` instead."

Store the URL as `$PAGE_URL`. Derive the domain:

```bash
DOMAIN=$(python3 -c "import sys; from urllib.parse import urlparse; print(urlparse(sys.argv[1]).netloc.lstrip('www.'))" "$PAGE_URL")
PAGE_PATH=$(python3 -c "import sys; from urllib.parse import urlparse; print(urlparse(sys.argv[1]).path)" "$PAGE_URL")
```

---

## Phase 0 — Preflight & Data Gathering

Read and follow `../shared/preamble.md` for script discovery and GSC auth.

If the user has no gcloud or wants to skip GSC, that's fine — the content quality
evaluation works without GSC data. GSC enriches the analysis but isn't required.

---

## Phase 1 — Parallel Data Collection

**Launch all of these in a single turn using parallel tool calls:**

### 1a. Fetch the page (WebFetch)
Fetch `$PAGE_URL` to get the full HTML. This is the primary input — everything
else enriches it.

**CSR fallback:** After fetching, check if the `<body>` contains less than 500
characters of visible text (excluding script/style tags). If so, the page is
likely client-side rendered (React, Next.js CSR, Vue SPA). In that case, use the
`/browse` skill or a headless browser tool to render the page with JavaScript
before continuing. Do not analyze an empty shell — you will produce garbage scores.

### 1a-2. SERP reality check (WebSearch)
Search for the page's likely primary keyword (infer from URL slug or title) to see
what actually ranks. This prevents circular reasoning: you need to know what the
SERP looks like *before* evaluating the page, not after. Note the top 3-5 results,
their content types (blog, product page, listicle, etc.), and any SERP features
(featured snippets, PAA, video carousels).

### 1b. Fetch robots.txt (WebFetch)
Fetch `{origin}/robots.txt` to check if the page is blocked.

### 1c. GSC page-level data (Bash — skip if no GSC access)
Pull performance data for this specific page:

```bash
python3 "$SKILL_SCRIPTS/analyze_gsc.py" \
  --site "$GSC_PROPERTY" \
  --days 90 \
  --page-filter "$PAGE_PATH"
```

After `analyze_gsc.py` completes, run `show_gsc.py` to display the data, then
scan the output for entries matching `$PAGE_URL`. Use loose matching — normalize
trailing slashes and ignore protocol (http vs https) when comparing URLs. If the
exact URL doesn't match, try the path portion only.

### 1d. Match GSC property (Bash — skip if no GSC access)
Before running URL Inspection or GSC queries, map the domain to the correct GSC
property. Run `list_gsc_sites.py` and match against `$DOMAIN`:

```bash
python3 "$SKILL_SCRIPTS/list_gsc_sites.py"
```

GSC properties can be domain properties (`sc-domain:example.com`) or URL-prefix
properties (`https://example.com/`). Prefer domain properties — they cover all
subdomains and protocols. Store the matched property as `$GSC_PROPERTY`. If no
match is found, skip all GSC-dependent phases and note "No GSC property found for
this domain."

### 1e. URL Inspection (Bash — skip if no GSC access)
```bash
python3 "$SKILL_SCRIPTS/url_inspection.py" \
  --site "$GSC_PROPERTY" \
  --urls "$PAGE_PATH"
```

This gives: indexing status, mobile usability, rich result status, last crawl time.

### 1f. Load business context (Bash)
```bash
BC_FILE="$HOME/.toprank/business-context/$DOMAIN.json"
[ -f "$BC_FILE" ] && cat "$BC_FILE" || echo "NOT_FOUND"
```

If not found, infer what you can from the page content. Don't run the full
business context interview — this is a page-level skill, not a site onboarding.

---

## Phase 2 — Page Content Extraction

From the fetched HTML, extract:

1. **Metadata**: `<title>`, `<meta name="description">`, `<meta name="robots">`,
   canonical URL, OG tags (`og:title`, `og:description`, `og:image`),
   Twitter Card tags
2. **Headings**: full heading hierarchy (H1, H2, H3, H4)
3. **Content body**: main content text (strip nav, footer, sidebar)
4. **Word count**: total words in main content
5. **Internal links**: all internal links with anchor text
6. **External links**: all outbound links with anchor text and domains
7. **Images**: all images with alt text, src, dimensions if available
8. **Schema markup**: all `<script type="application/ld+json">` blocks
9. **Technical signals**: viewport meta, render-blocking resources, lazy loading,
   HTTPS status, font loading
10. **Publish/update date**: look for `<time>`, `datePublished`, `dateModified`,
    or visible dates on the page

---

## Phase 3 — Content Quality Evaluation

Read `references/content-quality-framework.md` for the full scoring rubric.

### Indexability Gate (check FIRST)

Before scoring anything, check if the page is indexable:
- Is there a `<meta name="robots" content="noindex">` tag?
- Is robots.txt blocking the URL?
- Does URL Inspection show `NOT_INDEXED` or `CRAWLED_CURRENTLY_NOT_INDEXED`?
- Is the canonical pointing to a different URL?

If the page is NOT indexable, **stop scoring and lead the report with this.** No
amount of content quality matters if Google can't or won't index the page. Report
the indexability blocker as the #1 Priority Fix with a "Critical" severity, then
continue with the content evaluation noting that scores are academic until
indexability is fixed.

### Content Quality Evaluation

Evaluate the page across all six dimensions. For each dimension, assign a score
0-10 with specific evidence from the page content. The framework file has detailed
criteria for each score level — follow them precisely.

### 3a. Search Intent Alignment (weight: 20%)

Determine what search queries this page should rank for:
- **From GSC** (if available): use actual ranking queries from Phase 1c
- **From content**: infer the primary target keyword from the title, H1, and
  content focus
- **From URL**: the slug often reveals the target keyword

**Critical: avoid circular reasoning.** Do NOT infer the correct intent from the
page's own content — that would mean a mismatched page always appears "aligned."
Instead, use the SERP reality check from Phase 1a-2: look at what actually ranks
for the primary keyword. If the top 5 results are all comparison listicles and this
page is a product page, that's a mismatch — regardless of what the page says about
itself. The SERP is the ground truth for intent, not the page.

Classify the intent (informational, commercial, transactional, navigational) based
on the SERP results and the keyword signals, then evaluate whether this page's
format matches. A blog post for transactional intent is a mismatch. A thin product
page for informational intent is a mismatch.

Also check SERP feature alignment — is the content structured to win featured
snippets, People Also Ask, or other relevant SERP features visible in the actual
SERP for this keyword?

### 3b. E-E-A-T Evaluation (weight: 20%)

Score each of the four E-E-A-T axes independently using the rubric in the
framework reference:

- **Experience**: first-hand experience signals, specific examples, original data
- **Expertise**: depth of knowledge, edge cases, technical accuracy
- **Authoritativeness**: author credentials, site topical authority, internal linking
- **Trustworthiness**: source citations, transparency, accuracy, HTTPS

Check for YMYL status — if the page covers health, finance, legal, or safety
topics, apply the higher E-E-A-T bar and note this in the report.

### 3c. Content Quality & Depth (weight: 20%)

Evaluate:
- **Comprehensiveness**: does the page fully answer the query vs top competitors?
- **Original value**: what does this page offer that others don't?
- **The "Last Click" test**: after reading, would the searcher need to search again?
- **Helpful Content signals**: positive signals present, negative signals absent
- **Word count appropriateness**: not thin (for the topic), not padded
- **Freshness**: content currency, dated references, broken links

### 3d. On-Page SEO (weight: 15%)

Evaluate each on-page factor from the framework:
- Title tag (length, keyword, intent match, uniqueness, CTR appeal)
- Meta description (length, keyword, CTA, uniqueness)
- Headings (H1 presence, hierarchy, keywords, descriptiveness)
- Internal linking (count, anchor text quality, relevance)
- External linking (citations, source quality)
- Image optimization (alt text, format, sizing, lazy loading)
- URL structure (readable, keyword-rich, depth)

### 3e. Content Structure & UX (weight: 15%)

Evaluate:
- Readability (paragraph length, sentence variety, vocabulary level)
- Content UX (above-fold value, visual breaks, TOC, mobile-friendliness)
- Scanning ability (bold phrases, bullets, numbered lists)

### 3f. Technical SEO (weight: 10%)

Evaluate:
- Indexability (robots.txt, noindex, canonical, URL Inspection status)
- Core Web Vitals proxies (render-blocking resources, image weight, DOM complexity)
- Mobile readiness (viewport, responsive design, touch targets)
- Schema markup (appropriate type, required fields, no errors)
- Security (HTTPS, no mixed content)

---

## Phase 4 — GSC Performance Context

**Skip this phase if GSC data was unavailable.**

Analyze the page's actual search performance:

### Ranking Queries
For each query this page ranks for (from GSC):
- Current position, clicks, impressions, CTR
- Expected CTR for that position (use standard CTR curves)
- Gap: is CTR above or below expected?
- Intent classification of the query

### CTR Benchmarks
Use these position-based CTR benchmarks for the Gap column. Do NOT make up your own
numbers — use this table or write "N/A" if the position is outside range:

| Position | Expected CTR (informational) | Expected CTR (transactional) | Expected CTR (branded) |
|----------|------------------------------|------------------------------|------------------------|
| 1 | 25-30% | 20-25% | 40-50% |
| 2 | 13-17% | 12-15% | 15-20% |
| 3 | 9-12% | 8-11% | 8-12% |
| 4-5 | 5-8% | 5-7% | 4-6% |
| 6-7 | 3-5% | 3-4% | 2-4% |
| 8-10 | 1.5-3% | 1.5-3% | 1-2% |
| 11-20 | 0.5-1.5% | 0.5-1% | <1% |

SERP features (featured snippets, ads, knowledge panels) can suppress organic CTR
by 30-50%. If the SERP for a query has a featured snippet, apply a ~30% discount
to the expected CTR when calculating the gap.

### CTR Analysis
If CTR is below expected for the position:
- Is it a title tag problem? (title doesn't match query intent)
- Is it a meta description problem? (no compelling reason to click)
- Is it a SERP feature issue? (featured snippet, ads, or rich results pushing organic down)

### Trend
Is traffic to this page growing, stable, or declining? If declining:
- When did the decline start?
- Correlate with algorithm updates, content changes, or competitive entries

### Cannibalization Check
Are other pages on the same site competing for the same queries? If so:
- Which page is winning?
- Should this page be consolidated, differentiated, or canonicalized?

---

## Phase 5 — Competitive Quick-Check

You already have SERP data from the Phase 1a-2 WebSearch. Now **WebFetch the top
2-3 competitor URLs** from those results to get their actual content. Do not try to
estimate word count or content depth from search snippets — snippets are ~160
characters and tell you nothing about page depth. You need the real HTML.

For each fetched competitor page:
- Count the actual word count in the main content
- Note the page type and content format (blog, product, guide, listicle, etc.)
- List the H2 headings to see what subtopics they cover
- Note any SERP features they hold (featured snippet, FAQ, etc.)
- Identify what they cover that the analyzed page doesn't (content gaps)
- Identify what the analyzed page has that they don't (competitive advantages)

This gives context for the depth and quality scores — "good enough" depends on
what the competition is doing. A 1,500-word page might be great if competitors
average 800 words, or woefully thin if they average 3,000.

---

## Phase 6 — Report

Output the report in this exact format:

---

# Page SEO Analysis — [page URL]
*[date] · [GSC data: date range, or "No GSC data"]*

## Overall Score: [X.X]/10

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Search Intent Alignment | X/10 | 20% | X.X |
| E-E-A-T Signals | X/10 | 20% | X.X |
| Content Quality & Depth | X/10 | 20% | X.X |
| On-Page SEO | X/10 | 15% | X.X |
| Content Structure & UX | X/10 | 15% | X.X |
| Technical SEO | X/10 | 10% | X.X |
| **Overall** | | | **X.X** |

---

## Top Priority Fixes

3-5 specific, actionable fixes ordered by expected impact. Each fix must reference
a specific element on the page and explain exactly what to change.

**#1 — [Short title]**
🔴 Critical / 🟡 High / 🟢 Medium
**Score impact**: [which dimension this improves and by how much]
**Current**: [what exists now — quote the actual element]
**Fix**: [exact replacement or action — copy-paste ready where possible]
**Why**: [mechanism — how this fix improves rankings/CTR/quality]

*(Repeat for each fix)*

---

## E-E-A-T Breakdown

| Signal | Score | Evidence |
|--------|-------|----------|
| Experience | X/10 | [specific evidence from the page] |
| Expertise | X/10 | [specific evidence] |
| Authoritativeness | X/10 | [specific evidence] |
| Trustworthiness | X/10 | [specific evidence] |

[YMYL flag if applicable]

### E-E-A-T Gaps to Close
- [Specific gap #1 with fix]
- [Specific gap #2 with fix]

---

## Search Intent Analysis

**Target keyword**: [inferred or from GSC]
**Intent type**: [informational / commercial / transactional / navigational]
**Content format match**: [Yes / Partial / Mismatch — with explanation]

### SERP Feature Opportunities
| Feature | Optimized? | Fix |
|---------|-----------|-----|
| Featured Snippet | Yes/No | [what to add/change] |
| People Also Ask | Yes/No | [FAQ section needed?] |
| Rich Results | Yes/No | [schema needed?] |

---

## On-Page SEO Audit

### Metadata
| Element | Current | Status | Recommendation |
|---------|---------|--------|----------------|
| Title tag | "[actual title]" ([N] chars) | OK / Too long / Missing keyword | [fix] |
| Meta description | "[actual]" ([N] chars) | OK / Missing / Too short | [fix] |
| H1 | "[actual]" | OK / Missing / Duplicate | [fix] |
| Canonical | [URL] | OK / Missing / Wrong | [fix] |
| OG tags | Present / Missing | OK / Incomplete | [fix] |

### Heading Structure
```
H1: [actual]
  H2: [actual]
    H3: [actual]
  H2: [actual]
  ...
```
[Assessment: logical hierarchy? Keywords in headings? Descriptive?]

### Internal Links
Found [N] internal links. [Assessment of quality, anchor text, relevance]

| Anchor Text | Target | Quality |
|-------------|--------|---------|
| [text] | [URL] | Good / Generic / Missing |

### Images
Found [N] images.
| Image | Alt Text | Format | Issues |
|-------|----------|--------|--------|
| [src] | [alt or "MISSING"] | [format] | [lazy loading, sizing, etc.] |

---

## Content Quality Assessment

### Helpful Content Signals
| Signal | Present? | Evidence |
|--------|----------|----------|
| Clear target audience | Yes/No | [evidence] |
| Answers query completely | Yes/No | [evidence] |
| Original value added | Yes/No | [evidence] |
| Passes "Last Click" test | Yes/No | [evidence] |
| Appropriate depth | Yes/No | [word count: N] |
| First-hand knowledge | Yes/No | [evidence] |

### Content Gaps vs Competitors
| Topic/Subtopic | This Page | Competitors | Action |
|----------------|-----------|-------------|--------|
| [subtopic] | Missing / Covered | Covered by [N] of [M] | Add section |

---

## Technical SEO

| Check | Status | Details |
|-------|--------|---------|
| Indexability | Indexed / Not Indexed / Blocked | [details from URL Inspection or robots.txt] |
| Mobile Ready | Yes / Issues | [viewport, responsive, touch targets] |
| Schema Markup | [types found] / None | [appropriate? errors?] |
| Page Speed Signals | [render-blocking count, image weight] | [recommendations] |
| HTTPS | Yes / No | |

---

## GSC Performance Summary
*(Skip if no GSC data)*

| Metric | Value |
|--------|-------|
| Clicks (90d) | X |
| Impressions (90d) | X |
| Avg CTR | X% |
| Avg Position | X |
| Trend | Growing / Stable / Declining |

### Top Ranking Queries
| Query | Position | Clicks | Impressions | CTR | Expected CTR | Gap |
|-------|----------|--------|-------------|-----|-------------|-----|
| [query] | X | X | X | X% | X% | +/-X% |

---

## What to Improve Next

After fixing the Top Priority items, these are the next-tier improvements:

1. [Lower-priority improvement #1]
2. [Lower-priority improvement #2]
3. [Lower-priority improvement #3]

---

## Skill Handoffs

Based on findings, offer relevant next steps:

- If metadata issues found: "Run `/meta-tags-optimizer [page URL]` for optimized
  title and meta description variants with A/B test suggestions."
- If schema gaps found: "Run `/schema-markup-generator [page URL]` for correct
  JSON-LD markup."
- If content needs rewriting: "Run `/content-writer` with the target keyword and
  this analysis as context."
- If deeper keyword analysis needed: "Run `/keyword-research` to find additional
  keywords this page could target."
- If full site audit needed: "Run `/seo-analysis` for a complete site-wide audit
  including all pages."

---

## Report Rules

1. **Every score needs evidence.** Don't assign a 7/10 without citing what earned
   the 7 and what prevented an 8. Quote actual content from the page.
2. **Fixes must be specific.** "Improve the title tag" is useless. "Change the
   title from 'Services' to 'Dog Grooming Services in Portland — Same-Day
   Appointments | PawsVIP' (58 chars)" is actionable.
3. **Use GSC data to ground recommendations.** If you know the page ranks #7 for
   "dog grooming portland" with 1,200 impressions and 2.1% CTR, say that — and
   estimate the click gain from moving to #3.
4. **Compare to competitors.** A "good" page can still be below the bar if every
   competitor is better. Context matters.
5. **Flag the single biggest unlock.** If one change would have outsized impact
   (e.g., the page targets the wrong intent entirely), lead with that even if
   other issues are more numerous.
