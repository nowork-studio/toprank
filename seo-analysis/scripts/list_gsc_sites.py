#!/usr/bin/env python3
"""List all Google Search Console properties for the authenticated account."""

import json
import os
import sys

# Allow importing gsc_auth from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gsc_auth import get_session


def list_sites(session):
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites"
    try:
        resp = session.get(url)
    except Exception as e:
        print(f"ERROR: Network failure: {e}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 403:
        error_body = resp.text
        if "SERVICE_DISABLED" in error_body or "API not enabled" in error_body:
            print("ERROR: Search Console API not enabled. Run:", file=sys.stderr)
            print("  gcloud services enable searchconsole.googleapis.com", file=sys.stderr)
            sys.exit(1)
        if "USER_PROJECT_DENIED" in error_body or "quota_project" in error_body.lower():
            print("ERROR: Quota project not set. Run:", file=sys.stderr)
            print("  gcloud auth application-default set-quota-project $(gcloud config get-value project)", file=sys.stderr)
            sys.exit(1)
        print(f"ERROR 403: {error_body}", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    return resp.json().get("siteEntry", [])


def main():
    session = get_session()
    sites = list_sites(session)

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
