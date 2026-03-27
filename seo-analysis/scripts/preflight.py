#!/usr/bin/env python3
"""Pre-flight check for seo-analysis skill.

Verifies gcloud is installed and Google ADC credentials are configured.
No external dependencies — uses only Python stdlib and the gcloud CLI.

Exit codes:
  0 — all dependencies ready
  1 — unrecoverable error (gcloud missing, auth failed, etc.)
"""

import platform
import shutil
import subprocess
import sys


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


def check_adc_credentials():
    """Check ADC credentials exist; auto-trigger gcloud auth if not."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: gcloud timed out checking credentials. Check your network.", file=sys.stderr)
        sys.exit(1)

    if result.returncode == 0 and result.stdout.strip():
        return  # credentials found and working

    # No valid credentials — auto-trigger the browser auth flow (interactive terminal only)
    if not sys.stdin.isatty():
        print("ERROR: No Application Default Credentials found.", file=sys.stderr)
        print("Run in an interactive terminal:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print("    --scopes=https://www.googleapis.com/auth/webmasters.readonly", file=sys.stderr)
        sys.exit(1)

    print("No Google credentials found. Opening browser for authentication...", file=sys.stderr)
    print("", file=sys.stderr)
    auth_result = subprocess.run(
        ["gcloud", "auth", "application-default", "login",
         "--scopes=https://www.googleapis.com/auth/webmasters.readonly"],
    )
    if auth_result.returncode != 0:
        print("", file=sys.stderr)
        print("ERROR: Authentication failed or was cancelled.", file=sys.stderr)
        print("Run this manually and try again:", file=sys.stderr)
        print("  gcloud auth application-default login \\", file=sys.stderr)
        print("    --scopes=https://www.googleapis.com/auth/webmasters.readonly", file=sys.stderr)
        sys.exit(1)
    print("Authentication successful.", file=sys.stderr)


def main():
    check_python_version()
    check_gcloud()
    check_adc_credentials()
    print("OK: All dependencies ready.", file=sys.stderr)


if __name__ == "__main__":
    main()
