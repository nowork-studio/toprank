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

---

## Install — 30 seconds

**Requirements:** Python 3.8+, `gcloud` CLI (`brew install google-cloud-sdk`), and one of:
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Codex](https://github.com/openai/codex) (`npm install -g @openai/codex`)

### Claude Code

Open Claude Code and paste this. Claude does the rest.

> Install toprank: run **`git clone --single-branch --depth 1 https://github.com/nowork-studio/toprank.git ~/.claude/skills/toprank && cd ~/.claude/skills/toprank && ./setup`** then add a "toprank" section to CLAUDE.md that lists the available skills: /seo-analysis, /content-writer.

Add to your repo so teammates get it (optional):

> Add toprank to this project: run **`cp -Rf ~/.claude/skills/toprank .claude/skills/toprank && cd .claude/skills/toprank && ./setup`** then add a "toprank" section to this project's CLAUDE.md that lists the available skills: /seo-analysis, /content-writer.

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
├── setup                 ← run this to register skills
├── seo-analysis/
│   ├── SKILL.md          ← SEO audit workflow
│   ├── scripts/          ← Python scripts for GSC API
│   └── references/       ← setup guides
├── content-writer/
│   ├── SKILL.md          ← content creation workflow
│   └── references/       ← Google content best practices
└── toprank-upgrade/
    └── SKILL.md          ← auto-upgrade workflow
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

[MIT](LICENSE)
