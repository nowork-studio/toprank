# SEO Business Context

Business context captures stable facts about a business that don't change run-to-run — name, goals, competitors, audience, brand terms. Caching these avoids repeating the same questions on every audit and lets the analysis skip generic observations in favor of recommendations grounded in what this specific business is trying to do.

This is shared logic. Any SEO skill can reference it. The invoking skill controls when it runs. Assumes `preamble.md` has already run (GSC auth and `$SKILL_SCRIPTS` are set). Requires `$TARGET_URL` from Step 0.

---

## Cache location

```bash
DOMAIN=$(python3 -c "import sys; from urllib.parse import urlparse; print(urlparse(sys.argv[1]).netloc.lstrip('www.'))" "$TARGET_URL")
BC_FILE="$HOME/.toprank/business-context/$DOMAIN.json"
```

---

## Loading

Check whether a fresh cache exists and emit a status tag the invoking skill can branch on:

```bash
mkdir -p "$HOME/.toprank/business-context"
if [ -f "$BC_FILE" ]; then
  AGE_DAYS=$(python3 -c "
import json, sys
from datetime import datetime, timezone
data = json.load(open(sys.argv[1]))
gen = datetime.fromisoformat(data.get('generated_at', '1970-01-01T00:00:00+00:00'))
print((datetime.now(timezone.utc) - gen.astimezone(timezone.utc)).days)
" "$BC_FILE")
  cat "$BC_FILE"
  [ "$AGE_DAYS" -lt 90 ] && echo "CACHE_STATUS=fresh_loaded" || echo "CACHE_STATUS=stale"
else
  echo "CACHE_STATUS=not_found"
fi
```

**`CACHE_STATUS=fresh_loaded`**: profile is current. Extract `brand_terms` as a comma-joined string → `$BC_BRAND_TERMS`. Tell the user:
> "Using cached business profile for **$DOMAIN** (saved $AGE_DAYS days ago) — say *'refresh business context'* to update it."

Skip the brand-terms question in Phase 2.

**`CACHE_STATUS=stale`**: cache exists but is over 90 days old. Load the stale data as a pre-fill for questions in Generation below. Tell the user:
> "Your business profile for **$DOMAIN** is over 90 days old — I'll refresh it after collecting your GSC data."

**`CACHE_STATUS=not_found`**: no cache. Proceed to Generation after Phase 3.

---

## Generation (after Phase 3 GSC data is available)

At this point you have GSC data and homepage content. Infer as much as possible first so questions are as few as possible.

### Step 1 — Infer from data you already have

From GSC + homepage, extract:
- **Candidate brand terms**: queries that appear frequently but don't cluster with topical keywords
- **Key topics**: the top 5-8 query clusters by impression volume
- **Primary geographies**: the top 3-5 countries from the country split
- **Business type signals**: presence of `/pricing/`, `/checkout/`, `/shop/`, `/blog/`, `/locations/` in top page paths
- **Business summary clues**: the homepage `<title>` and `<meta description>`

### Step 2 — Ask minimal targeted questions

Ask all three in a single message. Questions 1 and 2 are optional — if the user skips them, fall back to your inferences from Step 1 (note this in the saved `notes` field).

> I'm building a business profile for **$DOMAIN** to make future audit recommendations more specific. Three quick questions — press Enter to skip any and I'll infer from your data:
>
> 1. **Business name and what you do** — one or two sentences. *(e.g., "Acme — project management software for remote engineering teams")*
> 2. **Primary goal of this website** — pick the closest or describe your own:
>    `lead generation` · `ecommerce` · `SaaS / subscription` · `local business` · `content / media` · `other`
> 3. **Main competitors** — 2–5 URLs or names *(optional)*

If `CACHE_STATUS=stale`, pre-fill the question with the cached values so the user can confirm or correct rather than re-enter from scratch.

Wait for the user's response before continuing.

### Step 3 — Synthesize and save

Normalize `primary_goal` to a consistent machine-readable form before saving:
```python
# e.g., "SaaS / subscription" → "saas_subscription", "lead generation" → "lead_generation"
raw_goal = user_answer_2.lower().strip()
primary_goal = raw_goal.replace(' / ', '_').replace('/', '_').replace(' ', '_') or "unknown"
```

Then write to cache:

```python
import json, os
from datetime import datetime, timezone

# --- fill from user answers + inferred data ---
domain           = "$DOMAIN"
target_url       = "$TARGET_URL"
business_name    = "<user answer 1, or inferred from homepage title>"
business_summary = "<1-2 sentence distillation>"
industry         = "<inferred from homepage + GSC topics>"
primary_goal     = "<normalized from user answer 2, or inferred from URL structure>"
target_audience  = "<inferred from GSC query patterns + homepage copy>"
target_locations = ["<top countries from GSC country split>"]
brand_terms      = ["<name variations from user answer 1 + GSC brand signal queries>"]
competitors      = ["<from user answer 3, or []>"]
key_topics       = ["<top 5-8 query clusters from GSC>"]
notes            = "<note if answers were inferred rather than user-provided>"
# ---------------------------------------------

data = {
    "domain":           domain,
    "target_url":       target_url,
    "generated_at":     datetime.now(timezone.utc).isoformat(),
    "business_name":    business_name,
    "business_summary": business_summary,
    "industry":         industry,
    "primary_goal":     primary_goal,
    "target_audience":  target_audience,
    "target_locations": target_locations,
    "brand_terms":      brand_terms,
    "competitors":      competitors,
    "key_topics":       key_topics,
    "notes":            notes,
}

bc_file = os.path.expanduser(f"~/.toprank/business-context/{domain}.json")
os.makedirs(os.path.dirname(bc_file), exist_ok=True)
with open(bc_file, "w") as f:
    json.dump(data, f, indent=2)
print(f"Business context saved to {bc_file}")
```

Output `CACHE_STATUS=fresh_loaded` after saving so downstream phases know context is ready.

Confirm to the user: "Business profile saved for **$DOMAIN** — I'll use this automatically in all future SEO audits."

---

## Using business context in analysis

Once loaded or generated, these values inform every phase that follows:

| Field | Use |
|-------|-----|
| `brand_terms` | Pass to `analyze_gsc.py --brand-terms`; skip the Phase 2 brand-terms question |
| `competitors` | Drive Phase 4.5 keyword gap analysis — compare their rankings to yours |
| `primary_goal` | Focus Phase 6 recommendations — `lead_generation` → landing pages; `ecommerce` → product/category pages; `content_media` → topical authority and freshness |
| `target_audience` | Cross-reference with Phase 3.7 personas — flag tension if personas don't match the stated audience |
| `key_topics` | Anchor content gap recommendations to confirmed topics, not speculative ones |
| `business_summary` | Open Phase 6 report with a one-liner so all recommendations read as contextual, not generic |

---

## Refreshing

If the user says "refresh business context", "update my business profile", or similar:

```bash
rm -f "$BC_FILE"
```

Then re-run Generation. No need to re-run any other phase.

---

## No-GSC fallback

If GSC was unavailable and the audit is technical-only (Phase 5):

- Skip Step 1 (no GSC data to infer from)
- Still ask the three questions in Step 2
- Infer what you can from homepage content alone
- Save the cache with `"notes": "Generated without GSC data — re-run with GSC access for better accuracy"`

---

## Schema reference

```json
{
  "domain":           "example.com",
  "target_url":       "https://example.com",
  "generated_at":     "2026-04-07T12:00:00+00:00",
  "business_name":    "Acme Corp",
  "business_summary": "Project management software for remote engineering teams.",
  "industry":         "SaaS / Developer Tools",
  "primary_goal":     "lead_generation",
  "target_audience":  "Engineering managers at companies with 20-500 employees",
  "target_locations": ["US", "UK", "CA"],
  "brand_terms":      ["Acme", "AcmeCorp", "acme.io"],
  "competitors":      ["linear.app", "asana.com", "monday.com"],
  "key_topics":       ["project management", "sprint planning", "engineering velocity"],
  "notes":            ""
}
```
