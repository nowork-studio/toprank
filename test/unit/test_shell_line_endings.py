"""Bash entrypoints must remain runnable in Windows checkouts."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HELPERS = [
    "bin/notfair-change-watch",
    "bin/notfair-config",
    "bin/notfair-update-check",
]


@pytest.mark.parametrize("relative_path", HELPERS)
def test_bash_helper_uses_lf(relative_path):
    assert b"\r\n" not in (ROOT / relative_path).read_bytes()
