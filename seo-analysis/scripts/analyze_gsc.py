#!/usr/bin/env python3
"""
Pull and analyze Google Search Console data.
Outputs structured JSON for the seo-analysis skill to process.

Usage:
  python3 analyze_gsc.py --site "sc-domain:example.com" --days 90
  python3 analyze_gsc.py --site "https://example.com/" --days 28
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error
from datetime import date, timedelta


def get_access_token():
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15
        )
    except FileNotFoundError:
        print("ERROR: gcloud not found. Install it and authenticate:", file=sys.stderr)
        print("  https://cloud.google.com/sdk/docs/install", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: gcloud timed out after 15s. Check your network or gcloud installation.", file=sys.stderr)
        sys.exit(1)
    if result.returncode != 0:
        print("ERROR: Not authenticated. Run:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print("    --scopes=https://www.googleapis.com/auth/webmasters.readonly", file=sys.stderr)
        sys.exit(1)
    token = result.stdout.strip()
    if not token:
        print("ERROR: gcloud returned an empty token. Re-authenticate:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print("    --scopes=https://www.googleapis.com/auth/webmasters.readonly", file=sys.stderr)
        sys.exit(1)
    return token


def gsc_query(token, site_url, body):
    """Call the Search Analytics query endpoint."""
    encoded = urllib.parse.quote(site_url, safe="")
    url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{encoded}/searchAnalytics/query"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else "(no body)"
        print(f"GSC API error {e.code}: {err_body}", file=sys.stderr)
        return {"rows": []}
    except urllib.error.URLError as e:
        print(f"GSC API network error: {e.reason}", file=sys.stderr)
        return {"rows": []}


def date_range(days_ago_start, days_ago_end=3):
    """Return (start, end) date strings. GSC data typically lags ~3 days."""
    end = date.today() - timedelta(days=days_ago_end)
    start = end - timedelta(days=days_ago_start)
    return start.isoformat(), end.isoformat()


def pull_top_queries(token, site, start, end, row_limit=50):
    body = {
        "startDate": start, "endDate": end,
        "dimensions": ["query"],
        "rowLimit": row_limit,
        "orderBy": [{"fieldName": "impressions", "sortOrder": "DESCENDING"}]
    }
    data = gsc_query(token, site, body)
    rows = []
    for r in data.get("rows", []):
        rows.append({
            "query": r["keys"][0],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": round(r["ctr"] * 100, 2),
            "position": round(r["position"], 1)
        })
    return rows


def pull_top_pages(token, site, start, end, row_limit=50):
    body = {
        "startDate": start, "endDate": end,
        "dimensions": ["page"],
        "rowLimit": row_limit,
        "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
    }
    data = gsc_query(token, site, body)
    rows = []
    for r in data.get("rows", []):
        rows.append({
            "page": r["keys"][0],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": round(r["ctr"] * 100, 2),
            "position": round(r["position"], 1)
        })
    return rows


def pull_position_buckets(token, site, start, end):
    """Queries by position bucket: 1-3 (winners), 4-10 (low-hanging fruit), 11-20 (almost there), 21+."""
    body = {
        "startDate": start, "endDate": end,
        "dimensions": ["query"],
        "rowLimit": 1000,
        "orderBy": [{"fieldName": "impressions", "sortOrder": "DESCENDING"}]
    }
    data = gsc_query(token, site, body)
    buckets = {"1-3": [], "4-10": [], "11-20": [], "21+": []}
    for r in data.get("rows", []):
        pos = r["position"]
        entry = {
            "query": r["keys"][0],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": round(r["ctr"] * 100, 2),
            "position": round(pos, 1)
        }
        if pos <= 3:
            buckets["1-3"].append(entry)
        elif pos <= 10:
            buckets["4-10"].append(entry)
        elif pos <= 20:
            buckets["11-20"].append(entry)
        else:
            buckets["21+"].append(entry)
    return buckets


def pull_period_comparison(token, site, days):
    """Compare current period vs prior period to find declines."""
    end_curr = date.today() - timedelta(days=3)
    start_curr = end_curr - timedelta(days=days)
    end_prev = start_curr - timedelta(days=1)
    start_prev = end_prev - timedelta(days=days)

    def fetch(start, end, dim):
        body = {
            "startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": [dim], "rowLimit": 200,
            "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
        }
        data = gsc_query(token, site, body)
        return {r["keys"][0]: r for r in data.get("rows", [])}

    # Pages comparison
    curr_pages = fetch(start_curr, end_curr, "page")
    prev_pages = fetch(start_prev, end_prev, "page")

    page_changes = []
    for page, curr in curr_pages.items():
        if page in prev_pages:
            prev = prev_pages[page]
            delta = curr["clicks"] - prev["clicks"]
            pct = round((delta / max(prev["clicks"], 1)) * 100, 1)
            if pct < -20 and prev["clicks"] > 10:  # Only flag meaningful drops
                page_changes.append({
                    "page": page,
                    "clicks_now": curr["clicks"],
                    "clicks_prev": prev["clicks"],
                    "change_pct": pct
                })
    page_changes.sort(key=lambda x: x["change_pct"])

    # Queries comparison
    curr_q = fetch(start_curr, end_curr, "query")
    prev_q = fetch(start_prev, end_prev, "query")

    query_changes = []
    for q, curr in curr_q.items():
        if q in prev_q:
            prev = prev_q[q]
            delta = curr["clicks"] - prev["clicks"]
            pct = round((delta / max(prev["clicks"], 1)) * 100, 1)
            if pct < -25 and prev["clicks"] > 5:
                query_changes.append({
                    "query": q,
                    "clicks_now": curr["clicks"],
                    "clicks_prev": prev["clicks"],
                    "change_pct": pct
                })
    query_changes.sort(key=lambda x: x["change_pct"])

    return {
        "period": f"{start_curr.isoformat()} to {end_curr.isoformat()}",
        "prior_period": f"{start_prev.isoformat()} to {end_prev.isoformat()}",
        "declining_pages": page_changes[:20],
        "declining_queries": query_changes[:20]
    }


def pull_summary(token, site, start, end):
    """Overall totals."""
    body = {"startDate": start, "endDate": end, "dimensions": []}
    data = gsc_query(token, site, body)
    rows = data.get("rows", [{}])
    r = rows[0] if rows else {}
    return {
        "clicks": r.get("clicks", 0),
        "impressions": r.get("impressions", 0),
        "ctr": round(r.get("ctr", 0) * 100, 2),
        "position": round(r.get("position", 0), 1)
    }


def pull_device_split(token, site, start, end):
    body = {
        "startDate": start, "endDate": end,
        "dimensions": ["device"],
        "rowLimit": 10
    }
    data = gsc_query(token, site, body)
    return [
        {"device": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"]}
        for r in data.get("rows", [])
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, help="GSC property URL")
    parser.add_argument("--days", type=int, default=90, help="Days of data to pull")
    _default_out = os.path.join(tempfile.gettempdir(), f"gsc_analysis_{os.getuid()}.json")
    parser.add_argument("--output", default=_default_out, help="Output file")
    args = parser.parse_args()

    print(f"Pulling {args.days} days of GSC data for: {args.site}", file=sys.stderr)

    token = get_access_token()
    start, end = date_range(args.days)

    print("Fetching summary...", file=sys.stderr)
    summary = pull_summary(token, args.site, start, end)

    print("Fetching top queries...", file=sys.stderr)
    queries = pull_top_queries(token, args.site, start, end)

    print("Fetching top pages...", file=sys.stderr)
    pages = pull_top_pages(token, args.site, start, end)

    print("Fetching position buckets...", file=sys.stderr)
    buckets = pull_position_buckets(token, args.site, start, end)

    print("Fetching period comparison...", file=sys.stderr)
    comparison = pull_period_comparison(token, args.site, 28)

    print("Fetching device split...", file=sys.stderr)
    devices = pull_device_split(token, args.site, start, end)

    # High-impression, low-CTR queries (title/snippet improvement targets)
    ctr_opportunities = [
        q for q in queries
        if q["impressions"] > 500 and q["ctr"] < 3.0 and q["position"] <= 20
    ]
    ctr_opportunities.sort(key=lambda x: x["impressions"], reverse=True)

    result = {
        "site": args.site,
        "period": {"start": start, "end": end, "days": args.days},
        "summary": summary,
        "top_queries": queries[:30],
        "top_pages": pages[:30],
        "position_buckets": {
            k: sorted(v, key=lambda x: x["impressions"], reverse=True)[:20]
            for k, v in buckets.items()
        },
        "ctr_opportunities": ctr_opportunities[:20],
        "comparison": comparison,
        "device_split": devices
    }

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nDone. Results saved to {args.output}", file=sys.stderr)
    print(f"\nSummary: {summary['clicks']:,} clicks | {summary['impressions']:,} impressions | "
          f"CTR {summary['ctr']}% | Avg position {summary['position']}", file=sys.stderr)


if __name__ == "__main__":
    main()
