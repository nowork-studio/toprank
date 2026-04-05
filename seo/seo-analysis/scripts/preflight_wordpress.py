#!/usr/bin/env python3
"""Pre-flight check for WordPress REST API integration.

Verifies WP_URL, WP_USERNAME, and WP_APP_PASSWORD are set, tests connectivity
via the WordPress REST API, detects installed SEO plugins (Yoast, RankMath),
and reports the total published entry count.

Uses WordPress Application Passwords (WP 5.6+) for authentication.
No external dependencies — uses only Python stdlib.

Exit codes:
  0 — WordPress connection ready
  1 — unrecoverable error (missing config, auth failed, wrong content type, etc.)
  2 — WordPress not configured (WP_URL not set) — non-fatal, caller skips
"""

import base64
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

    url = get("WP_URL").rstrip("/")
    username = get("WP_USERNAME")
    app_password = get("WP_APP_PASSWORD")
    content_type = get("WP_CONTENT_TYPE") or "posts"
    return url, username, app_password, content_type


# ── Security: SSRF protection ─────────────────────────────────────────────────

def _is_private_ip(ip_str):
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_loopback or addr.is_private or addr.is_link_local or addr.is_reserved
    except ValueError:
        return False


def validate_url(url):
    """Validate URL scheme and block SSRF targets."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        print("ERROR: WP_URL is not a valid URL.", file=sys.stderr)
        sys.exit(1)

    if parsed.scheme not in ("http", "https"):
        print(f"ERROR: WP_URL must use http:// or https:// (got '{parsed.scheme}://')", file=sys.stderr)
        sys.exit(1)

    hostname = parsed.hostname or ""
    if not hostname:
        print("ERROR: WP_URL has no hostname.", file=sys.stderr)
        sys.exit(1)

    if _is_private_ip(hostname):
        print(f"ERROR: WP_URL is a private/local address ('{hostname}'). Use a public WordPress URL.", file=sys.stderr)
        sys.exit(1)

    if hostname.lower() == "localhost":
        print("ERROR: WP_URL points to localhost. Use a reachable WordPress URL.", file=sys.stderr)
        sys.exit(1)

    try:
        for info in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM):
            if _is_private_ip(info[4][0]):
                print(f"ERROR: WP_URL resolves to an internal address ({info[4][0]}). Use a public WordPress URL.", file=sys.stderr)
                sys.exit(1)
    except (socket.gaierror, OSError):
        pass  # non-fatal; let the request fail naturally


# ── HTTP helper ───────────────────────────────────────────────────────────────

def wp_get(url, auth_header, path, params=None, timeout=15, retries=3):
    """GET {url}{path}?{params} with Basic auth. Retries on transient failures."""
    full_url = f"{url}{path}"
    if params:
        full_url = f"{full_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        full_url,
        headers={"Authorization": auth_header, "Accept": "application/json"},
    )
    last_exc = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read())
                total = int(resp.headers.get("X-WP-Total", 0))
                total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
                return body, total, total_pages
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


def make_auth_header(username, app_password):
    """Build Basic auth header from WP username + Application Password."""
    # Application Passwords are displayed with spaces for readability — strip them.
    password = app_password.replace(" ", "")
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {credentials}"


# ── Validation checks ─────────────────────────────────────────────────────────

def check_config(url, username, app_password):
    if not url:
        print("WP_NOT_CONFIGURED: Set WP_URL, WP_USERNAME, and WP_APP_PASSWORD to enable WordPress integration.", file=sys.stderr)
        sys.exit(2)

    if not username:
        print("ERROR: WP_USERNAME is not set.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Set your WordPress username in .env.local:", file=sys.stderr)
        print("  WP_USERNAME=your_username", file=sys.stderr)
        sys.exit(1)

    if not app_password:
        print("ERROR: WP_APP_PASSWORD is not set.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Create an Application Password in WordPress admin:", file=sys.stderr)
        print("  Users → Profile → Application Passwords → Add New Application Password", file=sys.stderr)
        print("", file=sys.stderr)
        print("Then set it in .env.local:", file=sys.stderr)
        print("  WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx", file=sys.stderr)
        sys.exit(1)

    validate_url(url)
    print(f"WordPress URL: {url}", file=sys.stderr)


def check_connectivity(url, auth_header, content_type):
    """Probe the REST API, detect SEO plugins, return total published count."""
    try:
        items, total, _ = wp_get(url, auth_header, f"/wp-json/wp/v2/{content_type}", {
            "status": "publish",
            "per_page": 1,
            "_fields": "id,yoast_head_json",
        })
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300] if e.fp else "(no body)"
        if e.code == 401:
            print("ERROR: WordPress returned 401 Unauthorized.", file=sys.stderr)
            print("Your WP_USERNAME or WP_APP_PASSWORD is invalid.", file=sys.stderr)
            print("Regenerate the Application Password in: Users → Profile → Application Passwords", file=sys.stderr)
            sys.exit(1)
        if e.code == 403:
            print("ERROR: WordPress returned 403 Forbidden.", file=sys.stderr)
            print(f"The user '{content_type}' may not have REST API access.", file=sys.stderr)
            sys.exit(1)
        if e.code == 404:
            print(f"ERROR: Content type '{content_type}' not found (404).", file=sys.stderr)
            print("Check the content type slug. Common values: posts, pages.", file=sys.stderr)
            print("Override with: WP_CONTENT_TYPE=your-type  (in .env.local)", file=sys.stderr)
            sys.exit(1)
        print(f"ERROR: WordPress API error {e.code}. Response: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot reach WordPress at {url}", file=sys.stderr)
        print(f"  Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Detect SEO plugins from first item's fields
    seo_plugin = "none detected"
    if items:
        item = items[0] if isinstance(items, list) else items
        if "yoast_head_json" in item:
            seo_plugin = "Yoast SEO"

    if seo_plugin == "none detected":
        # Check REST API namespaces for plugin detection
        try:
            ns_data, _, _ = wp_get(url, auth_header, "/wp-json/", timeout=10, retries=1)
            namespaces = ns_data.get("namespaces", [])
            if any(ns.startswith("yoast") for ns in namespaces):
                seo_plugin = "Yoast SEO"
            elif any(ns.startswith("rankmath") for ns in namespaces):
                seo_plugin = "RankMath"
        except Exception:
            pass

    print(f"WordPress REST API ready | content type: {content_type} | {total} published | SEO plugin: {seo_plugin}", file=sys.stderr)
    return total, seo_plugin


def main():
    url, username, app_password, content_type = get_config()
    check_config(url, username, app_password)
    auth_header = make_auth_header(username, app_password)
    total, seo_plugin = check_connectivity(url, auth_header, content_type)
    if total == 0:
        print(f"WARNING: No published entries found in '{content_type}'.", file=sys.stderr)
    print(f"OK: WordPress ready ({content_type}, {total} published, {seo_plugin})", file=sys.stderr)


if __name__ == "__main__":
    main()
