#!/usr/bin/env python3
"""
Mock analyze_gsc.py for E2E tests.

Reads sample_gsc_data.json from the test fixtures directory instead of
calling the real GSC API. Used to test the full skill workflow without
needing real Google credentials.

Usage (same interface as real script):
  python3 mock-analyze-gsc.py --site "sc-domain:example-saas.com" --days 90
"""

import argparse
import json
import os
import shutil
import sys

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'sample_gsc_data.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', required=True)
    parser.add_argument('--days', type=int, default=90)
    parser.add_argument('--output', default='/tmp/gsc_analysis.json')
    args = parser.parse_args()

    print(f'[mock] Loading fixture data for: {args.site}', file=sys.stderr)
    print(f'[mock] (No real GSC call — using test fixture)', file=sys.stderr)

    with open(FIXTURE_PATH) as f:
        data = json.load(f)

    # Override site in fixture to match requested site
    data['site'] = args.site
    data['period']['days'] = args.days

    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)

    summary = data['summary']
    print(f'\nDone. Results saved to {args.output}', file=sys.stderr)
    print(
        f'\nSummary: {summary["clicks"]:,} clicks | {summary["impressions"]:,} impressions | '
        f'CTR {summary["ctr"]}% | Avg position {summary["position"]}',
        file=sys.stderr,
    )


if __name__ == '__main__':
    main()
