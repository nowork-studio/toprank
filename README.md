# Toprank

**SEO + Google Ads skills for Claude Code. Data-driven decisions, not dashboards.**

Toprank gives your AI agent direct access to Google Search Console and Google Ads. It analyzes your traffic, surfaces what's hurting your rankings, finds wasted ad spend, and tells you exactly what to fix. When you have access to the repo, it goes further: rewriting meta tags, fixing headings, adding structured data, and shipping the changes.

> *"Am I wasting money on ads right now?"*
> *"Why did my traffic drop and how do I fix it?"*
> *"How do I get more conversions without spending more?"*

Free, open-source. Install in 30 seconds.

---

## See It Work

### Google Ads

```
You:    /toprank:ads-audit

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

        Business context saved — /toprank:ads-copy and /toprank:ads will use it.

You:    Do it all.

        [paused 3 wasteful keywords — saved $210/mo]
        [added 12 negative keywords — saved $130/mo]
        [increased bids on 2 high-performers]

        Done. All changes are reversible within 7 days.
```

### SEO

```
You:    /toprank:seo-analysis

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
```

---

## Install

Toprank is a **Claude Code plugin**. One-time setup, automatic updates.

### Step 1: Add the marketplace

Open Claude Code settings and add to `extraKnownMarketplaces`:

```json
{
  "extraKnownMarketplaces": {
    "nowork-studio": {
      "source": {
        "source": "github",
        "repo": "nowork-studio/toprank"
      }
    }
  }
}
```

### Step 2: Enable the plugin

Add to `enabledPlugins` in settings:

```json
{
  "enabledPlugins": {
    "toprank@nowork-studio": true
  }
}
```

### Step 3: Configure Google Ads (optional)

If you use Google Ads, set your AdsAgent API key (free from [adsagent.org](https://www.adsagent.org)):

```bash
export ADSAGENT_API_KEY=your_key_here
```

The plugin's bundled MCP server picks this up automatically. Or configure any Google Ads MCP server manually.

That's it. All skills are now available.

---

## Skills

### Google Ads

| Skill | What it does |
|-------|-------------|
| [`ads-audit`](skills/ads-audit/) | Account audit + business context setup. Run this first. Scores 7 health dimensions, identifies wasted spend, builds business profile. |
| [`ads`](skills/ads/) | Campaign management. Read performance, optimize keywords, adjust bids/budgets, add negatives, create campaigns. |
| [`ads-copy`](skills/ads-copy/) | RSA copy generator + A/B testing. Data-driven headlines and descriptions with character counts and pin positions. |

### SEO

| Skill | What it does |
|-------|-------------|
| [`seo-analysis`](skills/seo-analysis/) | Full SEO audit with GSC data. Quick wins, traffic drops, technical issues, 30-day action plan. |
| [`content-writer`](skills/content-writer/) | SEO content creation following E-E-A-T guidelines. Blog posts, landing pages, content improvements. |
| [`keyword-research`](skills/keyword-research/) | Keyword discovery, intent classification, topic clusters, prioritized content calendar. |
| [`meta-tags-optimizer`](skills/meta-tags-optimizer/) | Title tags, meta descriptions, OG/Twitter cards with A/B variations and CTR estimates. |
| [`schema-markup-generator`](skills/schema-markup-generator/) | JSON-LD structured data for rich results. FAQ, HowTo, Article, Product, LocalBusiness. |
| [`setup-cms`](skills/setup-cms/) | Connect WordPress, Strapi, Contentful, or Ghost for automated SEO field audits. |

All skills are namespaced: `/toprank:ads`, `/toprank:seo-analysis`, etc.

---

## How It Works

Toprank is a Claude Code plugin. Each skill is a `SKILL.md` file with supporting reference documents, scripts, and eval tests.

```
toprank/
├── .claude-plugin/
│   ├── plugin.json              <- plugin metadata
│   └── marketplace.json         <- registry entry
├── .mcp.json                    <- AdsAgent MCP server (auto-configured)
├── skills/
│   ├── seo-analysis/
│   │   ├── SKILL.md             <- SEO audit workflow
│   │   ├── scripts/             <- Python scripts for GSC API
│   │   ├── references/          <- domain expertise docs
│   │   └── evals/               <- quality tests
│   ├── ads/
│   │   ├── SKILL.md             <- Google Ads management
│   │   ├── references/          <- benchmarks, decision trees
│   │   └── evals/               <- quality tests
│   ├── ads-audit/
│   ├── ads-copy/
│   ├── keyword-research/
│   ├── meta-tags-optimizer/
│   ├── schema-markup-generator/
│   ├── content-writer/
│   ├── setup-cms/
│   └── toprank-upgrade/
├── test/                        <- unit + LLM-judge eval tests
└── VERSION
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

[MIT](LICENSE)
