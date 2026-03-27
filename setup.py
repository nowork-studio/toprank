#!/usr/bin/env python3
"""
Cross-platform toprank setup — register skills with Claude Code and/or Codex.

Equivalent to the ./setup bash script. Works on Windows, macOS, and Linux.
Run with: python setup.py [--host claude|codex|auto]
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile

TOPRANK_DIR = os.path.dirname(os.path.abspath(__file__))
TOPRANK_NAME = os.path.basename(TOPRANK_DIR)
SKILLS_DIR = os.path.dirname(TOPRANK_DIR)


def parse_args():
    parser = argparse.ArgumentParser(description="Register toprank skills with your agent")
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "auto"],
        default="auto",
        help="Target host (default: auto-detect)",
    )
    return parser.parse_args()


def make_bin_executable():
    bin_dir = os.path.join(TOPRANK_DIR, "bin")
    if not os.path.isdir(bin_dir):
        return
    if platform.system() == "Windows":
        return  # Windows uses file associations, not executable bits
    for fname in os.listdir(bin_dir):
        fpath = os.path.join(bin_dir, fname)
        if os.path.isfile(fpath):
            try:
                os.chmod(fpath, os.stat(fpath).st_mode | 0o111)
            except OSError:
                pass


def discover_skills():
    skills = []
    for entry in sorted(os.listdir(TOPRANK_DIR)):
        skill_dir = os.path.join(TOPRANK_DIR, entry)
        if os.path.isdir(skill_dir) and os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
            skills.append(entry)
    return skills


def inject_preamble(skills):
    preamble_file = os.path.join(TOPRANK_DIR, "bin", "preamble.md")
    if not os.path.isfile(preamble_file):
        return []

    with open(preamble_file) as f:
        preamble = f.read()

    injected = []
    for skill_name in skills:
        if skill_name == "toprank-upgrade":
            continue
        skill_path = os.path.join(TOPRANK_DIR, skill_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        with open(skill_path) as f:
            content = f.read()
        if "toprank-update-check" in content:
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        new_content = parts[0] + "---" + parts[1] + "---\n\n" + preamble + parts[2].lstrip("\n")
        skill_dir_path = os.path.dirname(skill_path)
        fd, tmp_path = tempfile.mkstemp(dir=skill_dir_path)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(new_content)
            os.replace(tmp_path, skill_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        injected.append(skill_name)

    return injected


def _symlink(src, dst):
    """Create symlink src→dst. Falls back to copy on Windows if symlinks fail."""
    if os.path.islink(dst):
        os.unlink(dst)

    try:
        os.symlink(src, dst)
        return "symlinked"
    except (OSError, NotImplementedError):
        # Windows: symlinks require either admin rights or Developer Mode.
        # Fall back to a directory junction (no admin needed) or copy.
        # Use src directly if absolute; otherwise resolve relative to SKILLS_DIR.
        full_src = src if os.path.isabs(src) else os.path.join(SKILLS_DIR, src)
        if platform.system() == "Windows":
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", dst, full_src],
                capture_output=True,
            )
            if result.returncode == 0:
                return "junctioned"
        # Last resort: copy
        if os.path.isdir(full_src):
            shutil.copytree(full_src, dst)
        else:
            shutil.copy2(full_src, dst)
        return "copied"


def setup_claude(skills):
    print("Claude Code:")
    linked = []
    for skill_name in skills:
        src = os.path.join(TOPRANK_NAME, skill_name)  # relative path for portability
        dst = os.path.join(SKILLS_DIR, skill_name)

        if os.path.exists(dst) and not os.path.islink(dst):
            print(f"  skipped {skill_name} (real directory exists at {dst})")
            continue

        method = _symlink(src, dst)
        linked.append(f"{skill_name} ({method})")

    if linked:
        print(f"  linked skills: {', '.join(linked)}")
    else:
        print("  no new skills to link")


def setup_codex(skills):
    print("Codex:")
    # Determine install location
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=TOPRANK_DIR,
        )
        repo_root = result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        repo_root = ""

    agents_dir = (
        os.path.join(repo_root, ".agents", "skills")
        if repo_root
        else os.path.join(os.path.expanduser("~"), ".codex", "skills")
    )

    linked = []
    for skill_name in skills:
        codex_skill_name = f"toprank-{skill_name}"
        codex_dir = os.path.join(agents_dir, codex_skill_name)
        os.makedirs(os.path.join(codex_dir, "agents"), exist_ok=True)

        # Read description from frontmatter
        skill_md = os.path.join(TOPRANK_DIR, skill_name, "SKILL.md")
        desc = f"Toprank {skill_name} skill"
        if os.path.isfile(skill_md):
            with open(skill_md) as f:
                content = f.read()
            in_desc = False
            desc_lines = []
            for line in content.splitlines():
                if line.startswith("description:"):
                    rest = line[len("description:"):].strip()
                    if rest and rest != ">":
                        desc = rest[:120]
                        break
                    in_desc = True
                elif in_desc:
                    if line.startswith("---") or (line and not line.startswith(" ")):
                        break
                    desc_lines.append(line.strip())
            if desc_lines:
                desc = " ".join(desc_lines)[:120]

        yaml_path = os.path.join(codex_dir, "agents", "openai.yaml")
        with open(yaml_path, "w") as f:
            f.write(f"""interface:
  display_name: "toprank-{skill_name}"
  short_description: "{desc}"
  default_prompt: "Use toprank-{skill_name} for this task."
policy:
  allow_implicit_invocation: true
""")

        # Symlink SKILL.md and asset directories (force-relink so upgrades take effect)
        for asset in ["SKILL.md", "scripts", "references"]:
            asset_src = os.path.join(TOPRANK_DIR, skill_name, asset)
            asset_dst = os.path.join(codex_dir, asset)
            if not os.path.exists(asset_src):
                continue
            _symlink(asset_src, asset_dst)

        linked.append(codex_skill_name)

    if linked:
        print(f"  linked skills: {', '.join(linked)}")
    else:
        print("  no new skills to link")


def detect_hosts(host_arg):
    install_claude = False
    install_codex = False

    if host_arg == "claude":
        install_claude = True
    elif host_arg == "codex":
        install_codex = True
    else:
        # Claude Code: we're inside ~/.claude/skills/
        claude_skills = os.path.join(".claude", "skills")
        if SKILLS_DIR.endswith(claude_skills) or SKILLS_DIR.replace("\\", "/").endswith(claude_skills):
            install_claude = True
        # Codex: codex CLI is available
        if shutil.which("codex"):
            install_codex = True
        # Default to Claude if nothing detected
        if not install_claude and not install_codex:
            install_claude = True

    return install_claude, install_codex


def main():
    args = parse_args()

    print("toprank setup")
    print("─────────────")
    print()

    make_bin_executable()

    skills = discover_skills()
    if not skills:
        print("  no skills found")
        return

    injected = inject_preamble(skills)
    if injected:
        print(f"  injected preamble: {' '.join(injected)}")

    install_claude, install_codex = detect_hosts(args.host)

    if install_claude:
        setup_claude(skills)
    if install_codex:
        setup_codex(skills)

    print()
    print("Done. Restart your agent and the skills are available.")


if __name__ == "__main__":
    main()
