---
name: toprank-upgrade
argument-hint: "<or just run '/toprank-upgrade'>"
description: >
  Upgrade toprank plugin to the latest version. Updates the marketplace repo,
  installs the new version to the plugin cache, and updates installed_plugins.json.
  Use when asked to "upgrade toprank", "update toprank", or "get latest version".
  Also handles inline upgrade prompts when a skill detects UPGRADE_AVAILABLE at startup.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# /toprank-upgrade

Upgrade the toprank plugin to the latest version and show what's new.

## Key paths

| What | Path |
|------|------|
| Marketplace repo | `~/.claude/plugins/marketplaces/nowork-studio/` |
| Plugin cache | `~/.claude/plugins/cache/nowork-studio/toprank/<version>/` |
| Installed plugins | `~/.claude/plugins/installed_plugins.json` |
| Update state | `~/.toprank/` |

---

## Inline upgrade flow

This section is used when a skill preamble outputs `UPGRADE_AVAILABLE`.

### Step 1: Auto-upgrade

Log "Upgrading toprank v{old} → v{new}..." and proceed to Step 2.

---

### Step 2: Detect current install

First check for dev symlink (see "Dev symlink detection" section). If detected, stop — do not upgrade.

```bash
# Find the currently installed plugin path
INSTALLED_DIR=$(ls -d ~/.claude/plugins/cache/nowork-studio/toprank/*/ 2>/dev/null | grep -v '.bak' | head -1)
if [ -z "$INSTALLED_DIR" ]; then
  echo "ERROR: toprank plugin not found in cache"; exit 1
fi
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/nowork-studio"
if [ ! -d "$MARKETPLACE_DIR/.git" ]; then
  echo "ERROR: marketplace repo not found at $MARKETPLACE_DIR"; exit 1
fi
echo "Current install: $INSTALLED_DIR"
echo "Marketplace repo: $MARKETPLACE_DIR"
```

### Step 3: Save old version

```bash
OLD_VERSION=$(cat "$INSTALLED_DIR/VERSION" 2>/dev/null | tr -d '[:space:]' || echo "unknown")
```

### Step 4: Update marketplace repo and install

```bash
cd "$MARKETPLACE_DIR"
git fetch origin
git reset --hard origin/main
NEW_VERSION=$(cat VERSION | tr -d '[:space:]')
GIT_SHA=$(git rev-parse HEAD)

# Create new versioned cache directory
NEW_CACHE_DIR="$HOME/.claude/plugins/cache/nowork-studio/toprank/$NEW_VERSION"
if [ -d "$NEW_CACHE_DIR" ]; then
  rm -rf "$NEW_CACHE_DIR"
fi
mkdir -p "$NEW_CACHE_DIR"

# Copy plugin files (exclude .git to save space)
rsync -a --exclude='.git' "$MARKETPLACE_DIR/" "$NEW_CACHE_DIR/"
```

If the copy fails, warn: "Upgrade failed — the old version is still active. Run `/toprank-upgrade` manually." and stop.

### Step 5: Update installed_plugins.json

Read `~/.claude/plugins/installed_plugins.json`, then update the `toprank@nowork-studio` entry:

```bash
python3 -c "
import json, os
from datetime import datetime, timezone

path = os.path.expanduser('~/.claude/plugins/installed_plugins.json')
with open(path) as f:
    data = json.load(f)

data['plugins']['toprank@nowork-studio'] = [{
    'scope': 'user',
    'installPath': os.path.expanduser('~/.claude/plugins/cache/nowork-studio/toprank/$NEW_VERSION'),
    'version': '$NEW_VERSION',
    'installedAt': data['plugins'].get('toprank@nowork-studio', [{}])[0].get('installedAt', datetime.now(timezone.utc).isoformat()),
    'lastUpdated': datetime.now(timezone.utc).isoformat(),
    'gitCommitSha': '$GIT_SHA'
}]

with open(path, 'w') as f:
    json.dump(data, f, indent=4)
print('Updated installed_plugins.json: toprank@nowork-studio -> v$NEW_VERSION')
"
```

### Step 6: Clean up old cache versions

Remove old versioned cache directories (keep only the new one). Never remove a `dev` symlink:

```bash
for dir in ~/.claude/plugins/cache/nowork-studio/toprank/*/; do
  ver=$(basename "$dir")
  if [ "$ver" != "$NEW_VERSION" ] && [ "$ver" != "dev" ]; then
    rm -rf "$dir"
    echo "Removed old cache: $ver"
  fi
done
```

### Step 7: Write marker + clear update state

```bash
mkdir -p ~/.toprank
echo "$OLD_VERSION" > ~/.toprank/just-upgraded-from
rm -f ~/.toprank/last-update-check
rm -f ~/.toprank/update-snoozed
```

### Step 8: Show What's New

Read `$NEW_CACHE_DIR/CHANGELOG.md`. Find all version entries between the old version and the new version. Summarize as 3-7 bullets grouped by theme — focus on user-facing changes, skip internal refactors.

Format:
```
toprank v{new} — upgraded from v{old}!

What's new:
- [bullet 1]
- [bullet 2]
- ...

The new version will be fully active on your next Claude Code session.
```

### Step 9: Continue

After showing What's New, continue with whatever skill the user originally invoked.

---

## Dev symlink detection

Before upgrading, check if the installed cache directory is a symlink named `dev`:

```bash
CACHE_DIR=$(ls -d ~/.claude/plugins/cache/nowork-studio/toprank/*/ 2>/dev/null | head -1)
if [ -L "${CACHE_DIR%/}" ] && [ "$(basename "$CACHE_DIR")" = "dev" ]; then
  echo "DEV_SYMLINK"
fi
```

If `DEV_SYMLINK`: tell the user "toprank is installed as a dev symlink — it always points to your local source (v$(cat "$CACHE_DIR/VERSION" 2>/dev/null | tr -d '[:space:]')). No upgrade needed." and **stop**. Do not proceed with Steps 2–8.

---

## Standalone usage

When invoked directly as `/toprank-upgrade`:

1. Check for dev symlink (see "Dev symlink detection" above). If detected, stop.

2. Force a fresh update check (bypass cache and snooze):
```bash
_UPD_BIN=$(ls ~/.claude/plugins/cache/nowork-studio/toprank/*/bin/toprank-update-check 2>/dev/null | head -1)
[ -n "$_UPD_BIN" ] && _UPD=$("$_UPD_BIN" --force 2>/dev/null || true) || _UPD=""
echo "$_UPD"
```

3. If `UPGRADE_AVAILABLE <old> <new>`: follow Steps 2–8 above.

4. If no `UPGRADE_AVAILABLE` output: tell the user "You're already on the latest version (v{LOCAL})."
