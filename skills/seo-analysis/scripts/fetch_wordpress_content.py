#!/usr/bin/env python3
"""Fetch published content from WordPress REST API for SEO analysis.

Paginates through all published posts (or pages/custom types), extracts SEO
fields from Yoast SEO or RankMath if present, and outputs structured JSON
in the normalized CMS content format consumed by seo-analysis.

No external dependencies — uses only Python stdlib.

Usage:
  python3 fetch_wordpress_content.py
  python3 fetch_wordpress_content.py --content-type pages --output /tmp/wp.json

Environment variables (or .env / .env.local):
  WP_URL            Required. Base URL, e.g. https://myblog.com
  WP_USERNAME       Required. WordPress username.
  WP_APP_PASSWORD   Required. Application Password (spaces OK).
  WP_CONTENT_TYPE   Optional. REST API slug (default: posts)
"""

import argparse
import base64
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


PAGE_SIZE = 100
_RETRY_CODES = {429, 502, 503, 504}


# ── SSRF protection ───────────────────────────────────────────────────────────

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
        print("ERROR: WP_URL is not a valid URL.", file=sys.stderr)
        sys.exit(1)
    if parsed.scheme not in ("http", "https"):
        print("ERROR: WP_URL must use http:// or https://", file=sys.stderr)
        sys.exit(1)
    hostname = parsed.hostname or ""
    if not hostname:
        print("ERROR: WP_URL has no hostname.", file=sys.stderr)
        sys.exit(1)
    if _is_private_ip(hostname):
        print(f"ERROR: WP_URL is a private/local address ('{hostname}').", file=sys.stderr)
        sys.exit(1)
    if hostname.lower() == "localhost":
        print("ERROR: WP_URL points to localhost.", file=sys.stderr)
        sys.exit(1)
    try:
        for info in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM):
            if _is_private_ip(info[4][0]):
                print(f"ERROR: WP_URL resolves to an internal address ({info[4][0]}).", file=sys.stderr)
                sys.exit(1)
    except (socket.gaierror, OSError):
        pass


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
        get("WP_URL").rstrip("/"),
        get("WP_USERNAME"),
        get("WP_APP_PASSWORD"),
        get("WP_CONTENT_TYPE") or "posts",
    )


def make_auth_header(username, app_password):
    password = app_password.replace(" ", "")
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {credentials}"


# ── HTTP helper with retry ────────────────────────────────────────────────────

def wp_get(base_url, auth_header, path, params, timeout=30, retries=3):
    full_url = f"{base_url}{path}?{urllib.parse.urlencode(params)}"
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
            body = e.read().decode()[:200] if e.fp else "(no body)"
            print(f"ERROR: WordPress API {e.code} on {path}: {body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  Network error ({e.reason}) — retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_exc = e
                continue
            print(f"ERROR: Network error on {base_url}{path}: {e.reason}", file=sys.stderr)
            sys.exit(1)
    raise last_exc


# ── SEO field extraction ──────────────────────────────────────────────────────

def extract_seo_fields(item):
    """Extract meta title and description from WordPress post/page.

    Priority:
    1. Yoast SEO — yoast_head_json.title / yoast_head_json.description
    2. RankMath  — meta.rank_math_title / meta.rank_math_description
    3. Title     — title.rendered (raw page title, no SEO override)
    """
    meta_title = ""
    meta_description = ""
    has_meta_image = False
    has_meta_social = False

    yoast = item.get("yoast_head_json") or {}
    if yoast:
        meta_title = yoast.get("title") or ""
        meta_description = yoast.get("description") or ""
        has_meta_image = bool(yoast.get("og_image"))
        has_meta_social = bool(yoast.get("og_title") or yoast.get("twitter_title"))

    if not meta_title or not meta_description:
        meta_obj = item.get("meta") or {}
        if not meta_title:
            meta_title = (
                meta_obj.get("rank_math_title") or
                meta_obj.get("_yoast_wpseo_title") or
                ""
            )
        if not meta_description:
            meta_description = (
                meta_obj.get("rank_math_description") or
                meta_obj.get("_yoast_wpseo_metadesc") or
                ""
            )

    # Do NOT fall back to title.rendered — a post with no Yoast/RankMath title
    # should be flagged as missing_meta_title=True, not silently pass because it
    # has a page title. The entry's "title" field is preserved for display.

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "has_meta_image": has_meta_image,
        "has_meta_social": has_meta_social,
    }


# ── Response normalisation ────────────────────────────────────────────────────

def normalise_entry(item):
    """Normalise a WordPress REST API post/page to the shared CMS entry format."""
    seo = extract_seo_fields(item)

    title_obj = item.get("title") or {}
    slug = item.get("slug") or ""
    published_at = item.get("date_gmt") or item.get("date") or ""
    updated_at = item.get("modified_gmt") or item.get("modified") or ""

    meta_title_len = len(seo["meta_title"])
    meta_desc_len = len(seo["meta_description"])

    return {
        "document_id": str(item.get("id", "")),
        "id": item.get("id"),
        "title": title_obj.get("rendered") or "",
        "slug": slug,
        "published_at": published_at,
        "updated_at": updated_at,
        "created_at": published_at,  # WP doesn't separate creation from publish
        "locale": "",
        "seo": seo,
        "missing_meta_title": not seo["meta_title"],
        "missing_meta_description": not seo["meta_description"],
        "meta_title_too_long": meta_title_len > 60,
        "meta_description_too_long": meta_desc_len > 160,
        "meta_description_too_short": 0 < meta_desc_len < 70,
    }


# ── Pagination ────────────────────────────────────────────────────────────────

def fetch_all_entries(base_url, auth_header, content_type):
    """Paginate through all published entries. Returns list of normalised entries."""
    path = f"/wp-json/wp/v2/{content_type}"
    all_entries = []
    page = 1
    total_pages = None

    while True:
        params = {
            "status": "publish",
            "per_page": PAGE_SIZE,
            "page": page,
            # Fetch fields needed for SEO extraction plus pagination headers
            "_fields": "id,slug,title,date,date_gmt,modified,modified_gmt,yoast_head_json,meta",
        }

        print(f"  Fetching page {page}...", file=sys.stderr)
        items, total, tp = wp_get(base_url, auth_header, path, params)

        if total_pages is None:
            total_pages = tp
            print(f"  {total} published {content_type} across {total_pages} page(s)", file=sys.stderr)

        if not items:
            break

        for item in items:
            all_entries.append(normalise_entry(item))

        print(f"  Page {page}/{total_pages} — {len(all_entries)}/{total} fetched", file=sys.stderr)

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
    parser.add_argument("--content-type", help="Override WP_CONTENT_TYPE env var")
    parser.add_argument("--output", help="Output JSON file path (default: secure tempfile)")
    args = parser.parse_args()

    base_url, username, app_password, content_type = get_config()
    if args.content_type:
        content_type = args.content_type

    if not base_url:
        print("WP_NOT_CONFIGURED: Set WP_URL, WP_USERNAME, and WP_APP_PASSWORD to enable WordPress integration.", file=sys.stderr)
        sys.exit(2)
    if not username or not app_password:
        print("ERROR: WP_USERNAME and WP_APP_PASSWORD must both be set.", file=sys.stderr)
        sys.exit(1)

    validate_url(base_url)
    auth_header = make_auth_header(username, app_password)

    print(f"Fetching {content_type} from {base_url}...", file=sys.stderr)
    entries = fetch_all_entries(base_url, auth_header, content_type)

    seo_audit = build_seo_audit(entries)

    result = {
        "cms_type": "wordpress",
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
