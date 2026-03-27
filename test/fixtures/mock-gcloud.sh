#!/bin/bash
# Mock gcloud binary for E2E tests.
# Returns a fake access token when called with auth credentials subcommands.
# All other subcommands are passed through to the real gcloud (if available).

if [[ "$*" == *"application-default print-access-token"* ]]; then
  echo "ya29.mock-token-for-testing-only"
  exit 0
fi

# Fall through to real gcloud for anything else
if command -v gcloud &>/dev/null; then
  exec gcloud "$@"
fi

exit 0
