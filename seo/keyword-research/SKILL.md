---
name: keyword-research
argument-hint: "<topic, niche, or seed keyword>"
description: >
  Discover, analyze, and prioritize keywords for SEO and GEO content strategies.
  Identifies high-value opportunities based on search volume, competition,
  intent, and business relevance. Generates topic clusters and content calendars.
  Use when asked to "find keywords", "keyword research", "what should I write
  about", "keyword analysis", "find me topics to write", "search volume",
  "keyword difficulty", "content ideas", or any keyword discovery task.
---

# Keyword Research



Discovers, analyzes, and prioritizes keywords for SEO and GEO content strategies. Identifies high-value opportunities based on search volume, competition, intent, and business relevance.

## When This Must Trigger

Use this when the conversation involves any of these situations — even if the user does not use SEO terminology:

Use this whenever the task needs reusable market intelligence that should influence strategy, not just an ad hoc answer.

- Starting a new content strategy or campaign
- Expanding into new topics or markets
- Finding keywords for a specific product or service
- Identifying long-tail keyword opportunities
- Understanding search intent for your industry
- Planning content calendars
- Researching keywords for GEO optimization

## What This Skill Does

1. **Keyword Discovery**: Generates comprehensive keyword lists from seed terms
2. **Intent Classification**: Categorizes keywords by user intent (informational, navigational, commercial, transactional)
3. **Difficulty Assessment**: Evaluates competition level and ranking difficulty
4. **Opportunity Scoring**: Prioritizes keywords by potential ROI
5. **Clustering**: Groups related keywords into topic clusters
6. **GEO Relevance**: Identifies keywords likely to trigger AI responses

## Quick Start

Start with one of these prompts.

### Basic Keyword Research

```
Research keywords for [topic/product/service]
```

```
Find keyword opportunities for a [industry] business targeting [audience]
```

### With Specific Goals

```
Find low-competition keywords for [topic] with commercial intent
```

```
Identify question-based keywords for [topic] that AI systems might answer
```

### Competitive Research

```
What keywords is [competitor URL] ranking for that I should target?
```

## Data Sources

> **Note:** All integrations are optional. This skill works without any API keys — users provide data manually when no tools are connected.

**With ~~SEO tool + ~~search console connected:**
Automatically pull historical search volume data, keyword difficulty scores, SERP analysis, current rankings from ~~search console, and competitor keyword overlap. The skill will fetch seed keyword metrics, related keyword suggestions, and search trend data.

**With manual data only:**
Ask the user to provide:
1. Seed keywords or topic description
2. Target audience and geographic location
3. Business goals (traffic, leads, sales)
4. Current domain authority (if known) or site age
5. Any known keyword performance data or search volume estimates

Proceed with the full analysis using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests keyword research:

1. **Understand the Context**

   Ask clarifying questions if not provided:
   - What is your product/service/topic?
   - Who is your target audience?
   - What is your business goal? (traffic, leads, sales)
   - What is your current domain authority? (new site, established, etc.)
   - Any specific geographic targeting?
   - Preferred language?

2. **Generate Seed Keywords**

   Start with:
   - Core product/service terms
   - Problem-focused keywords (what issues do you solve?)
   - Solution-focused keywords (how do you help?)
   - Audience-specific terms
   - Industry terminology

3. **Expand Keyword List**

   For each seed keyword, generate variations:
   
   ```markdown
   ## Keyword Expansion Patterns
   
   ### Modifiers
   - Best [keyword]
   - Top [keyword]
   - [keyword] for [audience]
   - [keyword] near me
   - [keyword] [year]
   - How to [keyword]
   - What is [keyword]
   - [keyword] vs [alternative]
   - [keyword] examples
   - [keyword] tools
   
   ### Long-tail Variations
   - [keyword] for beginners
   - [keyword] for small business
   - Free [keyword]
   - [keyword] software/tool/service
   - [keyword] template
   - [keyword] checklist
   - [keyword] guide
   ```

4. **Classify Search Intent**

   Categorize each keyword:

   | Intent | Signals | Example | Content Type |
   |--------|---------|---------|--------------|
   | Informational | what, how, why, guide, learn | "what is SEO" | Blog posts, guides |
   | Navigational | brand names, specific sites | "google analytics login" | Homepage, product pages |
   | Commercial | best, review, vs, compare | "best SEO tools [current year]" | Comparison posts, reviews |
   | Transactional | buy, price, discount, order | "buy SEO software" | Product pages, pricing |

5. **Assess Keyword Difficulty**

   Score each keyword (1-100 scale):

   ```markdown
   ### Difficulty Factors
   
   **High Difficulty (70-100)**
   - Major brands ranking
   - High domain authority competitors
   - Established content (1000+ backlinks)
   - Paid ads dominating SERP
   
   **Medium Difficulty (40-69)**
   - Mix of authority and niche sites
   - Some opportunities for quality content
   - Moderate backlink requirements
   
   **Low Difficulty (1-39)**
   - Few authoritative competitors
   - Thin or outdated content ranking
   - Long-tail variations
   - New or emerging topics
   ```

6. **Calculate Opportunity Score**

   Formula: `Opportunity = (Volume × Intent Value) / Difficulty`

   **Intent Value** assigns a numeric weight by search intent:
   - Informational = 1
   - Navigational = 1
   - Commercial = 2
   - Transactional = 3

   ```markdown
   ### Opportunity Matrix
   
   | Scenario | Volume | Difficulty | Intent | Priority |
   |----------|--------|------------|--------|----------|
   | Quick Win | Low-Med | Low | High | ⭐⭐⭐⭐⭐ |
   | Growth | High | Medium | High | ⭐⭐⭐⭐ |
   | Long-term | High | High | High | ⭐⭐⭐ |
   | Research | Low | Low | Low | ⭐⭐ |
   ```

7. **Identify GEO Opportunities**

   Keywords likely to trigger AI responses:
   
   ```markdown
   ### GEO-Relevant Keywords
   
   **High GEO Potential**
   - Question formats: "What is...", "How does...", "Why is..."
   - Definition queries: "[term] meaning", "[term] definition"
   - Comparison queries: "[A] vs [B]", "difference between..."
   - List queries: "best [category]", "top [number] [items]"
   - How-to queries: "how to [action]", "steps to [goal]"
   
   **AI Answer Indicators**
   - Query is factual/definitional
   - Answer can be summarized concisely
   - Topic is well-documented online
   - Low commercial intent
   ```

8. **Create Topic Clusters**

   Group keywords into content clusters:

   ```markdown
   ## Topic Cluster: [Main Topic]
   
   **Pillar Content**: [Primary keyword]
   - Search volume: [X]
   - Difficulty: [X]
   - Content type: Comprehensive guide
   
   **Cluster Content**:
   
   ### Sub-topic 1: [Secondary keyword]
   - Volume: [X]
   - Difficulty: [X]
   - Links to: Pillar
   - Content type: [Blog post/Tutorial/etc.]
   
   ### Sub-topic 2: [Secondary keyword]
   - Volume: [X]
   - Difficulty: [X]
   - Links to: Pillar + Sub-topic 1
   - Content type: [Blog post/Tutorial/etc.]
   
   [Continue for all cluster keywords...]
   ```

9. **Generate Output Report**

   Produce a report containing: Executive Summary, Top Keyword Opportunities (Quick Wins, Growth, GEO), Topic Clusters, Content Calendar, and Next Steps.

   > **Reference**: See [references/example-report.md](references/example-report.md) for the full report template and example.

## Validation Checkpoints

### Input Validation
- [ ] Seed keywords or topic description clearly provided
- [ ] Target audience and business goals specified
- [ ] Geographic and language targeting confirmed
- [ ] Domain authority or site maturity level established

### Output Validation
- [ ] Every recommendation cites specific data points (not generic advice)
- [ ] Search volume and difficulty scores included for each keyword
- [ ] Keywords grouped by intent and mapped to content types
- [ ] Topic clusters show clear pillar-to-cluster relationships
- [ ] Source of each data point clearly stated (~~SEO tool data, user-provided, or estimated)

## Example

> **Reference**: See [references/example-report.md](references/example-report.md) for a complete example report for "project management software for small businesses".

### Advanced Usage

- **Intent Mapping**: `Map all keywords for [topic] by search intent and funnel stage`
- **Seasonal Analysis**: `Identify seasonal keyword trends for [industry]`
- **Competitor Gap**: `What keywords do [competitor 1], [competitor 2] rank for that I'm missing?`
- **Local Keywords**: `Research local keywords for [business type] in [city/region]`

## Tips for Success

1. **Start with seed keywords** that describe your core offering
2. **Don't ignore long-tail** - they often have highest conversion rates
3. **Match content to intent** - informational queries need guides, not sales pages
4. **Group into clusters** for topical authority
5. **Prioritize quick wins** to build momentum and credibility
6. **Include GEO keywords** in your strategy for AI visibility
7. **Review quarterly** - keyword dynamics change over time



## Reference Materials

- [Keyword Intent Taxonomy](references/keyword-intent-taxonomy.md) — Complete intent classification with signal words and content strategies
- [Topic Cluster Templates](references/topic-cluster-templates.md) — Hub-and-spoke architecture templates for pillar and cluster content
- [Keyword Prioritization Framework](references/keyword-prioritization-framework.md) — Priority scoring matrix, categories, and seasonal keyword patterns
- [Example Report](references/example-report.md) — Complete example keyword research report for project management software

## Next Best Skill

- **Primary**: [content-writer](../content-writer/SKILL.md) — turn keyword opportunities into optimized content.
