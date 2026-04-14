---
name: ads-landing
description: Score and diagnose Google Ads landing pages. Use when asked to audit a landing page, check landing page quality, diagnose high-CTR but low-conversion-rate ad groups, improve Quality Score's Landing Page Experience component, or compare an ad group's messaging against its landing page. Trigger on "landing page audit", "landing page score", "landing page quality", "why is my conversion rate low", "LPX", "landing page experience", "ad to page match", or when `/ads-audit` surfaces a high-CTR / low-CVR ad group.
argument-hint: "<landing page URL or ad group name>"
---

## Setup

Read and follow `../shared/preamble.md` — it handles MCP detection, token, and account selection. If config is already cached, this is instant.

# Landing Page Scoring + Diagnostic

Google Ads campaigns fail on the landing page more often than in the auction. A great RSA that sends traffic to a slow, unfocused, or mismatched page burns budget twice — once on the click, once on the lost conversion. This skill scores landing pages on **5 weighted dimensions** and emits concrete fixes.

## When to run this

| Trigger | Source |
|---------|--------|
| User explicitly asks for a landing page audit | Direct invocation |
| `/ads-audit` Layer 4 finds ad groups with CTR > account avg AND CVR < 50% of account avg | Auto-handoff |
| Quality Score diagnosis flags "Landing Page Experience: Below Average" on high-spend keywords | `/ads` routes here |
| `/ads-copy` is about to write copy for a page the user hasn't validated | Preflight check |

Only score pages that actually run ad traffic. Don't score random marketing pages.

## Reference Documents

- `references/scoring-rubric.md` — The 5-dimension weighted rubric, thresholds, and evidence fields (read this before running any score)
- `../ads-audit/references/business-context.md` — Uses `{data_dir}/business-context.json` for brand voice and differentiators to check message match
- `../ads/references/quality-score-framework.md` — Read only if the user's goal is QS improvement specifically

## Phase 1: Resolve the target pages

Figure out which URLs to score. In priority order:

1. **User supplied a URL** — score that one page, skip discovery.
2. **User supplied an ad group or campaign name** — pull `listAds` for that ad group and extract unique final URLs. Normalize (strip tracking params, preserve path + query that affects routing).
3. **Auto-handoff from `/ads-audit`** — the handoff passes the specific ad groups flagged in Layer 4. Pull their final URLs.
4. **No arguments** — pull `listAds` for the whole account, rank final URLs by spend (last 30 days), and propose the top 3 to score. Ask the user to confirm.

**De-duplicate aggressively.** Many ads point to the same final URL — score each unique URL once, then map back to all the ad groups that use it.

## Phase 2: Gather signal (parallel)

Run all of these in a single tool-use turn:

1. **WebFetch the landing page** — capture visible headline, subheadline, primary CTA text, form fields, trust signals, body copy tone. Also capture the full HTML so we can spot script bloat and above-the-fold content.
2. **PageSpeed Insights API call** — use `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo` via WebFetch. No API key needed for single-URL queries. Extract LCP, CLS, INP, TTI, performance score, and the top 3 opportunities (`lighthouseResult.audits`).
3. **Pull the referring ad copy** — from the ad group(s) that send traffic here, get headlines and descriptions via `listAds`. This is the message-match baseline.
4. **Read `{data_dir}/business-context.json`** — for brand voice, differentiators, offers, target audience. If it's missing, point the user to `/ads-audit` first. Don't guess the business.
5. **Pull conversion data** for the ad group(s) — `listAds` + search term report for the ad groups pointing here. Used to calculate CVR and to ground dollar-impact estimates.

If any single call fails, continue — note the gap in the report rather than blocking. PageSpeed Insights can rate-limit; if it does, fall back to manual timing annotation ("PSI unavailable — could not score Page Speed") and deflate the final grade's confidence rather than skipping the dimension.

## Phase 3: Score the page

Read `references/scoring-rubric.md` and score each dimension 0-100 with evidence. Weight and sum:

```
Landing Page Score = 0.25 * Message Match
                   + 0.25 * Page Speed
                   + 0.20 * Mobile Experience
                   + 0.15 * Trust Signals
                   + 0.15 * Form & CTA
```

Map the score to a grade:
- **A** (90-100): Page is an asset — scale traffic
- **B** (75-89): Solid — minor optimization
- **C** (60-74): Leaking conversions — fix top 2 dimensions
- **D** (45-59): Actively burning budget — do not scale
- **F** (<45): Diverting traffic away is cheaper than fixing it

**Margin-aware impact:** If `business-context.json.unit_economics` has `aov_usd` + `profit_margin`, compute the estimated monthly lift from reaching grade B (see `../shared/ppc-math.md`):

```
Assumed CVR lift      = (target_score - current_score) / 100 * 0.5   # cap at 50% relative lift
Current conversions   = ad group conversions from last 30d
Additional conversions = current_conversions * assumed_CVR_lift
Additional revenue    = additional_conversions * AOV
Additional profit     = additional_conversions * AOV * profit_margin
```

Present the lift as "fixing this page is worth ~$X/mo" — never as a guarantee. The 50% cap keeps us out of fantasy territory.

## Phase 4: Deliver the report

Max 60 lines. Lead with the grade and the single biggest fix.

```
# Landing Page Score — [URL]
**Grade: [A-F] · Score: XX/100**
Ads sending traffic here: [N ad groups] · [X clicks/mo] · [$Y spent/mo] · CVR [Z%]
[If unit_economics available] Estimated lift to B: ~$X/mo profit

**The single biggest problem:** [one sentence, naming the dimension]

## Score Breakdown
| Dimension | Weight | Score | Grade | Top Finding |
|-----------|--------|-------|-------|-------------|
| Message Match | 25% | XX | [A-F] | [one line] |
| Page Speed | 25% | XX | [A-F] | LCP Xs / INP Xms / CLS X |
| Mobile Experience | 20% | XX | [A-F] | [one line] |
| Trust Signals | 15% | XX | [A-F] | [one line] |
| Form & CTA | 15% | XX | [A-F] | [one line] |

## Fix First (top 3, ranked by score delta x weight)
1. **[Action]** — expected +X points · `severity` · `time_to_fix`
   Evidence: [the actual text/number/screenshot-description from the page]
2. **[Action]** — expected +X points · `severity` · `time_to_fix`
3. **[Action]** — expected +X points · `severity` · `time_to_fix`

## Message Match Analysis
Ad headline: "[actual headline from top-spending ad]"
Page H1:    "[actual H1 from landing page]"
Verdict:    [Match | Drift | Broken] — [one-line rationale]

## Handoff
[Pick one:]
- Page speed dominates the problem → "Share these fixes with your developer: [list]"
- Message mismatch dominates → "Run /ads-copy to rewrite ads to match the page, or update the page to match the ads"
- Form friction dominates → "Reduce form to [specific fields]. Every removed field is ~10% more conversions"
```

## Writing back to history

Append the score to `{data_dir}/landing-page-history.json` so re-audits can show deltas:

```json
{
  "pages": {
    "https://example.com/services/roofing": {
      "history": [
        {
          "date": "2026-04-14",
          "grade": "C",
          "score": 67,
          "dimensions": {
            "message_match": 72,
            "page_speed": 45,
            "mobile": 80,
            "trust": 70,
            "form_cta": 65
          },
          "psi_mobile_lcp_s": 4.2,
          "psi_mobile_cls": 0.15,
          "psi_mobile_inp_ms": 320,
          "ad_groups": ["Tukwila Search - Roofing"],
          "monthly_spend": 1240.50,
          "monthly_cvr": 2.1
        }
      ]
    }
  }
}
```

On subsequent runs against the same URL, show `Score: 78 (was 67)` and call out which dimensions moved.

## Rules

1. **Never score a page without WebFetch'ing it.** The rubric demands evidence. No WebFetch = no score. Ask the user to help if the page is gated or requires auth.
2. **Never report a PSI number you didn't measure.** If PSI failed, say "PSI unavailable" — don't estimate.
3. **One page at a time unless the user asks for multiple.** Scoring three pages in one turn creates unreadable reports. Batch only when explicitly requested.
4. **Don't rewrite copy here.** This skill diagnoses the page. Handoff to `/ads-copy` for new headlines or `/ads` for bid/negative/budget moves.
5. **Margin-aware dollar impact requires verified unit economics.** If `unit_economics.source == "inferred_from_template"`, append `_(using industry defaults — confirm your AOV/margin for sharper estimates)_` to the lift line.
6. **Always persist.** Every scored page goes into `landing-page-history.json`, even if the user doesn't ask — future audits depend on the baseline.
