#!/usr/bin/env python3
"""Fetch published content from Ghost for SEO analysis.

Paginates through all published posts or pages, extracts Ghost's native SEO
fields (meta_title, meta_description), and outputs structured JSON in the
normalized CMS content format consumed by seo-analysis.

Ghost has native meta_title and meta_description fields on every post/page —
no plugin needed.

Supports Ghost 4.x+ (/ghost/api/content/) and 3.x (/ghost/api/v3/content/).
No external dependencies — uses only Python stdlib.

Usage:
  python3 fetch_ghost_content.py
  python3 fetch_ghost_content.py --content-type pages --output /tmp/ghost.json

Environment variables (or .env / .env.local):
  GHOST_URL           Required. Ghost instance URL, e.g. https://myblog.ghost.io
  GHOST_CONTENT_KEY   Required. Content API key from Settings → Integrations.
  GHOST_CONTENT_TYPE  Optional. 'posts' or 'pages' (default: posts)
"""

import argparse
import ipaddress
import json
import os
import socket
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


PAGE_SIZE = 100  # Ghost supports up to at least 100 per request
_RETRY_CODES = {429, 502, 503, 504}
_API_PATHS = ["/ghost/api/content", "/ghost/api/v3/content"]

_SEO_FIELDS = "id,title,slug,published_at,updated_at,meta_title,meta_description,og_image,og_title,og_description,twitter_title,twitter_description"


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
        get("GHOST_URL").rstrip("/"),
        get("GHOST_CONTENT_KEY"),
        get("GHOST_CONTENT_TYPE") or "posts",
    )


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
        print("ERROR: GHOST_URL must use http:// or https://", file=sys.stderr)
        sys.exit(1)
    hostname = parsed.hostname or ""
    if not hostname:
        print("ERROR: GHOST_URL has no hostname.", file=sys.stderr)
        sys.exit(1)
    if _is_private_ip(hostname):
        print(f"ERROR: GHOST_URL is a private/local address ('{hostname}').", file=sys.stderr)
        sys.exit(1)
    if hostname.lower() == "localhost":
        print("ERROR: GHOST_URL points to localhost.", file=sys.stderr)
        sys.exit(1)
    try:
        for info in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM):
            if _is_private_ip(info[4][0]):
                print(f"ERROR: GHOST_URL resolves to an internal address ({info[4][0]}).", file=sys.stderr)
                sys.exit(1)
    except (socket.gaierror, OSError):
        pass


# ── HTTP helper with retry ────────────────────────────────────────────────────

def ghost_get(base_url, api_path, content_key, resource, params, timeout=30, retries=3):
    all_params = {"key": content_key, **params}
    full_url = f"{base_url}{api_path}/{resource}/?{urllib.parse.urlencode(all_params)}"
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
            body = e.read().decode()[:200] if e.fp else "(no body)"
            print(f"ERROR: Ghost API {e.code}: {body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  Network error ({e.reason}) — retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_exc = e
                continue
            print(f"ERROR: Network error reaching Ghost: {e.reason}", file=sys.stderr)
            sys.exit(1)
    raise last_exc


def detect_api_path(base_url, content_key, content_type):
    """Try API paths in order, return the first that works.

    Uses a direct urllib probe so that 404s on the first path don't terminate
    the process — ghost_get calls sys.exit on errors, which would prevent
    the fallback from running.
    """
    for api_path in _API_PATHS:
        try:
            url = (
                f"{base_url}{api_path}/{content_type}/?"
                f"{urllib.parse.urlencode({'key': content_key, 'limit': 1, 'fields': 'id'})}"
            )
            req = urllib.request.Request(url, headers={"Accept-Version": "v5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
                return api_path
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("ERROR: Ghost returned 403 Forbidden.", file=sys.stderr)
                print("Your GHOST_CONTENT_KEY is invalid or has been revoked.", file=sys.stderr)
                print("Regenerate it in: Settings → Integrations", file=sys.stderr)
                sys.exit(1)
            # 404 = wrong API path; try next
            continue
        except urllib.error.URLError as e:
            print(f"ERROR: Cannot reach Ghost at {base_url}", file=sys.stderr)
            print(f"  Network error: {e.reason}", file=sys.stderr)
            sys.exit(1)
    print(f"ERROR: Could not find Ghost Content API at {base_url}", file=sys.stderr)
    print("Check that GHOST_URL points to your Ghost instance.", file=sys.stderr)
    sys.exit(1)


# ── Response normalisation ────────────────────────────────────────────────────

def normalise_entry(item):
    """Normalise a Ghost post/page to the shared CMS entry format."""
    # Ghost returns null for meta_title/meta_description when not explicitly set.
    # Do NOT fall back to item["title"] here — that would hide the fact that no
    # SEO override exists, causing missing_meta_title to be False for posts that
    # have never been SEO-optimized. The entry's "title" field is preserved
    # separately for display purposes.
    meta_title = item.get("meta_title") or ""
    meta_description = item.get("meta_description") or ""
    has_meta_image = bool(item.get("og_image"))
    has_meta_social = bool(item.get("og_title") or item.get("twitter_title"))

    seo = {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "has_meta_image": has_meta_image,
        "has_meta_social": has_meta_social,
    }

    meta_title_len = len(seo["meta_title"])
    meta_desc_len = len(seo["meta_description"])

    return {
        "document_id": item.get("id", ""),
        "id": item.get("id"),
        "title": item.get("title") or "",
        "slug": item.get("slug") or "",
        "published_at": item.get("published_at") or "",
        "updated_at": item.get("updated_at") or "",
        "created_at": item.get("published_at") or "",
        "locale": "",
        "seo": seo,
        "missing_meta_title": not meta_title,
        "missing_meta_description": not meta_description,
        "meta_title_too_long": meta_title_len > 60,
        "meta_description_too_long": meta_desc_len > 160,
        "meta_description_too_short": 0 < meta_desc_len < 70,
    }


# ── Pagination ────────────────────────────────────────────────────────────────

def fetch_all_entries(base_url, content_key, content_type):
    """Paginate through all published entries. Returns list of normalised entries."""
    api_path = detect_api_path(base_url, content_key, content_type)
    all_entries = []
    page = 1
    total_pages = None

    while True:
        params = {
            "limit": PAGE_SIZE,
            "page": page,
            "fields": _SEO_FIELDS,
            "order": "published_at desc",
        }

        print(f"  Fetching page {page}...", file=sys.stderr)
        data = ghost_get(base_url, api_path, content_key, content_type, params)

        items = data.get(content_type, [])
        if not items:
            break

        pagination = data.get("meta", {}).get("pagination", {})
        if total_pages is None:
            total_pages = pagination.get("pages", 1)
            total = pagination.get("total", 0)
            print(f"  {total} published {content_type} across {total_pages} page(s)", file=sys.stderr)

        for item in items:
            all_entries.append(normalise_entry(item))

        print(f"  Page {page}/{total_pages} — {len(all_entries)} fetched", file=sys.stderr)

        if page >= total_pages:
            break
        page += 1

    return all_entries


# ── SEO audit ─────────────────────────────────────────────────────────────────

def build_seo_audit(entries):
    missing_title = []
    missing_desc = []
    title_long = []
    desc_too_long = []
    desc_too_short = []
    broken_ids = set()

    for e in entries:
        broken = False
        if e["missing_meta_title"]:
            missing_title.append(e)
            broken = True
        if e["missing_meta_description"]:
            missing_desc.append(e)
            broken = True
        if e["meta_title_too_long"]:
            title_long.append(e)
            broken = True
        if e["meta_description_too_long"]:
            desc_too_long.append(e)
            broken = True
        if e["meta_description_too_short"]:
            desc_too_short.append(e)
            broken = True
        if broken:
            broken_ids.add(e["document_id"])

    return {
        "total": len(entries),
        "missing_meta_title": len(missing_title),
        "missing_meta_description": len(missing_desc),
        "meta_title_too_long": len(title_long),
        "meta_description_too_short": len(desc_too_short),
        "meta_description_too_long": len(desc_too_long),
        "complete_seo": len(entries) - len(broken_ids),
        "entries_missing_meta_title": [
            {"document_id": e["document_id"], "title": e["title"], "slug": e["slug"]}
            for e in missing_title[:20]
        ],
        "entries_missing_meta_description": [
            {"document_id": e["document_id"], "title": e["title"], "slug": e["slug"]}
            for e in missing_desc[:20]
        ],
        "entries_title_too_long": [
            {
                "document_id": e["document_id"],
                "title": e["title"],
                "meta_title": e["seo"]["meta_title"],
                "length": len(e["seo"]["meta_title"]),
            }
            for e in title_long[:20]
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-type", help="Override GHOST_CONTENT_TYPE (posts or pages)")
    parser.add_argument("--output", help="Output JSON file path (default: secure tempfile)")
    args = parser.parse_args()

    base_url, content_key, content_type = get_config()
    if args.content_type:
        content_type = args.content_type

    if not base_url:
        print("GHOST_NOT_CONFIGURED: Set GHOST_URL and GHOST_CONTENT_KEY to enable Ghost integration.", file=sys.stderr)
        sys.exit(2)
    if not content_key:
        print("ERROR: GHOST_CONTENT_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    validate_url(base_url)

    print(f"Fetching {content_type} from {base_url}...", file=sys.stderr)
    entries = fetch_all_entries(base_url, content_key, content_type)

    seo_audit = build_seo_audit(entries)

    result = {
        "cms_type": "ghost",
        "cms_url": base_url,
        "content_type": content_type,
        "total_published": len(entries),
        "seo_audit": seo_audit,
        "entries": entries,
    }

    if args.output:
        out_path = args.output
        out_dir = os.path.dirname(out_path) or "."
    else:
        out_dir = tempfile.gettempdir()
        out_path = os.path.join(out_dir, f"cms_content_{os.getuid()}.json")

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, suffix=".json.tmp")
    try:
        os.chmod(tmp_path, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(result, f, indent=2)
        os.replace(tmp_path, out_path)
    except Exception:
        os.unlink(tmp_path)
        raise

    print(f"\nDone. {len(entries)} entries saved to {out_path}", file=sys.stderr)
    print(
        f"SEO completeness: {seo_audit['complete_seo']}/{seo_audit['total']} entries fully complete",
        file=sys.stderr,
    )
    if seo_audit["missing_meta_title"]:
        print(f"  Missing meta title:        {seo_audit['missing_meta_title']}", file=sys.stderr)
    if seo_audit["missing_meta_description"]:
        print(f"  Missing meta description:  {seo_audit['missing_meta_description']}", file=sys.stderr)
    if seo_audit["meta_title_too_long"]:
        print(f"  Meta title too long (>60): {seo_audit['meta_title_too_long']}", file=sys.stderr)
    if seo_audit["meta_description_too_short"]:
        print(f"  Meta desc too short (<70): {seo_audit['meta_description_too_short']}", file=sys.stderr)


if __name__ == "__main__":
    main()
