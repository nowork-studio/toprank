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

### Claude Code (recommended)

Run these two commands in Claude Code:

```
/plugin marketplace add nowork-studio/toprank
```

```
/plugin install toprank@nowork-studio
```

That's it. All skills are now available as `/toprank:*` commands.

**Google Ads (optional):** Connect your account at [adsagent.org](https://www.adsagent.org) (free API key) — setup instructions are provided there.

### Manual Install

<details>
<summary>Prefer to edit settings.json directly?</summary>

Add the marketplace and enable the plugin in `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "nowork-studio": {
      "source": {
        "source": "github",
        "repo": "nowork-studio/toprank"
      }
    }
  },
  "enabledPlugins": {
    "toprank@nowork-studio": true
  }
}
```

</details>

---

## Skills

### Google Ads

| Skill | What it does |
|-------|-------------|
| [`ads-audit`](google-ads/ads-audit/) | Account audit + business context setup. Run this first. Scores 7 health dimensions, identifies wasted spend, builds business profile. |
| [`ads`](google-ads/ads/) | Campaign management. Read performance, optimize keywords, adjust bids/budgets, add negatives, create campaigns. |
| [`ads-copy`](google-ads/ads-copy/) | RSA copy generator + A/B testing. Data-driven headlines and descriptions with character counts and pin positions. |

### SEO

| Skill | What it does |
|-------|-------------|
| [`seo-analysis`](seo/seo-analysis/) | Full SEO audit with GSC data. Quick wins, traffic drops, technical issues, 30-day action plan. |
| [`content-writer`](seo/content-writer/) | SEO content creation following E-E-A-T guidelines. Blog posts, landing pages, content improvements. |
| [`keyword-research`](seo/keyword-research/) | Keyword discovery, intent classification, topic clusters, prioritized content calendar. |
| [`meta-tags-optimizer`](seo/meta-tags-optimizer/) | Title tags, meta descriptions, OG/Twitter cards with A/B variations and CTR estimates. |
| [`schema-markup-generator`](seo/schema-markup-generator/) | JSON-LD structured data for rich results. FAQ, HowTo, Article, Product, LocalBusiness. |
| [`setup-cms`](seo/setup-cms/) | Connect WordPress, Strapi, Contentful, or Ghost for automated SEO field audits. |

All skills are namespaced: `/toprank:ads`, `/toprank:seo-analysis`, etc.

---

## How It Works

Toprank is a Claude Code plugin. Each skill is a `SKILL.md` file with supporting reference documents, scripts, and eval tests.

```
toprank/
├── .claude-plugin/
│   ├── plugin.json              <- plugin metadata (explicit skill paths)
│   └── marketplace.json         <- registry entry
├── .mcp.json                    <- AdsAgent MCP server (auto-configured)
├── google-ads/
│   ├── ads/                     <- campaign management
│   ├── ads-audit/               <- account audit + business context
│   └── ads-copy/                <- RSA copy generator + A/B testing
├── seo/
│   ├── seo-analysis/            <- full SEO audit with GSC data
│   ├── content-writer/          <- E-E-A-T content creation
│   ├── keyword-research/        <- keyword discovery + topic clusters
│   ├── meta-tags-optimizer/     <- title tags, meta descriptions, OG
│   ├── schema-markup-generator/ <- JSON-LD structured data
│   └── setup-cms/               <- CMS connector
├── toprank-upgrade-skill/       <- self-updater
├── test/                        <- unit + LLM-judge eval tests
└── VERSION
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

[MIT](LICENSE)
