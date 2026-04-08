#!/usr/bin/env python3
"""
Pull PageSpeed Insights data for one or more URLs.
Outputs structured JSON with Core Web Vitals, performance scores,
and optimization opportunities.

Usage:
  python3 pagespeed.py --urls "https://example.com,https://example.com/about"
  python3 pagespeed.py --urls "https://example.com" --strategy mobile
  python3 pagespeed.py --urls "https://example.com" --api-key "YOUR_KEY"
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed


PSI_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _load_api_key_from_env_files():
    """Try to load PAGESPEED_API_KEY from .env files if not in environment."""
    for env_file in [".env", ".env.local", os.path.expanduser("~/.toprank/.env")]:
        if os.path.isfile(env_file):
            try:
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("PAGESPEED_API_KEY=") and not line.startswith("#"):
                            val = line.split("=", 1)[1].strip().strip("'\"")
                            if val:
                                return val
            except OSError:
                pass
    return None


def run_pagespeed(url, strategy="mobile", api_key=None):
    """Call PageSpeed Insights API for a single URL and strategy."""
    params = {
        "url": url,
        "strategy": strategy,
        "category": "PERFORMANCE",
    }
    if api_key:
        params["key"] = api_key

    api_url = f"{PSI_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(api_url)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else "(no body)"
        print(f"PSI API error {e.code} for {url}: {err_body}", file=sys.stderr)
        if e.code == 429:
            print("", file=sys.stderr)
            print("  HINT: Quota exceeded. Fix options:", file=sys.stderr)
            print("  1. Create an API key: https://console.cloud.google.com/apis/credentials", file=sys.stderr)
            print("     Then: export PAGESPEED_API_KEY='your-key'", file=sys.stderr)
            print("  2. Enable the API: gcloud services enable pagespeedonline.googleapis.com", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"PSI API network error for {url}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"PSI API unexpected error for {url}: {e}", file=sys.stderr)
        return None


def extract_crux_metric(metric_data):
    """Extract Chrome UX Report (field data) metric value and rating."""
    if not metric_data:
        return None
    percentile = metric_data.get("percentile")
    category = metric_data.get("category")
    distributions = metric_data.get("distributions", [])
    return {
        "value": percentile,
        "rating": category,  # FAST, AVERAGE, SLOW
        "distributions": [
            {"min": d.get("min", 0), "max": d.get("max"), "proportion": round(d.get("proportion", 0), 4)}
            for d in distributions
        ] if distributions else []
    }


def extract_field_data(loading_experience):
    """Extract CrUX field data from the loading experience object."""
    if not loading_experience or not loading_experience.get("metrics"):
        return None

    metrics = loading_experience["metrics"]
    result = {
        "overall_category": loading_experience.get("overall_category"),
    }

    metric_map = {
        "LARGEST_CONTENTFUL_PAINT_MS": "lcp",
        "INTERACTION_TO_NEXT_PAINT": "inp",
        "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls",
        "FIRST_CONTENTFUL_PAINT_MS": "fcp",
        "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "ttfb",
    }

    for api_key, short_key in metric_map.items():
        if api_key in metrics:
            result[short_key] = extract_crux_metric(metrics[api_key])

    return result


def extract_lab_data(lighthouse_result):
    """Extract Lighthouse lab data (synthetic test results)."""
    if not lighthouse_result:
        return None

    audits = lighthouse_result.get("audits", {})
    categories = lighthouse_result.get("categories", {})

    perf_score = None
    perf_category = categories.get("performance", {})
    if perf_category:
        perf_score = perf_category.get("score")
        if perf_score is not None:
            perf_score = round(perf_score * 100)

    def get_audit_value(audit_id, field="numericValue"):
        audit = audits.get(audit_id, {})
        val = audit.get(field)
        display = audit.get("displayValue", "")
        score = audit.get("score")
        return {"value": val, "display": display, "score": score}

    lab = {
        "performance_score": perf_score,
        "fcp": get_audit_value("first-contentful-paint"),
        "lcp": get_audit_value("largest-contentful-paint"),
        "cls": get_audit_value("cumulative-layout-shift"),
        "tbt": get_audit_value("total-blocking-time"),
        "si": get_audit_value("speed-index"),
        "tti": get_audit_value("interactive"),
    }

    return lab


def extract_opportunities(lighthouse_result, max_items=10):
    """Extract top optimization opportunities from Lighthouse."""
    if not lighthouse_result:
        return []

    audits = lighthouse_result.get("audits", {})
    categories = lighthouse_result.get("categories", {})
    perf = categories.get("performance", {})
    audit_refs = perf.get("auditRefs", [])

    # Collect opportunity-type audits that failed
    opportunities = []
    for ref in audit_refs:
        if ref.get("group") != "opportunity":
            continue
        audit_id = ref.get("id", "")
        audit = audits.get(audit_id, {})
        score = audit.get("score")
        if score is not None and score >= 0.9:
            continue  # already passing
        details = audit.get("details", {})
        overallSavingsMs = details.get("overallSavingsMs") or audit.get("numericValue", 0)
        if not overallSavingsMs or overallSavingsMs <= 0:
            continue
        overallSavingsBytes = details.get("overallSavingsBytes", 0)

        opportunities.append({
            "id": audit_id,
            "title": audit.get("title", audit_id),
            "description": audit.get("description", ""),
            "savings_ms": round(overallSavingsMs),
            "savings_bytes": overallSavingsBytes,
            "score": score,
            "display": audit.get("displayValue", ""),
        })

    opportunities.sort(key=lambda x: x["savings_ms"], reverse=True)
    return opportunities[:max_items]


def extract_diagnostics(lighthouse_result, max_items=10):
    """Extract diagnostic audit findings from Lighthouse."""
    if not lighthouse_result:
        return []

    audits = lighthouse_result.get("audits", {})
    categories = lighthouse_result.get("categories", {})
    perf = categories.get("performance", {})
    audit_refs = perf.get("auditRefs", [])

    diagnostics = []
    for ref in audit_refs:
        if ref.get("group") != "diagnostics":
            continue
        audit_id = ref.get("id", "")
        audit = audits.get(audit_id, {})
        score = audit.get("score")
        if score is not None and score >= 0.9:
            continue

        diagnostics.append({
            "id": audit_id,
            "title": audit.get("title", audit_id),
            "description": audit.get("description", ""),
            "display": audit.get("displayValue", ""),
            "score": score,
        })

    diagnostics.sort(key=lambda x: (x["score"] or 0))
    return diagnostics[:max_items]


def analyze_url(url, strategy, api_key):
    """Run PageSpeed analysis for a single URL and return structured results."""
    print(f"  Analyzing {url} ({strategy})...", file=sys.stderr)
    raw = run_pagespeed(url, strategy=strategy, api_key=api_key)
    if not raw:
        return {"url": url, "strategy": strategy, "error": "API call failed"}

    lighthouse = raw.get("lighthouseResult", {})

    result = {
        "url": url,
        "strategy": strategy,
        "field_data": extract_field_data(raw.get("loadingExperience")),
        "origin_field_data": extract_field_data(raw.get("originLoadingExperience")),
        "lab_data": extract_lab_data(lighthouse),
        "opportunities": extract_opportunities(lighthouse),
        "diagnostics": extract_diagnostics(lighthouse),
    }

    score = (result["lab_data"] or {}).get("performance_score")
    if score is not None:
        print(f"  \u2713 {url}: score {score}/100", file=sys.stderr)
    else:
        print(f"  \u2713 {url}: done (no score)", file=sys.stderr)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", required=True,
                        help="Comma-separated URLs to analyze")
    parser.add_argument("--strategy", default="mobile",
                        choices=["mobile", "desktop"],
                        help="Test strategy (default: mobile)")
    parser.add_argument("--both-strategies", action="store_true",
                        help="Run both mobile and desktop")
    parser.add_argument("--api-key", default=os.environ.get("PAGESPEED_API_KEY", ""),
                        help="Google API key (optional, increases rate limits)")
    _default_out = os.path.join(tempfile.gettempdir(), f"pagespeed_{os.getuid()}.json")
    parser.add_argument("--output", default=_default_out, help="Output file")
    args = parser.parse_args()

    urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    if not urls:
        print("ERROR: No URLs provided.", file=sys.stderr)
        sys.exit(1)

    strategies = ["mobile", "desktop"] if args.both_strategies else [args.strategy]
    api_key = args.api_key or _load_api_key_from_env_files()
    if api_key:
        print("Using PageSpeed API key.", file=sys.stderr)
    else:
        print("No API key found. Requests may hit quota limits.", file=sys.stderr)
        print("  Set PAGESPEED_API_KEY or add to ~/.toprank/.env", file=sys.stderr)

    tasks = []
    for url in urls:
        for strategy in strategies:
            tasks.append((url, strategy))

    print(f"Running PageSpeed analysis for {len(urls)} URL(s), "
          f"strategy: {', '.join(strategies)}...", file=sys.stderr)

    results = []
    # PSI API has rate limits; use modest concurrency
    max_workers = min(len(tasks), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(analyze_url, url, strategy, api_key): (url, strategy)
            for url, strategy in tasks
        }
        for future in as_completed(futures):
            url, strategy = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"  \u2717 {url} ({strategy}): {exc}", file=sys.stderr)
                results.append({"url": url, "strategy": strategy, "error": str(exc)})

    # Sort results: by URL then strategy for consistent output
    results.sort(key=lambda x: (x["url"], x.get("strategy", "")))

    # Build summary
    scored = [r for r in results if (r.get("lab_data") or {}).get("performance_score") is not None]
    summary = {
        "urls_tested": len(urls),
        "strategies": strategies,
        "results_count": len(results),
        "avg_performance_score": (
            round(sum(r["lab_data"]["performance_score"] for r in scored) / len(scored))
            if scored else None
        ),
    }

    output = {
        "summary": summary,
        "results": results,
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. Results saved to {args.output}", file=sys.stderr)
    if summary["avg_performance_score"] is not None:
        print(f"Average performance score: {summary['avg_performance_score']}/100", file=sys.stderr)


if __name__ == "__main__":
    main()
