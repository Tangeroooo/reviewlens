# General lens — correctness, requirements, maintainability

Use this for every reviewed change, regardless of language. Examine actual project conventions before relying on generic heuristics. Prefer issues that change behavior or raise long-term maintenance cost materially.

## Standards and design

- **Behavior**: Do inputs, outputs, errors, state transitions, ordering, and edge cases preserve the intended contract? Check negative paths, not just success paths.
- **Public contracts**: Check compatibility of APIs, wire formats, schema/config migrations, serialization, feature flags, and persisted data. Identify version-dependent consumers.
- **Design**: Ask whether the added abstraction solves a current need, makes ownership explicit, and respects module boundaries. Prefer simpler designs where equally correct; do not demand a personal favorite architecture.
- **Scope**: Flag unrelated behavioral changes or broad refactors that obscure the primary purpose when they add demonstrable risk.
- **Complexity**: Look for branches that are unreachable or wrongly ordered, duplication that will drift, hidden state, contradictory invariants, and nonlocal side effects. Code smells are prompts to investigate, not automatic defects.
- **Errors**: Apply the error handling, chaining, and message checks below to affected paths; follow callers through the boundary where failures are handled or exposed.
- **Security**: Review trust boundaries, access control, sanitization, secret exposure, and injection when relevant to changed flows. Avoid inventing unproven vulnerabilities.
- **Documentation**: Require changes when documented behavior becomes inaccurate, especially public APIs and operational settings. Do not demand redundant comments.
- **Observability**: Check existing log/metric conventions, important failure visibility, sensitive-data redaction, and excessive hot-path logging. Preserve the repository's existing logging technology.

## Performance applicability

For every changed path, determine whether work frequency, batching, processed data, external operations, reuse, lifetime, or scheduling changes. Include unchanged callers of modified helpers and new defaults/configuration. Bug-fix or safety intent does not exempt a path. Activate [Performance](performance.md) when triggered, independently of language or Systems applicability; return evidence for applicability and assigned checks. If uncertain, trace the operation rather than marking it inapplicable.

## Impact, boundaries and reuse

- Follow each changed contract from its entry point through implementations, adapters and consumers to an observable result. Look outside changed files for affected registrations, configuration, alternate entry points and tests. Stop when the effect is accounted for, or name the boundary you could not inspect.
- Compare changed paths within the PR for repeated decisions, validation and transformations. Separately search the repository for existing implementations, including packages outside the call graph. Search by behavior, input/output types, errors and domain terms when names differ. Inspect the implementations and their callers.
- For a reuse suggestion cite both locations, the policy they must keep in sync, and differences in inputs, results, errors or side effects. Check the cost of sharing: dependency direction, visibility and coupling. Keep independently owned implementations when their contracts differ.
- Check the owner of the changed responsibility against applicable design records, package declarations and actual imports. Trace which consumers must change with it. Tie structural concerns to a documented dependency rule or a concrete maintenance cost.

## Adversarial contracts (when Challenger is active)

Start by locating the *actual* guarantees in the changed interface. For each relevant contract, seek a counterexample rather than another design opinion:

- **Boundary values and state:** Empty/duplicate/oversized inputs; valid-but-unexpected ordering; state transition from partially initialized to visible; stale snapshots and caches.
- **Behavior under failure:** Error before/after a side effect; partial commit; retry after ambiguous success; cancellation; rollback that itself fails.
- **Compatibility:** An older producer/newer consumer pair; backwards-compatible schema or serialized encoding; persisted data from a previous release; previously legal API calls that now behave differently.
- **Security boundaries:** Authorization is checked at the correct resource/action boundary, not just an upstream handler; identity and tenant context survive nested calls; errors and logs do not leak sensitive fields.
- **Evidence:** Cite where the precondition is checked (or demonstrably is not), the reachable entry point, and the observable violation. The existence of multiple code paths alone is not a bug.

Do not infer a specification solely because an implementation looks odd. If the contract is an inference, label it **assumed** and seek corroboration.

## Error handling

- Trace failure origin, propagation, handling, and caller-visible outcome. Check whether ignored errors, defaults, empty results, or fallbacks misrepresent failure as success. Respect documented best-effort behavior.
- Verify that callers can distinguish failures requiring different actions, such as retry, rejection, or reconciliation. Check retry bounds and idempotency after side effects, including outcomes where completion is unknown.
- Examine partial success, rollback, cleanup, timeout, and cancellation where affected. Do not assume returning an error undoes prior work; use the Systems lens for relevant multi-step or asynchronous operations.

## Error chaining

- At wrapping/conversion boundaries, check preservation of the cause and any error type/code used by callers. Follow actual consumers before claiming that string conversion or type erasure breaks behavior.
- Check that added context identifies the failed operation or relevant target without repeatedly restating the same message. Do not require a wrapper at every layer.
- Check whether cleanup or rollback errors replace the primary failure and obscure diagnosis. Preserve relevant secondary failures using the repository's established mechanism.
- Internal causes may intentionally be hidden at public boundaries. Verify the required internal diagnostic path and external contract rather than requiring full chains in public responses.

## Error messages

- Identify the audience: end user, API consumer, or operator. Check that the message accurately describes the observed failure and, where needed, supplies safe diagnostic context or an actionable next step.
- Check for misleading claims about success, retry safety, missing resources, or authorization. Do not require speculative recovery advice that the implementation cannot guarantee.
- Examine sensitive values and internal details crossing trust boundaries, including causes rendered by existing logging/response code. Respect redaction and public error-disclosure policies.
- Prefer stable error codes/types for programmatic handling, but inspect existing consumers before judging message changes. Exact wording is a contract only where documented or actually depended on.
- Report concrete diagnostic loss, misleading behavior, disclosure, or contract violations; wording preferences alone are not findings.

## Test coverage and quality (independent of error review)

- Map materially changed behavior to a contract/invariant and the tests that protect it, searching relevant existing tests beyond the diff. Review successful behavior and general regression coverage even when error handling is unchanged. Use available requirements without inventing a spec.
- Select relevant scenarios: normal results, empty/boundary/duplicate inputs, ordering, state transitions, repeated calls, integration boundaries, serialization, configuration, persistence, backward compatibility, failures, and concurrency. Do not require every scenario for every change.
- Inspect assertions: would an incorrect observable result, state transition, or side effect make the test fail? Execution without meaningful assertions is not sufficient evidence of coverage.
- Inspect fixtures, mocks, and test wiring where relevant. A mock may bypass the changed behavior; an integration test may already cover a contract with no dedicated unit test. Check that the test is discoverable and applicable to the relevant feature/configuration before relying on it.
- For regression fixes, look for a test that distinguishes the previous faulty behavior from the intended behavior. State whether that distinction was inspected, executed, or remains unverified.
- Assess determinism and isolation when they affect reliability: uncontrolled timing, shared state, order dependence, and assertions that can pass without reaching the intended scenario.
- Coverage percentages are supporting evidence, not proof of behavior. Do not invent metrics, impose arbitrary thresholds/test counts, or request one test per implementation detail. Honor explicit repository coverage requirements.
- Separate demonstrated implementation defects, concrete test gaps, and inspection limitations. Test gaps normally belong in the test coverage assessment as advisories; explicit test-policy violations may be Standards findings. Do not promote missing tests into runtime defects or assign severity from test absence alone.
- For a meaningful gap, state the changed contract, uncovered scenario, relevant tests inspected, plausible regression they would miss, and a minimal behavioral test direction. Attach a regression-test direction to an existing defect rather than reporting the same issue twice.
- Report test presence/inspection separately from execution: passed, failed, or not run with a reason. Failure of a check is not automatically caused by this diff; inspect the failure. Never infer passing checks from configuration or imply complete coverage because no gaps were found.

## Spec lens (run as a distinct pass only when an authoritative spec exists)

Compare changed behavior against user-provided requirements, issue/PR description, ADR, or verifiable local spec. For each requirement, record evidence of coverage, a mismatch, or why inspection was impossible. Check missing scenarios and scope creep. Cite the source and exact requirement. **Do not infer an unwritten requirement from reviewer taste.** If no spec is available, report that this lens was not evaluated; do not declare a spec pass.

## Prioritizing findings

- A project-specific *documented rule* normally supersedes a generic style preference. Concrete safety/correctness issues can still override a local habit.
- Mandatory policy (e.g., production panic-producing `unwrap()` under ReviewLens defaults) may be recorded as a low severity standards issue even when a reachable crash is not demonstrated; a real crash requires a path and impact.
- Contextual advice (a new dependency, abstraction choice, naming, clone) becomes a finding only if it materially harms a stated requirement or shown behavior.
- Make comments terse, constructive, and directly linked to the changed line(s). Do not praise for padding.

Inspiration: Matt Pocock's separate Spec/Standards reviews and Google's engineering review guidance. The language here is independently written; see repository `docs/SOURCES.md`.
