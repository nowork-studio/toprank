# Contributing to Toprank

Thanks for wanting to contribute. Toprank is a community collection — the more skills, the better.

---

## Adding a New Skill

Each skill lives in its own folder under `skills/`:

```
skills/
└── your-skill-name/
    ├── SKILL.md          ← required
    ├── scripts/          ← optional Python/shell scripts
    └── references/       ← optional reference docs
```

### SKILL.md structure

Every skill needs a frontmatter header:

```yaml
---
name: your-skill-name
description: >
  One paragraph. Explain what the skill does AND when to trigger it.
  Be specific about trigger phrases — Claude uses this to decide when
  to invoke the skill. Err on the side of being "pushy" about triggering.
---
```

Then the body: step-by-step instructions Claude will follow. Write in the imperative. Explain the *why* behind each step, not just the what.

> **Preamble auto-injected.** You don't need to add the update-check preamble manually. `./setup` detects skills that are missing it and injects `bin/preamble.md` automatically after the frontmatter. If you want to test locally before running setup, copy the preamble from `bin/preamble.md`.

### Scripts

Scripts should:
- Use Python 3.8+ stdlib only, or `requests` (commonly available)
- Accept `--output` to write results to a file
- Print progress to stderr, structured data to stdout or the output file
- Handle auth errors gracefully with helpful messages

### References

Reference files are loaded on demand. Keep them focused. If a reference file is over 300 lines, add a table of contents at the top.

---

## Pull Request Guidelines

1. One skill per PR (or one meaningful improvement to an existing skill)
2. Test your skill on a real site before submitting
3. Update [CHANGELOG.md](CHANGELOG.md) with the new version (bump `VERSION` file too)
4. Keep the README skills table up to date

---

## Skill Ideas

Looking for something to build? Here are areas with high value and no existing skill:

| Skill | What it would do |
|-------|-----------------|
| `keyword-research` | Find keyword gaps from GSC data + surface competitor terms |
| `gsc-monitor` | Weekly GSC health snapshot with MoM trend |
| `technical-seo-fix` | Audit + auto-fix meta tags, headings, structured data in repo |
| `content-brief` | Turn a target keyword into a structured content brief |
| `sem-audit` | Quality score analysis and wasted spend detection |
| `backlink-audit` | Analyze backlink profile for toxic links and opportunities |
| `local-seo` | Audit local SEO signals — NAP consistency, Google Business Profile |

---

## Questions

Open an issue. We're friendly.
