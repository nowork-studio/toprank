#!/usr/bin/env python3
"""
Display PageSpeed Insights results in a terminal-friendly format.
Reads the JSON output from pagespeed.py.

Usage:
  python3 show_pagespeed.py
  python3 show_pagespeed.py --input /path/to/pagespeed.json
"""

import argparse
import json
import os
import sys
import tempfile


def rating_indicator(rating):
    """Return a visual indicator for CrUX rating."""
    if not rating:
        return "?"
    return {"FAST": "GOOD", "AVERAGE": "NEEDS WORK", "SLOW": "POOR"}.get(rating, rating)


def score_indicator(score):
    """Return a visual indicator for Lighthouse score."""
    if score is None:
        return "N/A"
    if score >= 90:
        return f"{score} (Good)"
    elif score >= 50:
        return f"{score} (Needs Work)"
    else:
        return f"{score} (Poor)"


def format_ms(val):
    """Format milliseconds for display."""
    if val is None:
        return "N/A"
    if val >= 1000:
        return f"{val / 1000:.1f} s"
    return f"{val:.0f} ms"


def format_bytes(val):
    """Format bytes for display."""
    if not val:
        return ""
    if val >= 1_048_576:
        return f"{val / 1_048_576:.1f} MB"
    if val >= 1024:
        return f"{val / 1024:.0f} KB"
    return f"{val} B"


def format_cls(val, is_crux=False):
    """Format CLS value.
    CrUX API returns CLS as an integer (CLS * 100), e.g. 10 means 0.10.
    Lighthouse returns CLS as a float, e.g. 0.10."""
    if val is None:
        return "N/A"
    if isinstance(val, (int, float)):
        if is_crux:
            return f"{val / 100:.3f}"
        return f"{val:.3f}"
    return str(val)


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_result(result):
    """Print a single URL's PageSpeed result."""
    url = result.get("url", "?")
    strategy = result.get("strategy", "?")

    if result.get("error"):
        print(f"\n  {url} ({strategy}): ERROR - {result['error']}")
        return

    print(f"\n  URL: {url}")
    print(f"  Strategy: {strategy}")

    # Lab data (Lighthouse)
    lab = result.get("lab_data")
    if lab:
        score = lab.get("performance_score")
        print(f"\n  Performance Score: {score_indicator(score)}")
        print(f"  {'─' * 40}")

        metrics = [
            ("First Contentful Paint", lab.get("fcp", {})),
            ("Largest Contentful Paint", lab.get("lcp", {})),
            ("Total Blocking Time", lab.get("tbt", {})),
            ("Cumulative Layout Shift", lab.get("cls", {})),
            ("Speed Index", lab.get("si", {})),
            ("Time to Interactive", lab.get("tti", {})),
        ]

        print(f"  {'Metric':<30} {'Value':<15} {'Score'}")
        print(f"  {'─' * 55}")
        for name, data in metrics:
            if not data:
                continue
            display = data.get("display", "")
            metric_score = data.get("score")
            if metric_score is not None:
                metric_score = f"{round(metric_score * 100)}/100"
            else:
                metric_score = "N/A"
            print(f"  {name:<30} {display:<15} {metric_score}")

    # Field data (CrUX - real user data)
    field = result.get("field_data")
    if field:
        print(f"\n  Real-User Data (Chrome UX Report)")
        print(f"  {'─' * 40}")
        overall = field.get("overall_category")
        if overall:
            print(f"  Overall: {rating_indicator(overall)}")

        crux_metrics = [
            ("LCP", field.get("lcp"), "ms", False),
            ("INP", field.get("inp"), "ms", False),
            ("CLS", field.get("cls"), "", True),
            ("FCP", field.get("fcp"), "ms", False),
            ("TTFB", field.get("ttfb"), "ms", False),
        ]

        print(f"  {'Metric':<8} {'Value':<12} {'Rating'}")
        print(f"  {'─' * 35}")
        for name, data, unit, is_cls in crux_metrics:
            if not data:
                continue
            val = data.get("value")
            rating = data.get("rating")
            if is_cls:
                display = format_cls(val, is_crux=True)
            elif unit == "ms":
                display = format_ms(val)
            else:
                display = str(val) if val is not None else "N/A"
            print(f"  {name:<8} {display:<12} {rating_indicator(rating)}")

    # Origin field data (site-wide CrUX)
    origin = result.get("origin_field_data")
    if origin and origin.get("overall_category"):
        print(f"\n  Origin (Site-Wide) Real-User Data")
        print(f"  {'─' * 40}")
        print(f"  Overall: {rating_indicator(origin.get('overall_category'))}")

        crux_metrics = [
            ("LCP", origin.get("lcp"), "ms", False),
            ("INP", origin.get("inp"), "ms", False),
            ("CLS", origin.get("cls"), "", True),
        ]
        for name, data, unit, is_cls in crux_metrics:
            if not data:
                continue
            val = data.get("value")
            rating = data.get("rating")
            if is_cls:
                display = format_cls(val, is_crux=True)
            elif unit == "ms":
                display = format_ms(val)
            else:
                display = str(val) if val is not None else "N/A"
            print(f"  {name:<8} {display:<12} {rating_indicator(rating)}")

    # Opportunities
    opportunities = result.get("opportunities", [])
    if opportunities:
        print(f"\n  Top Optimization Opportunities")
        print(f"  {'─' * 55}")
        print(f"  {'Opportunity':<40} {'Savings'}")
        print(f"  {'─' * 55}")
        for opp in opportunities:
            title = opp.get("title", "?")
            if len(title) > 38:
                title = title[:35] + "..."
            savings = format_ms(opp.get("savings_ms"))
            bytes_saved = opp.get("savings_bytes", 0)
            extra = f" ({format_bytes(bytes_saved)})" if bytes_saved else ""
            print(f"  {title:<40} {savings}{extra}")

    # Diagnostics
    diagnostics = result.get("diagnostics", [])
    if diagnostics:
        print(f"\n  Diagnostics")
        print(f"  {'─' * 55}")
        for diag in diagnostics:
            title = diag.get("title", "?")
            display = diag.get("display", "")
            score = diag.get("score")
            indicator = ""
            if score is not None:
                indicator = f" (score: {round(score * 100)}/100)"
            suffix = f" — {display}" if display else ""
            print(f"  - {title}{suffix}{indicator}")


def main():
    parser = argparse.ArgumentParser()
    _default_in = os.path.join(tempfile.gettempdir(), f"pagespeed_{os.getuid()}.json")
    parser.add_argument("--input", default=_default_in, help="Input JSON file")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        print("Run pagespeed.py first to generate the data.", file=sys.stderr)
        sys.exit(1)

    with open(args.input) as f:
        data = json.load(f)

    summary = data.get("summary", {})
    results = data.get("results", [])

    print_section("PageSpeed Insights Report")
    print(f"  URLs tested: {summary.get('urls_tested', '?')}")
    print(f"  Strategies: {', '.join(summary.get('strategies', []))}")
    avg = summary.get("avg_performance_score")
    if avg is not None:
        print(f"  Average score: {score_indicator(avg)}")

    for result in results:
        print(f"\n{'─' * 60}")
        print_result(result)

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
