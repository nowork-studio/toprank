#!/usr/bin/env bash
# test/install.test.sh — plugin structure validation tests
#
# Usage:
#   ./test/install.test.sh
#
# Validates that the toprank repo has the correct Claude Code plugin structure.

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

# ─── Helpers ─────────────────────────────────────────────────

pass() { echo "    PASS  $1"; PASS=$((PASS + 1)); }
fail() { echo "    FAIL  $1"; FAIL=$((FAIL + 1)); }

assert_file() {
  local path="$1" label="$2"
  [ -f "$path" ] && pass "$label" || fail "$label — expected file at $path"
}

assert_dir() {
  local path="$1" label="$2"
  [ -d "$path" ] && pass "$label" || fail "$label — expected directory at $path"
}

assert_json_field() {
  local path="$1" field="$2" label="$3"
  python3 -c "import json; d=json.load(open('$path')); assert '$field' in d" 2>/dev/null \
    && pass "$label" || fail "$label — field '$field' not in $path"
}

assert_contains() {
  local path="$1" needle="$2" label="$3"
  grep -q "$needle" "$path" 2>/dev/null && pass "$label" || fail "$label — '$needle' not in $path"
}

assert_not_contains() {
  local path="$1" needle="$2" label="$3"
  ! grep -q "$needle" "$path" 2>/dev/null && pass "$label" || fail "$label — '$needle' found in $path (should not be)"
}

# Skills expected in skills/ directory
SKILLS=(
  seo-analysis
  keyword-research
  meta-tags-optimizer
  schema-markup-generator
  content-writer
  setup-cms
  ads
  ads-audit
  ads-copy
  toprank-upgrade
)

# ─── Test 1: Plugin metadata exists and is valid ─────────────

echo ""
echo "=== 1. Plugin metadata ==="

assert_file "$REPO_ROOT/.claude-plugin/plugin.json" "plugin.json exists"
assert_file "$REPO_ROOT/.claude-plugin/marketplace.json" "marketplace.json exists"
assert_file "$REPO_ROOT/.mcp.json" ".mcp.json exists"

assert_json_field "$REPO_ROOT/.claude-plugin/plugin.json" "name" "plugin.json has name"
assert_json_field "$REPO_ROOT/.claude-plugin/plugin.json" "version" "plugin.json has version"
assert_json_field "$REPO_ROOT/.claude-plugin/plugin.json" "skills" "plugin.json has skills path"

assert_json_field "$REPO_ROOT/.claude-plugin/marketplace.json" "plugins" "marketplace.json has plugins"

# Plugin version matches VERSION file
PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/.claude-plugin/plugin.json'))['version'])")
FILE_VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
[ "$PLUGIN_VERSION" = "$FILE_VERSION" ] \
  && pass "plugin.json version ($PLUGIN_VERSION) matches VERSION file" \
  || fail "version mismatch: plugin.json=$PLUGIN_VERSION, VERSION=$FILE_VERSION"

# marketplace.json versions must also match
MKT_META_VERSION=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/.claude-plugin/marketplace.json'))['metadata']['version'])")
MKT_PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/.claude-plugin/marketplace.json'))['plugins'][0]['version'])")
[ "$MKT_META_VERSION" = "$FILE_VERSION" ] \
  && pass "marketplace.json metadata.version matches VERSION" \
  || fail "version mismatch: marketplace metadata=$MKT_META_VERSION, VERSION=$FILE_VERSION"
[ "$MKT_PLUGIN_VERSION" = "$FILE_VERSION" ] \
  && pass "marketplace.json plugins[0].version matches VERSION" \
  || fail "version mismatch: marketplace plugin=$MKT_PLUGIN_VERSION, VERSION=$FILE_VERSION"

# ─── Test 2: All skills exist with SKILL.md ──────────────────

echo ""
echo "=== 2. Skill directories ==="

for skill in "${SKILLS[@]}"; do
  assert_dir "$REPO_ROOT/skills/$skill" "skill directory: $skill"
  assert_file "$REPO_ROOT/skills/$skill/SKILL.md" "SKILL.md exists: $skill"
done

# Guard: actual SKILL.md count must match the SKILLS array
actual_skill_count=$(find "$REPO_ROOT/skills" -maxdepth 2 -name "SKILL.md" | wc -l | tr -d ' ')
if [ "$actual_skill_count" -ne "${#SKILLS[@]}" ]; then
  fail "SKILLS array has ${#SKILLS[@]} entries but skills/ has $actual_skill_count SKILL.md files"
else
  pass "skill count matches ($actual_skill_count)"
fi

# ─── Test 3: No old structure remains ────────────────────────

echo ""
echo "=== 3. Old structure removed ==="

[ ! -f "$REPO_ROOT/setup" ] \
  && pass "setup script removed" \
  || fail "setup script still exists (should be deleted)"

[ ! -d "$REPO_ROOT/bin" ] \
  && pass "bin/ directory removed" \
  || fail "bin/ directory still exists"

[ ! -d "$REPO_ROOT/seo" ] \
  && pass "seo/ directory removed" \
  || fail "seo/ directory still exists (skills should be in skills/)"

[ ! -d "$REPO_ROOT/google-ads" ] \
  && pass "google-ads/ directory removed" \
  || fail "google-ads/ directory still exists (skills should be in skills/)"

[ ! -f "$REPO_ROOT/skills/ads/mcporter.json" ] \
  && pass "mcporter.json removed" \
  || fail "mcporter.json still exists (replaced by .mcp.json)"

# ─── Test 4: No preamble injection remnants ──────────────────

echo ""
echo "=== 4. Preamble cleanup ==="

for skill in "${SKILLS[@]}"; do
  [ "$skill" = "toprank-upgrade" ] && continue
  assert_not_contains "$REPO_ROOT/skills/$skill/SKILL.md" "toprank-update-check" \
    "no preamble in $skill"
done

# ─── Test 5: MCP server configuration ───────────────────────

echo ""
echo "=== 5. MCP server config ==="

assert_contains "$REPO_ROOT/.mcp.json" "adsagent" ".mcp.json has adsagent server"
assert_contains "$REPO_ROOT/.mcp.json" "mcp-remote" ".mcp.json uses mcp-remote"
assert_contains "$REPO_ROOT/.mcp.json" "ADSAGENT_API_KEY" ".mcp.json references API key env var"

# ─── Test 6: Google Ads skills have MCP detection ────────────

echo ""
echo "=== 6. MCP detection in ads skills ==="

for skill in ads ads-audit ads-copy; do
  assert_contains "$REPO_ROOT/skills/$skill/SKILL.md" "MCP Server Detection" \
    "MCP detection section in $skill"
done

# ─── Test 7: Reference docs exist ───────────────────────────

echo ""
echo "=== 7. Reference documents ==="

assert_dir "$REPO_ROOT/skills/ads/references" "ads references directory"
assert_dir "$REPO_ROOT/skills/ads-audit/references" "ads-audit references directory"
assert_dir "$REPO_ROOT/skills/ads-copy/references" "ads-copy references directory"
assert_dir "$REPO_ROOT/skills/seo-analysis/references" "seo-analysis references directory"

# ─── Test 8: Eval files exist ────────────────────────────────

echo ""
echo "=== 8. Eval files ==="

assert_file "$REPO_ROOT/skills/ads/evals/evals.json" "ads evals exist"
assert_file "$REPO_ROOT/skills/ads-audit/evals/evals.json" "ads-audit evals exist"
assert_file "$REPO_ROOT/skills/ads-copy/evals/evals.json" "ads-copy evals exist"

# ─── Results ──────────────────────────────────────────────────

echo ""
echo "─────────────────────────────"
echo "  $PASS passed  |  $FAIL failed"
echo "─────────────────────────────"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
