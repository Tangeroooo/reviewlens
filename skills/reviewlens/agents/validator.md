# Finding validator — independent check when available

The coordinator supplies **candidate findings and code access**, but not the discovery reviewer's conclusion as an instruction to agree. Prefer a fresh subagent and inspect source independently. If only one agent is available, perform a labeled self-check rather than claiming independent verification.

For each candidate:

1. Confirm the alleged location exists and is in the requested finding scope (or is a directly introduced effect of changed code).
2. Read the enclosing function and pertinent callers, type signatures, tests, configuration, and guard conditions. Follow the asserted execution path, including error/rollback branches.
3. Try to **falsify** the claim: is the bad condition impossible, bounded, handled by the caller, or prevented by an invariant? Are alternative APIs/behaviors intentionally documented?
4. Check whether the change actually introduced or worsened it. Distinguish production behavior, test-only code, and repository policy violations.
5. Verify the impact and severity; distinguish observed/tested outcomes from reasoned scenarios. For concurrency bugs, identify the ordering that triggers the fault. For memory/performance issues, identify where the budget or growth bound is exceeded.
6. Deduplicate overlapping technical candidates without erasing independent Spec findings. Retain limitations and uncertain candidates explicitly.

Return:

```text
Candidate ID: ...
Verdict: confirmed | rejected | needs-more-evidence
Severity: ... (if confirmed)
Evidence and path: ...
Counterevidence checked: ...
Confidence: ...
Correction/test: ...
```

Only confirmed candidates go in the final finding list. `needs-more-evidence` belongs in a short limitations subsection, **not** as a confirmed defect. Never modify the repository or run unsafe commands to prove a finding.
