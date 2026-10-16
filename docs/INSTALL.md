# Installing ReviewLens (English — default)

[한국어 설치 가이드](INSTALL.ko.md) · [README](../README.md)

ReviewLens is a single [Agent Skill](https://agentskills.io/specification) shared by Claude Code and Codex. It needs no Python, Rust, or external service to run; review commands need normal access to the repository being reviewed. Install it by **one** of the methods below.

> **Publication prerequisite:** Remote commands referencing `Tangeroooo/reviewlens` work only after the maintainer creates and publishes that repository. To test before publication, install from the extracted source folder using the local/manual method.

## Option A — Portable skills installer (Claude Code + Codex)

Requires Node.js/npm for `npx`; Node.js is **only for installation**, not for running ReviewLens.

From your *target project* folder:

```bash
# Install into the current repository for both agents
npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex

# Alternative: install for your user account (all projects)
npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex -g
```

To select only one agent, remove the other `-a ...` flag. The installer may prompt for confirmation; add `-y` for noninteractive use. It places the skill under `.claude/skills/` and `.agents/skills/` (project) or `~/.claude/skills/` and `~/.agents/skills/` (user), or links a shared canonical copy. The *portable* skill dynamically delegates when the host supports it, otherwise reviews in separate sequential passes. See [Vercel skills CLI](https://github.com/vercel-labs/skills).

Use:

- Claude Code: `/reviewlens Review my changes against origin/main.`
- Codex: `$reviewlens Review my storage changes with Rust and Systems lenses.`

## Option B — Claude Code native plugin (recommended for native named subagents)

For **Claude Code only**, run inside a Claude Code session:

```text
/plugin marketplace add Tangeroooo/reviewlens
/plugin install reviewlens@reviewlens-marketplace
```

Or in a system terminal with Claude Code installed:

```bash
claude plugin marketplace add Tangeroooo/reviewlens
claude plugin install reviewlens@reviewlens-marketplace
```

Then invoke `/reviewlens:reviewlens Review this PR.`. This method also provides the namespaced `reviewlens-reviewer` and `reviewlens-validator` subagents. Their use is conditional; normal reviews do **not** require a fixed number of agents.

**Do not install both Option A and B into Claude Code unless you intentionally want duplicate skills.** If you already use Option A for Codex, you can use Option B for Claude Code and install Option A **only for Codex**:

```bash
npx skills add Tangeroooo/reviewlens --skill reviewlens -a codex -g
```

## Option C — Manual installation / local ZIP

Download/extract the repository archive (or, after publication, `git clone https://github.com/Tangeroooo/reviewlens.git`). In the extracted repository root, the distributable skill is `skills/reviewlens/`.

macOS/Linux:

```bash
# Claude Code, personal
mkdir -p ~/.claude/skills
cp -R skills/reviewlens ~/.claude/skills/reviewlens

# Codex, personal
mkdir -p ~/.agents/skills
cp -R skills/reviewlens ~/.agents/skills/reviewlens
```

For **project-scoped** installs use `./.claude/skills/reviewlens` and `./.agents/skills/reviewlens` in the target repository instead of home directory paths.

Windows PowerShell (from the extracted repo root):

```powershell
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -Force "skills/reviewlens" "$HOME/.claude/skills/reviewlens"
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
Copy-Item -Recurse -Force "skills/reviewlens" "$HOME/.agents/skills/reviewlens"
```

If the destination already exists, remove/update it consciously instead of copying a nested folder accidentally. Restart the agent if it does not discover the new skill immediately.

## Verify

In the *downloaded ReviewLens repository*:

```bash
python3 -m unittest discover -s tests -v
# Optional, requires Claude Code CLI:
claude plugin validate .
```

In Claude Code, `/reviewlens` appears for standalone installs and `/reviewlens:reviewlens` for plugin installs. In Codex, use `/skills` or type `$reviewlens` in the input. Ask for a focused review of a real Git diff. The final report should state the scope, review lenses used, and whether independent subagents actually ran. Missing spec must be reported as **not evaluated**, never silently fabricated.

## Updating

- Skills installer: `npx skills update reviewlens` (choose appropriate global/project scope).
- Plugin: use Claude Code's plugin update mechanism.
- Manual: replace the copied `skills/reviewlens/` directory with the new version.

## Troubleshooting and security

- **Skill not found:** verify `SKILL.md` is immediately inside the `reviewlens` directory, not `reviewlens/reviewlens/SKILL.md`; restart if needed.
- **No subagent delegation:** the platform may not expose subagent tools. ReviewLens falls back to separate single-agent passes and must disclose that in its report. Only the Claude native plugin bundles pre-registered named agents.
- **No requirements source:** the Spec lens is skipped and marked `not evaluated`; General/Rust/Systems review still runs.
- **No diff/base:** specify a Git base or show uncommitted changes. The skill must not guess a comparison point.
- **Review permissions:** only grant the coding agent repository read access necessary to inspect code. ReviewLens instructs read-only behavior, but agent permissions are controlled by the host. Review external skill files before allowing shell access.
- **Duplicate Claude entries:** remove either standalone or plugin installation.

Official reference: [Claude Code skills](https://code.claude.com/docs/en/skills), [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [Codex skills](https://developers.openai.com/codex/skills).
