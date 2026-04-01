#!/usr/bin/env python3
"""Push SEO metadata updates back to Strapi.

Reads a batch of recommended SEO updates, shows a diff of proposed changes,
and writes them to Strapi after confirmation.

Supports Strapi v4 (PUT /api/{type}/{id}) and v5 (PUT /api/{type}/{documentId}).
Locale-aware: for localized v5 content, pass --locale or include 'locale' in batch.
No external dependencies — uses only Python stdlib.

Usage — single entry:
  python3 push_strapi_seo.py \\
    --document-id clkgylmcc000008lcdd868feh \\
    --meta-title "New Title | Brand" \\
    --meta-description "Compelling 120-char description."

  # Localized v5:
  python3 push_strapi_seo.py \\
    --document-id clkgylmcc000008lcdd868feh \\
    --locale fr \\
    --meta-title "Nouveau titre | Marque"

Usage — batch from file:
  python3 push_strapi_seo.py --batch-file /tmp/seo_updates.json [--yes]

Batch file format (JSON array):
  [
    {
      "document_id": "clkgylmcc000008lcdd868feh",  // v5
      "id": 42,                                      // v4 fallback
      "locale": "en",                                // optional, v5 localized
      "seo_schema": "component",                     // "component" | "root_fields"
      "meta_title": "New Title | Brand",
      "meta_description": "New description.",
      "updated_at": "2024-01-20T14:30:00.000Z"      // optional: refuse if stale
    }
  ]

Environment variables (or .env / .env.local):
  STRAPI_URL            Required.
  STRAPI_API_KEY        Required. Must be Full-access token (not read-only).
  STRAPI_CONTENT_TYPE   Optional (default: articles).
  STRAPI_VERSION        Optional. Force '4' or '5'.
"""

import argparse
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
        get("STRAPI_VERSION"),
    )


# ── HTTP helpers with retry ───────────────────────────────────────────────────

def _headers(api_key):
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def strapi_get(base_url, api_key, path, params=None, timeout=15, retries=3):
    full_url = f"{base_url}{path}"
    if params:
        full_url = f"{full_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers=_headers(api_key))
    last_exc = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in _RETRY_CODES and attempt < retries - 1:
                time.sleep(2 ** attempt)
                last_exc = e
                continue
            raise
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                last_exc = e
                continue
            raise
    raise last_exc


def strapi_put(base_url, api_key, path, payload, timeout=30, retries=3):
    full_url = f"{base_url}{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        full_url, data=data, method="PUT", headers=_headers(api_key)
    )
    last_exc = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in _RETRY_CODES and attempt < retries - 1:
                time.sleep(2 ** attempt)
                last_exc = e
                continue
            raise
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                last_exc = e
                continue
            raise
    raise last_exc


# ── Version detection ─────────────────────────────────────────────────────────

def detect_version(raw, version_hint):
    """Detect v4 vs v5 from a single-entry GET response."""
    if version_hint in ("4", "5"):
        return int(version_hint)
    data = raw.get("data", {})
    return 4 if "attributes" in data else 5


# ── Current SEO value fetching ────────────────────────────────────────────────

def fetch_current_seo(base_url, api_key, content_type, entry_id, locale, version):
    params = {"populate": "seo"}
    if version == 5 and locale:
        params["locale"] = locale
    try:
        data = strapi_get(base_url, api_key, f"/api/{content_type}/{entry_id}", params)
    except Exception as e:
        print(f"  WARNING: Could not fetch current values for {entry_id}: {e}", file=sys.stderr)
        return {}, {}

    raw = data.get("data", {})
    attrs = raw.get("attributes", raw)  # works for both v4 and v5

    seo = attrs.get("seo") or {}
    if isinstance(seo, dict) and "data" in seo:
        seo = seo["data"].get("attributes", seo)

    current_seo = {
        "meta_title": seo.get("metaTitle") or attrs.get("metaTitle") or "",
        "meta_description": seo.get("metaDescription") or attrs.get("metaDescription") or "",
        "updated_at": attrs.get("updatedAt") or "",
    }
    return current_seo, attrs


# ── Payload builder ───────────────────────────────────────────────────────────

def build_payload(update, current_attrs, seo_schema):
    """Build the PUT payload. Respects the schema in use (component vs root fields)."""
    seo_patch = {}
    if "meta_title" in update:
        seo_patch["metaTitle"] = update["meta_title"]
    if "meta_description" in update:
        seo_patch["metaDescription"] = update["meta_description"]

    if not seo_patch:
        return None

    # Determine schema: prefer explicit flag from fetch output, else detect from attrs
    use_component = seo_schema == "component"
    if seo_schema not in ("component", "root_fields"):
        # Auto-detect: if current attrs have a 'seo' key, use component schema
        use_component = "seo" in (current_attrs or {})

    if use_component:
        # Merge with existing SEO component to avoid clobbering unrelated fields
        existing_seo = (current_attrs or {}).get("seo") or {}
        if isinstance(existing_seo, dict) and "data" in existing_seo:
            existing_seo = existing_seo["data"].get("attributes", {})
        merged_seo = {**{k: v for k, v in existing_seo.items()
                         if k not in ("metaImage", "metaSocial")},
                      **seo_patch}
        return {"data": {"seo": merged_seo}}
    else:
        # Root-level SEO fields
        return {"data": seo_patch}


# ── Diff display ──────────────────────────────────────────────────────────────

def print_diff(entry_id, update, current, locale=None):
    loc_label = f" [{locale}]" if locale else ""
    print(f"\n  Entry: {entry_id}{loc_label}", file=sys.stderr)
    for field in ("meta_title", "meta_description"):
        if field not in update:
            continue
        old_val = current.get(field) or "(empty)"
        new_val = update[field]
        label = "Meta Title" if field == "meta_title" else "Meta Description"
        char_limit = 60 if field == "meta_title" else 160
        print(f"  {label}:", file=sys.stderr)
        print(f"    - {old_val}", file=sys.stderr)
        print(f"    + {new_val}", file=sys.stderr)
        if len(new_val) > char_limit:
            print(f"    WARNING: exceeds {char_limit} chars ({len(new_val)})", file=sys.stderr)
        if len(new_val) == 0:
            print(f"    WARNING: new value is empty — will blank this field", file=sys.stderr)


# ── Confirmation ──────────────────────────────────────────────────────────────

def confirm_batch(count, auto_yes=False):
    if auto_yes:
        return True
    if not sys.stdin.isatty():
        print("ERROR: --yes flag required in non-interactive mode.", file=sys.stderr)
        sys.exit(1)
    print(f"\nApply {count} SEO update(s) to Strapi? [y/N] ", end="", file=sys.stderr, flush=True)
    return input().strip().lower() in ("y", "yes")


# ── Core update logic ─────────────────────────────────────────────────────────

def process_updates(base_url, api_key, content_type, updates, version_hint, auto_yes=False):
    if not updates:
        print("No updates to apply.", file=sys.stderr)
        return

    # Short-circuit: if version_hint is explicit, skip the probe entirely
    if version_hint in ("4", "5"):
        version = int(version_hint)
    else:
        version = 5  # default; probe to confirm
        for upd in updates:
            entry_id = upd.get("document_id") or str(upd.get("id", ""))
            if not entry_id:
                continue
            try:
                probe = strapi_get(base_url, api_key, f"/api/{content_type}/{entry_id}")
                version = detect_version(probe, version_hint)
                break
            except Exception:
                continue

    print(f"Strapi v{version} | {content_type}", file=sys.stderr)

    # Build diffs
    print(f"\nProposed changes ({len(updates)} entries):", file=sys.stderr)
    print("-" * 60, file=sys.stderr)

    enriched = []
    skipped = 0
    for upd in updates:
        entry_id = upd.get("document_id") or str(upd.get("id", ""))
        locale = upd.get("locale") or ""
        seo_schema = upd.get("seo_schema") or "auto"

        if not entry_id:
            print(f"  SKIP: entry missing document_id/id: {upd}", file=sys.stderr)
            skipped += 1
            continue

        current_seo, current_attrs = fetch_current_seo(
            base_url, api_key, content_type, entry_id, locale, version
        )

        # Stale-write guard: refuse if entry was modified since the batch was generated
        expected_updated_at = upd.get("updated_at") or ""
        live_updated_at = current_seo.get("updated_at") or ""
        if expected_updated_at and live_updated_at and expected_updated_at != live_updated_at:
            print(
                f"  SKIP {entry_id}: entry was modified since analysis "
                f"(expected {expected_updated_at}, got {live_updated_at}). "
                f"Re-run analysis before pushing.",
                file=sys.stderr,
            )
            skipped += 1
            continue

        print_diff(entry_id, upd, current_seo, locale)
        enriched.append((entry_id, upd, current_seo, current_attrs, locale, seo_schema))

    print("-" * 60, file=sys.stderr)

    if not enriched:
        print("No valid entries to update after review.", file=sys.stderr)
        sys.exit(0 if skipped == 0 else 1)

    if not confirm_batch(len(enriched), auto_yes):
        print("Aborted. No changes written.", file=sys.stderr)
        sys.exit(0)

    # Apply updates
    success = 0
    failed = 0
    for entry_id, upd, _current, current_attrs, locale, seo_schema in enriched:
        payload = build_payload(upd, current_attrs, seo_schema)
        if not payload:
            print(f"  SKIP {entry_id}: nothing to update", file=sys.stderr)
            continue

        path = f"/api/{content_type}/{entry_id}"
        params = {}
        if version == 5 and locale:
            params["locale"] = locale
        if params:
            path = f"{path}?{urllib.parse.urlencode(params)}"

        try:
            strapi_put(base_url, api_key, path, payload)
            loc_label = f" [{locale}]" if locale else ""
            print(f"  OK   {entry_id}{loc_label}", file=sys.stderr)
            success += 1
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200] if e.fp else "(no body)"
            print(f"  FAIL {entry_id}: HTTP {e.code}: {body}", file=sys.stderr)
            failed += 1
        except urllib.error.URLError as e:
            print(f"  FAIL {entry_id}: network error: {e.reason}", file=sys.stderr)
            failed += 1

    print(f"\nDone. {success} updated, {failed} failed, {skipped} skipped.", file=sys.stderr)
    if failed:
        sys.exit(1)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Push SEO updates to Strapi")
    parser.add_argument("--content-type", help="Override STRAPI_CONTENT_TYPE")
    parser.add_argument("--document-id", help="Strapi v5 documentId (single entry)")
    parser.add_argument("--id", type=int, help="Strapi v4 numeric id (single entry)")
    parser.add_argument("--locale", help="Locale for v5 localized content (e.g. 'fr', 'en')")
    parser.add_argument("--meta-title", help="New meta title (max 60 chars)")
    parser.add_argument("--meta-description", help="New meta description (70-160 chars)")
    parser.add_argument("--batch-file", help="JSON file with array of update objects")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    base_url, api_key, content_type, version_hint = get_config()
    if args.content_type:
        content_type = args.content_type

    if not base_url:
        print("ERROR: STRAPI_URL is not set.", file=sys.stderr)
        sys.exit(1)
    if not api_key:
        print("ERROR: STRAPI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    validate_url(base_url)

    if args.batch_file:
        try:
            with open(args.batch_file) as f:
                updates = json.load(f)
            if not isinstance(updates, list):
                print("ERROR: batch file must contain a JSON array.", file=sys.stderr)
                sys.exit(1)
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR: Could not read batch file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.document_id or args.id:
        if not args.meta_title and not args.meta_description:
            print("ERROR: Provide --meta-title and/or --meta-description.", file=sys.stderr)
            sys.exit(1)
        update = {}
        if args.document_id:
            update["document_id"] = args.document_id
        if args.id:
            update["id"] = args.id
        if args.locale:
            import re
            if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", args.locale):
                print(f"ERROR: Invalid locale '{args.locale}'. Expected format: 'en' or 'en-US'.", file=sys.stderr)
                sys.exit(1)
            update["locale"] = args.locale
        if args.meta_title:
            update["meta_title"] = args.meta_title
        if args.meta_description:
            update["meta_description"] = args.meta_description
        updates = [update]
    else:
        parser.print_help()
        sys.exit(1)

    process_updates(base_url, api_key, content_type, updates, version_hint, auto_yes=args.yes)


if __name__ == "__main__":
    main()
