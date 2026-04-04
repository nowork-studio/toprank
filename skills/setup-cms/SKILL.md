---
name: setup-cms
description: >
  Connect a CMS to toprank SEO tools. Guides users through configuring
  WordPress, Strapi, Contentful, or Ghost — tests the connection, and writes
  credentials to .env.local. Once set up, seo-analysis automatically cross-
  references CMS content against Google Search Console data. Use whenever the
  user says "connect my CMS", "set up WordPress", "configure Strapi", "add
  Contentful", "connect Ghost", or "CMS setup". Also trigger if the user asks
  why no CMS data appears in a seo-analysis report.
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

# /setup-cms

Guide the user through connecting their CMS to toprank's SEO analysis tools.

Once configured, `/seo-analysis` automatically pulls published content from
the CMS and cross-references it against Google Search Console data — finding
invisible pages, content gaps, stale articles, and missing SEO fields.

---

## Preamble (run first)

```bash
_UPD=$(~/.claude/skills/toprank/bin/toprank-update-check 2>/dev/null || \
       ~/.claude/skills/stockholm/bin/toprank-update-check 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true
```

If the output contains `UPGRADE_AVAILABLE <old> <new>`: follow the inline
upgrade flow in `/toprank-upgrade`, then return here and continue.

---

## Step 1 — Detect existing CMS configuration

```bash
SKILL_SCRIPTS=$(find ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
CMS_TYPE=$(python3 "$SKILL_SCRIPTS/cms_detect.py" 2>/dev/null)
CMS_STATUS=$?
echo "CMS_TYPE=$CMS_TYPE  EXIT=$CMS_STATUS"
```

- `CMS_STATUS=0` → a CMS is already configured (`$CMS_TYPE` is the name).
  Show the user: "You already have **[$CMS_TYPE]** connected. Would you like to
  reconfigure it, or switch to a different CMS?"
  Wait for their reply. If they say reconfigure/switch, continue to Step 2.
  If they say test or verify, jump to Step 5 (skip to connection test).

- `CMS_STATUS=2` → nothing configured yet. Continue to Step 2.

---

## Step 2 — Choose a CMS

Ask the user:

> "Which CMS are you connecting? I support:
>
> 1. **WordPress** — self-hosted or WordPress.com (uses REST API + Application Password)
> 2. **Strapi** — v4 or v5, self-hosted (uses API Token)
> 3. **Contentful** — cloud headless CMS (uses Delivery API key)
> 4. **Ghost** — Ghost.org or self-hosted (uses Content API key)
>
> Reply with the name or number."

Wait for their answer. Map to: `wordpress`, `strapi`, `contentful`, `ghost`.

---

## Step 3 — Credential setup by CMS

Jump to the sub-section for the chosen CMS.

---

### 3A — WordPress

WordPress uses the built-in **Application Passwords** feature (introduced in WP 5.6).
This is the safest way to grant API access — it never exposes your main password
and can be revoked at any time.

Tell the user:

> "I need three things to connect WordPress:
>
> 1. **Your WordPress URL** (e.g. `https://myblog.com`)
> 2. **Your WordPress username** (the one you log in with)
> 3. **An Application Password** — create one in:
>    WordPress Admin → Users → Profile → scroll to **Application Passwords**
>    → enter a name like "toprank" → click **Add New** → copy the generated password
>
> Paste each value when ready."

Collect values one at a time:
1. Ask for `WP_URL` → validate it starts with `http://` or `https://`
2. Ask for `WP_USERNAME`
3. Ask for `WP_APP_PASSWORD`
4. Ask for `WP_CONTENT_TYPE`:
   > "What content type should I analyze? Common values: `posts`, `pages`.
   > Press Enter to use `posts` (default), or enter a custom post type slug."

Once all four are collected, continue to Step 4 (test connection).

Write to `.env.local`:
```
WP_URL=<value>
WP_USERNAME=<value>
WP_APP_PASSWORD=<value>
WP_CONTENT_TYPE=<value or posts>
```

---

### 3B — Strapi

Tell the user:

> "I need two things to connect Strapi:
>
> 1. **Your Strapi URL** (e.g. `https://cms.example.com`)
> 2. **A Full-access API Token** — create one in:
>    Strapi Admin → Settings → Global settings → API Tokens → Create new API Token
>    → Type: **Full access** → copy the token
>
> Optionally:
> - **Content type** — the plural API ID of your content collection (default: `articles`).
>   Find it in: Content-Type Builder → [your type] → API ID (plural)
> - **Strapi version** — `4` or `5` (auto-detected if omitted)
>
> Paste each value when ready."

Collect:
1. `STRAPI_URL`
2. `STRAPI_API_KEY`
3. `STRAPI_CONTENT_TYPE` (optional, default: `articles`)
4. `STRAPI_VERSION` (optional)

Write to `.env.local`:
```
STRAPI_URL=<value>
STRAPI_API_KEY=<value>
STRAPI_CONTENT_TYPE=<value or articles>
```
Include `STRAPI_VERSION=<value>` only if the user specified it.

---

### 3C — Contentful

Tell the user:

> "I need three things to connect Contentful:
>
> 1. **Space ID** — find it in: Contentful → Settings → General Settings → Space ID
> 2. **Content Delivery API token** — find it in:
>    Settings → API Keys → [your key] → Content Delivery API - access token
>    (If no key exists, create one under Settings → API Keys → Add API Key)
> 3. **Content type ID** — the API identifier for your content type.
>    Find it in: Content model → [your type] → API Identifier
>
> Optionally:
> - **Environment** (default: `master`)
>
> Paste each value when ready."

Collect:
1. `CONTENTFUL_SPACE_ID`
2. `CONTENTFUL_DELIVERY_TOKEN`
3. `CONTENTFUL_CONTENT_TYPE`
4. `CONTENTFUL_ENVIRONMENT` (optional, default: `master`)

Write to `.env.local`:
```
CONTENTFUL_SPACE_ID=<value>
CONTENTFUL_DELIVERY_TOKEN=<value>
CONTENTFUL_CONTENT_TYPE=<value>
CONTENTFUL_ENVIRONMENT=<value or master>
```

---

### 3D — Ghost

Tell the user:

> "I need two things to connect Ghost:
>
> 1. **Your Ghost URL** (e.g. `https://myblog.ghost.io`)
> 2. **Content API key** — create one in:
>    Ghost Admin → Settings → Integrations → Add custom integration
>    → copy the **Content API Key**
>
> Optionally:
> - **Content type**: `posts` (default) or `pages`
>
> Paste each value when ready."

Collect:
1. `GHOST_URL`
2. `GHOST_CONTENT_KEY`
3. `GHOST_CONTENT_TYPE` (optional, default: `posts`)

Write to `.env.local`:
```
GHOST_URL=<value>
GHOST_CONTENT_KEY=<value>
GHOST_CONTENT_TYPE=<value or posts>
```

---

## Step 4 — Write .env.local

Find the project's `.env.local` file. Search for it:
```bash
ENV_FILE=""
for candidate in ".env.local" "$HOME/.env.local"; do
  [ -f "$candidate" ] && ENV_FILE="$candidate" && break
done
[ -z "$ENV_FILE" ] && ENV_FILE=".env.local"
echo "Writing to: $ENV_FILE"
```

**Merge strategy** — do not overwrite the entire file. For each env var:
1. If the key already exists in the file, replace that line.
2. If it does not exist, append it to the end.

Read the file first (if it exists), then update key by key, then write back.

If the file doesn't exist yet, create it.

After writing, confirm:
> "Credentials written to `[path]`. Testing connection now..."

---

## Step 5 — Test connection

Run the appropriate preflight script and capture the exit code:

```bash
# WordPress
python3 "$SKILL_SCRIPTS/preflight_wordpress.py" 2>&1; PREFLIGHT_EXIT=$?

# Strapi
python3 "$SKILL_SCRIPTS/preflight_strapi.py" 2>&1; PREFLIGHT_EXIT=$?

# Contentful
python3 "$SKILL_SCRIPTS/preflight_contentful.py" 2>&1; PREFLIGHT_EXIT=$?

# Ghost
python3 "$SKILL_SCRIPTS/preflight_ghost.py" 2>&1; PREFLIGHT_EXIT=$?
```

The `2>&1` redirect surfaces error messages in the output so you can show them.

**`PREFLIGHT_EXIT=0`** — connection successful. Show the "OK: …" line to the user,
then continue to Step 6.

**`PREFLIGHT_EXIT=1`** — connection failed. Show the full error output verbatim.
Help the user diagnose:
- `401 Unauthorized` → wrong token/password — suggest regenerating
- `403 Forbidden` → token lacks permission — suggest a Full Access / unrestricted token
- `404 Not Found` → wrong URL or wrong content type slug
- Network error → URL unreachable — check the URL in a browser first

Ask: "Want to fix the credentials and try again (I'll go back to Step 3), or skip CMS setup for now?"

**`PREFLIGHT_EXIT=2`** → credentials were removed from `.env.local` between steps. Restart from Step 3.

---

## Step 6 — Confirm and summarize

Once the connection succeeds, show a summary:

```
CMS connected successfully!

  CMS:          [WordPress/Strapi/Contentful/Ghost]
  URL:          [cms_url]
  Content type: [content_type]
  Published:    [N] entries found

What this enables in /seo-analysis:
  • Cross-reference [N] published articles against Google Search Console data
  • Find published content with zero GSC impressions (unindexed or invisible)
  • Identify content gaps: queries ranking 11-30 with no matching article
  • Flag stale content: articles >6 months old with declining clicks
  • Audit SEO fields: missing meta titles/descriptions, length violations
```

Then offer:
> "Run `/seo-analysis` to see a full audit with your CMS content included,
> or type `/setup-cms` again to connect a different CMS."
