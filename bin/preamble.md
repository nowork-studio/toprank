## Preamble (run first)

```bash
_UPD=$(~/.claude/skills/toprank/bin/toprank-update-check 2>/dev/null || \
       ~/.claude/skills/stockholm/bin/toprank-update-check 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true
```

If the output contains `UPGRADE_AVAILABLE <old> <new>`: immediately follow the inline upgrade flow in the `/toprank-upgrade` skill (Step 1 onward) to auto-upgrade, then return here and continue.

If the output contains `JUST_UPGRADED <old> <new>`: mention "toprank upgraded from v{old} to v{new}" briefly, then continue.

---

