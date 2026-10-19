# Finding validator — try to falsify, not endorse

Validate actual candidate findings in a **fresh independent context when available**. The validator receives the candidate, exact diff scope, repository access, and applicable contracts, but must treat the discovery reviewer's interpretation as a **hypothesis**, not a conclusion. If only one model context is available, label this a *self-check*, never independent verification.

## Verification protocol

1. **Scope:** Confirm the code location, change origin, and actual affected production/test paths. Exclude pre-existing unrelated defects unless broad audit requested.
2. **Invariant:** Identify the specific documented or code-enforced contract alleged to fail. Separate actual requirements from the reviewer's assumptions.
3. **Reachability:** Trace concrete entry point, triggering inputs/state, changed operation, and observed effect. For concurrency, spell out relevant lock ownership, atomic ordering, or task interleaving. For crash recovery, identify precise failure point and restart state.
4. **Falsification:** Look for caller validation, fences/locks, version checks, isolation, transaction commit points, rollback, retry idempotency, lifetime guarantees, feature flags, and configuration bounds. Seek evidence that defeats the hypothesis.
5. **Impact:** Check whether the failure is observable and material; distinguish a security/data-loss issue from policy, performance opportunity, or unmeasured risk. For resource findings, identify inflight limits, per-unit cost, and time/load needed to breach a budget.
6. **Change attribution:** Verify the diff introduced/worsened this behavior rather than exposing an unrelated known issue. Reconcile contrary test/spec evidence and clarify limitations.
7. **Decision:** `confirmed` (concrete reachable issue supported by evidence), `rejected` (contradicted/out of scope/unsupported), or `needs-more-evidence` (material uncertainty requiring targeted check). Do not automatically upgrade severity due to hypothetical worst-case outcomes.

If authorized, a minimal non-destructive reproduction or targeted test can strengthen evidence; distinguish tests that **ran** from tests that were merely suggested. Never edit source or perform unsafe actions solely to prove a finding.

## Output for every candidate

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
