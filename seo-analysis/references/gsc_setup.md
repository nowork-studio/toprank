# Google Search Console API Setup Guide

## The Fastest Path: gcloud Application Default Credentials

If gcloud is installed, this is a single command:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

A browser window opens. Log in with the Google account that has access to Search Console for the site. Done. The token is stored at `~/.config/gcloud/application_default_credentials.json` and auto-refreshes.

**Verify it worked:**
```bash
gcloud auth application-default print-access-token
```
Should print a long token string (not an error).

---

## If gcloud Is Not Installed

### Option A: Install gcloud (recommended, ~5 min)

```bash
# macOS with Homebrew
brew install google-cloud-sdk

# Then authenticate
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

### Option B: OAuth Desktop App Flow (no gcloud)

1. Go to https://console.cloud.google.com/
2. Create a new project (or use an existing one)
3. Enable the **Google Search Console API**:
   - Go to APIs & Services → Library
   - Search "Search Console API" → Enable
4. Create credentials:
   - Go to APIs & Services → Credentials
   - Create credentials → OAuth client ID
   - Application type: Desktop app
   - Download the JSON file as `credentials.json`
5. Run the auth flow:
   ```bash
   python3 /path/to/skills/seo-analysis/scripts/oauth_setup.py \
     --credentials credentials.json
   ```
   This opens a browser, you authorize, and a `token.json` is saved.

---

## Checking Which Google Account Has GSC Access

Not sure which account has Search Console access? Check at:
https://search.google.com/search-console

The account you log in with there is the one to use for `gcloud auth application-default login`.

---

## Property Types in Search Console

GSC has two types of properties:

- **Domain property**: `sc-domain:example.com` — covers all URLs, protocols, subdomains
- **URL-prefix property**: `https://example.com/` — covers only that exact prefix

Domain properties are better (more complete data). The analysis scripts handle both.

---

## Troubleshooting

**"Access Not Configured" error**: The Search Console API isn't enabled in your GCP project. Run:
```bash
gcloud services enable searchconsole.googleapis.com
```

**"The caller does not have permission" error**: The authenticated account doesn't have access to the GSC property. Verify at https://search.google.com/search-console → Settings → Users and permissions.

**Token expired**: ADC tokens auto-refresh. If you get auth errors, re-run:
```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```
