"""Shared Google Search Console authentication helpers.

Handles ADC credential loading with automatic quota project detection.
Both list_gsc_sites.py and analyze_gsc.py import from here.
"""

import subprocess
import sys

try:
    import google.auth
    import google.auth.transport.requests
except ImportError:
    print("ERROR: google-auth package not installed. Run:", file=sys.stderr)
    print("  pip install google-auth", file=sys.stderr)
    sys.exit(1)


def _ensure_quota_project(credentials):
    """Ensure credentials have a quota project set (required for user credentials).

    If quota_project_id is missing from ADC, auto-detect from gcloud config.
    """
    if getattr(credentials, "quota_project_id", None):
        return credentials
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, timeout=10,
        )
        project = result.stdout.strip()
        if result.returncode == 0 and project:
            return credentials.with_quota_project(project)
    except (FileNotFoundError, subprocess.TimeoutExpired, AttributeError):
        pass
    return credentials


def get_credentials():
    """Load ADC credentials with automatic quota project detection.

    Returns (credentials, project) tuple. The credentials object has
    quota_project_id set, which AuthorizedSession uses to send the
    x-goog-user-project header automatically.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
    except google.auth.exceptions.DefaultCredentialsError:
        print("ERROR: No Application Default Credentials found. Run:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print("    --scopes=https://www.googleapis.com/auth/webmasters.readonly", file=sys.stderr)
        sys.exit(1)
    credentials = _ensure_quota_project(credentials)
    return credentials, project


def get_session():
    """Create an AuthorizedSession with ADC credentials and quota project."""
    credentials, _ = get_credentials()
    return google.auth.transport.requests.AuthorizedSession(credentials)
