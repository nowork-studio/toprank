#!/usr/bin/env python3
"""List all Google Search Console properties for the authenticated account."""

import json
import subprocess
import sys
import urllib.request
import urllib.error


def get_access_token():
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("ERROR: Could not get access token. Run:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print("    --scopes=https://www.googleapis.com/auth/webmasters.readonly", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def list_sites(token):
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("siteEntry", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def main():
    token = get_access_token()
    sites = list_sites(token)

    if not sites:
        print("No Search Console properties found for this account.")
        print("Make sure you're logged in with the right Google account.")
        sys.exit(0)

    print(f"Found {len(sites)} Search Console properties:\n")
    for i, site in enumerate(sites, 1):
        ptype = "Domain" if site["siteUrl"].startswith("sc-domain:") else "URL-prefix"
        level = site.get("permissionLevel", "unknown")
        print(f"  {i}. {site['siteUrl']}")
        print(f"     Type: {ptype} | Permission: {level}")

    # Also output as JSON for machine parsing
    with open("/tmp/gsc_sites.json", "w") as f:
        json.dump(sites, f, indent=2)
    print(f"\n(Full list saved to /tmp/gsc_sites.json)")


if __name__ == "__main__":
    main()
