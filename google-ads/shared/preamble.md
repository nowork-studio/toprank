# Google Ads Shared Preamble

Every google-ads skill reads this before doing anything else. It handles updates, API key verification, MCP detection, config resolution, and onboarding in one place — so individual skills don't repeat this logic.

## Step 0: Check for toprank updates

```bash
_UPD_BIN=$(ls ~/.claude/plugins/cache/nowork-studio/toprank/*/bin/toprank-update-check 2>/dev/null | head -1)
[ -n "$_UPD_BIN" ] && _UPD=$("$_UPD_BIN" 2>/dev/null || true) || _UPD=""
[ -n "$_UPD" ] && echo "$_UPD" || true
```

If the output contains `UPGRADE_AVAILABLE <old> <new>`: immediately follow the inline upgrade flow in the `/toprank-upgrade` skill (Step 1 onward) to auto-upgrade. After the upgrade completes, re-read the updated preamble from the new plugin cache and restart from Step 1 (the upgrade check itself doesn't need to run again).

If the output contains `JUST_UPGRADED <old> <new>`: mention "toprank upgraded from v{old} to v{new}" briefly, then continue to Step 1.

If neither: continue to Step 1 silently.

## Step 1: Verify API key — BLOCKING

The MCP server authenticates via the `ADSAGENT_API_KEY` environment variable, which Claude Code injects from `~/.claude/settings.json`. Without it, no MCP tools will work — so this check must happen before anything else.

**You MUST execute this step. Do NOT skip it. Do NOT check environment variables — you MUST read the file.**

1. Use the Read tool to read `~/.claude/settings.json`.
2. Parse the JSON and check if `env.ADSAGENT_API_KEY` exists and is a non-empty string.

**If the key exists and is non-empty:** proceed to Step 2 silently.

**If the key is missing, the `env` object doesn't exist, or the file doesn't exist:** you MUST stop and do the following — do NOT proceed to any other step, do NOT fulfill the user's request:

1. Output this message and STOP (do not call any tools, do not continue — just output this text and end your turn):

   > To use Google Ads features, you need an AdsAgent API key.
   > Sign up at [adsagent.org](https://adsagent.org) to get your key, then paste it below.

2. When the user replies with their key, read `~/.claude/settings.json` again (use `{}` if it doesn't exist). Deep-merge the key into the existing JSON — preserve all existing top-level fields and all existing keys within the `env` object. Only add/overwrite `ADSAGENT_API_KEY`:
   ```json
   {
     "...existing fields preserved...",
     "env": {
       "...existing env vars preserved...",
       "ADSAGENT_API_KEY": "<the key the user provided>"
     }
   }
   ```
   Write the updated JSON back to `~/.claude/settings.json` using the Write tool.

3. Tell the user the key has been saved. Note: the MCP server won't pick up the new key until Claude Code restarts. If MCP tools fail in Step 3, advise the user to restart Claude Code and re-run their command. Then proceed to Step 2.

## Step 2: Resolve config

Read config from three locations and merge fields (first non-null, non-empty-string value wins per field):

1. **Project-level** — `.adsagent.json` in the repository root (Claude Code's working directory)
2. **Claude project-level** — `~/.claude/projects/{project-path}/adsagent.json` (where `{project-path}` is the CWD-based path Claude Code uses for project memory, e.g. `-Users-alice-repos-petshop`)
3. **Global fallback** — `~/.adsagent/config.json`

Each file uses the same schema: `{ "accountId": "..." }`. Fields merge up the chain — a project file with only `accountId` inherits from global.

The API key is stored separately in `~/.claude/settings.json` under `env.ADSAGENT_API_KEY` (not in config files — the MCP server reads it from the environment).

### Resolved data directory

Data files (business-context, personas, change-log, account-baseline) are stored project-locally when a project-level config exists:

- If `.adsagent.json` exists in the current working directory → `{data_dir}` = `.adsagent/` (relative to project root)
- Otherwise → `{data_dir}` = `~/.adsagent/` (the Claude project-level config alone doesn't trigger project-local data — only a `.adsagent.json` in the repo does)

Create `{data_dir}` if it doesn't exist. Ensure `~/.adsagent/` also exists (needed for the global config file regardless of `{data_dir}`). Throughout this document and all skills, `{data_dir}` refers to this resolved directory.

**Important:** If using project-local storage (`.adsagent/`), ensure `.adsagent.json` and `.adsagent/` are in the project's `.gitignore` — they contain business-sensitive data that should not be committed.

Continue to Step 3 (MCP detection always runs).

## Step 3: MCP Server Detection

Always verify that a Google Ads MCP server is available — the MCP server could be down or misconfigured even with a valid API key and saved accountId.

1. Check for AdsAgent tools: try calling `mcp__adsagent__listConnectedAccounts` — save the result for reuse in Step 4
2. If not found, check for Google's official MCP: look for tools matching `mcp__google_ads_mcp__*` in the available tools
3. If neither exists, guide the user:

> No Google Ads MCP server detected.
>
> Your API key is configured, but the MCP server may not have started. Try restarting Claude Code — the toprank plugin's .mcp.json will auto-configure the server using your key.
>
> If the problem persists, check your MCP server settings or configure a Google Ads MCP server manually.

Stop here until the MCP server is available.

If `accountId` was already resolved in Step 2, skip to Step 5. Otherwise, continue to Step 4.

## Step 4: Onboarding (only if accountId is missing)

Use the `listConnectedAccounts` result from Step 3 (do not call it again):

1. **One account** → save automatically to the highest-priority config file that already exists (project > claude-project > global; if none exist yet, save to `~/.adsagent/config.json`), tell the user which was selected
2. **Multiple accounts** → show numbered list, ask user to pick, save choice to the same location
3. **Zero accounts** → direct to [adsagent.org](https://www.adsagent.org) to connect one

### Switching accounts

If the user explicitly asks to switch accounts, run `listConnectedAccounts`, let them pick, then ask:

> "Save this account for this project only, or globally?"

- **Project** → write `accountId` to `.adsagent.json` in the current working directory (create the file if needed)
- **Global** → write `accountId` to `~/.adsagent/config.json`

## Step 5: Calling tools

Use whichever MCP server prefix was detected:

- **AdsAgent MCP (default):** `mcp__adsagent__<toolName>` with `accountId` parameter
- **Google's official MCP:** `mcp__google_ads_mcp__<toolName>`

Always pass `accountId` from the resolved config (Step 2) to every tool call (except `listConnectedAccounts`).

### Prefer GAQL for multi-campaign reads

When a workflow needs data from 2+ campaigns, use `runGaqlQuery` with bulk queries instead of per-campaign helper calls. See `../shared/gaql-cookbook.md` for ready-to-use query patterns. This typically reduces API calls from `N × data_types` to just the number of data types (e.g., 7 queries instead of 30+). Fall back to per-campaign helpers if GAQL errors or you need >50 rows for a single campaign.

Config is loaded. Hand control back to the invoking skill.
