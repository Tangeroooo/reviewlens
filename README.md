# ReviewLens

**Evidence-driven code review, from general engineering to Rust and systems code.**

ReviewLens is a portable [Agent Skill](https://agentskills.io/specification) for **Claude Code and OpenAI Codex**. It examines a branch, PR, or working-tree diff through independent perspectives when the host supports subagents. It is intentionally small: six core files, two optional Claude Code agent adapters, and no runtime dependencies.

[English installation guide](docs/INSTALL.md) · [한국어 설치 가이드](docs/INSTALL.ko.md) · [한국어 README](README.ko.md)

## What it reviews

| Lens | What it catches | When it runs |
| --- | --- | --- |
| **General / Standards** | Behavior changes, design, tests, errors, compatibility, documented project rules | Always |
| **Spec** | Unmet requirements, unintended features, divergence from an actual spec | When a spec is available |
| **Rust** | Unsafe invariants, ownership/FFI, panic policy, locks, idiomatic Rust | For Rust changes |
| **Systems** | Async cancellation, bounded memory/backpressure, data visibility, durability/recovery | For relevant systems/storage changes |

A normal review uses **1–3 discovery reviewers**, not dozens of workers. Confirmed high-risk findings receive an additional validation check when supported. The coordinator keeps Spec results separate from Standards/Technical results; a pass on one does not imply a pass on the other.

ReviewLens is **read-only** by default. It is not a static analyzer and makes no promise to discover every bug.

## Review policies

- **Production `unwrap()` / `expect()`**: prohibited by the ReviewLens default; distinguish policy violations from reachable panics. Test-only use is allowed.
- **`parking_lot`**: do not prescribe it automatically. Evaluate contention, poisoning, async boundaries, behavior, dependency cost, and project conventions.
- **`tracing`**: do not prescribe it automatically. Follow the project's logging stack, including `log`, `tracing`, or other established approaches.
- **Findings**: require a changed location, concrete trigger, likely impact, evidence, and a repair or regression-test direction.
- **Other languages**: the General and Spec lenses still work even without Rust code.

## Installation (quick start)

After this repository is published on GitHub:

```bash
# Portable Agent Skills installation (project scope, both agents)
npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex
```

For installation across all local projects add `-g`; for unattended installation add `-y`. This path installs the portable skill. For Claude Code **native plugin + registered subagents**, use the marketplace method instead:

```text
/plugin marketplace add Tangeroooo/reviewlens
/plugin install reviewlens@reviewlens-marketplace
```

Use `/reviewlens:reviewlens` when installed as a Claude Code plugin, `/reviewlens` for a standalone Claude Code skill, or `$reviewlens` in Codex.

**Do not install both the standalone and plugin form in the same Claude Code environment unless you intentionally want two entries.** The plugin adds named Claude-specific reviewer/validator agents; the standalone skill uses the host's available delegation mechanism and falls back to sequential review if necessary.

Full instructions, manual installation, verification, troubleshooting, and Windows notes: [INSTALL.md](docs/INSTALL.md) / [INSTALL.ko.md](docs/INSTALL.ko.md).

## How it works

```text
Diff / target
    |
Scope + repository conventions + optional authoritative spec
    |
    +-- General / Standards ----------------------+
    +-- Spec (only with source of truth) ----------+--> candidate findings
    +-- Rust + Systems (when relevant) ------------+            |
                                                         validator (selective)
                                                               |
                                                    evidence-backed report
```

The two Markdown files in `skills/reviewlens/agents/` are **portable prompt contracts**, not executable code. Native Claude Code plugin agent definitions are at repository `agents/` and share those contracts. No dependencies, network service, or generated report files are required.

## Repository layout

```text
.claude-plugin/                 # Claude Code plugin + marketplace metadata
agents/                         # Claude Code native subagent adapters
skills/reviewlens/
  SKILL.md                      # Portable coordinator
  agents/reviewer.md            # Portable worker contract
  agents/validator.md           # Portable verifier contract
  references/general.md         # General engineering + Spec
  references/rust.md            # Trail of Bits + NVIDIA-inspired Rust lens
  references/systems.md         # NVIDIA-inspired systems + original DB lens
docs/INSTALL.md                 # English installation (default)
docs/INSTALL.ko.md              # Korean installation
docs/SOURCES.md                 # Attribution + licensing approach
```

## Example requests

- Claude Code plugin: `/reviewlens:reviewlens Review my working-tree changes.`
- Claude Code standalone: `/reviewlens Review my branch relative to origin/main.`
- Codex: `$reviewlens Review this PR against the issue requirements and check Rust concurrency.`
- Any host: `Use ReviewLens to review these storage-layer changes; focus on crash recovery and memory bounds.`

## Testing and distribution

```bash
python3 -m unittest discover -s tests -v
# With Claude Code installed:
claude plugin validate .
```

The tests validate packaging, links, manifests, and local skill installation layout; they are **not** a real-world review accuracy benchmark. Validate with representative buggy PRs before claiming improved detection rates. No benchmarks or production adoption are claimed.

## Publishing (maintainer only)

A safe publishing script is included for the **Tangeroooo personal GitHub account only**:

```bash
# In the extracted repository root; requires GitHub CLI authenticated to Tangeroooo
bash scripts/publish.sh
```

The script checks the active GitHub login, forces `github.com`, refuses existing repositories/remotes/history or parent checkouts, sets a personal GitHub no-reply author/committer **for this one commit only**, runs local tests, then creates and pushes the public `Tangeroooo/reviewlens` repository. It never uses a global Git identity or silently pushes to a corporate account. If a repository already exists, stop and publish updates manually after reviewing the remote.

## Provenance and license

ReviewLens combines **ideas and review concepts**, not copied prompts, from Trail of Bits `rust-review`, NVIDIA Switchyard `switchyard-rust-review`, Matt Pocock `code-review`, Google Engineering Practices, and obra Superpowers. The exact references and licenses are listed in [SOURCES.md](docs/SOURCES.md). The independently written ReviewLens files are provided under the [MIT License](LICENSE). This does **not** relicense any upstream material.

Maintainer/target repository: **[Tangeroooo/reviewlens](https://github.com/Tangeroooo/reviewlens)**.
