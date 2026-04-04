#!/usr/bin/env python3
"""Fetch published content from Contentful for SEO analysis.

Paginates through all entries of a content type, resolves linked SEO entries,
and outputs structured JSON in the normalized CMS content format.

Contentful's Delivery API only returns published content by default.
No external dependencies — uses only Python stdlib.

Usage:
  python3 fetch_contentful_content.py
  python3 fetch_contentful_content.py --content-type blogPost --output /tmp/cf.json

Environment variables (or .env / .env.local):
  CONTENTFUL_SPACE_ID        Required. Space ID from Settings → General Settings.
  CONTENTFUL_DELIVERY_TOKEN  Required. Content Delivery API access token.
  CONTENTFUL_CONTENT_TYPE    Required. API Identifier for your content type.
  CONTENTFUL_ENVIRONMENT     Optional. Environment ID (default: master).
"""

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


PAGE_SIZE = 1000  # Contentful max per request
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

def contentful_get(token, path, params=None, timeout=30, retries=3):
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
            body = e.read().decode()[:200] if e.fp else "(no body)"
            print(f"ERROR: Contentful API {e.code}: {body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  Network error ({e.reason}) — retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_exc = e
                continue
            print(f"ERROR: Network error reaching Contentful: {e.reason}", file=sys.stderr)
            sys.exit(1)
    raise last_exc


# ── SEO field extraction ──────────────────────────────────────────────────────

def extract_seo_fields(fields, includes_by_id):
    """Extract SEO meta title and description from a Contentful entry's fields.

    Tries three patterns in priority order:
    1. Linked SEO entry: fields.seo → linked entry with fields.title + fields.description
    2. Direct SEO fields: fields.seoTitle, fields.metaTitle, fields.seo_title, etc.
    3. Content fields fallback: fields.title, fields.description, fields.excerpt
    """
    meta_title = ""
    meta_description = ""
    has_meta_image = False
    has_meta_social = False

    # Pattern 1: linked SEO component entry
    seo_ref = fields.get("seo")
    if isinstance(seo_ref, dict) and seo_ref.get("sys", {}).get("type") == "Link":
        linked_id = seo_ref.get("sys", {}).get("id")
        linked = includes_by_id.get(linked_id, {})
        linked_fields = linked.get("fields", {})
        meta_title = linked_fields.get("title") or linked_fields.get("metaTitle") or ""
        meta_description = linked_fields.get("description") or linked_fields.get("metaDescription") or ""
        has_meta_image = bool(linked_fields.get("image") or linked_fields.get("ogImage"))
        has_meta_social = bool(linked_fields.get("openGraphTitle") or linked_fields.get("twitterTitle"))

    # Pattern 2: direct SEO fields
    if not meta_title:
        meta_title = (
            fields.get("seoTitle") or
            fields.get("metaTitle") or
            fields.get("seo_title") or
            fields.get("meta_title") or
            ""
        )
    if not meta_description:
        meta_description = (
            fields.get("seoDescription") or
            fields.get("metaDescription") or
            fields.get("seo_description") or
            fields.get("meta_description") or
            ""
        )

    # Do NOT fall back to fields["title"] — that's the content title, not an SEO
    # meta title override. Entries without explicit SEO titles should be flagged
    # as missing_meta_title=True so the audit surfaces them. The "title" field
    # is preserved in the normalised entry for display purposes.

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "has_meta_image": has_meta_image,
        "has_meta_social": has_meta_social,
    }


# ── Response normalisation ────────────────────────────────────────────────────

def normalise_entry(item, includes_by_id):
    """Normalise a Contentful entry to the shared CMS entry format."""
    sys_data = item.get("sys", {})
    fields = item.get("fields", {})

    document_id = sys_data.get("id", "")
    published_at = sys_data.get("createdAt") or ""  # Delivery API = publishedAt equivalent
    updated_at = sys_data.get("updatedAt") or ""
    locale = sys_data.get("locale") or ""

    # Slug: try slug, then title-derived, then id
    slug = fields.get("slug") or fields.get("url") or fields.get("path") or ""
    title = fields.get("title") or fields.get("name") or fields.get("heading") or ""

    seo = extract_seo_fields(fields, includes_by_id)

    meta_title_len = len(seo["meta_title"])
    meta_desc_len = len(seo["meta_description"])

    return {
        "document_id": document_id,
        "id": document_id,
        "title": title,
        "slug": slug,
        "published_at": published_at,
        "updated_at": updated_at,
        "created_at": published_at,
        "locale": locale,
        "seo": seo,
        "missing_meta_title": not seo["meta_title"],
        "missing_meta_description": not seo["meta_description"],
        "meta_title_too_long": meta_title_len > 60,
        "meta_description_too_long": meta_desc_len > 160,
        "meta_description_too_short": 0 < meta_desc_len < 70,
    }


# ── Pagination ────────────────────────────────────────────────────────────────

def fetch_all_entries(space_id, token, content_type, environment):
    """Paginate through all entries. Returns list of normalised entries."""
    path = f"/spaces/{space_id}/environments/{environment}/entries"
    all_entries = []
    skip = 0
    total = None

    while True:
        params = {
            "content_type": content_type,
            "limit": PAGE_SIZE,
            "skip": skip,
            "include": 1,  # Resolve one level of linked entries (SEO components)
            "order": "-sys.updatedAt",
        }

        page_num = skip // PAGE_SIZE + 1
        print(f"  Fetching page {page_num}...", file=sys.stderr)
        data = contentful_get(token, path, params)

        if total is None:
            total = data.get("total", 0)
            print(f"  {total} entries total", file=sys.stderr)

        items = data.get("items", [])
        if not items:
            break

        # Build a lookup of included entries (linked SEO components, etc.)
        includes = data.get("includes", {})
        includes_by_id = {}
        for entry in includes.get("Entry", []):
            entry_id = entry.get("sys", {}).get("id")
            if entry_id:
                includes_by_id[entry_id] = entry
        for asset in includes.get("Asset", []):
            asset_id = asset.get("sys", {}).get("id")
            if asset_id:
                includes_by_id[asset_id] = asset

        for item in items:
            all_entries.append(normalise_entry(item, includes_by_id))

        skip += len(items)
        print(f"  {len(all_entries)}/{total} entries fetched", file=sys.stderr)

        if skip >= total:
            break

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
    parser.add_argument("--content-type", help="Override CONTENTFUL_CONTENT_TYPE env var")
    parser.add_argument("--output", help="Output JSON file path (default: secure tempfile)")
    args = parser.parse_args()

    space_id, token, content_type, environment = get_config()
    if args.content_type:
        content_type = args.content_type

    if not space_id:
        print("CONTENTFUL_NOT_CONFIGURED: Set CONTENTFUL_SPACE_ID and CONTENTFUL_DELIVERY_TOKEN.", file=sys.stderr)
        sys.exit(2)
    if not token:
        print("ERROR: CONTENTFUL_DELIVERY_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)
    if not content_type:
        print("ERROR: CONTENTFUL_CONTENT_TYPE is not set.", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching {content_type} from Contentful space {space_id}...", file=sys.stderr)
    entries = fetch_all_entries(space_id, token, content_type, environment)

    seo_audit = build_seo_audit(entries)

    result = {
        "cms_type": "contentful",
        "cms_url": f"https://app.contentful.com/spaces/{space_id}",
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
