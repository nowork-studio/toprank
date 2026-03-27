# Contributing

Thanks for wanting to contribute! Here's how to get started.

## Adding a Skill

Each skill lives in its own folder under `skills/`:

```
skills/
└── your-skill-name/
    ├── SKILL.md          <- required
    ├── scripts/          <- optional
    └── references/       <- optional
```

### SKILL.md

Every skill needs a frontmatter header:

```yaml
---
name: your-skill-name
description: >
  One paragraph. Explain what the skill does AND when to trigger it.
  Be specific about trigger phrases.
---
```

Then the body: step-by-step instructions Claude will follow. Write in the imperative.

> The update-check preamble is auto-injected by `./setup` — you don't need to add it manually.

### Scripts

- Python 3.8+ stdlib only (or `requests`)
- Accept `--output` for file output
- stderr for progress, stdout for data

## Pull Requests

1. One skill per PR
2. Test your skill before submitting
3. Bump `VERSION` and update `CHANGELOG.md`

## Questions

Open an issue. We're friendly.
