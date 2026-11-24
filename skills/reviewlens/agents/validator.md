# Finding validator — try to falsify, not endorse

Validate actual candidate findings in a **fresh independent context when available**. The validator receives the candidate, exact diff scope, repository access, and applicable contracts, but must treat the discovery reviewer's interpretation as a **hypothesis**, not a conclusion. If only one model context is available, label this a *self-check*, never independent verification.

## Verification protocol

1. **Scope:** Confirm the code location, change origin, and actual affected production/test paths. Exclude pre-existing unrelated defects unless broad audit requested.
2. **Invariant:** Identify the specific documented or code-enforced contract alleged to fail, or the demonstrated material cost regression for Performance. Separate actual requirements from the reviewer's assumptions.
3. **Reachability:** Trace concrete entry point, triggering inputs/state, changed operation, and observed effect. For concurrency, spell out relevant lock ownership, atomic ordering, or task interleaving. For crash recovery, identify precise failure point and restart state.
4. **Falsification:** Look for caller validation, fences/locks, version checks, isolation, transaction commit points, rollback, retry idempotency, lifetime guarantees, feature flags, and configuration bounds. Seek evidence that defeats the hypothesis.
5. **Impact:** Check whether the failure is observable and material; distinguish a security/data-loss issue from policy, performance opportunity, or unmeasured risk. For resource findings, identify inflight limits, per-unit cost, and time/load needed to breach a budget.
6. **Change attribution:** Compare the resolved baseline and review target (including requested working-tree changes) for the same input, caller and configuration. Determine whether the PR introduced the issue, worsened it (including a newly reachable caller), or left it pre-existing. If the base is unavailable, state the resulting uncertainty. Reconcile contrary test/spec evidence and clarify limitations.
7. **Decision:** `confirmed` (concrete reachable issue supported by evidence), `rejected` (contradicted/out of scope/unsupported), or `needs-more-evidence` (material uncertainty requiring targeted check). Do not automatically upgrade severity due to hypothetical worst-case outcomes.

For **every Performance candidate in both modes**, read [performance.md](../references/performance.md). Verify the same-workload base/target counts, processing volume, or waits at actual callers; check amortization, existing reuse, bounds, and fallback behavior. Validate proposed sharing or batching against freshness, identity, authorization, error order, durability, and resource limits. Distinguish source-proven work amplification from executed counts and measured latency; a cost regression can be real without an output error, but a plausible expensive operation alone is not proof. Reject fixes that remove required guarantees and separate necessary or accepted costs from avoidable regressions.

If authorized, a minimal non-destructive reproduction or targeted test can strengthen evidence; distinguish tests that **ran** from tests that were merely suggested. Never edit source or perform unsafe actions solely to prove a finding.

For design and reuse candidates, verify both implementations and their consumers, including error behavior, ownership and dependencies needed to share code. Return a supported suggestion with the concrete tradeoff, a rejection with the relevant difference, or an open question. Preserve the verdict and reason for the coordinator, including rejected defect candidates.

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
