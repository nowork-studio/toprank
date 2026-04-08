# Content Quality Evaluation Framework

Industry-standard framework for evaluating a single page's SEO content quality.
Combines Google's E-E-A-T quality rater guidelines, Helpful Content System signals,
and on-page SEO best practices into a structured scoring system.

---

## Table of Contents

1. [Scoring System](#scoring-system)
2. [E-E-A-T Evaluation](#e-e-a-t-evaluation)
3. [Helpful Content Signals](#helpful-content-signals)
4. [On-Page SEO Factors](#on-page-seo-factors)
5. [Content Structure & Readability](#content-structure--readability)
6. [Search Intent Alignment](#search-intent-alignment)
7. [Technical SEO Signals](#technical-seo-signals)
8. [Content Freshness & Depth](#content-freshness--depth)

---

## Scoring System

Each dimension is scored 0-10. The overall page score is a weighted average:

| Dimension | Weight | Why |
|-----------|--------|-----|
| Search Intent Alignment | 20% | Wrong intent = won't rank, regardless of quality |
| E-E-A-T Signals | 20% | Google's core quality framework |
| Content Quality & Depth | 20% | Determines if the page satisfies the query |
| On-Page SEO | 15% | Technical ranking signals |
| Content Structure & UX | 15% | Readability, engagement, time-on-page |
| Technical SEO | 10% | Page speed, mobile, schema — table stakes |

**Score interpretation:**
- 9-10: Excellent on-page quality — competitive for top 3 *if domain authority supports it*
- 7-8: Good — some gaps to close for top positions
- 5-6: Average — multiple issues holding back rankings
- 3-4: Below average — significant rework needed
- 0-2: Poor — fundamental problems

**Scoring discipline — avoid the "average trap":**
Most pages are NOT 5-7. A generic auto-generated page with no E-E-A-T signals,
thin content, and boilerplate meta descriptions is a 2-3, not a 5. A well-written
expert guide with original data, proper schema, and strong internal linking is an
8-9, not a 7. Use the full range. If you find yourself scoring everything 5-7,
you are not differentiating — re-read the criteria for each score level.

**Calibration anchors:**
- **2/10 page**: Auto-generated city landing page with template text, no author,
  no unique content, missing meta description, no schema, stock images
- **5/10 page**: Decent blog post that covers the topic but adds no original
  insight, has basic metadata, no author bio, no citations, no schema
- **8/10 page**: Expert guide with original data/examples, author with credentials,
  comprehensive coverage, proper schema, optimized title targeting real queries,
  strong internal linking to related content
- **10/10 page**: Industry-defining resource: original research, cited by others,
  perfect technical execution, featured snippets owned, rich results active

**Important limitation:** This framework evaluates **on-page quality only.** It
does not measure off-page factors (backlinks, domain authority, brand signals)
which account for roughly half of ranking ability. A 10/10 on-page score on a
brand-new domain will not rank for competitive terms. Always note this in the
report — recommend backlink/DR analysis separately if the user asks about ranking
potential.

---

## E-E-A-T Evaluation

### Experience (0-10)
| Score | Criteria |
|-------|----------|
| 9-10 | First-hand experience clearly demonstrated: specific examples, real data, case studies, "we tested/built/used" language, original screenshots/photos |
| 7-8 | Some experience signals: references to practical scenarios, industry-specific language that implies hands-on knowledge |
| 5-6 | Generic content that could be written without experience — compilation of publicly available information |
| 3-4 | No experience signals — reads like a summary of other articles |
| 0-2 | Contradicts practical experience or contains factual errors a practitioner would catch |

**What to check:**
- Does the page contain specific examples from real use?
- Are there original data points, screenshots, or case studies?
- Does the language reflect direct involvement? ("we found", "in practice", "after testing")
- Is there information only someone with hands-on experience would know?

### Expertise (0-10)
| Score | Criteria |
|-------|----------|
| 9-10 | Deep subject matter expertise — covers edge cases, nuances, caveats only an expert would know; uses technical terms correctly and explains them |
| 7-8 | Solid knowledge demonstrated — goes beyond surface-level, handles complexity |
| 5-6 | Surface-level coverage — accurate but doesn't go deeper than a basic search |
| 3-4 | Shallow — misses important nuances, oversimplifies complex topics |
| 0-2 | Inaccurate or misleading information |

**What to check:**
- Does the content cover edge cases and exceptions?
- Are technical terms used correctly and explained?
- Does it go beyond what the top 3 search results already say?
- Would a subject matter expert find errors or omissions?

### Authoritativeness (0-10)
| Score | Criteria |
|-------|----------|
| 9-10 | Clear authority: author bio with credentials, the site is a recognized source on this topic, strong internal linking shows topical depth |
| 7-8 | Good authority signals: author identified, some credentials, site covers the topic area across multiple pages |
| 5-6 | Minimal authority: no author identified, or author has no visible credentials for this topic |
| 3-4 | Weak authority: the site has no other content on this topic, isolated page with no context |
| 0-2 | No authority signals whatsoever |

**What to check:**
- Is there an author byline with relevant credentials?
- Does the site have other content on this topic (topical authority)?
- Are there internal links to/from related pages?
- Do external authoritative sources link to this content?

### Trustworthiness (0-10)
| Score | Criteria |
|-------|----------|
| 9-10 | Highly trustworthy: sources cited for claims, transparent about limitations, no conflicts of interest, secure site, clear contact info |
| 7-8 | Trustworthy: most claims sourced, content is accurate and current |
| 5-6 | Adequate: some claims unsourced, content generally accurate |
| 3-4 | Low trust: unsourced claims, potentially outdated, no transparency |
| 0-2 | Untrustworthy: misleading, deceptive, or harmful content |

**What to check:**
- Are statistics and claims backed by sources?
- Is the content up to date?
- Are limitations and conflicts disclosed?
- Does the page have HTTPS, contact info, privacy policy?

### YMYL Detection
Flag if the page covers YMYL (Your Money or Your Life) topics:
- Health and medical information
- Financial advice or transactions
- Legal information
- Safety information
- News and current events that impact civic life

YMYL pages require the highest E-E-A-T bar — a 7/10 on a YMYL page is effectively
a failing grade. Note this in the report with specific E-E-A-T gaps to close.

---

## Helpful Content Signals

### Positive Signals (check each)
- [ ] Has a clear, specific target audience — not "everyone"
- [ ] Answers the search query directly and completely
- [ ] Provides original value: analysis, insight, data — not just compilation
- [ ] Leaves the reader satisfied (the "last click" test)
- [ ] Written for humans first, search engines second
- [ ] Has a satisfying depth — not thin, not padded
- [ ] Demonstrates first-hand knowledge of the topic

### Negative Signals (flag each found)
- [ ] Content exists primarily to attract search traffic, not serve users
- [ ] Summarizes others' content without adding value
- [ ] Uses excessive hedging ("it depends", "many factors") without commitments
- [ ] Covers a topic outside the site's core expertise
- [ ] Leaves the reader needing to search again
- [ ] Feels automated or mass-produced
- [ ] Promises an answer in the title but doesn't deliver

### The "Last Click" Test
Ask: after reading this page, would the searcher need to go back to Google and
try another result? If yes, the content fails regardless of other signals.

---

## On-Page SEO Factors

### Title Tag (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Length | 50-60 chars | Over 60 (truncation) or under 30 (wasted opportunity) |
| Keyword | Primary keyword present, front-loaded | Missing primary keyword or buried at end |
| Intent match | Title matches search intent type | Informational title for transactional query or vice versa |
| Uniqueness | Unique across site | Duplicate title found on other pages |
| CTR appeal | Power words, value prop, brand | Generic or boring (e.g., just "Services") |

### Meta Description (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Length | 120-160 chars | Missing entirely, under 70, or over 160 |
| Keyword | Contains primary keyword | Missing keyword |
| CTA | Has call-to-action or compelling reason to click | Passive description |
| Uniqueness | Unique across site | Duplicate meta description |

### Headings (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| H1 | Single H1, contains primary keyword | Multiple H1s, missing H1, or keyword-less H1 |
| Hierarchy | Logical H1 > H2 > H3, no skipped levels | Skipping from H1 to H3, or random heading levels |
| Keywords | Primary/secondary keywords in 1-2 H2s naturally | Keyword-stuffed headings or no keywords |
| Descriptive | Headings summarize section content | Vague headings ("More info", "Details") |

### Internal Linking (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Count | 3-10 for short content; scale with page length and type | Zero internal links, or excessive relative to content length (not a fixed cap — e-commerce and pillar pages legitimately have 30-50+) |
| Anchor text | Descriptive, keyword-relevant | "Click here", "Read more", or naked URLs |
| Relevance | Links to topically related pages | Random unrelated pages |
| Reciprocal | Related pages link back to this page | Orphan page (no inbound internal links) |

### External Linking (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Sources | Links to authoritative sources for claims | No citations for factual claims |
| Quality | Links go to reputable domains | Links to low-quality or spammy sites |
| Rel attrs | Appropriate use of nofollow where needed | Missing nofollow on paid/sponsored links |

### Image Optimization (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Alt text | Descriptive alt text on all images | Missing alt text, or alt="image" |
| Format | WebP/AVIF for photos, SVG for icons | Unoptimized JPEG/PNG |
| Size | Properly sized for display (not 3000px in 400px container) | Oversized images |
| Lazy loading | Images below fold use loading="lazy" | All images eager-loaded |

### URL Structure (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Readable | Short, keyword-rich slug (`/blog/seo-title-tags`) | Long, parameter-heavy, or meaningless URLs |
| Depth | 2-3 levels from root | Deeply nested (>4 levels) |
| Consistency | Follows site-wide URL pattern | Inconsistent with rest of site |

---

## Content Structure & Readability

### Readability Score (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Paragraph length | 2-4 sentences per paragraph | Wall-of-text blocks (>6 sentences) |
| Sentence length | Varied, mostly 15-25 words | Consistently long (>30 words) or robotic uniformity |
| Vocabulary | Matches audience level | Jargon without explanation, or oversimplified |
| Scanning | Bold key phrases, bullets, numbered lists | No formatting aids in long content |

### Content UX (0-10)
| Factor | Ideal | Penalty for |
|--------|-------|-------------|
| Above the fold | Value immediately visible | Hero image with no text, or walls of navigation |
| Visual breaks | Images, tables, callouts every 300-500 words | Text-only for >1000 words |
| Table of contents | Present for content >1500 words | Long content with no TOC |
| Mobile UX | Readable on mobile without zoom/scroll issues | Broken tables, tiny text, horizontal scroll |

---

## Search Intent Alignment

### Intent Classification
| Intent Type | Keyword Signals | Expected Content Format |
|-------------|----------------|------------------------|
| Informational | "how to", "what is", "guide", "tutorial" | Blog post, guide, tutorial with depth |
| Commercial Investigation | "best", "vs", "review", "top", "compare" | Comparison, listicle, review |
| Transactional | "buy", "price", "near me", "order", "signup" | Product/service page with CTA |
| Navigational | brand name, product name | Homepage, specific product page |

### Alignment Score (0-10)
| Score | Criteria |
|-------|----------|
| 9-10 | Content format perfectly matches intent — blog for informational, product page for transactional, comparison for commercial |
| 7-8 | Content mostly matches but has minor format issues (e.g., informational content that's too thin for the query depth) |
| 5-6 | Partial mismatch — content addresses the topic but in the wrong format |
| 3-4 | Significant mismatch — e.g., a blog post trying to rank for "buy [product]" |
| 0-2 | Complete mismatch — content has nothing to do with the search intent |

### SERP Feature Alignment
Check if the page is optimized for relevant SERP features:
- **Featured snippet**: Is the answer formatted for extraction (definition, list, table)?
- **People Also Ask**: Does the page have FAQ/question-answer sections?
- **Video carousel**: Is there video content if competitors have it?
- **Image pack**: Are images optimized with alt text for image search?
- **Local pack**: Does the page have LocalBusiness schema if targeting local queries?

---

## Technical SEO Signals

### Core Web Vitals Proxies (from HTML analysis)
- Render-blocking resources in `<head>` (CSS/JS not deferred)
- Total estimated page weight (images, scripts, stylesheets)
- DOM complexity (excessive nesting, large node count)
- Third-party script count and domains

### Mobile Readiness
- Viewport meta tag present
- Responsive design indicators
- Touch target sizes (buttons/links too small)
- Font sizes readable without zoom

### Schema Markup
- Appropriate JSON-LD for page type
- Required fields present
- No errors in existing schema

### Security & Trust Signals
- HTTPS
- No mixed content
- Privacy policy / terms linked

---

## Content Freshness & Depth

### Freshness (0-10)
| Factor | What to Check |
|--------|--------------|
| Publication date | Is there a visible publish/update date? |
| Content currency | Are statistics, links, and references current? |
| Broken references | Do outbound links still work? |
| Industry currency | Does the content reflect current best practices? |
| Competitors | Is this content more or less fresh than top-ranking competitors? |

### Depth Score (0-10)
| Factor | What to Check |
|--------|--------------|
| Comprehensiveness | Does it cover the topic fully vs top competitors? |
| Word count | Appropriate for the topic (not inflated, not thin) |
| Subtopics | Are important subtopics addressed? |
| Unique value | What does this page offer that competitors don't? |
| Follow-up coverage | Does it anticipate and answer follow-up questions? |
