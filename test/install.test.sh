#!/usr/bin/env bash
# test/install.test.sh — mock-$HOME install tests for ./setup
#
# Usage:
#   ./test/install.test.sh
#
# Tests run in isolated temp directories. No system state is modified.

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

# ─── Helpers ─────────────────────────────────────────────────

pass() { echo "    PASS  $1"; PASS=$((PASS + 1)); }
fail() { echo "    FAIL  $1"; FAIL=$((FAIL + 1)); }

assert_link() {
  local path="$1" label="$2"
  [ -L "$path" ] && pass "$label" || fail "$label — expected symlink at $path"
}

assert_no_link() {
  local path="$1" label="$2"
  [ ! -L "$path" ] && pass "$label" || fail "$label — unexpected symlink at $path"
}

assert_file() {
  local path="$1" label="$2"
  [ -f "$path" ] && pass "$label" || fail "$label — expected file at $path"
}

assert_contains() {
  local path="$1" needle="$2" label="$3"
  grep -q "$needle" "$path" 2>/dev/null && pass "$label" || fail "$label — '$needle' not in $path"
}

assert_exit_nonzero() {
  local code="$1" label="$2"
  [ "$code" -ne 0 ] && pass "$label" || fail "$label — expected non-zero exit"
}

run_setup() {
  (cd "$1" && ./setup "${@:2}") >/dev/null 2>&1
}

# Skills that should be registered (everything with a SKILL.md)
SKILLS=(
  seo-analysis
  content-writer
  keyword-research
  meta-tags-optimizer
  schema-markup-generator
  geo-content-optimizer
  toprank-upgrade
)

# Make a fresh copy of the repo in a subdirectory of TMP (exclude .git to
# avoid confusing git rev-parse in tests that set up their own git repo)
clone_into() {
  local dest="$1"
  mkdir -p "$dest"
  rsync -a --exclude='.git' --exclude='.claude' "$REPO_ROOT/" "$dest/"
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ─── Test 1: Claude Code global install (--host claude) ───────

echo ""
echo "=== 1. Claude Code global install ==="

T1="$TMP/t1"
SKILLS_DIR="$T1/.claude/skills"
TOPRANK_DIR="$SKILLS_DIR/toprank"

clone_into "$TOPRANK_DIR"
run_setup "$TOPRANK_DIR" --host claude

for skill in "${SKILLS[@]}"; do
  assert_link "$SKILLS_DIR/$skill" "symlink created: $skill"
done

# Each symlink must point to toprank/<skill> (relative)
for skill in "${SKILLS[@]}"; do
  target="$(readlink "$SKILLS_DIR/$skill" 2>/dev/null || echo '')"
  [ "$target" = "toprank/$skill" ] \
    && pass "symlink target correct: $skill" \
    || fail "symlink target wrong for $skill — got '$target'"
done

# SKILL.md files (except toprank-upgrade) must have preamble injected
for skill in "${SKILLS[@]}"; do
  [ "$skill" = "toprank-upgrade" ] && continue
  assert_contains "$TOPRANK_DIR/$skill/SKILL.md" "toprank-update-check" "preamble injected: $skill"
done

# ─── Test 2: Auto-detect via path (no --host flag) ────────────

echo ""
echo "=== 2. Auto-detect: path ends in .claude/skills ==="

T2="$TMP/t2"
SKILLS_DIR2="$T2/.claude/skills"
TOPRANK_DIR2="$SKILLS_DIR2/toprank"

clone_into "$TOPRANK_DIR2"
run_setup "$TOPRANK_DIR2"  # no --host flag

for skill in "${SKILLS[@]}"; do
  assert_link "$SKILLS_DIR2/$skill" "auto-detected and linked: $skill"
done

# ─── Test 3: Idempotency — running setup twice is safe ────────

echo ""
echo "=== 3. Idempotency (setup runs twice) ==="

run_setup "$TOPRANK_DIR" --host claude  # second run on T1

for skill in "${SKILLS[@]}"; do
  assert_link "$SKILLS_DIR/$skill" "symlink still valid after re-run: $skill"
done

# No extra symlinks created
actual_count="$(find "$SKILLS_DIR" -maxdepth 1 -type l | wc -l | tr -d ' ')"
expected_count="${#SKILLS[@]}"
[ "$actual_count" -eq "$expected_count" ] \
  && pass "no duplicate links ($actual_count total)" \
  || fail "wrong link count — got $actual_count, want $expected_count"

# ─── Test 4: Real directory is not overwritten ────────────────

echo ""
echo "=== 4. Existing real directory is not overwritten ==="

T4="$TMP/t4"
SKILLS_DIR4="$T4/.claude/skills"
TOPRANK_DIR4="$SKILLS_DIR4/toprank"

clone_into "$TOPRANK_DIR4"
mkdir -p "$SKILLS_DIR4/seo-analysis"  # real dir, not a symlink

output="$(cd "$TOPRANK_DIR4" && ./setup --host claude 2>&1 || true)"

assert_no_link "$SKILLS_DIR4/seo-analysis" "real dir not overwritten"
echo "$output" | grep -q "skipped seo-analysis" \
  && pass "skip message shown for existing real dir" \
  || fail "no skip message for existing real dir"

# Other skills still get linked
for skill in "${SKILLS[@]}"; do
  [ "$skill" = "seo-analysis" ] && continue
  assert_link "$SKILLS_DIR4/$skill" "other skills linked despite skip: $skill"
done

# ─── Test 5: Codex install (--host codex) ─────────────────────

echo ""
echo "=== 5. Codex install ==="

T5="$TMP/t5"
REPO="$T5/myproject"
TOPRANK_DIR5="$REPO/.agents/skills/toprank"
AGENTS_DIR="$REPO/.agents/skills"

git init "$REPO" >/dev/null 2>&1
clone_into "$TOPRANK_DIR5"
run_setup "$TOPRANK_DIR5" --host codex

for skill in "${SKILLS[@]}"; do
  codex_name="toprank-$skill"
  assert_file  "$AGENTS_DIR/$codex_name/agents/openai.yaml" "openai.yaml created: $codex_name"
  assert_link  "$AGENTS_DIR/$codex_name/SKILL.md"           "SKILL.md symlinked: $codex_name"
done

# openai.yaml must have required fields
yaml="$AGENTS_DIR/toprank-seo-analysis/agents/openai.yaml"
assert_contains "$yaml" "display_name"             "openai.yaml has display_name"
assert_contains "$yaml" "allow_implicit_invocation" "openai.yaml has allow_implicit_invocation"
assert_contains "$yaml" "toprank-seo-analysis"      "openai.yaml has correct skill name"

# ─── Test 6: Invalid --host value exits non-zero ──────────────

echo ""
echo "=== 6. Invalid --host exits non-zero ==="

T6="$TMP/t6"
clone_into "$T6/toprank"
exit_code=0
(cd "$T6/toprank" && ./setup --host badvalue) >/dev/null 2>&1 || exit_code=$?
assert_exit_nonzero "$exit_code" "--host badvalue exits non-zero"

# ─── Results ──────────────────────────────────────────────────

echo ""
echo "─────────────────────────────"
echo "  $PASS passed  |  $FAIL failed"
echo "─────────────────────────────"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
