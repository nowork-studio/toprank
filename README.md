# Toprank

**SEO that reads your data, tells you what's wrong, and fixes it.**

Toprank gives Claude direct access to your Google Search Console and Google Ads data. Run it inside your website repo and it doesn't just analyze — it rewrites your meta tags, fixes your headings, adds structured data, and ships the changes.

> *"Why did my traffic drop last month?"*
> *"What keywords am I almost ranking for?"*
> *"Fix my title tags for pages losing clicks."*

Free, open-source skill for Claude Code and Codex. Install in 30 seconds.

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

**Requirements:** Python 3.8+, `gcloud` CLI (`brew install google-cloud-sdk`), and one of:
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Codex](https://github.com/openai/codex) (`npm install -g @openai/codex`)

### Claude Code

Open Claude Code and paste this. Claude does the rest.

> Install toprank: run **`git clone --single-branch --depth 1 https://github.com/nowork-studio/toprank.git ~/.claude/skills/toprank && cd ~/.claude/skills/toprank && ./setup`** then add a "toprank" section to CLAUDE.md that lists the available skills: /seo-analysis.

Add to your repo so teammates get it (optional):

> Add toprank to this project: run **`cp -Rf ~/.claude/skills/toprank .claude/skills/toprank && cd .claude/skills/toprank && ./setup`** then add a "toprank" section to this project's CLAUDE.md that lists the available skills: /seo-analysis.

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
│   ├── SKILL.md          ← workflow instructions Claude follows
│   ├── scripts/          ← Python scripts for API calls and data processing
│   └── references/       ← guides and docs loaded as needed
└── (future skills go here)
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

[MIT](LICENSE)
