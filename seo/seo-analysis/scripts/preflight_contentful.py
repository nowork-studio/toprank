#!/usr/bin/env python3
"""Pre-flight check for Contentful Content Delivery API integration.

Verifies CONTENTFUL_SPACE_ID, CONTENTFUL_DELIVERY_TOKEN, and
CONTENTFUL_CONTENT_TYPE are set, tests the Delivery API, and reports the
total published entry count for the configured content type.

No external dependencies — uses only Python stdlib.

Exit codes:
  0 — Contentful connection ready
  1 — unrecoverable error (missing config, auth failed, wrong content type, etc.)
  2 — Contentful not configured (CONTENTFUL_SPACE_ID not set) — non-fatal, caller skips
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


_RETRY_CODES = {429, 502, 503, 504}
_CONTENTFUL_API = "https://cdn.contentful.com"


# ── Config loading ────────────────────────────────────────────────────────────

def load_env_file(path):
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, raw_value = line.partition("=")
                key = key.strip()
                value = raw_value.strip().strip('"').strip("'")
                if key:
                    env[key] = value
    except (OSError, PermissionError):
        pass
    return env


def find_and_load_env():
    env = {}
    search = os.path.abspath(os.getcwd())
    for _ in range(6):
        for name in (".env.local", ".env"):
            candidate = os.path.join(search, name)
            if os.path.isfile(candidate):
                env.update(load_env_file(candidate))
        parent = os.path.dirname(search)
        if parent == search:
            break
        search = parent
    return env


def get_config():
    file_env = find_and_load_env()

    def get(key):
        return os.environ.get(key) or file_env.get(key, "")

    return (
        get("CONTENTFUL_SPACE_ID"),
        get("CONTENTFUL_DELIVERY_TOKEN"),
        get("CONTENTFUL_CONTENT_TYPE"),
        get("CONTENTFUL_ENVIRONMENT") or "master",
    )


# ── HTTP helper with retry ────────────────────────────────────────────────────

def contentful_get(token, path, params=None, timeout=15, retries=3):
    """GET {_CONTENTFUL_API}{path}?{params} with Bearer auth."""
    full_url = f"{_CONTENTFUL_API}{path}"
    if params:
        full_url = f"{full_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        full_url,
        headers={"Authorization": f"Bearer {token}"},
    )
    last_exc = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in _RETRY_CODES and attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  HTTP {e.code} — retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_exc = e
                continue
            raise
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  Network error ({e.reason}) — retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_exc = e
                continue
            raise
    raise last_exc


# ── Validation checks ─────────────────────────────────────────────────────────

def check_config(space_id, token, content_type):
    if not space_id:
        print("CONTENTFUL_NOT_CONFIGURED: Set CONTENTFUL_SPACE_ID and CONTENTFUL_DELIVERY_TOKEN to enable Contentful integration.", file=sys.stderr)
        sys.exit(2)

    if not token:
        print("ERROR: CONTENTFUL_DELIVERY_TOKEN is not set.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Create a Content Delivery API key in Contentful:", file=sys.stderr)
        print("  Settings → API Keys → Add API Key → copy Content Delivery API - access token", file=sys.stderr)
        print("", file=sys.stderr)
        print("Then set it in .env.local:", file=sys.stderr)
        print("  CONTENTFUL_DELIVERY_TOKEN=your_token_here", file=sys.stderr)
        sys.exit(1)

    if not content_type:
        print("ERROR: CONTENTFUL_CONTENT_TYPE is not set.", file=sys.stderr)
        print("Set the content type API ID in .env.local:", file=sys.stderr)
        print("  CONTENTFUL_CONTENT_TYPE=blogPost", file=sys.stderr)
        print("Find it in: Content model → [your type] → API Identifier", file=sys.stderr)
        sys.exit(1)

    print(f"Contentful space: {space_id}", file=sys.stderr)


def check_connectivity(space_id, token, content_type, environment):
    """Probe the space and content type, return total entry count."""
    # First verify auth by fetching the space
    try:
        contentful_get(token, f"/spaces/{space_id}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("ERROR: Contentful returned 401 Unauthorized.", file=sys.stderr)
            print("Your CONTENTFUL_DELIVERY_TOKEN is invalid or expired.", file=sys.stderr)
            print("Regenerate it in: Settings → API Keys", file=sys.stderr)
            sys.exit(1)
        if e.code == 404:
            print(f"ERROR: Space '{space_id}' not found (404).", file=sys.stderr)
            print("Check CONTENTFUL_SPACE_ID in Settings → General Settings.", file=sys.stderr)
            sys.exit(1)
        # Non-fatal for space check — content type check below will surface the real error
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot reach Contentful API.", file=sys.stderr)
        print(f"  Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Verify content type and get count
    try:
        data = contentful_get(token, f"/spaces/{space_id}/environments/{environment}/entries", {
            "content_type": content_type,
            "limit": 1,
        })
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300] if e.fp else "(no body)"
        if e.code == 400:
            print(f"ERROR: Contentful returned 400 Bad Request.", file=sys.stderr)
            print(f"Content type '{content_type}' may not exist.", file=sys.stderr)
            print("Check CONTENTFUL_CONTENT_TYPE — find it in: Content model → [your type] → API Identifier", file=sys.stderr)
            sys.exit(1)
        if e.code == 404:
            print(f"ERROR: Environment '{environment}' not found.", file=sys.stderr)
            print(f"Check CONTENTFUL_ENVIRONMENT (default: master).", file=sys.stderr)
            sys.exit(1)
        print(f"ERROR: Contentful API error {e.code}. Response: {body}", file=sys.stderr)
        sys.exit(1)

    total = data.get("total", 0)
    print(f"Contentful ready | space: {space_id} | env: {environment} | content type: {content_type} | {total} entries", file=sys.stderr)
    return total


def main():
    space_id, token, content_type, environment = get_config()
    check_config(space_id, token, content_type)
    total = check_connectivity(space_id, token, content_type, environment)
    if total == 0:
        print(f"WARNING: No entries found in content type '{content_type}'.", file=sys.stderr)
    print(f"OK: Contentful ready ({content_type}, {total} entries)", file=sys.stderr)


if __name__ == "__main__":
    main()
