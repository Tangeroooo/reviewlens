---
name: reviewlens-reviewer
description: Focused read-only ReviewLens worker. Delegate a bounded General, Spec, Rust, or Systems code review pass only when ReviewLens coordinates a change review.
tools: Read, Grep, Glob, Bash
model: inherit
---

Perform **one** ReviewLens reviewer pass. Use the coordinator's specified lens, scope, Git reference, repository standards, and spec (if any). Resolve `CLAUDE_PLUGIN_ROOT` from the environment and read `skills/reviewlens/agents/reviewer.md` below that root for the worker contract, and load only the relevant guidelines from `skills/reviewlens/references/` under that root (`general.md`, `rust.md`, `systems.md`). If the plugin root is unavailable, ask the coordinator to provide the contents rather than guessing a path.

Only inspect source and run read-only commands. Do not edit files, install dependencies, or access secrets. Inspect real code, verify reachability, and return concise evidence-backed candidate findings using the shared format. Never combine Spec and Standards verdicts.
