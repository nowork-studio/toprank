# Toprank

**SEO that reads your data, tells you what's wrong, and fixes it.**

Toprank gives Claude direct access to your Google Search Console and Google Ads data. Run it inside your website repo and it doesn't just analyze — it rewrites your meta tags, fixes your headings, adds structured data, and ships the changes.

> *"Why did my traffic drop last month?"*
> *"What keywords am I almost ranking for?"*
> *"Fix my title tags for pages losing clicks."*

Free, open-source skill for Claude Code and Codex. Install in 30 seconds.

---

## See It Work

```
You:    /seo-analysis

Claude: Found your site at mystore.com — pulling Search Console data now.

        [90 days of real traffic data loaded]
        [pages crawled for technical issues]

        Three things hurting you most:

        Your homepage lives at two addresses. Google splits your ranking
        power between them. Easy fix.

        Two pages targeting the same search terms — they compete against
        each other and neither wins.

        One page gets 400 monthly impressions but ranks #52. The title
        doesn't match what people actually search for.

        Here's your 30-day plan, most impactful first.

You:    Implement all of it.

        [fixes duplicate homepage — 2 lines of config]
        [consolidates competing pages, updates all internal links]
        [rewrites page titles to match real search queries]

        Done. Ready to ship.
```

---

## Skills

### [`seo-analysis`](seo-analysis/) — SEO Audit & Search Console Analysis

A full SEO audit in one command. Connects to Google Search Console, auto-detects your site, and produces a prioritized action plan.

**What it does:**
- Guides you through GSC API setup if needed (one `gcloud` command)
- Auto-detects your site URL if you're inside a website repo
- Pulls 90 days of query/page performance data
- Surfaces **quick wins**: position 4–10 queries, high-impression low-CTR pages
- Flags **traffic drops** with period-over-period comparison
- **Technical audit**: indexability, meta tags, headings, structured data, canonical URLs
- Outputs a structured report with a 30-day action plan

**How to trigger:**
> "analyze my SEO", "SEO audit", "why is my traffic down", "what keywords am I ranking for", "check my search console", "improve my rankings", "technical SEO audit"

### [`content-writer`](content-writer/) — SEO Content Creation

Write blog posts, landing pages, or improve existing content following Google's E-E-A-T and Helpful Content guidelines. Works standalone or spawned automatically by `seo-analysis` when content gaps are found.

**What it does:**
- Determines content type from context (blog post, landing page, or content improvement)
- Researches search intent and SERP landscape before writing
- Produces publication-ready content with SEO metadata, JSON-LD structured data, and internal linking plan
- Quality gate checks: "last click" test, E-E-A-T signals, anti-pattern detection
- When spawned by `seo-analysis`, writes multiple pieces in parallel for identified content gaps

**How to trigger:**
> "write a blog post about X", "create a landing page for Y", "improve this page", "content for keyword X", "draft an article", "rewrite this page"

### [`keyword-research`](keyword-research/) — Keyword Discovery & Analysis

Discover high-value keywords, assess difficulty, classify search intent, and build topic clusters. Works standalone or feeds directly into `content-writer`.

**What it does:**
- Generates keyword lists from seed terms with long-tail variations
- Classifies search intent (informational, navigational, commercial, transactional)
- Scores keyword difficulty and calculates opportunity (volume × intent / difficulty)
- Groups keywords into topic clusters with pillar/cluster relationships
- Identifies GEO-relevant keywords likely to trigger AI responses
- Produces a prioritized content calendar

**How to trigger:**
> "keyword research", "find keywords", "what should I write about", "keyword analysis", "content ideas", "search volume", "keyword difficulty"

### [`meta-tags-optimizer`](meta-tags-optimizer/) — Title Tags, Meta Descriptions & Social Tags

Create and optimize meta tags for better click-through rates in search results and social sharing.

**What it does:**
- Writes compelling title tags (50–60 chars) with keyword placement and power words
- Creates meta descriptions (150–160 chars) with clear CTAs
- Generates Open Graph and Twitter Card tags for social previews
- Provides multiple A/B test variations with CTR impact estimates
- Validates character lengths for proper SERP display

**How to trigger:**
> "optimize title tag", "write meta description", "improve CTR", "Open Graph tags", "fix my meta tags", "social media preview", "my click rate is low"

### [`schema-markup-generator`](schema-markup-generator/) — JSON-LD Structured Data

Generate valid JSON-LD schema markup for rich results in Google Search.

**What it does:**
- Selects appropriate schema types based on content (FAQ, HowTo, Article, Product, LocalBusiness, etc.)
- Generates ready-to-paste JSON-LD with all required properties
- Handles complex multi-type schemas on a single page
- Provides SERP preview showing expected rich result appearance
- Includes validation guidance and implementation instructions

**How to trigger:**
> "add schema markup", "generate structured data", "JSON-LD", "rich snippets", "FAQ schema", "product markup"

### [`geo-content-optimizer`](geo-content-optimizer/) — AI Citation Optimization (GEO)

Optimize content to appear in AI-generated responses from ChatGPT, Perplexity, Google AI Overviews, and Claude.

**What it does:**
- Analyzes content for AI-friendliness across 8 GEO factors
- Creates quotable definitions (25–50 words, standalone)
- Adds authority signals (expert quotes, source citations)
- Restructures content for AI comprehension (Q&A, tables, numbered lists)
- Improves factual density with verifiable statistics
- Scores before/after GEO readiness (typically 50%+ improvement)

**How to trigger:**
> "optimize for AI", "get cited by ChatGPT", "GEO optimization", "appear in AI answers", "AI doesn't mention my brand", "generative engine optimization"

---

## Install — 30 seconds

**Requirements:** Python 3.8+, `gcloud` CLI (`brew install google-cloud-sdk`), and one of:
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Codex](https://github.com/openai/codex) (`npm install -g @openai/codex`)

### Claude Code

Open Claude Code and paste this. Claude does the rest.

> Install toprank: run **`git clone --single-branch --depth 1 https://github.com/nowork-studio/toprank.git ~/.claude/skills/toprank && cd ~/.claude/skills/toprank && ./setup`** then add a "toprank" section to CLAUDE.md that lists the available skills: /seo-analysis, /content-writer, /keyword-research, /meta-tags-optimizer, /schema-markup-generator, /geo-content-optimizer.

Add to your repo so teammates get it (optional):

> Add toprank to this project: run **`cp -Rf ~/.claude/skills/toprank .claude/skills/toprank && cd .claude/skills/toprank && ./setup`** then add a "toprank" section to this project's CLAUDE.md that lists the available skills: /seo-analysis, /content-writer, /keyword-research, /meta-tags-optimizer, /schema-markup-generator, /geo-content-optimizer.

### Codex

Install to one repo:

```bash
git clone --single-branch --depth 1 https://github.com/nowork-studio/toprank.git .agents/skills/toprank
cd .agents/skills/toprank && ./setup --host codex
```

Install globally:

```bash
git clone --single-branch --depth 1 https://github.com/nowork-studio/toprank.git ~/toprank
cd ~/toprank && ./setup --host codex
```

Setup auto-detects which agents you have when you use `--host auto` (the default).

---

## How Skills Work

Each skill is a `SKILL.md` file that your agent loads as an instruction set. The agent reads the skill and follows its workflow, calling scripts, crawling pages, querying APIs, to produce a structured output.

Skills are discovered automatically. Claude Code reads from `~/.claude/skills/`, Codex reads from `.agents/skills/`. The `./setup` script handles both.

```
toprank/
├── setup                      ← run this to register skills
├── seo-analysis/
│   ├── SKILL.md               ← SEO audit workflow
│   ├── scripts/               ← Python scripts for GSC API
│   └── references/            ← setup guides
├── content-writer/
│   ├── SKILL.md               ← content creation workflow
│   └── references/            ← Google content best practices
├── keyword-research/
│   ├── SKILL.md               ← keyword discovery & analysis
│   └── references/            ← intent taxonomy, cluster templates
├── meta-tags-optimizer/
│   ├── SKILL.md               ← title/description/OG optimization
│   └── references/            ← formulas, CTR data, code templates
├── schema-markup-generator/
│   ├── SKILL.md               ← JSON-LD structured data generation
│   └── references/            ← schema templates, validation guide
├── geo-content-optimizer/
│   ├── SKILL.md               ← AI citation optimization (GEO)
│   └── references/            ← citation patterns, GEO techniques
└── toprank-upgrade/
    └── SKILL.md               ← auto-upgrade workflow
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

[MIT](LICENSE)
