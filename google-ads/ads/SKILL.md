---
name: ads
description: Manage Google Ads campaigns — read performance, optimize keywords, adjust bids and budgets, add negatives, pause/enable campaigns, manage ads/ad groups, tracking templates, location targeting, network settings, rename campaigns/ad groups, bulk operations, and undo changes. Use this skill whenever the user mentions Google Ads, campaigns, keywords, ad spend, CPA, ROAS, search terms, negative keywords, bids, budgets, ads performance, location targeting, geo targeting, or campaign settings — even if they don't say "ads" explicitly.
version: 2.0.0
triggers:
  - google ads
  - campaigns
  - keywords
  - ad spend
  - CPA
  - ROAS
  - search terms
  - negative keywords
  - bid
  - budget
  - pause campaign
  - ads performance
  - location targeting
  - geo targeting
  - campaign settings
  - rename campaign
  - rename ad group
  - bulk keywords
---

# AdsAgent — Google Ads Management

Call Google Ads tools using the AdsAgent MCP server.

## Configuration

All persistent config lives in `~/.adsagent/config.json`. This file survives across sessions and works in every context — Claude Code, Claude Desktop, MCP servers, etc.

The config file has this shape:

```json
{
  "apiKey": "asa_...",
  "accountId": "1234567890"
}
```

## Onboarding

Before doing anything else, check whether the user is set up. Follow these steps in order — stop at the first issue and resolve it before continuing.

### Step 0: Check for the AdsAgent MCP server

Try calling `mcp__adsagent__listConnectedAccounts`. If it responds, the MCP server is connected — skip to Step 1.

If the tool doesn't exist, the MCP server isn't configured yet. Guide the user:

> The AdsAgent MCP server isn't connected. To set it up:
>
> 1. **Get a free token** at [adsagent.org](https://www.adsagent.org)
> 2. **Add the MCP server** to your Claude settings (`mcpServers`):
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
> If you installed toprank via the setup script, re-run `./setup --api-key YOUR_KEY` to configure everything automatically.

### Step 1: Check for token

Read `~/.adsagent/config.json` (create `~/.adsagent/` if it doesn't exist).

Look for `apiKey` (the token) in the config file. If it's present, skip to Step 2.

If it's missing, tell the user:

> To use AdsAgent, you need a free token. You can get one from [adsagent.org](https://www.adsagent.org).
> Once you have it, paste it here and I'll save it for you.

When the user provides the key, save it to `~/.adsagent/config.json`.

Then continue to Step 2.

### Step 2: Select a Google Ads account

Look for `accountId` in the config file. If it's present, proceed to fulfil the user's request.

If `accountId` is not set:

1. Run `listConnectedAccounts` to get all connected Google Ads accounts.
2. **If there is exactly one account**, save it automatically — no need to bother the user. Write `accountId` to `~/.adsagent/config.json` and tell the user which account was selected (show account name and ID).
3. **If there are multiple accounts**, present them as a numbered list showing account name and ID, then ask the user to pick one. Save their choice to `~/.adsagent/config.json`.
4. **If there are zero accounts**, tell the user they don't have any Google Ads accounts connected yet and direct them to [adsagent.org](https://www.adsagent.org) to connect one.

### Switching accounts

If the user wants to switch accounts, run `listConnectedAccounts`, let them pick, and update `accountId` in `~/.adsagent/config.json`.

## Calling tools

Call tools directly via the MCP server using the `mcp__adsagent__<toolName>` pattern. Read `~/.adsagent/config.json` first to get the `accountId`.

**Examples:**

```
mcp__adsagent__listCampaigns(accountId: "1234567890")
mcp__adsagent__getKeywords(accountId: "1234567890", campaignId: "111222333")
mcp__adsagent__listConnectedAccounts()
```

Always pass `accountId` from `~/.adsagent/config.json` to every tool call (except `listConnectedAccounts`). All responses are JSON.

## Available Tools

### Read (safe, no side effects)
- **getAccountInfo** — Account name, currency, timezone, test status
- **listCampaigns** — All campaigns with impressions, clicks, cost, conversions
- **getCampaignPerformance** — Daily metrics over a date range
- **getKeywords** — Top keywords with quality scores
- **getSearchTermReport** — Actual search queries triggering ads
- **runGaqlQuery** — Run a custom read-only GAQL SELECT query (max 50 rows)
- **getChanges** — Recent AdsAgent changes with `changeId`s for undo
- **listConnectedAccounts** — All connected Google Ads accounts
- **getTrackingTemplate** — Current tracking template at account/campaign/ad-group/ad level
- **listAdGroups** — Ad groups in a campaign with metrics
- **listAds** — Ads in a campaign/ad group with copy, URLs, status, metrics
- **getImpressionShare** — Search/top/abs-top IS and budget/rank-lost IS
- **getConversionActions** — Conversion actions and settings
- **getAccountSettings** — Auto-tagging, tracking template, conversion tracking IDs
- **getCampaignSettings** — Bidding, network, locations, schedule
- **getNegativeKeywords** — List negative keywords for a campaign (check before adding new negatives to avoid duplicates)
- **getRecommendations** — Google optimization recommendations

### Write (mutates the account — always confirm with user first)
All write tools return a `changeId` on success. Use this with `undoChange` to reverse the operation within 7 days.
- **pauseKeyword** — Stop a keyword
- **enableKeyword** — Re-enable a paused keyword
- **addKeyword** — Add a new keyword to an ad group
- **updateBid** — Change CPC bid (manual/enhanced CPC only, max 25% change)
- **addNegativeKeyword** — Block irrelevant search terms (phrase match)
- **removeNegativeKeyword** — Remove a negative keyword
- **updateCampaignBudget** — Change daily budget (max 50% change)
- **createCampaign** — Create a full paused search campaign
- **pauseCampaign** — Pause all ads in a campaign
- **enableCampaign** — Re-enable a paused campaign
- **setTrackingTemplate** — Set/clear tracking template
- **createAdGroup** — Create a new ad group
- **createAd** — Create a new Responsive Search Ad
- **pauseAd** — Pause an ad
- **enableAd** — Re-enable an ad
- **updateAdFinalUrl** — Change an ad's landing page URL
- **updateAdAssets** — Replace an RSA's headlines/descriptions (complete replacement — provide every asset, not just changed ones; optionally pin assets to positions)
- **bulkUpdateBids** — Update up to 50 keyword bids in one call (each capped at 25% change)
- **bulkPauseKeywords** — Pause up to 100 keywords in one call (partial success possible)
- **bulkAddKeywords** — Add up to 100 keywords to an ad group in one call (partial success possible)
- **moveKeywords** — Move keywords between ad groups in the same campaign (adds to destination first, pauses source on success, rolls back on failure)
- **renameCampaign** — Rename a campaign
- **renameAdGroup** — Rename an ad group
- **updateCampaignSettings** — Update network targeting (Google Search, Search Partners, Display Network) and/or location targeting (add/remove geo targets by geo target constant ID, e.g. '2840' for US, '200840' for Seattle-Tacoma DMA). Also supports negative location targeting (exclusions).
- **undoChange** — Reverse a previous write by `changeId`

## Rules

1. **Never make write changes without explicit user confirmation.** Always show what you plan to change, the current value, and the new value before executing.
2. **Start with reads.** When the user asks about ads, begin with `getAccountInfo` and `listCampaigns` to build context.
3. **Show numbers clearly.** Format cost as dollars, show CTR as percentages, include date ranges.
4. **Recommend before acting.** When you spot waste (high-spend zero-conversion keywords, irrelevant search terms), recommend the action and wait for approval.
5. **Guardrails are server-side.** Bid changes >25% and budget changes >50% will be rejected by the server. Don't try to circumvent this.
6. **After every write, note the `changeId`.** Tell the user they can undo the change within 7 days. Use `getChanges` to review recent operations.

## Common Workflows

### "How are my ads doing?"
1. `getAccountInfo` → `listCampaigns` → summarize top spenders, best/worst performers, total spend

### "Find wasted spend"
1. `listCampaigns` → pick top-spend campaigns
2. `getKeywords` for each → find high-spend, zero-conversion keywords
3. `getSearchTermReport` → find irrelevant search terms
4. Recommend: pause wasteful keywords + add negative keywords

### "Optimize bids"
1. `getKeywords` → find keywords with good conversion rates but low impression share
2. `getImpressionShare` / `getCampaignSettings` as needed for context
3. Recommend bid increases (within 25% limit) for high-performers
4. Recommend bid decreases for underperformers
