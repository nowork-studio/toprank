# Changelog

All notable changes to Toprank will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.2.0] — 2026-03-27

### Added
- **Autoupdate system** — skills now check GitHub for new versions on every invocation
  - `bin/toprank-update-check` — fetches `VERSION` from GitHub with 60-min cache; outputs `UPGRADE_AVAILABLE <old> <new>` or nothing
  - `bin/toprank-config` — read/write `~/.toprank/config.yaml`; supports `update_check`, `auto_upgrade` keys
  - `toprank-upgrade/SKILL.md` — upgrade skill with inline and standalone flows, snooze (24h/48h/7d backoff), auto-upgrade mode, changelog diff
  - Preamble in `seo-analysis` and auto-inject via `setup` for all future skills
  - `bin/preamble.md` — single source of truth for the preamble template
- `VERSION` file — tracks current release for update checks

### Fixed
- `toprank-update-check`: validate local VERSION format before writing cache; exit after `JUST_UPGRADED` to prevent dual stdout output; move `mkdir -p` to top of script
- `setup`: atomic SKILL.md writes via temp file + `os.replace()`; add `pipefail` to catch silent Python errors
- `toprank-upgrade`: clear stale `.bak` before vendored upgrade to prevent collision

---

## [0.3.0] — 2026-03-27

### Added
- **Python test suite** — full pytest infrastructure under `test/` replacing the prior TypeScript/Bun approach; no build step required
  - `test/unit/` — 42 fast unit tests (stdlib only, no API calls); covers date math, GSC data processing, report structure, and skill SKILL.md content validation
  - `test/test_skill_e2e.py` — E2E skill tests gated behind `EVALS=1`; uses mock `gcloud` + mock `analyze_gsc.py` fixture to run the full skill workflow without real credentials
  - `test/test_skill_llm_eval.py` — LLM-as-judge quality evals gated behind `EVALS=1`; scores report clarity, actionability, and phase coverage on a 1–5 scale
  - `test/test_skill_routing_e2e.py` — routing evals verify the skill triggers on SEO prompts and stays silent on unrelated requests
  - `test/helpers/` — session runner (spawns `claude -p --output-format stream-json`), LLM judge, eval store, and diff-based test selection
  - `test/fixtures/` — mock gcloud binary, mock analyze_gsc.py, and sample GSC JSON fixture data
  - `conftest.py` — root-level pytest config for import path setup
  - `requirements-test.txt` — minimal test dependencies

### Fixed
- **Routing tests** — added harness failure guard; `should-not-trigger` tests no longer silently pass when the subprocess times out or crashes
- **Env isolation** — test subprocess now strips `ANTHROPIC_*` vars (in addition to `CLAUDE_*`) to prevent `ANTHROPIC_BASE_URL` or `ANTHROPIC_MODEL` from redirecting evals to an unintended endpoint
- **LLM judge retry** — exponential backoff (3 attempts: 1s, 2s, 4s) replaces single-retry on rate limit
- **Mock gcloud** — removed fall-through to real `gcloud` binary that caused infinite recursion when mock was first in PATH
- **`.gitignore`** — restored credential patterns (`credentials.json`, `token.json`, `.env`, etc.) accidentally dropped in initial commit

---

## [0.2.1] — 2026-03-27

### Changed
- **`seo-analysis` Phase 1** — replaced two-step auth check (token print + separate site list) with single `list_gsc_sites.py` call that tests auth, scopes, and GSC access in one shot; added distinct handling for each failure mode (wrong account, wrong scopes, API not enabled, gcloud not installed)
- **`seo-analysis` script paths** — replaced hardcoded `~/.claude/skills/seo-analysis/scripts/` with a `find`-based `SKILL_SCRIPTS` lookup that works for Claude Code, Codex, and custom install paths; added guard for empty result so missing installs fail with a clear error instead of a confusing path error
- **`seo-analysis` property selection** — added explicit rule to prefer domain property (`sc-domain:example.com`) over URL-prefix when both exist for the same site
- **`gsc_setup.md`** — moved "Which Google Account" guidance to top (most common failure cause); replaced broken `oauth_setup.py` Option B with Linux (Debian/Ubuntu, RPM) and Windows install instructions; fixed deprecated `apt-key` with `gpg --dearmor` for Debian 12+/Ubuntu 24.04+; expanded troubleshooting to cover `insufficient_scope` 403s

### Fixed
- **`list_gsc_sites.py`** — unhandled `FileNotFoundError` when gcloud is not installed now shows a clean error message; added `URLError` handling for network failures (DNS, TLS, proxy)
- **`analyze_gsc.py`** — same `FileNotFoundError` and `URLError` fixes
- **`gsc_setup.md`** — removed reference to `oauth_setup.py` which did not exist
- **`seo-analysis` SKILL.md** — corrected error-branch description from "Python traceback" to "ERROR: gcloud not found" to match the actual script output

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
