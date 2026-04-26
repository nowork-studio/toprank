"""Portable per-user identifier and secure tmp-file helpers.

Why this exists
---------------
The seo-analysis scripts cache intermediate JSON in the system tempdir between
invocations (e.g. ``analyze_gsc.py`` writes, ``show_gsc.py`` reads). Filenames
are keyed by a per-user suffix so that on shared POSIX hosts two users running
the scripts in the same ``/tmp`` don't collide.

Two primitives:

- :func:`portable_uid` — stable, path-safe identifier for the current user.
  Uses ``os.getuid()`` on POSIX (preserving the historical filename suffix on
  Linux/macOS), sanitized ``getpass.getuser()`` on Windows where ``getuid``
  doesn't exist, and a hashed env-based fallback if neither is available.

- :func:`secure_write_json` — atomic, mode-0600, symlink-safe JSON write,
  matching the pattern already used in the CMS fetchers
  (``fetch_*_content.py``). Writes to a fresh ``mkstemp()`` file in the
  destination directory, then ``os.replace()``s it into place. Defends
  against symlink attacks on shared tmpdirs because POSIX ``rename(2)``
  removes a pre-existing symlink at the destination instead of following it.

Usage as a module: ``python3 -m _uid`` prints the portable uid (used by the
SKILL.md heredoc in place of the previous ``os.getuid()`` shell call).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from typing import Any

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9_-]")


def portable_uid() -> str:
    """Return a stable, path-safe identifier for the current user."""
    getuid = getattr(os, "getuid", None)
    if getuid is not None:
        return str(getuid())

    import getpass
    try:
        username = getpass.getuser()
    except Exception:
        username = ""

    # Sanitize: env-var-derived usernames could contain path separators or
    # null bytes; we interpolate the result into a filesystem path.
    safe = _SAFE_CHARS.sub("_", username)[:32].strip("_")
    if safe:
        return safe

    seed = os.environ.get("APPDATA") or os.environ.get("USERPROFILE") or ""
    if seed:
        return hashlib.sha1(seed.encode("utf-8", "replace")).hexdigest()[:8]

    return f"pid{os.getpid()}"


def secure_write_json(path: str, data: Any) -> None:
    """Atomically write ``data`` as JSON to ``path`` with mode 0600.

    Defends against symlink-based clobber attacks on shared tempdirs.
    """
    out_dir = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, suffix=".json.tmp")
    try:
        try:
            os.chmod(tmp_path, 0o600)
        except (OSError, NotImplementedError):
            # Windows / unusual filesystems may not honor POSIX modes.
            pass
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    sys.stdout.write(portable_uid())
