---
name: toprank-upgrade
description: >
  Upgrade toprank skills to the latest version. Detects global vs vendored
  install, runs the upgrade, and shows what's new. Use when asked to "upgrade
  toprank", "update toprank skills", or "get latest version". Also handles
  inline upgrade prompts when a skill detects UPGRADE_AVAILABLE at startup.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# /toprank-upgrade

Upgrade toprank skills to the latest version and show what's new.

---

## Inline upgrade flow

This section is used when a skill preamble outputs `UPGRADE_AVAILABLE`.

### Step 1: Ask the user (or auto-upgrade)

Check if auto-upgrade is enabled:
```bash
_AUTO=$(~/.claude/skills/toprank/bin/toprank-config get auto_upgrade 2>/dev/null || \
        ~/.claude/skills/stockholm/bin/toprank-config get auto_upgrade 2>/dev/null || true)
echo "AUTO_UPGRADE=$_AUTO"
```

**If `AUTO_UPGRADE=true` or `AUTO_UPGRADE=1`:** Skip the question. Log "Auto-upgrading toprank v{old} → v{new}..." and proceed to Step 2. If `./setup` fails, restore from backup (`.bak` directory) and warn: "Auto-upgrade failed — restored previous version. Run `/toprank-upgrade` manually."

**Otherwise**, use AskUserQuestion:
- Question: "toprank skills **v{new}** available (you're on v{old}). Upgrade now?"
- Options: `["Yes, upgrade now", "Always keep me up to date", "Not now", "Never ask again"]`

**"Yes, upgrade now"** → proceed to Step 2.

**"Always keep me up to date":**
```bash
~/.claude/skills/toprank/bin/toprank-config set auto_upgrade true 2>/dev/null || \
~/.claude/skills/stockholm/bin/toprank-config set auto_upgrade true 2>/dev/null || true
```
Tell user: "Auto-upgrade enabled — future updates will install automatically." Then proceed to Step 2.

**"Not now":** Write snooze state (escalating backoff: first=24h, second=48h, third+=7d):
```bash
_SNOOZE_FILE=~/.toprank/update-snoozed
_REMOTE_VER="{new}"
_CUR_LEVEL=0
if [ -f "$_SNOOZE_FILE" ]; then
  _SNOOZED_VER=$(awk '{print $1}' "$_SNOOZE_FILE")
  if [ "$_SNOOZED_VER" = "$_REMOTE_VER" ]; then
    _CUR_LEVEL=$(awk '{print $2}' "$_SNOOZE_FILE")
    case "$_CUR_LEVEL" in *[!0-9]*) _CUR_LEVEL=0 ;; esac
  fi
fi
_NEW_LEVEL=$((_CUR_LEVEL + 1))
[ "$_NEW_LEVEL" -gt 3 ] && _NEW_LEVEL=3
echo "$_REMOTE_VER $_NEW_LEVEL $(date +%s)" > "$_SNOOZE_FILE"
```
Tell the user the snooze duration ("Next reminder in 24h" / 48h / 1 week). Then continue with the skill that was originally invoked.

**"Never ask again":**
```bash
~/.claude/skills/toprank/bin/toprank-config set update_check false 2>/dev/null || \
~/.claude/skills/stockholm/bin/toprank-config set update_check false 2>/dev/null || true
```
Tell user: "Update checks disabled. Run `toprank-config set update_check true` to re-enable." Then continue.

---

### Step 2: Detect install type

```bash
if [ -d "$HOME/.claude/skills/toprank/.git" ]; then
  INSTALL_TYPE="global-git"; INSTALL_DIR="$HOME/.claude/skills/toprank"
elif [ -d "$HOME/.claude/skills/stockholm/.git" ]; then
  INSTALL_TYPE="global-git"; INSTALL_DIR="$HOME/.claude/skills/stockholm"
elif [ -d ".claude/skills/toprank/.git" ]; then
  INSTALL_TYPE="local-git"; INSTALL_DIR=".claude/skills/toprank"
elif [ -d ".claude/skills/stockholm/.git" ]; then
  INSTALL_TYPE="local-git"; INSTALL_DIR=".claude/skills/stockholm"
elif [ -d "$HOME/.claude/skills/toprank" ]; then
  INSTALL_TYPE="vendored-global"; INSTALL_DIR="$HOME/.claude/skills/toprank"
elif [ -d "$HOME/.claude/skills/stockholm" ]; then
  INSTALL_TYPE="vendored-global"; INSTALL_DIR="$HOME/.claude/skills/stockholm"
else
  echo "ERROR: toprank skills not found"; exit 1
fi
echo "Install type: $INSTALL_TYPE at $INSTALL_DIR"
```

### Step 3: Save old version

```bash
OLD_VERSION=$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo "unknown")
```

### Step 4: Upgrade

**For git installs** (global-git, local-git):
```bash
cd "$INSTALL_DIR"
STASH_OUTPUT=$(git stash 2>&1)
git fetch origin
git reset --hard origin/main
./setup
```
If the stash output contains "Saved working directory", warn: "Note: local changes were stashed. Run `git stash pop` in the install directory to restore them."

**For vendored installs** (vendored, vendored-global):
```bash
TMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/nowork-studio/toprank.git "$TMP_DIR/toprank"
# Remove stale backup from a previous failed upgrade if present.
rm -rf "$INSTALL_DIR.bak"
mv "$INSTALL_DIR" "$INSTALL_DIR.bak"
mv "$TMP_DIR/toprank" "$INSTALL_DIR"
cd "$INSTALL_DIR" && ./setup
rm -rf "$INSTALL_DIR.bak" "$TMP_DIR"
```
If `./setup` fails, restore: `rm -rf "$INSTALL_DIR" && mv "$INSTALL_DIR.bak" "$INSTALL_DIR"` and warn the user.

### Step 5: Write marker + clear cache

```bash
mkdir -p ~/.toprank
echo "$OLD_VERSION" > ~/.toprank/just-upgraded-from
rm -f ~/.toprank/last-update-check
rm -f ~/.toprank/update-snoozed
```

### Step 6: Show What's New

Read `$INSTALL_DIR/CHANGELOG.md`. Find all version entries between the old version and the new version. Summarize as 3-7 bullets grouped by theme — focus on user-facing changes, skip internal refactors.

Format:
```
toprank v{new} — upgraded from v{old}!

What's new:
- [bullet 1]
- [bullet 2]
- ...

Enjoy the new skills!
```

### Step 7: Continue

After showing What's New, continue with whatever skill the user originally invoked.

---

## Standalone usage

When invoked directly as `/toprank-upgrade`:

1. Force a fresh update check (bypass cache and snooze):
```bash
~/.claude/skills/toprank/bin/toprank-update-check --force 2>/dev/null || \
~/.claude/skills/stockholm/bin/toprank-update-check --force 2>/dev/null || true
```

2. If `UPGRADE_AVAILABLE <old> <new>`: follow Steps 2–6 above.

3. If no `UPGRADE_AVAILABLE` output: tell the user "You're already on the latest version (v{LOCAL})."
