#!/usr/bin/env python3
"""Pre-flight check for Strapi integration.

Verifies STRAPI_URL and STRAPI_API_KEY are set, tests connectivity,
detects API version (v4 or v5), and confirms the content type is accessible.
Credentials are loaded from environment variables or .env files.

No external dependencies — uses only Python stdlib.

Exit codes:
  0 — Strapi connection ready
  1 — unrecoverable error (missing config, auth failed, wrong content type, etc.)
  2 — Strapi not configured (STRAPI_URL not set) — non-fatal, caller skips
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

    url = get("STRAPI_URL").rstrip("/")
    api_key = get("STRAPI_API_KEY")
    content_type = get("STRAPI_CONTENT_TYPE") or "articles"
    version_hint = get("STRAPI_VERSION")  # "4" or "5" — explicit override
    return url, api_key, content_type, version_hint


# ── Security: SSRF protection ─────────────────────────────────────────────────

def _is_private_ip(ip_str):
    """Return True if the IP is loopback, private, link-local, or reserved."""
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_loopback or addr.is_private or addr.is_link_local or addr.is_reserved
    except ValueError:
        return False


def _hostname_resolves_to_internal(hostname):
    """Resolve hostname and check if any address is internal. Non-fatal on DNS failure."""
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        for info in infos:
            ip = info[4][0]
            if _is_private_ip(ip):
                return True, ip
    except (socket.gaierror, OSError):
        pass
    return False, None


def validate_url(url):
    """Validate URL scheme and block SSRF targets (localhost, RFC1918, link-local)."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        print("ERROR: STRAPI_URL is not a valid URL.", file=sys.stderr)
        sys.exit(1)

    if parsed.scheme not in ("http", "https"):
        print(f"ERROR: STRAPI_URL must use http:// or https:// (got '{parsed.scheme}://')", file=sys.stderr)
        sys.exit(1)

    hostname = parsed.hostname or ""
    if not hostname:
        print("ERROR: STRAPI_URL has no hostname.", file=sys.stderr)
        sys.exit(1)

    # If the hostname is a literal IP, check it directly via ipaddress (no DNS needed).
    # If it's a hostname, fall through to the DNS-based check below.
    if _is_private_ip(hostname):
        print(f"ERROR: STRAPI_URL is a private/local address ('{hostname}'). Use a public CMS URL.", file=sys.stderr)
        sys.exit(1)

    if hostname.lower() in ("localhost",):
        print(f"ERROR: STRAPI_URL points to localhost. Use a reachable CMS URL.", file=sys.stderr)
        sys.exit(1)

    # DNS-based check for hostnames that resolve to internal IPs (best-effort)
    is_internal, resolved_ip = _hostname_resolves_to_internal(hostname)
    if is_internal:
        print(f"ERROR: STRAPI_URL resolves to an internal address ({resolved_ip}). Use a public CMS URL.", file=sys.stderr)
        sys.exit(1)


# ── HTTP helper with retry ────────────────────────────────────────────────────

_RETRY_CODES = {429, 502, 503, 504}


def strapi_get(url, api_key, path, params=None, timeout=15, retries=3):
    """GET {url}{path}?{params}. Retries on transient failures with backoff."""
    full_url = f"{url}{path}"
    if params:
        full_url = f"{full_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        full_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
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
    raise last_exc  # all retries exhausted


# ── Version detection ─────────────────────────────────────────────────────────

def detect_version(data, version_hint):
    """Return 4 or 5. Explicit hint wins; otherwise infer from response structure."""
    if version_hint in ("4", "5"):
        return int(version_hint)
    items = data.get("data", [])
    if items:
        return 4 if "attributes" in items[0] else 5
    # Empty collection: cannot infer from items. Check pagination meta shape.
    # v4 pagination has "total", v5 also has "total" — not distinguishable here.
    # Fall back to v5 (newer default). User can override with STRAPI_VERSION=4.
    return 5


def publication_param(version):
    """Return the correct publication filter param for the detected Strapi version."""
    if version == 4:
        return {"publicationState": "live"}
    return {"status": "published"}


# ── Validation checks ─────────────────────────────────────────────────────────

def check_config(url, api_key):
    if not url:
        print("STRAPI_NOT_CONFIGURED: Set STRAPI_URL and STRAPI_API_KEY to enable Strapi integration.", file=sys.stderr)
        sys.exit(2)

    if not api_key:
        print("ERROR: STRAPI_API_KEY is not set.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Create a Full-access API token in Strapi admin:", file=sys.stderr)
        print("  Settings → Global settings → API Tokens → Create new API Token", file=sys.stderr)
        print("", file=sys.stderr)
        print("Then set it in .env.local:", file=sys.stderr)
        print("  STRAPI_API_KEY=your_token_here", file=sys.stderr)
        sys.exit(1)

    validate_url(url)
    print(f"Strapi URL: {url}", file=sys.stderr)


def check_connectivity(url, api_key, content_type, version_hint):
    """Probe the content type, detect version, return (version, total)."""
    # Probe without publication filter first — lets us detect version from response.
    probe_params = {"pagination[page]": 1, "pagination[pageSize]": 1}
    try:
        data = strapi_get(url, api_key, f"/api/{content_type}", probe_params)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200] if e.fp else "(no body)"  # truncate — don't leak stack traces
        if e.code == 401:
            print("ERROR: Strapi returned 401 Unauthorized.", file=sys.stderr)
            print("Your STRAPI_API_KEY is invalid or expired.", file=sys.stderr)
            print("Regenerate it in: Settings → API Tokens", file=sys.stderr)
            sys.exit(1)
        if e.code == 403:
            print("ERROR: Strapi returned 403 Forbidden.", file=sys.stderr)
            print(f"The API token lacks permission to read '{content_type}'.", file=sys.stderr)
            print("Use a Full-access token or grant find/findOne permissions.", file=sys.stderr)
            sys.exit(1)
        if e.code == 404:
            print(f"ERROR: Content type '{content_type}' not found (404).", file=sys.stderr)
            print("Check the plural API ID in Strapi admin:", file=sys.stderr)
            print("  Content-Type Builder → [your type] → API ID (plural)", file=sys.stderr)
            print("Override with: STRAPI_CONTENT_TYPE=blog-posts  (in .env.local)", file=sys.stderr)
            sys.exit(1)
        print(f"ERROR: Strapi API error {e.code}. Response: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot reach Strapi at {url}", file=sys.stderr)
        print(f"  Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    version = detect_version(data, version_hint)

    # Now fetch published count with the correct version-specific param
    pub_params = {"pagination[page]": 1, "pagination[pageSize]": 1, **publication_param(version)}
    try:
        pub_data = strapi_get(url, api_key, f"/api/{content_type}", pub_params)
    except Exception:
        pub_data = data  # fall back to probe result

    total = pub_data.get("meta", {}).get("pagination", {}).get("total", 0)

    if version_hint and version_hint not in ("4", "5"):
        print(f"WARNING: STRAPI_VERSION='{version_hint}' is invalid. Use '4' or '5'. Detected v{version}.", file=sys.stderr)

    print(f"Strapi v{version} detected | content type: {content_type} | {total} published entries", file=sys.stderr)
    return version, total


def main():
    url, api_key, content_type, version_hint = get_config()
    check_config(url, api_key)
    version, total = check_connectivity(url, api_key, content_type, version_hint)
    if total == 0:
        print(f"WARNING: No published entries found in '{content_type}'.", file=sys.stderr)
        if not version_hint:
            print("  If this is a v4 instance with live content, set STRAPI_VERSION=4 in .env.local", file=sys.stderr)
    print(f"OK: Strapi ready (v{version}, {content_type}, {total} published)", file=sys.stderr)


if __name__ == "__main__":
    main()
