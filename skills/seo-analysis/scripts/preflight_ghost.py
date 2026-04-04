#!/usr/bin/env python3
"""Pre-flight check for Ghost Content API integration.

Verifies GHOST_URL and GHOST_CONTENT_KEY are set, tests connectivity
via the Ghost Content API, and reports the total published entry count.

Supports Ghost 4.x+ (/ghost/api/content/) and 3.x (/ghost/api/v3/content/).
No external dependencies — uses only Python stdlib.

Exit codes:
  0 — Ghost connection ready
  1 — unrecoverable error (missing config, auth failed, etc.)
  2 — Ghost not configured (GHOST_URL not set) — non-fatal, caller skips
"""

import ipaddress
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


_RETRY_CODES = {429, 502, 503, 504}
# API path candidates: try newest first, fall back to v3
_API_PATHS = ["/ghost/api/content", "/ghost/api/v3/content"]


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

    url = get("GHOST_URL").rstrip("/")
    content_key = get("GHOST_CONTENT_KEY")
    content_type = get("GHOST_CONTENT_TYPE") or "posts"
    return url, content_key, content_type


# ── Security: SSRF protection ─────────────────────────────────────────────────

def _is_private_ip(ip_str):
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_loopback or addr.is_private or addr.is_link_local or addr.is_reserved
    except ValueError:
        return False


def validate_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        print("ERROR: GHOST_URL is not a valid URL.", file=sys.stderr)
        sys.exit(1)

    if parsed.scheme not in ("http", "https"):
        print(f"ERROR: GHOST_URL must use http:// or https:// (got '{parsed.scheme}://')", file=sys.stderr)
        sys.exit(1)

    hostname = parsed.hostname or ""
    if not hostname:
        print("ERROR: GHOST_URL has no hostname.", file=sys.stderr)
        sys.exit(1)

    if _is_private_ip(hostname):
        print(f"ERROR: GHOST_URL is a private/local address ('{hostname}'). Use a public Ghost URL.", file=sys.stderr)
        sys.exit(1)

    if hostname.lower() == "localhost":
        print("ERROR: GHOST_URL points to localhost. Use a reachable Ghost URL.", file=sys.stderr)
        sys.exit(1)

    try:
        for info in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM):
            if _is_private_ip(info[4][0]):
                print(f"ERROR: GHOST_URL resolves to an internal address ({info[4][0]}). Use a public Ghost URL.", file=sys.stderr)
                sys.exit(1)
    except (socket.gaierror, OSError):
        pass


# ── HTTP helper with retry ────────────────────────────────────────────────────

def ghost_get(url, api_path, content_key, resource, params=None, timeout=15, retries=3):
    """GET {url}{api_path}/{resource}/?key={key}&{params}."""
    all_params = {"key": content_key, **(params or {})}
    full_url = f"{url}{api_path}/{resource}/?{urllib.parse.urlencode(all_params)}"
    req = urllib.request.Request(full_url, headers={"Accept-Version": "v5.0"})
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

def check_config(url, content_key):
    if not url:
        print("GHOST_NOT_CONFIGURED: Set GHOST_URL and GHOST_CONTENT_KEY to enable Ghost integration.", file=sys.stderr)
        sys.exit(2)

    if not content_key:
        print("ERROR: GHOST_CONTENT_KEY is not set.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Create a Content API key in Ghost admin:", file=sys.stderr)
        print("  Settings → Integrations → Add custom integration → copy Content API Key", file=sys.stderr)
        print("", file=sys.stderr)
        print("Then set it in .env.local:", file=sys.stderr)
        print("  GHOST_CONTENT_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    validate_url(url)
    print(f"Ghost URL: {url}", file=sys.stderr)


def check_connectivity(url, content_key, content_type):
    """Try each API path version; return (api_path, total)."""
    last_error = None

    for api_path in _API_PATHS:
        try:
            data = ghost_get(url, api_path, content_key, content_type, {"limit": 1, "fields": "id"})
            total = data.get("meta", {}).get("pagination", {}).get("total", 0)
            version = "v4+" if "/v3/" not in api_path else "v3"
            print(f"Ghost {version} detected | content type: {content_type} | {total} published entries", file=sys.stderr)
            return api_path, total
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("ERROR: Ghost returned 403 Forbidden.", file=sys.stderr)
                print("Your GHOST_CONTENT_KEY is invalid or has been revoked.", file=sys.stderr)
                print("Regenerate it in: Settings → Integrations", file=sys.stderr)
                sys.exit(1)
            if e.code == 404 and api_path == _API_PATHS[-1]:
                print(f"ERROR: Could not find Ghost Content API at {url}", file=sys.stderr)
                print("Check that GHOST_URL points to your Ghost instance (not a CDN/proxy URL).", file=sys.stderr)
                sys.exit(1)
            last_error = e
            continue
        except urllib.error.URLError as e:
            print(f"ERROR: Cannot reach Ghost at {url}", file=sys.stderr)
            print(f"  Network error: {e.reason}", file=sys.stderr)
            sys.exit(1)

    if last_error:
        body = last_error.read().decode()[:200] if last_error.fp else "(no body)"
        print(f"ERROR: Ghost API error {last_error.code}. Response: {body}", file=sys.stderr)
    sys.exit(1)


def main():
    url, content_key, content_type = get_config()
    check_config(url, content_key)
    api_path, total = check_connectivity(url, content_key, content_type)
    if total == 0:
        print(f"WARNING: No published entries found in '{content_type}'.", file=sys.stderr)
    print(f"OK: Ghost ready ({content_type}, {total} published)", file=sys.stderr)


if __name__ == "__main__":
    main()
