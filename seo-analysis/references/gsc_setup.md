# Google Search Console API Setup Guide

## Step 0 — Which Google Account Has GSC Access?

This is the most common source of confusion. You need to authenticate with the
**exact Google account** that has access to Search Console for this site.

Check which account it is:
1. Go to https://search.google.com/search-console
2. Note which Google account you're logged in as (top-right corner)
3. Use that same account in all the steps below

If you have multiple Google accounts (work email, personal Gmail, different org),
make sure you pick the right one. A valid gcloud token from the wrong account will
appear to work but return no GSC properties.

---

## The Fastest Path: gcloud Application Default Credentials

Two steps: install the Python dependency, then authenticate.

```bash
pip install google-auth
```

Then authenticate with a single command:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

A browser window opens. Log in with the Google account from Step 0. Done. The
token auto-refreshes and is stored at
`~/.config/gcloud/application_default_credentials.json`.

The scripts auto-detect the quota project from your gcloud config, so no extra
setup is needed.

**Verify it worked** (should list your GSC properties):
```bash
SKILL_SCRIPTS=$(find ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
python3 "$SKILL_SCRIPTS/list_gsc_sites.py"
```

---

## If gcloud Is Not Installed

### macOS (Homebrew)

```bash
brew install google-cloud-sdk

# Then authenticate
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

### Linux (Debian/Ubuntu)

```bash
# Install prerequisites (curl may already be present)
sudo apt-get install -y curl apt-transport-https ca-certificates gnupg

# Add the Google Cloud GPG key (modern keyring method, works on Debian 12+/Ubuntu 22.04+)
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Add the Cloud SDK apt repository
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
  https://packages.cloud.google.com/apt cloud-sdk main" \
  | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list

sudo apt-get update && sudo apt-get install -y google-cloud-cli

# Then authenticate
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

### Linux (RPM/Fedora/RHEL)

```bash
sudo tee /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el8-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM
sudo dnf install google-cloud-cli

# Then authenticate
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

### Windows

Download and run the installer from:
https://cloud.google.com/sdk/docs/install#windows

Then in PowerShell:
```powershell
gcloud auth application-default login `
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

---

## Property Types in Search Console

GSC has two types of properties:

- **Domain property**: `sc-domain:example.com` — covers all URLs, protocols, subdomains
- **URL-prefix property**: `https://example.com/` — covers only that exact prefix

Domain properties are better (more complete data). The analysis scripts handle both.

---

## Troubleshooting

**"No Search Console properties found"**: gcloud is working but the wrong Google
account is authenticated. Re-run `gcloud auth application-default login` and log
in with the account that has GSC access (see Step 0 above).

**"Access Not Configured" / HTTP 403 with "API not enabled"**: The Search Console
API isn't enabled in your GCP project. Run:
```bash
gcloud services enable searchconsole.googleapis.com
```

**"The caller does not have permission"**: The authenticated account doesn't have
access to the specific GSC property. Verify at
https://search.google.com/search-console → Settings → Users and permissions.

**"insufficient_scope" or 403 on API calls despite valid token**: You have ADC
configured for a different Google service (Firebase, GCS, BigQuery, etc.) without
the `webmasters.readonly` scope. Re-run:
```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

**"quota project not set" / 403 with quota error**: The scripts auto-detect the
quota project from `gcloud config`. If this still fails, set it explicitly:
```bash
gcloud auth application-default set-quota-project "$(gcloud config get-value project)"
```

**"google-auth package not installed"**: The scripts require the `google-auth`
Python package. Install it:
```bash
pip install google-auth
```

**Token expired**: ADC tokens auto-refresh. If you get persistent auth errors,
re-run the `gcloud auth application-default login` command above.
