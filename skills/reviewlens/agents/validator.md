# Finding validator — try to falsify, not endorse

Validate actual candidate findings in a **fresh independent context when available**. The validator receives the candidate, exact diff scope, repository access, and applicable contracts, but must treat the discovery reviewer's interpretation as a **hypothesis**, not a conclusion. If only one model context is available, label this a *self-check*, never independent verification.

The coordinator supplies `output_language`. Use it for explanations, human-readable headings, verdict reasons, and any authorized deliverables under the shared language rules in [SKILL.md](../SKILL.md). Preserve finding IDs, paths, exact quotations, and machine-required keys/status values; English templates below are structural examples, not a language override.

## Verification protocol

1. **Scope:** Confirm the code location, change origin, and actual affected production/test paths. Exclude pre-existing unrelated defects unless broad audit requested.
2. **Invariant:** Identify the specific documented or code-enforced contract alleged to fail, or the demonstrated material cost regression for Performance. Separate actual requirements from the reviewer's assumptions.
3. **Reachability:** Trace concrete entry point, triggering inputs/state, changed operation, and observed effect. For concurrency, spell out relevant lock ownership, atomic ordering, or task interleaving. For crash recovery, identify precise failure point and restart state.
4. **Falsification:** Look for caller validation, fences/locks, version checks, isolation, transaction commit points, rollback, retry idempotency, lifetime guarantees, feature flags, and configuration bounds. Seek evidence that defeats the hypothesis.
5. **Impact:** Check whether the failure is observable and material; distinguish a security/data-loss issue from policy, performance opportunity, or unmeasured risk. For resource findings, identify inflight limits, per-unit cost, and time/load needed to breach a budget.
6. **Change attribution:** Compare the resolved baseline and review target (including requested working-tree changes) for the same input, caller and configuration. Determine whether the PR introduced the issue, worsened it (including a newly reachable caller), or left it pre-existing. If the base is unavailable, state the resulting uncertainty. Reconcile contrary test/spec evidence and clarify limitations.
7. For error candidates, inspect downstream classification, fallback, retry, logging/redaction, and public response boundaries. Try to disprove claimed cause loss or misleading messages using actual consumers and documented contracts; intentional public sanitization or best-effort behavior may be correct.
8. For test-related candidates, inspect existing unit/integration coverage, assertions, mocks, and applicable repository requirements. Separate a demonstrated runtime defect from a concrete coverage gap or policy violation. Confirm that the alleged missing scenario is not already protected at another test layer; if test access is incomplete, report a limitation rather than assert absence. Keep test-gap advisories outside the confirmed defect list unless an applicable explicit policy/spec violation is established.
9. **Decision:** `confirmed` (concrete reachable issue supported by evidence), `rejected` (contradicted/out of scope/unsupported), or `needs-more-evidence` (material uncertainty requiring targeted check). Do not automatically upgrade severity due to hypothetical worst-case outcomes.

For **every Performance candidate in both modes**, read [performance.md](../references/performance.md). Verify the same-workload base/target counts, processing volume, or waits at actual callers; check amortization, existing reuse, bounds, and fallback behavior. Validate proposed sharing or batching against freshness, identity, authorization, error order, durability, and resource limits. Distinguish source-proven work amplification from executed counts and measured latency; a cost regression can be real without an output error, but a plausible expensive operation alone is not proof. Reject fixes that remove required guarantees and separate necessary or accepted costs from avoidable regressions.

If authorized, a minimal non-destructive reproduction or targeted test can strengthen evidence; distinguish tests that **ran** from tests that were merely suggested. Never edit source or perform unsafe actions solely to prove a finding.

## Code-quality advisory check

This check can be performed by the coordinator; independent defect-validation rules above remain unchanged. For every quality/design/reuse suggestion, compare base and target and inspect the cited callers, state updates, or related implementations. Check whether the alleged comprehension/maintenance burden is present in the changed scope, not a preference or imagined future requirement. Read relevant conventions and look for a reason the existing shape is useful: compatibility, a stable format, deliberately separate policies, a test seam, or an ownership boundary.

Verify that the smallest proposed change preserves behavior, error timing, ownership and dependency direction; for reuse, inspect both implementations and their consumers. Return `supported advisory`, `unsupported`, or `open question` with the evidence, tradeoff and remaining uncertainty. Absence of a runtime failure does not reject a supported advisory, and support does not turn it into a confirmed bug. If a concrete behavior or policy violation emerges, send it through the normal defect protocol. Preserve reasons for rejected suggestions and deduplicate suggestions that share one cause.

For cohesion advice, trace the current responsibilities, shared state/invariants, and actual reasons the affected units change together. For reuse, distinguish shared policy from similar syntax and verify the proposed owner's dependencies and contract compatibility. For pattern advice, compare the mapped functions/types/modules with keeping the existing design and a smaller local change; verify a present variation or coupling problem and the cost of added indirection. Reject pattern-name matching and speculative extension needs, but support a pattern when it solves the evidenced problem better than the alternatives.

## Output for every defect candidate

```text
Candidate ID: ...
Verdict: confirmed | rejected | needs-more-evidence
Scope / invariant: ...
Trigger and traced path: ...
Evidence for: ...
Counterevidence and defenses checked: ...
Impact / severity / confidence: ...
Execution status: inspected only | tested <exact command/result>
Minimal correction or falsifying test: ...
```

The final report includes **only confirmed issues** as findings. Put unresolved candidates under **coverage limitations / checks still needed** rather than silently discarding them or reporting them as proven defects. The coordinator may deduplicate confirmed technical findings; preserve separate Spec judgments and materially different failure triggers.

Return the candidate's associated checklist record IDs and the actual validation extent: source paths/consumers/scenarios inspected, excluded or inaccessible boundaries and why, and tools/tests actually executed. Confirmation or rejection resolves only that candidate's hypothesis; it cannot close a broader checklist item without evidence for the remaining scope. No candidate requiring validation is a valid reason for no validator invocation.
