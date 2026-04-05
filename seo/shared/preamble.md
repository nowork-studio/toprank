# SEO Shared Preamble

Every SEO skill reads this before doing anything else. It handles script discovery, GSC authentication, and site selection in one place — so individual skills don't repeat this logic.

## Step 1: Check for cached GSC session

If gcloud credentials already exist and the user has previously selected a GSC property in this session, skip to Step 4. Signs of a cached session:
- `gcloud auth application-default print-access-token` succeeds silently
- The target URL is already known from the conversation

If both are true, skip straight to Step 4.

## Step 2: Locate skill scripts

All SEO skills share the scripts in `seo-analysis/scripts/`. Locate them once:

```bash
SKILL_SCRIPTS=$(find ~/.claude/plugins ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
[ -z "$SKILL_SCRIPTS" ] && echo "ERROR: seo-analysis scripts not found" && exit 1
```

Use `$SKILL_SCRIPTS` for all subsequent script calls.

## Step 3: Preflight — gcloud and GSC API

Run the preflight check to ensure gcloud is installed, a GCP project exists, and the Search Console API is enabled:

```bash
python3 "$SKILL_SCRIPTS/preflight.py"
```

- **`OK: All dependencies ready.`** — continue to Step 4.
- **Browser opens for Google login** — user needs to log in with the Google account that owns their Search Console properties. Preflight finishes automatically after login.
- **`gcloud init` runs** — first-time user. The wizard walks them through setup. After it completes, preflight continues automatically.
- **`Search Console API: enabled`** — preflight auto-enabled the API. No action needed.
- **ERROR: Could not enable the Search Console API** — user needs to enable manually: `gcloud services enable searchconsole.googleapis.com`
- **gcloud not found** — OS-specific install instructions are printed. Install gcloud, then re-run.
- **No gcloud and user wants to skip GSC** — that is fine. GSC data won't be available, but skills can still operate on URL-only analysis (technical crawl, meta tags, schema).

> **Reference**: For manual setup or troubleshooting, see `../seo-analysis/references/gsc_setup.md`.

## Step 4: Proceed

Scripts are located at `$SKILL_SCRIPTS`, auth is ready. All subsequent script calls in the invoking skill should use `$SKILL_SCRIPTS` directly — do not re-run the find command. Hand control back to the invoking skill.
