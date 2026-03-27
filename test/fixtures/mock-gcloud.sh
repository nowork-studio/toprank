#!/bin/bash
# Mock gcloud binary for E2E tests.
# Returns a fake access token when called with auth credentials subcommands.
# All other subcommands are passed through to the real gcloud (if available).

if [[ "$*" == *"application-default print-access-token"* ]]; then
  echo "ya29.mock-token-for-testing-only"
  exit 0
fi

# Unknown subcommands: exit cleanly (don't fall through — mock is first in PATH
# so `command -v gcloud` would resolve back to this script causing infinite recursion)
exit 0
