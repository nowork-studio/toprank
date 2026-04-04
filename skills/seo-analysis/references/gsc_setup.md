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

## Step 1 — Install the gcloud CLI

Skip this step if you already have gcloud installed (`gcloud --version` to check).

### macOS (Homebrew)

```bash
brew install google-cloud-sdk
```

### Linux (Debian/Ubuntu)

```bash
# Install prerequisites
sudo apt-get install -y curl apt-transport-https ca-certificates gnupg

# Add the Google Cloud GPG key (modern keyring method, works on Debian 12+/Ubuntu 22.04+)
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Add the Cloud SDK apt repository
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
  https://packages.cloud.google.com/apt cloud-sdk main" \
  | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list

sudo apt-get update && sudo apt-get install -y google-cloud-cli
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
```

### Windows

```powershell
winget install Google.CloudSDK
```

Or download the installer:
https://cloud.google.com/sdk/docs/install#windows

---

## Step 2 — Initialize gcloud (First-Time Users)

Skip this step if you've used gcloud before and already have a project configured
(`gcloud config get-value project` to check).

```bash
gcloud init
```

This interactive wizard will:
1. **Log you into Google** — a browser window opens. Sign in with the account from Step 0.
2. **Select or create a GCP project** — if you don't have one, choose "Create a new project" and give it any name (e.g., `my-seo-tools`). The project is free — it's just a container for API access.

After `gcloud init` completes, verify:
```bash
gcloud config get-value project
# Should print your project name, e.g. "my-seo-tools"
```

---

## Step 3 — Enable the Search Console API

The Search Console API must be enabled in your GCP project before you can pull data.

```bash
gcloud services enable searchconsole.googleapis.com
```

This is a one-time step per project. It's free — the Search Console API has no charges.

**If you get a billing error**: Some GCP projects require a billing account even for free APIs. Either:
- Link a billing account at https://console.cloud.google.com/billing (you won't be charged for Search Console API usage)
- Or create a new project at https://console.cloud.google.com/projectcreate and try again

---

## Step 4 — Authenticate for Search Console Access (OAuth)

This is the key step. You need Application Default Credentials (ADC) with the
Search Console scopes. The `--scopes` flag is required — omitting it defaults to
the broad `cloud-platform` scope, which asks for access to BigQuery, Compute Engine,
and other services you don't need.

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly
```

A browser window opens. **Log in with the Google account from Step 0** — the one
that has access to Search Console for your site.

You'll see a consent screen asking to grant "Search Console API" access.
Click **Allow**.

The token is stored at `~/.config/gcloud/application_default_credentials.json`
and auto-refreshes — you won't need to do this again unless the token is revoked.

The scripts auto-detect the quota project from your gcloud config, so no extra
setup is needed.

---

## Step 5 — Verify Everything Works

```bash
SKILL_SCRIPTS=$(find ~/.claude/plugins ~/.claude/skills ~/.codex/skills .agents/skills -type d -name scripts -path "*seo-analysis*" 2>/dev/null | head -1)
python3 "$SKILL_SCRIPTS/list_gsc_sites.py"
```

This should list your Search Console properties. If it does, you're done.

---

## Property Types in Search Console

GSC has two types of properties:

- **Domain property**: `sc-domain:example.com` — covers all URLs, protocols, subdomains
- **URL-prefix property**: `https://example.com/` — covers only that exact prefix

Domain properties are better (more complete data). The analysis scripts handle both.

---

## Troubleshooting

**"No Search Console properties found"**: gcloud is working but the wrong Google
account is authenticated. Re-run Step 4 and log in with the account that has GSC
access (see Step 0).

**"Access Not Configured" / HTTP 403 with "API not enabled"**: The Search Console
API isn't enabled in your GCP project. Run Step 3:
```bash
gcloud services enable searchconsole.googleapis.com
```

**"The caller does not have permission"**: The authenticated account doesn't have
access to the specific GSC property. Verify at
https://search.google.com/search-console → Settings → Users and permissions.

**"insufficient_scope" or 403 on API calls despite valid token**: Your ADC token
was created without `--scopes` (which defaults to `cloud-platform`), or was set up
for a different Google service. The preflight script now detects this automatically
and re-authenticates. To fix manually, re-run Step 4:
```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly
```

**"quota project not set" / 403 with quota error**: The scripts auto-detect the
quota project from `gcloud config`. If this still fails, set it explicitly:
```bash
gcloud auth application-default set-quota-project "$(gcloud config get-value project)"
```

**"No project configured" / gcloud init never run**: Run Step 2:
```bash
gcloud init
```

**Token expired**: ADC tokens auto-refresh. If you get persistent auth errors,
re-run Step 4.

**Billing required error when enabling API**: Link a billing account at
https://console.cloud.google.com/billing — the Search Console API is free, but
some GCP projects require billing to be configured.
