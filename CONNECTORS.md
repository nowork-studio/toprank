# Connectors

Toprank skills reference external tools using the `~~category` placeholder pattern. This makes skills tool-agnostic — they work with any MCP server that provides the required capability.

## Connected Tools

| Category | Placeholder | Default Server | Alternatives |
|----------|-------------|---------------|--------------|
| Google Ads | `~~google-ads` | [AdsAgent MCP](https://www.adsagent.org) (`mcp__adsagent__*`) | Google Ads MCP (`mcp__google_ads_mcp__*`) |
| Search Console | `~~search-console` | gcloud CLI + Search Console API | Any GSC-compatible MCP server |
| CMS | `~~cms` | Direct API (WordPress REST, Strapi, Contentful, Ghost) | Any CMS MCP server |

## How Connectors Work

Skills use conditional blocks based on available tools:

```markdown
If ~~google-ads is connected:
- Pull campaign performance data
- Manage keywords and bids

If ~~search-console is connected:
- Fetch GSC performance data
- Run URL Inspection API checks
```

If a connector is not available, the skill gracefully degrades — for example, `seo-analysis` can still run a technical crawl without GSC data.

## Setup

### Google Ads (used by: ads, ads-audit, ads-copy)

See `google-ads/shared/preamble.md`. Requires:
1. AdsAgent API key from [adsagent.org](https://www.adsagent.org)
2. Set `ADSAGENT_API_KEY` environment variable
3. The `.mcp.json` in this plugin auto-configures the MCP server

### Search Console (used by: seo-analysis)

See `seo/shared/preamble.md`. Requires:
1. Google Cloud SDK (`gcloud`) installed
2. Search Console API enabled on your GCP project
3. OAuth login with the Google account that owns your GSC properties

### CMS (used by: seo-analysis, setup-cms)

Run `/setup-cms` to configure. Supports WordPress, Strapi, Contentful, and Ghost.
Credentials are saved to `.env.local` in the project root.
