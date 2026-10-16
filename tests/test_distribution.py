"""No-network smoke tests for ReviewLens distribution structure and safety policies."""
import json
import os
import subprocess
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "reviewlens"
CORE = [
    "SKILL.md", "agents/reviewer.md", "agents/validator.md",
    "references/general.md", "references/rust.md", "references/systems.md",
]


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise AssertionError(f"Missing YAML frontmatter in {path}")
    return match.group(1)


class ReviewLensDistributionTest(unittest.TestCase):
    def test_all_six_core_files_present(self):
        for item in CORE:
            with self.subTest(file=item):
                self.assertTrue((SKILL / item).is_file(), f"missing {item}")
        self.assertEqual(len(CORE), 6)

    def test_agent_skill_frontmatter(self):
        fm = frontmatter(SKILL / "SKILL.md")
        self.assertRegex(fm, r"(?m)^name: reviewlens$")
        self.assertRegex(fm, r"(?m)^description: .{50,}$")
        self.assertRegex(fm, r"(?m)^license: MIT$")
        self.assertLessEqual(len((SKILL / "SKILL.md").read_text().splitlines()), 500)

    def test_claude_agent_adapters(self):
        for name in ("reviewlens-reviewer", "reviewlens-validator"):
            with self.subTest(name=name):
                fm = frontmatter(ROOT / "agents" / f"{name}.md")
                self.assertIn(f"name: {name}", fm)
                self.assertIn("tools: Read, Grep, Glob, Bash", fm)
                self.assertNotIn("Edit", fm)
                self.assertNotIn("Write", fm)

    def test_marketplace_manifest(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(plugin["name"], "reviewlens")
        self.assertEqual(market["name"], "reviewlens-marketplace")
        self.assertEqual(len(market["plugins"]), 1)
        self.assertEqual(market["plugins"][0]["name"], plugin["name"])
        self.assertEqual(market["plugins"][0]["source"]["repo"], "Tangeroooo/reviewlens")

    def test_local_markdown_links(self):
        for path in ROOT.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            for dest in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if dest.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                with self.subTest(source=str(path.relative_to(ROOT)), target=dest):
                    self.assertTrue((path.parent / dest.split("#")[0]).exists(), dest)

    def test_source_and_licenses(self):
        text = (ROOT / "docs/SOURCES.md").read_text(encoding="utf-8")
        for upstream in ("Trail of Bits", "NVIDIA", "Matt Pocock", "Google", "Superpowers"):
            self.assertIn(upstream, text)
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())

    def test_review_policies(self):
        rust = (SKILL / "references/rust.md").read_text(encoding="utf-8")
        systems = (SKILL / "references/systems.md").read_text(encoding="utf-8")
        self.assertIn("Production `unwrap()` / `expect()` policy", rust)
        self.assertIn("Never require `parking_lot`", rust)
        self.assertIn("Never demand `tracing`", systems)
        self.assertIn("Durability", systems)

    def test_safe_publish_guard(self):
        text = (ROOT / "scripts/publish.sh").read_text(encoding="utf-8")
        self.assertIn("authenticated GitHub user", text)
        self.assertIn("Tangeroooo", text)
        self.assertIn("users.noreply.github.com", text)
        self.assertIn("GH_HOST=github.com", text)

    @unittest.skipUnless(shutil.which("bash"), "requires bash")
    def test_publish_refuses_company_account_before_git_init(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unpacked = root / "reviewlens"
            shutil.copytree(ROOT, unpacked, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            bin_dir = root / "bin"
            bin_dir.mkdir()
            stub = bin_dir / "gh"
            stub.write_text("#!/bin/sh\nif [ \"$1\" = api ]; then\n  echo company-user\n  exit 0\nfi\nexit 1\n")
            stub.chmod(0o755)
            env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
            result = subprocess.run(["bash", "scripts/publish.sh"], cwd=unpacked,
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not 'Tangeroooo'", result.stderr)
            self.assertFalse((unpacked / ".git").exists(), "Rejected auth must not initialize Git")

    def test_bilingual_installation_parity(self):
        for path in (ROOT / "docs/INSTALL.md", ROOT / "docs/INSTALL.ko.md"):
            text = path.read_text(encoding="utf-8")
            for snippet in (
                "npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex",
                "/plugin marketplace add Tangeroooo/reviewlens",
                "/plugin install reviewlens@reviewlens-marketplace",
                "~/.claude/skills", "~/.agents/skills",
            ):
                with self.subTest(path=path.name, snippet=snippet):
                    self.assertIn(snippet, text)

    def test_manual_installation_simulation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for location in (".claude/skills", ".agents/skills"):
                target = root / location / "reviewlens"
                shutil.copytree(SKILL, target)
                self.assertTrue((target / "SKILL.md").exists())
                self.assertTrue((target / "references/rust.md").exists())
                self.assertRegex(frontmatter(target / "SKILL.md"), r"(?m)^name: reviewlens$")


if __name__ == "__main__":
    unittest.main()
