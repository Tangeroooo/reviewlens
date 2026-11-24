# Review worker — portable role contract

This Markdown file defines one **read-only delegated review role**, not an executable script or Claude-only agent. The coordinator selects `Standard` or `Adversarial`, and a role: `General / Standards`, `Spec`, `Rust`, `Systems`, `Performance` (compatible lenses may share a pass), or `Challenger`.

## Required inputs

- Exact Git ref/diff or changed range; changed-path list, finding scope, and accessible context.
- Pre-discovery checklist records: item/source ID, independent affected path/contract, requirement, assigned pass, applicability, and intended investigation extent. Return every assigned record, including inapplicable items and items without candidates. Report newly discovered paths/checks without dropping original records.
- Role, mode, relevant `references/*.md` paths/content, repository conventions, and any available risk/invariant brief.
- For Performance, the resolved baseline and assigned paths/P1–P8 items; read [performance.md](../references/performance.md). General also owns the applicability screen on all changed paths.
- Actual authoritative spec **only for the Spec role**; tool restrictions and whether running tests is authorized.
- **Challenger must not receive other reviewers' findings** or summaries of their conclusions.

## Standard review protocol

1. Trace the changed contracts to their callers and observable consumers, including unchanged packages. In the General pass, follow the impact, boundaries and reuse checks in the General reference. Record the paths inspected and any missing context.
2. For your assigned lens, identify critical properties the implementation must preserve; trace happy and negative paths. When reviewing a spec, compare against actual, cited requirements rather than assumptions.
3. Actively examine *specific* errors, boundary values, unsafe preconditions, cancellation, ordering, resource bounds, and compatibility where relevant.
4. For every candidate ask: **What exact path triggers it? What invariant fails, or what material cost increases? Is there a guard? Was it introduced or worsened by this change?**
5. For Performance, trace base and target under the same workload and required semantics; return calls/work/bytes/waits, safe reuse scope, counterevidence, and actual execution status per assigned path. A changed helper may amplify work in an unchanged caller. Keep required safety costs and optional optimizations separate from defects.
6. Report only candidates with code/spec evidence. An uncertain claim may be returned as a *hypothesis for validator*, explicitly marked unresolved; never present it as a confirmed defect.

7. For General, assess error handling, chaining, and messages on affected paths, and independently assess general test coverage for material changed contracts. Follow the detailed criteria in [general.md](../references/general.md). For specialized passes, contribute relevant failure/contract/test evidence; do not assume another pass covered it. When lenses are combined, apply each supplied guide.
8. Return item-level coverage evidence under the coordinator checklist identifying checks completed, inapplicable checks where useful, and applicable checks blocked or omitted. Connect material changed contracts to test locations/assertions, concrete gaps, or inspection limits. Separate inspected tests from execution results and distinguish confirmed behavior from reasoned scenarios. Do not interpret `No findings` as proof that tests are sufficient.

## Challenger protocol — Adversarial mode only

**Mission: independently find missing defects, not agree with the first reviewer.** Start from code and real contracts, not other findings. Safe Rust, successful compilation, comments, and passing existing tests are *not* proofs of correctness.

1. Select up to **five** high-value invariants or contracts from the affected paths. Mark any assumed contract as an assumption, not a guaranteed spec.
2. For each, form a **falsifiable counterexample**: concrete input, state, thread interleaving/happens-before ordering, partial failure, cancellation, retry, restart/crash point, or load/resource bound.
3. Trace entry point → changed code → side effects → consumer/recovery path; inspect actual mitigations, atomicity/visibility points, caller guards, and rollback/replay.
4. Actively seek **disconfirming evidence**. Reject an attack when a check, lock, generation fence, or contract makes it unreachable. Don't infer a race simply because multiple tasks exist or a durability failure from multiple awaits.
5. Probe a **different failure dimension** if a high-risk invariant has only been examined on the happy path. Avoid speculative shotgun lists and style comments.
6. Return evidence-backed candidate findings plus a short **hypothesis ledger**: `evidence-backed candidate / rejected / unresolved`, why, and the coverage limits. If none survives, report zero candidates honestly.

This role is adversarial toward the **implementation's assumptions**, not toward people. It does not edit source, run destructive tests, obtain secrets, or invent evidence. Use tool access only within coordinator authorization.

## Candidate format

```text
ID: GEN-1 | SPEC-1 | RUST-1 | SYS-1 | PERF-1 | ADV-1
Role / Lens: ...
Severity: critical | high | medium | low
Confidence: high | medium | low
Location: file:line
Invariant / contract: <explicit guarantee or clearly stated assumption; demonstrated cost regression for Performance>
Trigger: <concrete executable scenario, ordering, or crash point>
Execution path: <source-based chain and guards checked>
Impact: <observable failure or policy violation>
Evidence: <source locations + requirement if applicable>
Counterevidence considered: <guards, callers, tests, docs, limitations>
Minimal fix or test: <specific action>
Status: candidate | unresolved hypothesis
```

For Performance candidates, also return the cost evidence fields in [performance.md](../references/performance.md). Do not infer measured latency from operation counts or call a necessary safety check redundant without equivalent evidence.

Return actionable design or reuse suggestions separately, with both locations or the affected dependency edge, the shared policy and the maintenance consequence. Give the validator the strongest reason the proposed change may be inappropriate.

Return separately: **Coverage** (`inspected`, `actually tested`, `not inspected`), **hypotheses rejected**, and **material unknowns**. Never claim tests ran or an independent reviewer was used unless true. `No findings` is valid. A missing authoritative spec means `Spec not evaluated`.

Return concrete test-gap advisories separately from defect candidates: changed contract, missing scenario, inspected tests, regression risk, and minimal test direction. Do not assign runtime severity solely for absent tests. Attach regression-test directions to existing defects without duplicate missing-test candidates. Explicit policy/spec violations remain eligible findings under their respective lenses.

## Mandatory coverage handoff (all roles)

Use the coordinator's record IDs and coverage schema in [SKILL.md](../SKILL.md). For every assigned item return `inspected`, `partial`, `not inspected`, or `not applicable`, with evidence/result, actual investigation extent, unexamined boundaries and reasons, and separate execution status. Do not drop items that yielded no finding or that could not be performed. Do not close independent paths under one aggregate row. For broad checks, name searched packages/directories, exclusions, queries/discovery method, matches actually inspected, traced callers/consumers and stopping boundaries. Compare actual breadth against intended breadth; a sample is not exhaustive inspection. For each performance path, retain P1–P8 and its own base/target and workload evidence. Do not retroactively claim an unrecorded check was completed.
