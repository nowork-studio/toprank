#!/usr/bin/env python3
"""Pre-flight check for seo-analysis skill.

Verifies gcloud is installed, a GCP project is configured, the Search Console
API is enabled, and Google ADC credentials are configured with the correct scope.
No external dependencies — uses only Python stdlib and the gcloud CLI.

Exit codes:
  0 — all dependencies ready
  1 — unrecoverable error (gcloud missing, auth failed, etc.)
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request


def check_python_version():
    if sys.version_info < (3, 8):
        print(f"ERROR: Python 3.8+ required (you have {sys.version.split()[0]})", file=sys.stderr)
        print("  Upgrade: https://python.org/downloads", file=sys.stderr)
        sys.exit(1)


def check_gcloud():
    """Verify gcloud CLI is installed; print OS-specific install instructions if not."""
    if shutil.which("gcloud"):
        return

    system = platform.system()
    print("ERROR: gcloud CLI not found.", file=sys.stderr)
    print("", file=sys.stderr)

    if system == "Darwin":
        print("Install with Homebrew (recommended):", file=sys.stderr)
        print("  brew install google-cloud-sdk", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or download the installer:", file=sys.stderr)
        print("  https://cloud.google.com/sdk/docs/install#mac", file=sys.stderr)
    elif system == "Linux":
        distro = ""
        try:
            with open("/etc/os-release") as f:
                distro = f.read().lower()
        except FileNotFoundError:
            pass

        if "ubuntu" in distro or "debian" in distro:
            print("Install with apt:", file=sys.stderr)
            print("  sudo apt-get install google-cloud-cli", file=sys.stderr)
        elif "fedora" in distro or "rhel" in distro or "centos" in distro:
            print("Install with dnf:", file=sys.stderr)
            print("  sudo dnf install google-cloud-cli", file=sys.stderr)
        else:
            print("Install via curl:", file=sys.stderr)
            print("  curl https://sdk.cloud.google.com | bash", file=sys.stderr)
        print("", file=sys.stderr)
        print("Full guide: https://cloud.google.com/sdk/docs/install#linux", file=sys.stderr)
    elif system == "Windows":
        print("Install with winget:", file=sys.stderr)
        print("  winget install Google.CloudSDK", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or download the installer:", file=sys.stderr)
        print("  https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", file=sys.stderr)
    else:
        print("See: https://cloud.google.com/sdk/docs/install", file=sys.stderr)

    sys.exit(1)


def check_gcloud_project():
    """Ensure gcloud has an active project. Run gcloud init if not."""
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: gcloud timed out. Check your network.", file=sys.stderr)
        sys.exit(1)

    project = result.stdout.strip()
    # gcloud prints "(unset)" to stderr when no project is set
    if project and project != "(unset)":
        print(f"GCP project: {project}", file=sys.stderr)
        return

    # No project configured — first-time gcloud user
    print("No GCP project configured.", file=sys.stderr)

    if not sys.stdin.isatty():
        print("Run in an interactive terminal:", file=sys.stderr)
        print("  gcloud init", file=sys.stderr)
        print("This will create or select a Google Cloud project.", file=sys.stderr)
        sys.exit(1)

    print("Running 'gcloud init' to set up your project...", file=sys.stderr)
    print("", file=sys.stderr)
    init_result = subprocess.run(["gcloud", "init"])
    if init_result.returncode != 0:
        print("", file=sys.stderr)
        print("ERROR: gcloud init failed or was cancelled.", file=sys.stderr)
        print("Run 'gcloud init' manually and try again.", file=sys.stderr)
        sys.exit(1)

    # Verify project was set
    verify = subprocess.run(
        ["gcloud", "config", "get-value", "project"],
        capture_output=True, text=True, timeout=15,
    )
    project = verify.stdout.strip()
    if not project or project == "(unset)":
        print("ERROR: No project selected during gcloud init.", file=sys.stderr)
        print("Run 'gcloud init' again and select or create a project.", file=sys.stderr)
        sys.exit(1)

    print(f"GCP project: {project}", file=sys.stderr)


def check_search_console_api():
    """Ensure the Search Console API is enabled in the active project."""
    try:
        result = subprocess.run(
            ["gcloud", "services", "list", "--enabled",
             "--filter=config.name:searchconsole.googleapis.com",
             "--format=value(config.name)"],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("WARNING: Timed out checking Search Console API status.", file=sys.stderr)
        print("If you get API errors later, run:", file=sys.stderr)
        print("  gcloud services enable searchconsole.googleapis.com", file=sys.stderr)
        return  # non-fatal — let it fail later with a clear error

    if "searchconsole.googleapis.com" in result.stdout:
        print("Search Console API: enabled", file=sys.stderr)
        return

    # API not enabled — try to enable it automatically
    print("Search Console API is not enabled. Enabling it now...", file=sys.stderr)
    enable_result = subprocess.run(
        ["gcloud", "services", "enable", "searchconsole.googleapis.com"],
        capture_output=True, text=True, timeout=60,
    )
    if enable_result.returncode == 0:
        print("Search Console API: enabled", file=sys.stderr)
        return

    # Enable failed — print manual instructions
    print("", file=sys.stderr)
    print("ERROR: Could not enable the Search Console API automatically.", file=sys.stderr)
    stderr_msg = enable_result.stderr.strip()
    if stderr_msg:
        print(f"  Reason: {stderr_msg}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Enable it manually:", file=sys.stderr)
    print("  gcloud services enable searchconsole.googleapis.com", file=sys.stderr)
    print("", file=sys.stderr)
    print("Or via the Cloud Console:", file=sys.stderr)
    print("  https://console.cloud.google.com/apis/library/searchconsole.googleapis.com", file=sys.stderr)
    sys.exit(1)


_GSC_SCOPES = (
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/webmasters.readonly",
)
_GSC_SCOPES_ARG = ",".join(_GSC_SCOPES)


def _token_has_gsc_scope(token):
    """Return True if the token includes at least one Search Console scope.

    Calls the Google tokeninfo endpoint to inspect the granted scopes.
    Returns None if the check cannot be completed (network error, etc.).
    """
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?access_token={token}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        granted = set(data.get("scope", "").split())
        return bool(granted & set(_GSC_SCOPES))
    except Exception:
        return None  # can't verify — caller decides what to do


def check_adc_credentials():
    """Check ADC credentials exist with correct Search Console scope.

    If credentials are missing or have the wrong scope (e.g. cloud-platform from
    a prior bare `gcloud auth application-default login`), re-authenticates with
    the correct scopes.
    """
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: gcloud timed out checking credentials. Check your network.", file=sys.stderr)
        sys.exit(1)

    needs_auth = True
    if result.returncode == 0 and result.stdout.strip():
        token = result.stdout.strip()
        has_scope = _token_has_gsc_scope(token)
        if has_scope is True:
            print("Google credentials: OK (Search Console scope confirmed)", file=sys.stderr)
            return
        elif has_scope is None:
            # tokeninfo unreachable — assume credentials are fine, let the API call fail
            print("Google credentials: found (scope check skipped — no network)", file=sys.stderr)
            return
        else:
            # Credentials exist but have the wrong scope (e.g. cloud-platform)
            print("WARNING: Existing credentials are missing the Search Console scope.", file=sys.stderr)
            print("  This happens when `gcloud auth application-default login` was run", file=sys.stderr)
            print("  without --scopes, granting broad cloud-platform access instead.", file=sys.stderr)
            print("  Re-authenticating with the correct scope now...", file=sys.stderr)
            print("", file=sys.stderr)
            needs_auth = True

    if needs_auth and not sys.stdin.isatty():
        print("ERROR: No Application Default Credentials with Search Console scope.", file=sys.stderr)
        print("Run in an interactive terminal:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print(f"    --scopes={_GSC_SCOPES_ARG}", file=sys.stderr)
        sys.exit(1)

    print("Opening browser for Google authentication...", file=sys.stderr)
    print("(Log in with the Google account that has access to Search Console.)", file=sys.stderr)
    print("", file=sys.stderr)
    auth_result = subprocess.run(
        ["gcloud", "auth", "application-default", "login",
         f"--scopes={_GSC_SCOPES_ARG}"],
    )
    if auth_result.returncode != 0:
        print("", file=sys.stderr)
        print("ERROR: Authentication failed or was cancelled.", file=sys.stderr)
        print("Run this manually and try again:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print(f"    --scopes={_GSC_SCOPES_ARG}", file=sys.stderr)
        sys.exit(1)
    print("Authentication successful.", file=sys.stderr)


def _get_adc_quota_project():
    """Return the quota_project_id from the ADC JSON file, or None if absent."""
    adc_dir = os.environ.get("CLOUDSDK_CONFIG") or os.path.join(
        os.path.expanduser("~"), ".config", "gcloud"
    )
    adc_path = os.path.join(adc_dir, "application_default_credentials.json")
    if not os.path.isfile(adc_path):
        return None
    try:
        with open(adc_path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data.get("quota_project_id") or None
    except (OSError, ValueError):
        return None


def check_quota_project():
    """Ensure ADC has a quota project set; auto-configure it from the active gcloud project.

    Without a quota project, user-credential ADC calls to Search Console return 403:
      "The searchconsole.googleapis.com API requires a quota project."
    Fix: gcloud auth application-default set-quota-project PROJECT_ID

    Returns True if quota project is confirmed set, False if it could not be configured.
    """
    if _get_adc_quota_project():
        return True  # already configured

    # Look up the active gcloud project
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        print("WARNING: gcloud timed out getting project for quota setup.", file=sys.stderr)
        return False

    project = result.stdout.strip() if result.returncode == 0 else ""
    if not project or project == "(unset)":
        print("WARNING: Cannot set quota project — no active GCP project.", file=sys.stderr)
        print("  Run: gcloud auth application-default set-quota-project YOUR_PROJECT_ID", file=sys.stderr)
        return False

    print(f"Setting ADC quota project to '{project}'...", file=sys.stderr)
    try:
        set_result = subprocess.run(
            ["gcloud", "auth", "application-default", "set-quota-project", project],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("WARNING: gcloud timed out setting quota project.", file=sys.stderr)
        print(f"  Run manually: gcloud auth application-default set-quota-project '{project}'", file=sys.stderr)
        return False
    if set_result.returncode == 0:
        print(f"ADC quota project: {project}", file=sys.stderr)
        return True
    else:
        print("WARNING: Could not set quota project automatically.", file=sys.stderr)
        print(f"  Run manually: gcloud auth application-default set-quota-project '{project}'", file=sys.stderr)
        stderr_msg = set_result.stderr.strip()
        if stderr_msg:
            print(f"  Reason: {stderr_msg}", file=sys.stderr)
        return False


def main():
    check_python_version()
    check_gcloud()
    check_gcloud_project()
    check_search_console_api()
    check_adc_credentials()
    quota_ok = check_quota_project()
    if quota_ok:
        print("OK: All dependencies ready.", file=sys.stderr)
    else:
        print("OK: All dependencies ready (quota project not confirmed — GSC may return 403).", file=sys.stderr)


if __name__ == "__main__":
    main()
