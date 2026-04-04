# Toprank

**SEO + Google Ads skills for Claude Code and Codex. Data-driven decisions, not dashboards.**

Toprank gives your AI agent direct access to Google Search Console and Google Ads. It analyzes your traffic, surfaces what's hurting your rankings, finds wasted ad spend, and tells you exactly what to fix. When you have access to the repo, it goes further: rewriting meta tags, fixing headings, adding structured data, and shipping the changes.

> *"Am I wasting money on ads right now?"*
> *"Why did my traffic drop and how do I fix it?"*
> *"How do I get more conversions without spending more?"*

Free, open-source. Install in 30 seconds.

---

## See It Work

### Google Ads

```
You:    /ads-audit

Claude: Connected to your Google Ads account (MyStore).

        3 campaigns active. $2,400 spent this month.

        Scorecard:
        ┌──────────────────────┬──────────┬──────────────────────────────┐
        │ Dimension            │ Status   │ Summary                      │
        ├──────────────────────┼──────────┼──────────────────────────────┤
        │ Conversion tracking  │ OK       │ 3 actions firing correctly   │
        │ Keyword health       │ Critical │ 8 keywords burning cash      │
        │ Search term quality  │ Warning  │ 12 irrelevant queries        │
        │ Impression share     │ Warning  │ Losing 35% to rank           │
        │ Spend efficiency     │ Critical │ $340/mo wasted               │
        └──────────────────────┴──────────┴──────────────────────────────┘

        Top 3 actions:
        1. Pause 3 keywords ($210/mo, zero conversions)
        2. Add 12 negative keywords ($130/mo wasted on irrelevant terms)
        3. Increase bids 15% on 2 high-converting keywords losing IS

        Business context saved — /ads-copy and /ads will use it.

You:    Do it all.

        [paused 3 wasteful keywords — saved $210/mo]
        [added 12 negative keywords — saved $130/mo]
        [increased bids on 2 high-performers]

        Done. All changes are reversible within 7 days.
```

```
You:    Write new ad copy for my boarding service

Claude: [reads your business context — knows your brand voice,
         differentiators, seasonal peaks, keyword landscape]

        [pulls current ad performance and search term language]

        VARIANT A: "Safety-First"
          H1 [Pin 1]: Dog Boarding in Seattle       (25 chars)
          H2: Cage-Free, Supervised Care             (26 chars)
          H3: Book Your Pet's Stay                   (20 chars)
          D1: Safe, cage-free boarding. Supervised play, daily updates.
          D2: Open 7 days. 3 locations. Book online now.

        VARIANT B: "Convenience"
          H1 [Pin 1]: Dog Boarding Near SeaTac       (25 chars)
          H2: Drop Off Anytime, 7 Days               (24 chars)
          ...

        Deploy Variant A?

You:    Yes, both as an A/B test.

        [created 2 RSAs in ad group, both paused]
        [enabled both — A/B test running]

        Check back in 2 weeks or after 100 clicks per variant.
```

### SEO

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

## Google Ads Setup

The ads skills need an MCP server that talks to the Google Ads API. Two options:

### Option A: Free hosted server (easiest)

[AdsAgent](https://www.adsagent.org) runs a free MCP server so you don't have to deal with Google Ads API credentials, OAuth, or infrastructure.

1. **Get a free token** at [adsagent.org](https://www.adsagent.org) — sign in with Google to connect your Google Ads account
2. **Run `/ads-audit`** in Claude Code — it walks you through setup and saves your token to `~/.adsagent/config.json`
3. **Done** — all ads skills (`/ads`, `/ads-audit`, `/ads-copy`) now work

<details>
<summary>Manual MCP config (if you skipped the setup script)</summary>

Add this to your Claude Code MCP config (`~/.claude/settings.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "adsagent": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://www.adsagent.org/api/mcp",
        "--transport", "http-first",
        "--header", "Authorization:Bearer YOUR_TOKEN_HERE"
      ],
      "env": {
        "ADS_AGENT_KEY": "YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Replace `YOUR_TOKEN_HERE` with the token from [adsagent.org](https://www.adsagent.org).

</details>

### Option B: Self-hosted MCP server

If you already have Google Ads API access and prefer to run your own MCP server, point the skills at your server instead. The only requirement is that your server implements the same MCP tool interface (e.g. `listCampaigns`, `getKeywords`, `pauseKeyword`, etc.).

Update the MCP config to point at your server:

```json
{
  "mcpServers": {
    "adsagent": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://your-server.example.com/mcp",
        "--transport", "http-first",
        "--header", "Authorization:Bearer YOUR_AUTH_TOKEN"
      ]
    }
  }
}
```

As long as your server exposes the same tools, the skills work identically.

---

## Google Ads Skills

### [`ads-audit`](google-ads/ads-audit/) — Account Audit & Business Context Setup

**Run this first.** Audits your Google Ads account health and builds a business context profile that all other ads skills reuse.

**What it does:**
- Pulls all account data (campaigns, keywords, search terms, ads, impression share, conversions)
- Scores 7 health dimensions: conversion tracking, campaign structure, keyword health, search term quality, ad copy, impression share, spend efficiency
- Identifies wasted spend with specific keywords and dollar amounts
- Builds and saves business context (brand voice, seasonality, competitors, keyword landscape) to `~/.adsagent/business-context.json`
- Produces a prioritized action plan — top 3 things to fix first

**How to trigger:**
> "audit my ads", "ads audit", "set up my ads", "account overview", "how's my account", "ads health check", "what should I fix"

### [`ads`](google-ads/ads/) — Google Ads Management

Manage your Google Ads campaigns directly from Claude. Read performance data, optimize keywords, adjust bids and budgets, add negative keywords, and more. Powered by [AdsAgent](https://www.adsagent.org)'s free MCP server.

**What it does:**
- Reads campaign performance, keywords, search terms, impression share
- Pauses wasteful keywords and adds negative keywords
- Adjusts bids (within guardrails) and campaign budgets
- Creates campaigns, ad groups, and responsive search ads
- Every change is reversible within 7 days via `undoChange`

**How to trigger:**
> "how are my ads doing", "find wasted spend", "optimize bids", "add negative keywords", "pause campaign", "Google Ads performance", "check my ads"

### [`ads-copy`](google-ads/ads-copy/) — Ad Copy Generator & A/B Testing

Write Google Ads RSA copy grounded in your performance data and business context. Generates multiple variants with distinct messaging angles, deploys them, and tracks A/B test results.

**What it does:**
- Reads business context and current ad performance before writing
- Generates RSA headlines (≤30 chars) and descriptions (≤90 chars) with character counts
- Presents 2-3 named variants with pin positions and messaging angles
- Deploys approved variants directly via `createAd` / `updateAdAssets`
- Sets up and evaluates A/B tests with clear winner criteria

**How to trigger:**
> "write ad copy", "new headlines", "improve my ads CTR", "A/B test my ads", "RSA copy", "ad variants", "write me an ad"

**Setup:** All Google Ads skills need a free token from [adsagent.org](https://www.adsagent.org). The setup script or `/ads-audit` will walk you through it.

---

## SEO Skills

### [`seo-analysis`](seo/seo-analysis/) — SEO Audit & Search Console Analysis

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

### [`content-writer`](seo/content-writer/) — SEO Content Creation

Write blog posts, landing pages, or improve existing content following Google's E-E-A-T and Helpful Content guidelines. Works standalone or spawned automatically by `seo-analysis` when content gaps are found.

**What it does:**
- Determines content type from context (blog post, landing page, or content improvement)
- Researches search intent and SERP landscape before writing
- Produces publication-ready content with SEO metadata, JSON-LD structured data, and internal linking plan
- Quality gate checks: "last click" test, E-E-A-T signals, anti-pattern detection
- When spawned by `seo-analysis`, writes multiple pieces in parallel for identified content gaps

**How to trigger:**
> "write a blog post about X", "create a landing page for Y", "improve this page", "content for keyword X", "draft an article", "rewrite this page"

### [`keyword-research`](seo/keyword-research/) — Keyword Discovery & Analysis

Discover high-value keywords, assess difficulty, classify search intent, and build topic clusters. Works standalone or feeds directly into `content-writer`.

**What it does:**
- Generates keyword lists from seed terms with long-tail variations
- Classifies search intent (informational, navigational, commercial, transactional)
- Scores keyword difficulty and calculates opportunity (volume x intent / difficulty)
- Groups keywords into topic clusters with pillar/cluster relationships
- Produces a prioritized content calendar

**How to trigger:**
> "keyword research", "find keywords", "what should I write about", "keyword analysis", "content ideas", "search volume", "keyword difficulty"

### [`meta-tags-optimizer`](seo/meta-tags-optimizer/) — Title Tags, Meta Descriptions & Social Tags

Create and optimize meta tags for better click-through rates in search results and social sharing.

**What it does:**
- Writes compelling title tags (50–60 chars) with keyword placement and power words
- Creates meta descriptions (150–160 chars) with clear CTAs
- Generates Open Graph and Twitter Card tags for social previews
- Provides multiple A/B test variations with CTR impact estimates
- Validates character lengths for proper SERP display

**How to trigger:**
> "optimize title tag", "write meta description", "improve CTR", "Open Graph tags", "fix my meta tags", "social media preview", "my click rate is low"

### [`schema-markup-generator`](seo/schema-markup-generator/) — JSON-LD Structured Data

Generate valid JSON-LD schema markup for rich results in Google Search.

**What it does:**
- Selects appropriate schema types based on content (FAQ, HowTo, Article, Product, LocalBusiness, etc.)
- Generates ready-to-paste JSON-LD with all required properties
- Handles complex multi-type schemas on a single page
- Provides SERP preview showing expected rich result appearance
- Includes validation guidance and implementation instructions

**How to trigger:**
> "add schema markup", "generate structured data", "JSON-LD", "rich snippets", "FAQ schema", "product markup"

---

## Install — 30 seconds

**Requirements:** Python 3.8+, `gcloud` CLI (`brew install google-cloud-sdk`), and one of:
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Codex](https://github.com/openai/codex) (`npm install -g @openai/codex`)

### Claude Code

Open Claude Code and paste this. Claude does the rest.

> Install toprank: run **`git clone --single-branch --depth 1 https://github.com/nowork-studio/toprank.git ~/.claude/skills/toprank && cd ~/.claude/skills/toprank && ./setup`** then add a "toprank" section to CLAUDE.md that lists the available skills: /seo-analysis, /content-writer, /keyword-research, /meta-tags-optimizer, /schema-markup-generator, /ads-audit, /ads, /ads-copy.

Add to your repo so teammates get it (optional):

> Add toprank to this project: run **`cp -Rf ~/.claude/skills/toprank .claude/skills/toprank && cd .claude/skills/toprank && ./setup`** then add a "toprank" section to this project's CLAUDE.md that lists the available skills: /seo-analysis, /content-writer, /keyword-research, /meta-tags-optimizer, /schema-markup-generator, /ads-audit, /ads, /ads-copy.

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
├── setup                          <- run this to register skills
├── seo/                           <- SEO skills
│   ├── seo-analysis/
│   │   ├── SKILL.md               <- SEO audit workflow
│   │   ├── scripts/               <- Python scripts for GSC API
│   │   └── references/
│   ├── content-writer/
│   │   ├── SKILL.md               <- content creation workflow
│   │   └── references/
│   ├── keyword-research/
│   │   ├── SKILL.md               <- keyword discovery & analysis
│   │   └── references/
│   ├── meta-tags-optimizer/
│   │   ├── SKILL.md               <- title/description/OG optimization
│   │   └── references/
│   ├── schema-markup-generator/
│   │   ├── SKILL.md               <- JSON-LD structured data
│   │   └── references/
│   └── setup-cms/
│       └── SKILL.md               <- CMS configuration wizard
├── google-ads/                    <- Google Ads skills
│   ├── ads-audit/
│   │   └── SKILL.md               <- account audit + business context
│   ├── ads/
│   │   ├── SKILL.md               <- Google Ads management
│   │   └── mcporter.json          <- MCP server config
│   └── ads-copy/
│       └── SKILL.md               <- RSA copy generator + A/B testing
└── toprank-upgrade/
    └── SKILL.md                   <- auto-upgrade workflow
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

[MIT](LICENSE)
