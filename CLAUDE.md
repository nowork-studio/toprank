# Toprank — Public Claude Code Plugin

**This is the public, open-source repository that ships to all customers and the community.**

Toprank is a Claude Code plugin providing SEO and Google Ads skills. It is distributed via the `nowork-studio` marketplace and installed by end users into Claude Code / Claude Desktop. Every change here is user-facing.

## Repository purpose

- Home of the `toprank` plugin — the public artifact customers install.
- Contains skills under `google-ads/`, `seo/`, `gemini/`, and `toprank-upgrade-skill/`.
- Registered via `.claude-plugin/plugin.json` (skills list) and `.claude-plugin/marketplace.json` (plugin metadata).
- Paired with the AdsAgent MCP server (`https://www.adsagent.org`) for Google Ads write operations, and with Google Search Console for SEO reads.

## Critical: this ships to users

- Treat every commit as a release candidate. Broken skills, bad prompts, or missing files become customer bug reports.
- Never add internal-only notes, secrets, credentials, dev scratch files, or references to private infra. This repo is public.
- Test skills end-to-end before shipping — `SKILL.md` frontmatter (`name`, `description`, triggers) is how Claude decides to invoke them; typos or stale descriptions break discovery.

## When adding or modifying a skill

1. Create/edit the skill directory under the appropriate category (`google-ads/`, `seo/`, etc.) with a `SKILL.md` containing valid frontmatter.
2. **Register it in `.claude-plugin/plugin.json`** under the `skills` array. A skill that exists on disk but isn't listed here will NOT appear in the installed plugin — this has already bitten us once with `ads-landing`.
3. Bump the version in three places so upgrades propagate:
   - `.claude-plugin/plugin.json` → `version`
   - `.claude-plugin/marketplace.json` → both `metadata.version` and `plugins[0].version`
   - `VERSION` file at repo root
4. Update `CHANGELOG.md` with a user-facing note.
5. Verify locally, then ship via `/ship`. Users pick up the new version through `toprank:toprank-upgrade`.

## Versioning

Semantic-ish: bump patch for skill additions / fixes, minor for new categories or meaningful capability jumps, major for breaking skill API changes. Keep `VERSION`, `plugin.json`, and `marketplace.json` in lockstep — drift causes upgrade detection bugs.

## Related repos

- `adsagent-plugin/` (sibling dir, separate public repo) — a smaller Google-Ads-only plugin. Some skills are mirrored there; don't confuse it with this one.
- AdsAgent MCP server — private, powers the Google Ads tool calls the skills depend on.
