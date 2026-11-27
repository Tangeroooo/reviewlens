# ReviewLens

**Adversarial discovery, conservative reporting — general, Rust, and systems code reviews.**

ReviewLens is a portable [Agent Skill](https://agentskills.io/specification) for **Claude Code and OpenAI Codex**. It examines a branch, PR, or working-tree diff through independent perspectives when the host supports subagents. It is intentionally small: eight core Markdown files, three optional Claude Code agent adapters, and an optional Python standard-library coverage checker.

[English installation guide](docs/INSTALL.md) · [한국어 설치 가이드](docs/INSTALL.ko.md) · [한국어 README](README.ko.md)

## What it reviews

| Lens | What it catches | When it runs |
| --- | --- | --- |
| **General / Standards** | Behavior, code quality/maintainability (Q1–Q5), design/reuse, test coverage, errors, compatibility, documented project rules | Always |
| **Performance** | Lost batching, repeated computation, I/O/work amplification, allocations, serial waits, and contention | Every diff is screened; applicable paths in any language |
| **Spec** | Unmet requirements, unintended features, divergence from an actual spec | When a spec is available |
| **Rust** | Unsafe invariants, ownership/FFI, panic policy, locks, idiomatic Rust | For Rust changes |
| **Systems** | Async cancellation, bounded memory/backpressure, data visibility, durability/recovery | For relevant systems/storage changes |

**Standard** uses 1–3 bounded discovery passes. **Adversarial** adds one *independent Challenger* to challenge assumptions with concrete failure scenarios (when subagents exist), followed by verification of every substantive candidate defect. High-risk changes (unsafe/FFI, storage recovery, atomic ordering, authentication, cancellation, etc.) automatically select Adversarial; you can request it explicitly for any diff.

Both modes enumerate every source-linked review item, including inapplicable and unperformed checks, with evidence, actual investigation extent, remaining boundaries, and omission reasons. A separate Coverage Auditor compares original instructions, the pre-discovery plan, per-path evidence, and the draft report even when there are no findings. The JSON coverage checker rejects missing records, grouped independent performance paths, and unsupported completion status; it cannot establish evidence quality or source-inventory completeness. An outstanding applicable check makes the review partial. The coordinator performs final review of the full diff and coverage gaps after validation. The General pass traces consumers beyond the diff and checks both new duplication and existing reusable code. Rust reviews also inspect crate dependencies and public boundaries. Actionable design suggestions are reported separately from defects. The coordinator keeps Spec results separate from Standards/Technical results. A standalone skill falls back to clearly labeled single-agent passes if delegation is unavailable.

Performance checks compare base and target work for the same workload, including correctness/security/durability fixes. The [Performance reference](skills/reviewlens/references/performance.md) tracks P1–P8 separately per affected path and requires safe reuse boundaries. It shares existing discovery passes, preserves other coverage, and validates every performance candidate in both modes. Proven operation-count growth is distinguished from measured latency; necessary safety costs are not automatically defects.

ReviewLens is **read-only** by default. It is not a static analyzer and makes no promise to discover every bug.

Code quality is reviewed even when outputs are correct. General checks readability, interfaces, state, abstraction cost, and change/test locality against actual callers and conventions. Supported advice includes a current maintenance cost, a minimal compatible correction and its tradeoff. It is source-checked and kept separate from defects, test gaps, and unanswered questions. Naming tastes, arbitrary function-length limits, and speculative future frameworks are not actionable advice.

Detailed review files, audit files, and the chat answer use the language of the user's review request, unless the user explicitly chooses another output language. Code identifiers and machine-required values stay unchanged. The chat answer explains the conclusion, material findings and their impact, investigation breadth, test gaps, audit verdict, and next actions before linking the full reports. The Coverage Auditor checks language consistency and that this summary accurately represents the detailed evidence.

## Review policies

- **Production `unwrap()` / `expect()`**: prohibited by the ReviewLens default; distinguish policy violations from reachable panics. Test-only use is allowed.
- **`parking_lot`**: do not prescribe it automatically. Evaluate contention, poisoning, async boundaries, behavior, dependency cost, and project conventions.
- **`tracing`**: do not prescribe it automatically. Follow the project's logging stack, including `log`, `tracing`, or other established approaches.
- **Findings**: require a changed location, violated invariant or demonstrated cost regression, concrete trigger or crash/interleaving, reachable path, impact, defenses checked, and a fix/test direction. Unsupported hypotheses are not confirmed defects.
- **Test coverage**: assess changed behavioral contracts across success paths, boundaries, state transitions, integration, compatibility, and relevant failures/concurrency. Report concrete test gaps separately from demonstrated defects; coverage percentages alone do not prove correctness. Distinguish review coverage, test evidence, and tests actually executed.
- **Other languages**: the General, Spec, and Performance lenses work without Rust or systems code.

## Choose review depth

- **Standard (default for low-risk diffs):** check behavior, standards, requirements, and applicable Performance/Rust/Systems constraints; validate important candidates.
- **Adversarial (automatic for high-risk diffs, or on request):** invariant-first analysis, independent Challenger when supported, failure/crash/concurrency hypotheses, falsification of **all substantive** candidates, and a coverage/uncertainty record.

Example calls:

```text
/reviewlens:reviewlens Adversarially review this segment lifecycle PR against origin/main.
$reviewlens Review this storage-engine diff in adversarial mode; find and verify counterexamples.
```

The Challenger returns **evidence-backed candidates, rejected hypotheses, and unresolved paths**; only validator-confirmed defects appear as findings. "Inspected" never means "executed" or "proven safe". See [evaluation guide](docs/EVALUATION.md) for measuring detection, false positives, coverage, and cost on real PRs.

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

**Do not install both the standalone and plugin form in the same Claude Code environment unless you intentionally want two entries.** The plugin adds named Claude-specific reviewer/validator/coverage-auditor agents; the standalone skill uses the host's available delegation mechanism and falls back to sequential review if necessary.

Full instructions, manual installation, verification, troubleshooting, and Windows notes: [INSTALL.md](docs/INSTALL.md) / [INSTALL.ko.md](docs/INSTALL.ko.md).

## How it works

```text
Diff / target
    |
Scope + repository conventions + optional authoritative spec
    |
    +-- General / Standards ----------------------+
    +-- Spec (only with source of truth) ----------+--> candidate findings
    +-- Performance / Rust / Systems (as needed) --+            |
    +-- Challenger (adversarial mode only) ---------+            |
                                                         independent validator
                                                               |
                                                separate Coverage Auditor
                                                               |
                                                coordinator resolves audit gaps
                                                               |
                                                   evidence + coverage report
```

The three Markdown files in `skills/reviewlens/agents/` are **portable prompt contracts** (reviewer including Challenger, validator, and Coverage Auditor), not executable code. Native Claude Code plugin agent definitions are at repository `agents/` and share those contracts. No network service or generated report files are required. The optional mechanical checker reads JSON on stdin using Python 3 with no third-party packages; without Python, disclose manual accounting. Without subagents, disclose a self-audit instead of claiming independent audit.

## Repository layout

```text
.claude-plugin/                 # Claude Code plugin + marketplace metadata
agents/                         # Claude Code native subagent adapters
skills/reviewlens/
  SKILL.md                      # Portable coordinator
  agents/reviewer.md            # Portable worker contract
  agents/validator.md           # Portable verifier contract
  agents/coverage-auditor.md    # Independent completeness audit
  scripts/check_coverage.py    # Read-only JSON coverage accounting
  references/general.md         # General engineering + Spec
  references/performance.md     # Language-independent cost and safe reuse checks
  references/rust.md            # Trail of Bits + NVIDIA-inspired Rust lens
  references/systems.md         # NVIDIA-inspired systems + original DB lens
docs/INSTALL.md                 # English installation (default)
docs/INSTALL.ko.md              # Korean installation
docs/EVALUATION.md              # English review-quality evaluation
docs/EVALUATION.ko.md           # Korean evaluation
docs/SOURCES.md                 # Attribution + licensing approach
```

## Example requests

- Claude Code plugin: `/reviewlens:reviewlens Review my working-tree changes.`
- Claude Code standalone: `/reviewlens Review my branch relative to origin/main.`
- Codex: `$reviewlens Review this PR against the issue requirements and check Rust concurrency.`
- Any host: `Use ReviewLens to review these storage-layer changes; focus on crash recovery and memory bounds.`

## v0.5.0 changes

- General always reviews code quality through Q1–Q5: readability/control flow, responsibilities/interfaces, state representation, proportional abstraction/dependencies, and change locality/testability.
- Report source-checked maintenance advice even when current behavior is correct, separately from confirmed bugs and open questions. Each suggestion needs a present cost, minimal compatible correction, and tradeoff; no style quota or automatic refactor.
- Preserve the existing discovery-pass budget, correctness/performance checks, and coverage audit. Review workers, validators, and auditors share the same advisory contract.

## v0.4.0 changes

- Screen every changed path for performance impact, regardless of language or PR intent.
- Add per-path cost comparison, P1–P8 coverage, and validation without weakening correctness or increasing the discovery pass budget.
- Extend evaluation with cross-domain regression/control pairs; distribution checks do not establish detection accuracy.

## v0.2.0 changes

- Added risk-based **Adversarial** mode with an independent Challenger role, without increasing the six-file core.
- Required invariant/failure-hypothesis coverage and accurate reporting of what was inspected versus actually tested.
- Hardened Rust unsafe/synchronization probes and storage crash/retry/resource-budget checks.
- Validator now actively falsifies every substantive candidate in Adversarial mode.

## Testing and distribution

```bash
python3 -m unittest discover -s tests -v
# With Claude Code installed:
claude plugin validate .
```

The tests validate packaging, links, manifests, review-protocol contracts, and local skill installation layout; they are **not** a real-world review accuracy benchmark. Follow [EVALUATION.md](docs/EVALUATION.md) with buggy **and clean** PRs before claiming improved detection rates. No benchmarks or production adoption are claimed.

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
