# Changelog

All notable changes to Toprank will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.2] — 2026-03-27

### Changed
- **`seo-analysis` Phase 1** — replaced two-step auth check (token print + separate site list) with single `list_gsc_sites.py` call that tests auth, scopes, and GSC access in one shot; added distinct handling for each failure mode (wrong account, wrong scopes, API not enabled, gcloud not installed)
- **`seo-analysis` script paths** — replaced hardcoded `~/.claude/skills/seo-analysis/scripts/` with a `find`-based `SKILL_SCRIPTS` lookup that works for Claude Code, Codex, and custom install paths
- **`seo-analysis` property selection** — added explicit rule to prefer domain property (`sc-domain:example.com`) over URL-prefix when both exist for the same site
- **`gsc_setup.md`** — moved "Which Google Account" guidance to top (most common failure cause); replaced broken `oauth_setup.py` Option B with Linux (Debian/Ubuntu, RPM) and Windows install instructions; fixed deprecated `apt-key` with `gpg --dearmor` for Debian 12+/Ubuntu 24.04+; expanded troubleshooting to cover `insufficient_scope` 403s

### Fixed
- **`list_gsc_sites.py`** — unhandled `FileNotFoundError` when gcloud is not installed now shows a clean error message instead of a Python traceback
- **`analyze_gsc.py`** — same `FileNotFoundError` fix
- **`gsc_setup.md`** — removed reference to `oauth_setup.py` which did not exist

---

## [0.1.1] — 2026-03-27

### Changed
- **README intro** — rewritten to lead with user outcome ("Finally know what to do about your SEO") and emphasize zero-risk install; blockquote examples now show real questions users would type

---

## [0.1.0] — 2026-03-26

### Added
- **`seo-analysis` skill** — comprehensive SEO audit powered by Google Search Console
  - Phase 1: GSC API setup detection and guided auth via `gcloud` Application Default Credentials
  - Phase 2: Auto-detect site URL from website repo (`package.json`, `next.config.js`, `astro.config.*`, etc.) or prompt for URL
  - Phase 3: Data collection — top queries, top pages, position buckets (1–3, 4–10, 11–20, 21+), CTR opportunities, 28-day period comparison, device split
  - Phase 4a: Search Console analysis — quick wins, content gaps, traffic drops
  - Phase 4b: Technical SEO audit — indexability, meta tags, heading structure, structured data, performance signals
  - Phase 5: Structured report with executive summary, traffic snapshot, and 30-day action plan
- `scripts/list_gsc_sites.py` — list all GSC properties for the authenticated account
- `scripts/analyze_gsc.py` — pull and process GSC data, output structured JSON
- `references/gsc_setup.md` — complete setup guide for gcloud ADC and OAuth fallback
