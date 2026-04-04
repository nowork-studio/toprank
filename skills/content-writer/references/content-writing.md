# Content Writing Guidelines — Google Best Practices

Reference for writing content that ranks. Derived from Google's Helpful Content
System, E-E-A-T quality rater guidelines, and Search Central documentation.

---

## Table of Contents

1. [E-E-A-T Framework](#e-e-a-t-framework)
2. [Helpful Content Signals](#helpful-content-signals)
3. [Blog Posts](#blog-posts)
4. [Landing Pages](#landing-pages)
5. [Search Intent Matching](#search-intent-matching)
6. [On-Page SEO Checklist](#on-page-seo-checklist)
7. [Anti-Patterns](#anti-patterns)

---

## E-E-A-T Framework

Google evaluates content on four axes:

### Experience
- Show first-hand experience — specific examples, scenarios, case studies
- Use language that reflects direct involvement ("we found", "in our testing")
- Reference real data, outcomes, or results

### Expertise
- Go beyond surface-level — cover edge cases only a practitioner would know
- Use precise terminology correctly but define it for the reader
- Link to authoritative sources for factual claims

### Authoritativeness
- Establish why this source is credible on this topic
- Include author bios with relevant credentials
- Build topical authority via internal linking to related content

### Trustworthiness
- Be transparent about limitations and conflicts of interest
- Cite sources for statistics and claims
- Keep content accurate and up to date

**YMYL topics** (health, finance, safety, legal) require the highest E-E-A-T bar.

---

## Helpful Content Signals

### Content IS helpful when it:
- Has a clear, specific audience in mind
- Leaves the reader feeling they've learned enough to achieve their goal
- Provides original value — analysis, insight, research, not just compilation
- Has a satisfying amount of information (not thin, not padded)

### The "Last Click" Test
After reading, would the reader need to search again? If yes, the content isn't
done. The goal is to be the last click.

---

## Blog Posts

### When to Use
Informational and commercial-investigation intent: "how to", "what is", "best X",
"X vs Y", guides, tutorials, listicles, reviews.

### Structure
```
H1: Primary topic (one per page, includes primary keyword)
  H2: Major section (answer core question first — don't bury the lead)
    H3: Supporting detail
  H2: Practical examples / case studies
  H2: Common mistakes
  H2: FAQ (targets People Also Ask)
```

### Writing Rules
1. **Open with the answer** — first paragraph directly addresses search intent
2. **Show experience** — specific examples, data, "we found that..." language
3. **Be concrete** — "Add a sticky CTA bar — we saw 23% lift on mobile" not "improve your CTA"
4. **Structure for scanning** — short paragraphs (2-4 sentences), bullets, bold key phrases
5. **Link internally** — 3-5 related pages, descriptive anchor text
6. **Cite sources** — link to data sources and authoritative references
7. **Write to completeness, not word count** — cover the topic fully, then stop

### Keyword Placement
- Title tag (front-loaded, < 60 chars)
- H1
- First 100 words
- 1-2 H2 headings naturally
- Meta description (120-160 chars)
- After that: synonyms and natural language — no stuffing

### Required Sections
1. Opening hook — state the problem, signal you'll answer concretely
2. Core content — main answer with clear H2/H3 structure
3. Practical examples — at least one real scenario
4. Common mistakes — what people get wrong
5. Next steps / CTA
6. FAQ (3-5 questions targeting related searches)

### Metadata
- **Title tag:** < 60 chars, keyword front-loaded, includes value prop
- **Meta description:** 120-160 chars, keyword + reason to click
- **URL slug:** short, readable, keyword-rich. `/blog/optimize-title-tags`
- **Structured data:** `Article` or `BlogPosting`; add `HowTo` for tutorials, `FAQPage` for FAQ sections

---

## Landing Pages

### When to Use
Transactional and commercial intent: "buy", "pricing", "near me", "[service] in
[city]", "best [product] for [use case]".

### Core Principles
1. **Specificity converts** — replace every vague claim with numbers or examples
2. **Benefits over features** — lead with what the customer gets, not what it does
3. **Address objections directly** — price, trust, switching costs, "does it work?"
4. **One page, one job** — every element moves toward the CTA
5. **Social proof is mandatory** — testimonials, logos, stats, case studies

### Structure by Page Type

**Service page:**
```
H1: Service + Primary Benefit
Hero subhead + Primary CTA
H2: The Problem (show you understand their situation)
H2: How It Works (3-4 clear steps)
H2: Results (specific outcomes with numbers)
H2: Social Proof (testimonials, logos, case studies)
H2: Pricing (if applicable)
H2: FAQ (5-8 objection-handling questions)
Final CTA
```

**Product page:**
```
H1: Product + Key Benefit
Hero + CTA
H2: Features → Benefits (not just feature lists)
H2: How It Works
H2: Who It's For (specific use cases)
H2: Reviews / Social Proof
H2: Pricing
H2: FAQ
Final CTA
```

**Location page:**
```
H1: [Service] in [City]
Local value prop + CTA
H2: Local-specific content (NOT generic copy with city swapped)
H2: Why Choose Us in [City] (local presence, case studies)
H2: Service Areas
H2: FAQ (local-specific concerns)
CTA with local contact
```

### SEO for Landing Pages
- Lighter keyword density than blog posts
- Primary keyword in: title, H1, first paragraph, 1 H2, meta description
- 500-1500 words of genuine content (thin pages with just a headline + form don't rank)
- FAQ section serves dual purpose: conversion (objection handling) + SEO (long-tail queries)

### Metadata
- **Title tag:** "[Service/Product] — [Benefit] | [Brand]" (< 60 chars)
- **Meta description:** 120-160 chars, includes CTA ("Get started free", "See pricing")
- **URL slug:** `/[service-name]`, `/products/[product-name]`, `/[service]-[city]`
- **Structured data:** Service page → `Service` + `FAQPage`; Product → `Product` + `Offer` + `FAQPage`; Local → `LocalBusiness` + `FAQPage`

---

## Search Intent Matching

| Intent | Keyword Signals | Content Type |
|--------|----------------|-------------|
| **Informational** | "how to", "what is", "guide" | Blog post, tutorial |
| **Commercial** | "best", "vs", "review", "top" | Comparison, listicle |
| **Transactional** | "buy", "price", "near me" | Landing/product page |
| **Navigational** | brand name, product name | Homepage, product page |

**How to verify:** search the keyword incognito, look at top 5 results. Match
that format — don't fight the SERP.

**Mismatch = won't rank:**
- Blog post targeting "buy [product]" → should be product page
- Product page targeting "how to [task]" → should be tutorial
- Generic page targeting "[service] in [city]" → should be location page

---

## On-Page SEO Checklist

### Must-Have
- [ ] Title tag with primary keyword, < 60 chars
- [ ] Meta description with keyword + CTA, 120-160 chars
- [ ] Single H1 with primary keyword
- [ ] Logical heading hierarchy (H1 → H2 → H3)
- [ ] Primary keyword in first 100 words naturally
- [ ] Internal links to 3-5 related pages
- [ ] Images have descriptive alt text
- [ ] URL is short, readable, includes keyword slug

### Should-Have
- [ ] Structured data (Article, Product, Service, HowTo, FAQPage)
- [ ] Table of contents for long content (> 1500 words)
- [ ] External links to authoritative sources
- [ ] Author byline with credentials
- [ ] Last-updated date for evergreen content
- [ ] Open Graph + Twitter Card meta tags

---

## Anti-Patterns

### Content Anti-Patterns
- **Keyword stuffing** — use the keyword naturally; synonyms after the first few placements
- **Thin content** — pages under 300 words competing for hard terms
- **Content for content's sake** — topics with no real expertise behind them
- **Wall of text** — no headings, no lists, no visual breaks
- **Duplicate intent** — two pages targeting same keyword = cannibalization
- **Stale content** — outdated stats, deprecated methods, old pricing

### AI Content Anti-Patterns
Google doesn't penalize AI content per se — it penalizes unhelpful content.
Common AI failure modes:
- Generic summaries restating common knowledge
- Excessive hedging ("it depends", "many factors") without commitments
- Missing experience signals — no examples, data, or first-hand knowledge
- Perfect grammar, zero original insight

**Fix:** inject real data, specific examples, original analysis, concrete
recommendations. Make it something only someone with actual expertise could write.
