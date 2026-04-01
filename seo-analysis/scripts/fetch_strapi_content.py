#!/usr/bin/env python3
"""Fetch published content from Strapi for SEO analysis.

Paginates through all published entries, extracts SEO fields (official
strapi-community/plugin-seo component + common custom field names),
and outputs structured JSON for the seo-analysis skill.

Supports Strapi v4 (nested attributes) and v5 (flat response).
No external dependencies — uses only Python stdlib.

Usage:
  python3 fetch_strapi_content.py
  python3 fetch_strapi_content.py --content-type blog-posts --output /tmp/strapi.json

Environment variables (or .env / .env.local):
  STRAPI_URL            Required. Base URL, e.g. https://cms.example.com
  STRAPI_API_KEY        Required. Full-access API token.
  STRAPI_CONTENT_TYPE   Optional. Plural API ID (default: articles)
  STRAPI_VERSION        Optional. Force '4' or '5' if auto-detection is wrong.
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


PAGE_SIZE = 100  # Strapi default max; configurable up to 250 in config/api.js

_RETRY_CODES = {429, 502, 503, 504}


# ── SSRF protection ───────────────────────────────────────────────────────────

def _is_private_ip(ip_str):
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_loopback or addr.is_private or addr.is_link_local or addr.is_reserved
    except ValueError:
        return False


def validate_url(url):
    """Block SSRF targets. Called before any HTTP requests are made."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        print("ERROR: STRAPI_URL is not a valid URL.", file=sys.stderr)
        sys.exit(1)
    if parsed.scheme not in ("http", "https"):
        print(f"ERROR: STRAPI_URL must use http:// or https://", file=sys.stderr)
        sys.exit(1)
    hostname = parsed.hostname or ""
    if not hostname:
        print("ERROR: STRAPI_URL has no hostname.", file=sys.stderr)
        sys.exit(1)
    if _is_private_ip(hostname):
        print(f"ERROR: STRAPI_URL is a private/local address ('{hostname}').", file=sys.stderr)
        sys.exit(1)
    if hostname.lower() == "localhost":
        print("ERROR: STRAPI_URL points to localhost.", file=sys.stderr)
        sys.exit(1)
    # DNS-based check (best-effort)
    try:
        for info in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM):
            if _is_private_ip(info[4][0]):
                print(f"ERROR: STRAPI_URL resolves to an internal address ({info[4][0]}).", file=sys.stderr)
                sys.exit(1)
    except (socket.gaierror, OSError):
        pass  # non-fatal; let the request fail naturally


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
        get("STRAPI_URL").rstrip("/"),
        get("STRAPI_API_KEY"),
        get("STRAPI_CONTENT_TYPE") or "articles",
        get("STRAPI_VERSION"),  # "4" or "5" explicit override
    )


# ── HTTP helper with retry ────────────────────────────────────────────────────

def strapi_get(base_url, api_key, path, params, timeout=30, retries=3):
    full_url = f"{base_url}{path}?{urllib.parse.urlencode(params)}"
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
                print(f"  HTTP {e.code} on page — retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_exc = e
                continue
            body = e.read().decode()[:200] if e.fp else "(no body)"
            print(f"ERROR: Strapi API {e.code} on {path}: {body}", file=sys.stderr)
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


# ── Version detection ─────────────────────────────────────────────────────────

def detect_version(data, version_hint):
    """Return 4 or 5. Explicit hint wins; otherwise infer from response structure."""
    if version_hint in ("4", "5"):
        return int(version_hint)
    items = data.get("data", [])
    if items:
        return 4 if "attributes" in items[0] else 5
    # Empty collection: fall back to v5. Set STRAPI_VERSION=4 to override.
    return 5


def publication_params(version):
    """Return the correct publication filter for the Strapi version."""
    if version == 4:
        return {"publicationState": "live"}
    return {"status": "published"}


# ── Response normalisation ────────────────────────────────────────────────────

def extract_seo_component(seo_val):
    """Normalise the SEO component from plugin-seo. Returns {} if absent."""
    if not seo_val or not isinstance(seo_val, dict):
        return {}
    # v4 may wrap under .data.attributes; v5 is already flat
    attrs = seo_val.get("attributes", seo_val)
    return {
        "meta_title": attrs.get("metaTitle") or "",
        "meta_description": attrs.get("metaDescription") or "",
        "has_meta_image": bool(attrs.get("metaImage")),
        "has_meta_social": bool(attrs.get("metaSocial")),
    }


def normalise_entry(raw, v4):
    """Return a flat dict regardless of v4/v5 response format."""
    if v4:
        document_id = str(raw.get("id", ""))
        attrs = raw.get("attributes", {})
    else:
        document_id = raw.get("documentId", "")
        attrs = raw

    item_id = raw.get("id")
    title = attrs.get("title") or attrs.get("name") or attrs.get("heading") or ""
    slug = attrs.get("slug") or attrs.get("url") or ""
    published_at = attrs.get("publishedAt") or ""
    updated_at = attrs.get("updatedAt") or ""
    created_at = attrs.get("createdAt") or ""
    locale = attrs.get("locale") or ""

    # Official plugin-seo component
    seo_component = extract_seo_component(attrs.get("seo"))

    # Fallback: common root-level custom fields when plugin is not installed
    if not seo_component.get("meta_title"):
        seo_component["meta_title"] = (
            attrs.get("metaTitle") or attrs.get("seoTitle") or
            attrs.get("meta_title") or attrs.get("seo_title") or ""
        )
    if not seo_component.get("meta_description"):
        seo_component["meta_description"] = (
            attrs.get("metaDescription") or attrs.get("seoDescription") or
            attrs.get("meta_description") or attrs.get("seo_description") or ""
        )

    # Detect which schema was used — push_strapi_seo.py needs this to write correctly
    seo_schema = "component" if attrs.get("seo") else "root_fields"

    meta_title_len = len(seo_component.get("meta_title", ""))
    meta_desc_len = len(seo_component.get("meta_description", ""))

    return {
        "document_id": document_id,
        "id": item_id,
        "title": title,
        "slug": slug,
        "published_at": published_at,
        "updated_at": updated_at,
        "created_at": created_at,
        "locale": locale,
        "seo": seo_component,
        "seo_schema": seo_schema,  # "component" | "root_fields"
        "missing_meta_title": not seo_component.get("meta_title"),
        "missing_meta_description": not seo_component.get("meta_description"),
        "meta_title_too_long": meta_title_len > 60,
        "meta_description_too_long": meta_desc_len > 160,
        "meta_description_too_short": 0 < meta_desc_len < 70,
    }


# ── Pagination ────────────────────────────────────────────────────────────────

def fetch_all_entries(base_url, api_key, content_type, version_hint):
    """Paginate through all published entries. Returns (entries, strapi_version)."""
    path = f"/api/{content_type}"
    all_entries = []

    # Version detection: skip probe when version_hint is already explicit
    if version_hint in ("4", "5"):
        strapi_version = int(version_hint)
        print(f"  Strapi v{strapi_version} (from STRAPI_VERSION)", file=sys.stderr)
    else:
        # Probe without publication filter so response structure reveals v4 vs v5
        probe_data = strapi_get(base_url, api_key, path, {"pagination[page]": 1, "pagination[pageSize]": 1})
        strapi_version = detect_version(probe_data, version_hint)
        print(f"  Strapi v{strapi_version} detected", file=sys.stderr)

    pub_filter = publication_params(strapi_version)
    page = 1

    while True:
        params = {
            "populate": "seo,seo.metaImage,seo.metaSocial",
            **pub_filter,
            "pagination[page]": page,
            "pagination[pageSize]": PAGE_SIZE,
            "sort[0]": "publishedAt:desc",
        }

        print(f"  Fetching page {page}...", file=sys.stderr)
        data = strapi_get(base_url, api_key, path, params)

        items = data.get("data", [])
        if not items:
            break

        for raw in items:
            all_entries.append(normalise_entry(raw, v4=(strapi_version == 4)))

        pagination = data.get("meta", {}).get("pagination", {})
        page_count = pagination.get("pageCount", 1)
        total = pagination.get("total", len(all_entries))

        print(
            f"  Page {page}/{page_count} — {len(all_entries)}/{total} entries fetched",
            file=sys.stderr,
        )

        if page >= page_count:
            break
        page += 1

    return all_entries, strapi_version


# ── SEO completeness audit ────────────────────────────────────────────────────

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
    parser.add_argument("--content-type", help="Override STRAPI_CONTENT_TYPE env var")
    parser.add_argument("--output", help="Output JSON file path (default: secure tempfile)")
    args = parser.parse_args()

    base_url, api_key, content_type, version_hint = get_config()
    if args.content_type:
        content_type = args.content_type

    if not base_url:
        print("STRAPI_NOT_CONFIGURED: Set STRAPI_URL and STRAPI_API_KEY to enable Strapi integration.", file=sys.stderr)
        sys.exit(2)
    if not api_key:
        print("ERROR: STRAPI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    validate_url(base_url)

    print(f"Fetching {content_type} from {base_url}...", file=sys.stderr)
    entries, version = fetch_all_entries(base_url, api_key, content_type, version_hint)

    seo_audit = build_seo_audit(entries)

    result = {
        "strapi_url": base_url,
        "content_type": content_type,
        "strapi_version": version,
        "total_published": len(entries),
        "seo_audit": seo_audit,
        "entries": entries,
    }

    # Atomic write to a private tempfile, then rename into place
    if args.output:
        out_path = args.output
        out_dir = os.path.dirname(out_path) or "."
    else:
        out_dir = tempfile.gettempdir()
        out_path = os.path.join(out_dir, f"strapi_content_{os.getuid()}.json")

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
