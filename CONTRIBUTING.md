# Contributing to Toprank

Thank you for your interest in contributing to Toprank! We welcome contributions from the community to help make this the best SEO and Google Ads plugin for Claude Code.

## Code of Conduct

Please be respectful and professional in all your interactions with the community.

## How to Contribute

### 1. Adding a New Skill

Each skill lives in its own folder under a category directory (e.g., `seo/`, `google-ads/`).

1.  **Create the Skill Directory**: `mkdir seo/your-new-skill`
2.  **Add `SKILL.md`**: This is the heart of the skill. It must contain frontmatter with `name` and `description`.
3.  **Optional Scripts/References**: Add any supporting Python scripts in a `scripts/` folder and reference documents in a `references/` folder within your skill directory.
4.  **Register the Skill**: Add the path to your skill (relative to the repo root) to the `skills` array in `.claude-plugin/plugin.json`.
5.  **Bump Versions**: Update the version in:
    *   `.claude-plugin/plugin.json`
    *   `.claude-plugin/marketplace.json`
    *   `VERSION`
6.  **Update Changelog**: Add a brief description of your new skill to `CHANGELOG.md`.

### 2. Improving Existing Skills

*   Refine prompts in `SKILL.md` for better accuracy.
*   Add more robust error handling to scripts.
*   Update reference documentation.

### 3. Bug Fixes and Documentation

*   Fix issues in scripts or skill logic.
*   Improve the `README.md` or other documentation files.

## Development Workflow

1.  **Fork the repository**.
2.  **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/toprank.git`
3.  **Create a branch**: `git checkout -b feature/your-feature-name`
4.  **Make your changes**.
5.  **Run tests**: We use `pytest` for the main test suite, but `unittest` is also used for script-specific unit tests. Ensure your changes don't break existing functionality.
    ```bash
    pip install -r requirements-test.txt
    pytest
    # or run specific unit tests
    python3 test/unit/test_your_script.py
    ```
6.  **Commit and push**: Use descriptive commit messages.
7.  **Open a Pull Request**: Provide a clear description of your changes and why they are beneficial.

## Quality Standards

*   **Be brutally honest**: If a skill won't work in certain scenarios, document it.
*   **Relentless quality**: High-quality, reliable, and maintainable code is a must.
*   **No secrets**: Never include API keys or sensitive information in your commits.

## Testing

Ensure your skill is discovery-ready by Claude Code. Test it locally by pointing your Claude Code to your local repository or a development version of the plugin.

---

We look forward to your contributions!
