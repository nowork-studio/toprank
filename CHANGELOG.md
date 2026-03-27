# Changelog

All notable changes to Toprank will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
