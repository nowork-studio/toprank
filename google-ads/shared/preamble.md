# Google Ads Shared Preamble

Every google-ads skill reads this before doing anything else. It handles MCP detection, authentication, and upgrade checks in one place — so individual skills don't repeat this logic.

## Step 1: Check config cache

Read `~/.adsagent/config.json`. If both `apiKey` and `accountId` are present, skip to Step 4. The MCP server is already configured and the account is selected — no further setup needed.

## Step 2: MCP Server Detection

Only runs if Step 1 found missing config.

1. Check for AdsAgent tools: try calling `mcp__adsagent__listConnectedAccounts`
2. If not found, check for Google's official MCP: look for tools matching `mcp__google_ads_mcp__*` in the available tools
3. If neither exists, guide the user:

> No Google Ads MCP server detected. The easiest setup:
>
> 1. Get a free API key at [adsagent.org](https://www.adsagent.org)
> 2. Set the environment variable: `export ADSAGENT_API_KEY=your_key`
> 3. Restart Claude Code (the toprank plugin's .mcp.json will auto-configure the server)
>
> Or configure any Google Ads MCP server manually in your MCP settings.

Stop here until the MCP server is available.

## Step 3: Onboarding (only if config is incomplete)

Read `~/.adsagent/config.json` (create `~/.adsagent/` if it doesn't exist).

### Token

If `apiKey` is missing:

> To use AdsAgent, you need a free token. You can get one from [adsagent.org](https://www.adsagent.org).
> Once you have it, paste it here and I'll save it for you.

Save the token to `~/.adsagent/config.json` when provided.

### Account selection

If `accountId` is missing:

1. Run `listConnectedAccounts`
2. **One account** → save automatically, tell the user which was selected
3. **Multiple accounts** → show numbered list, ask user to pick, save choice
4. **Zero accounts** → direct to [adsagent.org](https://www.adsagent.org) to connect one

### Switching accounts

If the user explicitly asks to switch accounts, run `listConnectedAccounts`, let them pick, and update `accountId` in `~/.adsagent/config.json`.

## Step 4: Calling tools

Use whichever MCP server prefix was detected:

- **AdsAgent MCP (default):** `mcp__adsagent__<toolName>` with `accountId` parameter
- **Google's official MCP:** `mcp__google_ads_mcp__<toolName>`

Always pass `accountId` from `~/.adsagent/config.json` to every tool call (except `listConnectedAccounts`).

## Step 5: Proceed

Config is loaded. Hand control back to the invoking skill.
