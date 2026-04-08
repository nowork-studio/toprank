## Preamble (run first)

```bash
_UPD_BIN=$(ls ~/.claude/plugins/cache/nowork-studio/toprank/*/bin/toprank-update-check 2>/dev/null | head -1)
[ -n "$_UPD_BIN" ] && _UPD=$("$_UPD_BIN" 2>/dev/null || true) || _UPD=""
[ -n "$_UPD" ] && echo "$_UPD" || true
```

If the output contains `UPGRADE_AVAILABLE <old> <new>`: immediately follow the inline upgrade flow in the `/toprank-upgrade` skill (Step 1 onward) to auto-upgrade, then return here and continue.

If the output contains `JUST_UPGRADED <old> <new>`: mention "toprank upgraded from v{old} to v{new}" briefly, then continue.

---

