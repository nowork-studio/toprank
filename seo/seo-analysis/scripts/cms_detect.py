#!/usr/bin/env python3
"""Detect which CMS is configured via environment variables.

Checks for CMS-specific env vars and prints the detected CMS type to stdout.
Used by seo-analysis to determine which preflight/fetch scripts to run.

No external dependencies — uses only Python stdlib.

Exit codes:
  0 — CMS found (prints: wordpress | contentful | ghost | strapi)
  2 — No CMS configured
"""

import os
import sys


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


def main():
    file_env = find_and_load_env()

    def get(key):
        return os.environ.get(key) or file_env.get(key, "")

    # Check each CMS by its unique required env var.
    # Order matters when multiple are set: prefer the most recently added CMSes
    # (WordPress, Contentful, Ghost) over the original Strapi support, so that
    # users who migrate don't silently fall back to Strapi.
    if get("WP_URL"):
        print("wordpress")
        sys.exit(0)
    if get("CONTENTFUL_SPACE_ID"):
        print("contentful")
        sys.exit(0)
    if get("GHOST_URL"):
        print("ghost")
        sys.exit(0)
    if get("STRAPI_URL"):
        print("strapi")
        sys.exit(0)

    sys.exit(2)


if __name__ == "__main__":
    main()
