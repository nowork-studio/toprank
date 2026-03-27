# Toprank

**Open-source Claude Code skills for SEO and SEM.**

Toprank is a collection of AI agent skills that give you the leverage of a search marketing expert — pulling real data from Google Search Console, auditing technical SEO, finding quick wins, and diagnosing traffic drops. Works inside Claude Code with no extra tooling beyond a `gcloud` install.

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

---

## Install — 30 seconds

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Python 3.8+, `gcloud` CLI (`brew install google-cloud-sdk`)

### Step 1: Install on your machine

Open Claude Code and paste this. Claude does the rest.

> Install toprank: run **`git clone --single-branch --depth 1 https://github.com/nowork-studio/ads-agent.git /tmp/ads-agent && cp -Rf /tmp/ads-agent/toprank ~/.claude/skills/toprank && cd ~/.claude/skills/toprank && ./setup && rm -rf /tmp/ads-agent`** then add a "toprank" section to CLAUDE.md that lists the available skills: /seo-analysis.

### Step 2: Add to your repo so teammates get it (optional)

> Add toprank to this project: run **`cp -Rf ~/.claude/skills/toprank .claude/skills/toprank && cd .claude/skills/toprank && ./setup`** then add a "toprank" section to this project's CLAUDE.md that lists the available skills: /seo-analysis.

---

## How Skills Work

Each skill is a `SKILL.md` file that Claude Code loads as an instruction set. Claude reads the skill and follows its workflow — calling scripts, crawling pages, querying APIs — to produce a structured output.

Skills live in `~/.claude/skills/` and are discovered automatically. No configuration needed.

```
toprank/
├── setup                 ← run this to register skills
├── seo-analysis/
│   ├── SKILL.md          ← workflow instructions Claude follows
│   ├── scripts/          ← Python scripts for API calls and data processing
│   └── references/       ← guides and docs loaded as needed
└── (future skills go here)
```

---

## Contributing

Contributions are very welcome. If you've built a skill that helps with SEO, SEM, content strategy, or search analytics — open a PR.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ideas for new skills:**
- `keyword-research` — find keyword gaps from GSC data + competitor analysis
- `gsc-monitor` — daily/weekly GSC health check with alerts
- `technical-seo-fix` — audit + auto-fix common technical issues in a Next.js/Astro repo
- `sem-audit` — Google Ads quality score analysis and bid recommendations
- `content-gap` — find queries you rank 11–30 for and generate content briefs

---

## License

[MIT](LICENSE)
