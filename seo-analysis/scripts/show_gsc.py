#!/usr/bin/env python3
"""
Display a human-readable summary of the GSC analysis JSON output.

Usage:
  python3 show_gsc.py [path/to/gsc_analysis.json]

If no path is given, reads from the default temp file location.
"""

import json
import os
import sys
import tempfile

DEFAULT_PATH = os.path.join(tempfile.gettempdir(), f"gsc_analysis_{os.getuid()}.json")


def fmt_ctr(ctr):
    """CTR is stored as a percentage (e.g. 4.79 means 4.79%)."""
    return f"{ctr:.2f}%"


def show(path):
    with open(path) as f:
        data = json.load(f)

    summary = data.get("summary", {})
    print(f"\nSite: {data.get('site', '?')}")
    period = data.get("period", {})
    print(f"Period: {period.get('start', '?')} to {period.get('end', '?')} ({period.get('days', '?')} days)")
    print(f"\nSummary: {summary.get('clicks', 0):,} clicks | {summary.get('impressions', 0):,} impressions "
          f"| CTR {fmt_ctr(summary.get('ctr', 0))} | Avg position {summary.get('position', 0)}")

    # Top pages
    top_pages = data.get("top_pages", [])
    if top_pages:
        print(f"\n=== TOP {len(top_pages)} PAGES ===")
        for i, p in enumerate(top_pages, 1):
            print(f"  {i:2}. {p['clicks']:5,} clk | {p['impressions']:7,} imp "
                  f"| CTR {fmt_ctr(p['ctr'])} | pos {p['position']} | {p['page']}")

    # Top queries
    top_queries = data.get("top_queries", [])
    if top_queries:
        print(f"\n=== TOP {len(top_queries)} QUERIES ===")
        for i, q in enumerate(top_queries, 1):
            print(f"  {i:2}. {q['clicks']:5,} clk | {q['impressions']:7,} imp "
                  f"| CTR {fmt_ctr(q['ctr'])} | pos {q['position']} | {q['query']}")

    # Position buckets
    buckets = data.get("position_buckets", {})
    if buckets:
        print("\n=== POSITION BUCKETS ===")
        for bucket_name in ["1-3", "4-10", "11-20", "21+"]:
            rows = buckets.get(bucket_name, [])
            print(f"  [{bucket_name}]: {len(rows)} queries")

    # CTR opportunities
    ctr_opps = data.get("ctr_opportunities", [])
    if ctr_opps:
        print(f"\n=== CTR OPPORTUNITIES (high impressions, low CTR) ===")
        for q in ctr_opps[:10]:
            print(f"  {q['impressions']:6,} imp | CTR {fmt_ctr(q['ctr'])} | pos {q['position']} | {q['query']}")

    # Cannibalization
    cannib = data.get("cannibalization", [])
    if cannib:
        print(f"\n=== CANNIBALIZATION ({len(cannib)} queries) ===")
        for c in cannib[:5]:
            print(f"  '{c['query']}' → winner: {c['winner_page']}")
            print(f"    losers: {', '.join(c['loser_pages'])}")
            print(f"    action: {c['recommended_action']}")

    # Declining pages/queries
    comparison = data.get("comparison", {})
    declining_pages = comparison.get("declining_pages", [])
    declining_queries = comparison.get("declining_queries", [])
    comp_period = comparison.get("period", "?")
    comp_prior = comparison.get("prior_period", "?")
    if declining_pages or declining_queries:
        print(f"\n=== TRAFFIC CHANGES ({comp_period} vs {comp_prior}) ===")
        if declining_pages:
            print(f"  Declining pages ({len(declining_pages)}):")
            for p in declining_pages[:5]:
                print(f"    {p['change_pct']:+.1f}% | {p['clicks_now']:,} → {p['clicks_prev']:,} | {p['page']}")
        if declining_queries:
            print(f"  Declining queries ({len(declining_queries)}):")
            for q in declining_queries[:5]:
                print(f"    {q['change_pct']:+.1f}% | {q['clicks_now']:,} → {q['clicks_prev']:,} | {q['query']}")

    # Device split
    devices = data.get("device_split", [])
    if devices:
        print("\n=== DEVICE SPLIT ===")
        for d in devices:
            print(f"  {d['device']:10} {d['clicks']:6,} clk | CTR {fmt_ctr(d['ctr'])} | pos {d['position']}")

    # Search type split
    search_types = data.get("search_type_split", [])
    if search_types:
        print("\n=== SEARCH TYPE SPLIT ===")
        for t in search_types:
            print(f"  {t['type']:12} {t['clicks']:6,} clk | CTR {fmt_ctr(t['ctr'])} | pos {t['position']}")

    # Branded split
    branded = data.get("branded_split")
    if branded:
        b = branded.get("branded", {})
        nb = branded.get("non_branded", {})
        print("\n=== BRANDED vs NON-BRANDED ===")
        print(f"  Branded:     {b.get('clicks', 0):6,} clk | {b.get('impressions', 0):,} imp "
              f"| CTR {fmt_ctr(b.get('ctr', 0))} | {b.get('query_count', 0)} queries")
        print(f"  Non-branded: {nb.get('clicks', 0):6,} clk | {nb.get('impressions', 0):,} imp "
              f"| CTR {fmt_ctr(nb.get('ctr', 0))} | {nb.get('query_count', 0)} queries")

    # Page groups
    page_groups = data.get("page_groups", [])
    if page_groups:
        print("\n=== PAGE GROUPS ===")
        for g in page_groups:
            print(f"  {g['group']:15} {g['page_count']:3} pages | {g['clicks']:6,} clk "
                  f"| CTR {fmt_ctr(g['ctr'])} | pos {g['position']}")

    print()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    if not os.path.exists(path):
        print(f"ERROR: GSC data file not found: {path}", file=sys.stderr)
        print("Run analyze_gsc.py first to generate it.", file=sys.stderr)
        sys.exit(1)
    show(path)
