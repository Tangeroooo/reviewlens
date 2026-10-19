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
        self.assertRegex(fm, r"(?m)^  version: \"0\.2\.0\"$")
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
        self.assertEqual(plugin["version"], "0.2.0")
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

    def test_risk_triggered_adversarial_mode(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Default to **Standard**", skill)
        self.assertIn("automatically use **Adversarial**", skill)
        for requirement in ("FFI", "authorization/security", "recovery", "cancellation", "high-risk"):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, skill)

    def test_adversarial_role_separation_and_budget(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        worker = (SKILL / "agents/reviewer.md").read_text(encoding="utf-8")
        native = (ROOT / "agents/reviewlens-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("at most three standard discovery passes", skill)
        self.assertIn("one additional Challenger", skill)
        self.assertIn("do not provide other reviewers' candidate findings", skill)
        self.assertIn("Challenger must not receive other reviewers' findings", worker)
        self.assertIn("Challenger", native)
        self.assertEqual(len(list((ROOT / "agents").glob("*.md"))), 2,
                         "Reuse the existing reviewer adapter; no new agent definition")

    def test_invariant_first_and_counterexample_contract(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        worker = (SKILL / "agents/reviewer.md").read_text(encoding="utf-8")
        for phrase in ("Risk/invariant brief", "violated invariant", "coverage", "counterexamples"):
            self.assertIn(phrase.lower(), skill.lower())
        for phrase in ("Challenger protocol", "falsifiable counterexample", "disconfirming evidence",
                       "hypothesis ledger", "No findings"):
            self.assertIn(phrase.lower(), worker.lower())

    def test_falsification_and_uncertainty_gate(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        validator = (SKILL / "agents/validator.md").read_text(encoding="utf-8")
        self.assertIn("every substantive", skill)
        self.assertIn("needs-more-evidence", skill)
        self.assertIn("confirmed | rejected | needs-more-evidence", validator)
        self.assertIn("Falsification", validator)
        self.assertIn("only confirmed issues", validator)
        self.assertIn("self-check", validator)

    def test_coverage_truthfulness(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        worker = (SKILL / "agents/reviewer.md").read_text(encoding="utf-8")
        for phrase in ("inspected", "actually tested", "not inspected", "rejected", "unresolved"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)
                self.assertIn(phrase, worker)

    def test_context_specific_failure_probes(self):
        general = (SKILL / "references/general.md").read_text(encoding="utf-8")
        rust = (SKILL / "references/rust.md").read_text(encoding="utf-8")
        systems = (SKILL / "references/systems.md").read_text(encoding="utf-8")
        self.assertIn("Adversarial contracts", general)
        self.assertIn("Adversarial Rust probes", rust)
        self.assertIn("Failure matrix", systems)
        for phrase in ("Crash/restart", "Cancellation", "Retry", "Backpressure", "Visibility"):
            self.assertIn(phrase, systems)
        # The new level of rigor must not erase the user's prior policy choices.
        self.assertIn("Never require `parking_lot`", rust)
        self.assertIn("Production `unwrap()` / `expect()` policy", rust)
        self.assertIn("Never demand `tracing`", systems)

    def test_bilingual_evaluation_guide_exists(self):
        for name in ("EVALUATION.md", "EVALUATION.ko.md"):
            with self.subTest(file=name):
                document = ROOT / "docs" / name
                self.assertTrue(document.is_file())
                data = document.read_text(encoding="utf-8")
                self.assertIn("Adversarial", data)
                self.assertTrue(any(word in data.lower() for word in ("false positive", "false positives")))
        self.assertIn("docs/EVALUATION.md", (ROOT / "README.md").read_text())
        self.assertIn("docs/EVALUATION.ko.md", (ROOT / "README.ko.md").read_text())

    def test_installation_docs_mention_adversarial(self):
        for name in ("INSTALL.md", "INSTALL.ko.md"):
            with self.subTest(file=name):
                content = (ROOT / "docs" / name).read_text(encoding="utf-8")
                self.assertIn("Adversarial", content)
                self.assertIn("Standard", content)
                self.assertIn("EVALUATION", content)

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
