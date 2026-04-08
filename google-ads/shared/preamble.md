# Google Ads Shared Preamble

Every google-ads skill reads this before doing anything else. It handles MCP detection, authentication, and upgrade checks in one place — so individual skills don't repeat this logic.

## Step 0: Check for toprank updates

```bash
_UPD_BIN=$(ls ~/.claude/plugins/cache/nowork-studio/toprank/*/bin/toprank-update-check 2>/dev/null | head -1)
[ -n "$_UPD_BIN" ] && _UPD=$("$_UPD_BIN" 2>/dev/null || true) || _UPD=""
[ -n "$_UPD" ] && echo "$_UPD" || true
```

If the output contains `UPGRADE_AVAILABLE <old> <new>`: immediately follow the inline upgrade flow in the `/toprank-upgrade` skill (Step 1 onward) to auto-upgrade, then return here and continue.

If the output contains `JUST_UPGRADED <old> <new>`: mention "toprank upgraded from v{old} to v{new}" briefly, then continue.

## Step 1: Resolve config

Read config from three locations and merge fields (first non-null, non-empty-string value wins per field):

1. **Project-level** — `.adsagent.json` in the repository root (Claude Code's working directory)
2. **Claude project-level** — `~/.claude/projects/{project-path}/adsagent.json` (where `{project-path}` is the CWD-based path Claude Code uses for project memory, e.g. `-Users-alice-repos-petshop`)
3. **Global fallback** — `~/.adsagent/config.json`

Each file uses the same schema: `{ "accountId": "...", "apiKey": "..." }`. Fields merge up the chain — a project file with only `accountId` inherits `apiKey` from global.

If both `apiKey` and `accountId` are resolved after merging, skip to Step 4.

### Resolved data directory

Data files (business-context, personas, change-log, account-baseline) are stored project-locally when a project-level config exists:

- If `.adsagent.json` exists in the current working directory → `{data_dir}` = `.adsagent/` (relative to project root)
- Otherwise → `{data_dir}` = `~/.adsagent/` (the Claude project-level config alone doesn't trigger project-local data — only a `.adsagent.json` in the repo does)

Create `{data_dir}` if it doesn't exist. Throughout this document and all skills, `{data_dir}` refers to this resolved directory.

**Important:** If using project-local storage (`.adsagent/`), ensure `.adsagent.json` and `.adsagent/` are in the project's `.gitignore` — they contain API keys and business-sensitive data that should not be committed.

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

Read the merged config from Step 1. Ensure `~/.adsagent/` exists (needed for the global config file regardless of `{data_dir}`).

### Token

If `apiKey` is missing:

> To use AdsAgent, you need a free token. You can get one from [adsagent.org](https://www.adsagent.org).
> Once you have it, paste it here and I'll save it for you.

Save the token to `~/.adsagent/config.json` (global — API keys are shared across projects).

### Account selection

If `accountId` is missing:

1. Run `listConnectedAccounts`
2. **One account** → save automatically to the highest-priority config file that already exists (project > claude-project > global; if none exist yet, save to `~/.adsagent/config.json`), tell the user which was selected
3. **Multiple accounts** → show numbered list, ask user to pick, save choice to the same location
4. **Zero accounts** → direct to [adsagent.org](https://www.adsagent.org) to connect one

### Switching accounts

If the user explicitly asks to switch accounts, run `listConnectedAccounts`, let them pick, then ask:

> "Save this account for this project only, or globally?"

- **Project** → write `accountId` to `.adsagent.json` in the current working directory (create the file if needed)
- **Global** → write `accountId` to `~/.adsagent/config.json`

## Step 4: Calling tools

Use whichever MCP server prefix was detected:

- **AdsAgent MCP (default):** `mcp__adsagent__<toolName>` with `accountId` parameter
- **Google's official MCP:** `mcp__google_ads_mcp__<toolName>`

Always pass `accountId` from the resolved config (Step 1) to every tool call (except `listConnectedAccounts`).

### Prefer GAQL for multi-campaign reads

When a workflow needs data from 2+ campaigns, use `runGaqlQuery` with bulk queries instead of per-campaign helper calls. See `../shared/gaql-cookbook.md` for ready-to-use query patterns. This typically reduces API calls from `N × data_types` to just the number of data types (e.g., 7 queries instead of 30+). Fall back to per-campaign helpers if GAQL errors or you need >50 rows for a single campaign.

## Step 5: Proceed

Config is loaded. Hand control back to the invoking skill.
