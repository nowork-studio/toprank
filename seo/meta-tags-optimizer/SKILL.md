---
name: meta-tags-optimizer
argument-hint: "<URL or page title to optimize>"
description: >
  Optimize title tags, meta descriptions, Open Graph, and Twitter cards for
  maximum click-through rate. Generates multiple A/B test variations with
  character counting and SERP preview. Use when asked to "optimize title tag",
  "write meta description", "improve CTR", "Open Graph tags", "fix my meta
  tags", "social media preview", "my click rate is low", "title optimization",
  or any meta tag task.
---

# Meta Tags Optimizer

This skill creates compelling, optimized meta tags that improve click-through rates from search results and enhance social media sharing. It covers title tags, meta descriptions, and social meta tags.

## When This Must Trigger

Use this when the conversation involves any of these situations — even if the user does not use SEO terminology:

Use this whenever the task needs a shippable asset or transformation that should feed directly into quality review, deployment, or monitoring.

- Creating meta tags for new pages
- Optimizing existing meta tags for better CTR
- Preparing pages for social media sharing
- Fixing duplicate or missing meta tags
- A/B testing title and description variations
- Optimizing for specific SERP features
- Creating meta tags for different page types

## What This Skill Does

1. **Title Tag Creation**: Writes compelling, keyword-optimized titles
2. **Meta Description Writing**: Creates click-worthy descriptions
3. **Open Graph Optimization**: Prepares pages for social sharing
4. **Twitter Card Setup**: Optimizes Twitter-specific meta tags
5. **CTR Analysis**: Suggests improvements for better click rates
6. **Character Counting**: Ensures proper length for SERP display
7. **A/B Test Suggestions**: Provides variations for testing

## Quick Start

Start with one of these prompts.

### Create Meta Tags

```
Create meta tags for a page about [topic] targeting [keyword]
```

```
Write title and meta description for this content: [content/URL]
```

### Optimize Existing Tags

```
Improve these meta tags for better CTR: [current tags]
```

### Social Media Tags

```
Create Open Graph and Twitter card tags for [page/URL]
```

## Data Sources

**With ~~search console + ~~SEO tool connected:**
Automatically pull current meta tags, CTR data by query, competitor title/description patterns, SERP preview data, and impression/click metrics to identify optimization opportunities.

**With manual data only:**
Ask the user to provide:
1. Current title and meta description (if optimizing existing)
2. Target primary keyword and 2-3 secondary keywords
3. Page URL and main content/value proposition
4. Competitor URLs or examples of well-performing titles in the SERP

Proceed with the full workflow using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests meta tag optimization:

1. **Gather Page Information**

   ```markdown
   ### Page Analysis
   
   **Page URL**: [URL]
   **Page Type**: [blog/product/landing/service/homepage]
   **Primary Keyword**: [keyword]
   **Secondary Keywords**: [keywords]
   **Target Audience**: [audience]
   **Primary CTA**: [action you want users to take]
   **Unique Value Prop**: [what makes this page special]
   ```

2. **Create Optimized Title Tag**

   ```markdown
   ### Title Tag Optimization
   
   **Requirements**:
   - Length: 50-60 characters (displays fully in SERP)
   - Include primary keyword (preferably near front)
   - Make it compelling and click-worthy
   - Match search intent
   - Include brand name if appropriate
   
   **Title Tag Formula Options**:
   
   1. **Keyword | Benefit | Brand**
      "[Primary Keyword]: [Benefit] | [Brand Name]"
      
   2. **Number + Keyword + Promise**
      "[Number] [Keyword] That [Promise/Result]"
      
   3. **How-to Format**
      "How to [Keyword]: [Benefit/Result]"
      
   4. **Question Format**
      "What is [Keyword]? [Brief Answer/Hook]"
      
   5. **Year + Keyword**
      "[Keyword] in [Year]: [Hook/Update]"
   
   **Generated Title Options**:
   
   | Option | Title | Length | Power Words | Keyword Position |
   |--------|-------|--------|-------------|------------------|
   | 1 | [Title] | [X] chars | [words] | [Front/Middle] |
   | 2 | [Title] | [X] chars | [words] | [Front/Middle] |
   | 3 | [Title] | [X] chars | [words] | [Front/Middle] |
   
   **Recommended**: Option [X]
   **Reasoning**: [Why this option is best]
   
   **Title Tag Code**:
   ```html
   <title>[Selected Title]</title>
   ```
   ```

3. **Write Meta Description**

   ```markdown
   ### Meta Description Optimization
   
   **Requirements**:
   - Length: 150-160 characters (displays fully in SERP)
   - Include primary keyword naturally
   - Include clear call-to-action
   - Match page content accurately
   - Create urgency or curiosity
   - Avoid duplicate descriptions
   
   **Meta Description Formula**:
   
   [What the page offers] + [Benefit to user] + [Call-to-action]
   
   **Power Elements to Include**:
   - Numbers and statistics
   - Current year
   - Emotional triggers
   - Action verbs
   - Unique value proposition
   
   **Generated Description Options**:
   
   | Option | Description | Length | CTA | Emotional Trigger |
   |--------|-------------|--------|-----|-------------------|
   | 1 | [Description] | [X] chars | [CTA] | [Trigger] |
   | 2 | [Description] | [X] chars | [CTA] | [Trigger] |
   | 3 | [Description] | [X] chars | [CTA] | [Trigger] |
   
   **Recommended**: Option [X]
   **Reasoning**: [Why this option is best]
   
   **Meta Description Code**:
   ```html
   <meta name="description" content="[Selected Description]">
   ```
   ```

4. **Create Open Graph, Twitter Card, and Additional Meta Tags**

   Generate OG tags (og:type, og:url, og:title, og:description, og:image), Twitter Card tags, canonical URL, robots, viewport, author, and article-specific tags. Then combine into a complete meta tag block.

   > **Reference**: See [references/meta-tag-code-templates.md](references/meta-tag-code-templates.md) for OG type selection guide, Twitter card type selection, all HTML code templates, and the complete meta tag block template.

5. **CORE-EEAT Alignment Check**

   Verify meta tags align with content quality standards (CORE-EEAT Benchmark).

   ```markdown
   ### CORE-EEAT Meta Tag Alignment

   | Check | Status | Notes |
   |-------|--------|-------|
   | **C01 Intent Alignment**: Title promise matches actual content delivery | ✅/⚠️/❌ | [Does the title accurately represent what the page delivers?] |
   | **C02 Direct Answer**: Meta description reflects the core answer available in first 150 words | ✅/⚠️/❌ | [Does the description preview the direct answer?] |

   **If C01 fails**: Title is misleading — rewrite to match actual content.
   **If C02 fails**: Content may need restructuring to front-load the answer, or description should better reflect available content.
   ```

9. **Provide CTR Optimization Tips**

   ```markdown
   ## CTR Optimization Analysis

   ### Power Words Used
   - [Word 1] - Creates [emotion/action]
   - [Word 2] - Creates [emotion/action]

   ### CTR Boosting Elements

   | Element | Present | Impact |
   |---------|---------|--------|
   | Numbers | Yes/No | +20-30% CTR |
   | Current Year | Yes/No | +15-20% CTR |
   | Power Words | Yes/No | +10-15% CTR |
   | Question | Yes/No | +10-15% CTR |
   | Brackets | Yes/No | +10% CTR |

   ### A/B Test Suggestions

   Test these variations:

   **Version A** (Current):
   - Title: [Title]
   - Description: [Description]

   **Version B** (Test):
   - Title: [Alternative title]
   - Description: [Alternative description]
   - Hypothesis: [Why this might perform better]
   ```

## Validation Checkpoints

### Input Validation
- [ ] Primary keyword confirmed and matches page content
- [ ] Page type identified (blog/product/landing/service/homepage)
- [ ] Target audience and search intent clearly defined
- [ ] Unique value proposition articulated

### Output Validation
- [ ] Title length 50-60 characters (displays fully in SERP)
- [ ] Meta description length 150-160 characters
- [ ] Primary keyword appears in both title and description
- [ ] Open Graph image specified (1200x630px recommended)
- [ ] All HTML syntax valid (no unclosed quotes or tags)
- [ ] Source of each data point clearly stated (~~search console CTR data, ~~SEO tool competitor data, user-provided, or estimated)

## Example

**User**: "Create meta tags for a blog post about 'how to start a podcast in [current year]'"

**Output**:

```markdown
## Meta Tags: How to Start a Podcast ([current year])

### Title Tag
```html
<title>How to Start a Podcast in [current year]: Complete Beginner's Guide</title>
```
**Length**: ~55 characters ✅
**Keyword**: "how to start a podcast" at front ✅
**Power Words**: "Complete", "Beginner's" ✅

### Meta Description
```html
<meta name="description" content="Learn how to start a podcast in [current year] with our step-by-step guide. Covers equipment, hosting, recording, and launching your first episode. Start podcasting today!">
```
**Length**: ~163 characters ✅
**Keyword**: Included naturally ✅
**CTA**: "Start podcasting today!" ✅

_Complete meta tag block (with OG, Twitter, Article tags) generated using template from [references/meta-tag-code-templates.md](references/meta-tag-code-templates.md)._

### A/B Test Variations

**Title Variation B**:
"Start a Podcast in [current year]: Step-by-Step Guide (+ Free Checklist)"

**Title Variation C**:
"How to Start a Podcast: [current year] Guide [Equipment + Software + Tips]"

**Description Variation B**:
"Want to start a podcast in [current year]? This guide covers everything: equipment ($100 budget option), best hosting platforms, recording tips, and how to get your first 1,000 listeners."
```

## Tips for Success

1. **Front-load keywords** - Put important terms at the beginning
2. **Match intent** - Description should preview what page delivers
3. **Be specific** - Vague descriptions get ignored
4. **Test variations** - Small changes can significantly impact CTR
5. **Update regularly** - Add current year, refresh messaging
6. **Check competitors** - See what's working in your SERP


## Reference Materials

- [Meta Tag Formulas](references/meta-tag-formulas.md) — Proven title and description formulas
- [CTR and Social Reference](references/ctr-and-social-reference.md) — Page-type templates, CTR data, OG best practices

## Next Best Skill

- **Primary**: [schema-markup-generator](../schema-markup-generator/SKILL.md) — complete the SERP packaging with structured data.
