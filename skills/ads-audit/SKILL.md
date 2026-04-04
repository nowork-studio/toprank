---
name: ads-audit
description: Google Ads account audit and business context setup. Run this first — it gathers business information, analyzes account health, and saves context that all other ads skills reuse. Trigger on "audit my ads", "ads audit", "set up my ads", "onboard", "account overview", "how's my account", "ads health check", "what should I fix in my ads", or when the user is new to AdsAgent and hasn't run an audit before. Also trigger proactively when other ads skills detect that business-context.json is missing.
---

# Google Ads Audit + Business Context Setup

This is the starting point for any Google Ads account. It does two things:

1. **Audits the account** — surfaces what's working, what's wasting money, and what to fix first
2. **Builds business context** — gathers and saves business information to `~/.adsagent/business-context.json` so every other ads skill (copy, landing pages, competitive analysis) can use it without re-asking

Run this before anything else. If another ads skill finds `business-context.json` missing, it should point the user here.

## Setup

Before anything else, verify the user has the AdsAgent MCP server connected and a token configured. Follow these steps in order — stop at the first issue and resolve it before continuing.

### Step 1: Check for the AdsAgent MCP server

Try calling `mcp__adsagent__listConnectedAccounts`. If the tool exists and responds, the MCP server is connected — skip to Step 2.

If the tool doesn't exist (not in available tools), the MCP server isn't configured. Guide the user:

> The AdsAgent MCP server isn't connected yet. To set it up:
>
> 1. **Get a free token** at [adsagent.org](https://www.adsagent.org)
> 2. **Add the MCP server** to your Claude settings. Open your Claude Code settings (or Claude Desktop config) and add this to `mcpServers`:
>
> ```json
> {
>   "adsagent": {
>     "command": "npx",
>     "args": [
>       "-y", "mcp-remote",
>       "https://www.adsagent.org/api/mcp",
>       "--transport", "http-first",
>       "--header", "Authorization:Bearer YOUR_API_KEY"
>     ]
>   }
> }
> ```
>
> Replace `YOUR_API_KEY` with the token from step 1.
>
> 3. **Restart Claude** to pick up the new MCP server.
>
> Alternatively, if you installed toprank via the setup script, re-run `./setup --api-key YOUR_KEY` and it will configure everything automatically.

Wait for the user to complete setup before proceeding.

### Step 2: Check for token and account

Read `~/.adsagent/config.json` for `apiKey` (the token) and `accountId`.

- If `apiKey` is missing, ask the user for their token and save it as `apiKey` in `~/.adsagent/config.json`.
- If `accountId` is missing, run `mcp__adsagent__listConnectedAccounts`:
  - **One account** → save it automatically
  - **Multiple accounts** → show list, ask user to pick
  - **Zero accounts** → direct user to [adsagent.org](https://www.adsagent.org) to connect a Google Ads account

## Phase 1: Pull Account Data

Gather everything in parallel before asking the user a single question. The goal is to show up informed.

**Account basics:**
- `mcp__adsagent__getAccountInfo` — business name, currency, timezone
- `mcp__adsagent__getAccountSettings` — auto-tagging, tracking template, conversion setup

**Campaign structure:**
- `mcp__adsagent__listCampaigns` — all campaigns with spend, clicks, conversions
- `mcp__adsagent__listAdGroups` — ad groups per campaign (focus on top-spend campaigns)

**Performance data:**
- `mcp__adsagent__getCampaignPerformance` — daily trends for the last 30 days
- `mcp__adsagent__getKeywords` — top keywords with quality scores, bids, conversions
- `mcp__adsagent__getSearchTermReport` — actual search queries triggering ads
- `mcp__adsagent__getImpressionShare` — search IS, top IS, budget-lost IS, rank-lost IS

**Ads and conversions:**
- `mcp__adsagent__listAds` — ad copy, status, and per-ad metrics
- `mcp__adsagent__getConversionActions` — what conversions are set up and how they're configured
- `mcp__adsagent__getNegativeKeywords` — existing negative keyword coverage

**Recommendations:**
- `mcp__adsagent__getRecommendations` — Google's optimization suggestions (evaluate critically, don't blindly follow)

## Phase 2: Analyze and Score

Work through each dimension. For each one, assign a quick status: OK / Needs Work / Critical.

### Account Health Dimensions

**1. Conversion tracking**
- Are conversion actions set up? Are they firing?
- Is auto-tagging enabled?
- Red flag: spending money with no conversion tracking = flying blind

**2. Campaign structure**
- Are campaigns organized by service/product and location?
- Are ad groups tightly themed (5-20 keywords each)?
- Red flag: one ad group with 200 keywords = poor relevance

**3. Keyword health**
- What's the average quality score? (Below 5 = problems)
- Any high-spend, zero-conversion keywords?
- Are match types appropriate? (Broad match without negatives = waste)
- Are there enough negatives blocking irrelevant queries?

**4. Search term quality**
- What % of search terms are relevant?
- Are there obvious negatives missing?
- Are there high-converting search terms not yet added as keywords?

**5. Ad copy**
- How many RSAs per ad group? (Should have at least 2 for testing)
- Are headlines and descriptions varied or repetitive?
- Are there ads with low CTR that need refreshing?

**6. Impression share**
- How much traffic are you losing to budget vs. rank?
- Budget-lost IS > 20% = you're leaving money on the table or need to tighten targeting
- Rank-lost IS > 50% = quality score or bid issues

**7. Spend efficiency**
- What's the overall CPA? How does it compare across campaigns?
- Any campaigns with high spend but low conversions?
- What % of spend goes to converting keywords vs. non-converting?

## Phase 3: Build Business Context

Now that you understand the account, fill in the business context. Pull as much as possible from the data you already have — only ask the user for what you can't infer.

### What to infer from account data

| Field | Source |
|-------|--------|
| `business_name` | `getAccountInfo` |
| `services` | Campaign and ad group names, keyword themes |
| `locations` | Campaign geo-targeting, location extensions |
| `brand_voice` | Existing ad copy tone and word choices |
| `keyword_landscape.high_intent_terms` | Top-converting keywords |
| `keyword_landscape.competitive_terms` | Low impression share keywords with high CPC |
| `keyword_landscape.long_tail_opportunities` | Converting search terms not yet added as keywords |

### What to ask the user

Present what you inferred, then ask for what's missing. Frame it conversationally, not as a checklist.

**Always ask:**
- "What makes you different from competitors?" → `differentiators`
- "Who are your main competitors?" → `competitors`
- "Is your business seasonal? When's your busiest time?" → `seasonality`
- "What's your website URL?" → for landing page context

**Ask if not obvious from data:**
- Industry (if campaign names don't make it clear)
- Target audience (if search terms don't reveal it)
- Current offers or promotions
- Social proof (reviews, awards, years in business)

### Website analysis

If the user provides their website URL (or it's visible in ad final URLs):

- Note the URL in `landing_pages`
- Look at what the ads link to — do headlines match landing page content?
- Note any offers, trust signals, or CTAs visible on the site that could inform ad copy

### Save the context

Write the complete business context to `~/.adsagent/business-context.json`:

```json
{
  "business_name": "",
  "industry": "",
  "website": "",
  "services": [],
  "locations": [],
  "target_audience": "",
  "brand_voice": {
    "tone": "",
    "words_to_avoid": [],
    "words_to_use": []
  },
  "differentiators": [],
  "competitors": [],
  "seasonality": {
    "peak_months": [],
    "slow_months": [],
    "seasonal_hooks": []
  },
  "keyword_landscape": {
    "high_intent_terms": [],
    "competitive_terms": [],
    "long_tail_opportunities": []
  },
  "social_proof": [],
  "offers_or_promotions": [],
  "landing_pages": {},
  "notes": "",
  "audit_date": "",
  "account_id": ""
}
```

Include `audit_date` (today's date) and `account_id` so future skills know when this was last refreshed.

## Phase 4: Deliver the Audit Report

Present findings as a concise, actionable report. No fluff — every line should either inform a decision or recommend an action.

### Report format

```
# Google Ads Audit: [Business Name]
**Account:** [ID] | **Period:** Last 30 days | **Date:** [today]

## Scorecard
| Dimension            | Status      | Summary                              |
|----------------------|-------------|--------------------------------------|
| Conversion tracking  | OK / Needs Work / Critical | [one line]          |
| Campaign structure   | ...         | ...                                  |
| Keyword health       | ...         | ...                                  |
| Search term quality  | ...         | ...                                  |
| Ad copy              | ...         | ...                                  |
| Impression share     | ...         | ...                                  |
| Spend efficiency     | ...         | ...                                  |

## Key Numbers
- **Total spend (30d):** $X,XXX
- **Conversions:** XX at $XX CPA
- **Top campaign:** [name] — XX% of spend, XX% of conversions
- **Wasted spend:** ~$XXX on non-converting keywords/terms

## Top 3 Actions (do these first)
1. **[Action]** — [why, expected impact]
2. **[Action]** — [why, expected impact]
3. **[Action]** — [why, expected impact]

## Detailed Findings
[Organized by dimension — only include dimensions that need work.
For each, state the problem, show the data, recommend the fix.]

## Business Context Saved
Saved to ~/.adsagent/business-context.json — other ads skills
(/ads-copy, /ads-landing, /ads-compete) will use this automatically.
[List any fields that are incomplete and need user input later.]
```

### What makes a good action item

- **Specific:** "Pause keyword 'free dog food' — $847 spent, 0 conversions" not "Review underperforming keywords"
- **Quantified:** Include the spend, impressions, or conversions at stake
- **Prioritized:** Highest-impact items first. Stopping waste > starting new things
- **Actionable with /ads:** Every recommendation should be something the user can execute immediately using the `/ads` skill

## Rules

1. **Data first, questions second.** Pull all account data before asking the user anything. Show up informed.
2. **Infer before asking.** Don't ask "what industry are you in?" if the campaigns clearly say "plumbing services."
3. **Be specific.** Name the campaigns, keywords, and dollar amounts. Vague advice is useless.
4. **Prioritize by money.** The biggest waste or biggest opportunity comes first.
5. **Save the context.** Always write `business-context.json` — this is the handoff to every other ads skill.
6. **Don't fix things here.** This skill diagnoses and recommends. The user executes fixes with `/ads`. Offer to switch to `/ads` for implementation.
