# General lens — correctness, requirements, maintainability

Use this for every reviewed change, regardless of language. Examine actual project conventions before relying on generic heuristics. Prefer issues that change behavior or raise long-term maintenance cost materially.

## Standards and design

- **Behavior**: Do inputs, outputs, errors, state transitions, ordering, and edge cases preserve the intended contract? Check negative paths, not just success paths.
- **Public contracts**: Check compatibility of APIs, wire formats, schema/config migrations, serialization, feature flags, and persisted data. Identify version-dependent consumers.
- **Design**: Ask whether the added abstraction solves a current need, makes ownership explicit, and respects module boundaries. Prefer simpler designs where equally correct; do not demand a personal favorite architecture.
- **Scope**: Flag unrelated behavioral changes or broad refactors that obscure the primary purpose when they add demonstrable risk.
- **Complexity**: Look for branches that are unreachable or wrongly ordered, duplication that will drift, hidden state, contradictory invariants, and nonlocal side effects. Code smells are prompts to investigate, not automatic defects.
- **Errors**: Verify error meaning and propagation, retries, rollback, idempotency, and caller-visible behavior. Consider partial success and failure after side effects.
- **Security**: Review trust boundaries, access control, sanitization, secret exposure, and injection when relevant to changed flows. Avoid inventing unproven vulnerabilities.
- **Documentation**: Require changes when documented behavior becomes inaccurate, especially public APIs and operational settings. Do not demand redundant comments.
- **Observability**: Check existing log/metric conventions, important failure visibility, sensitive-data redaction, and excessive hot-path logging. Preserve the repository's existing logging technology.

## Adversarial contracts (when Challenger is active)

Start by locating the *actual* guarantees in the changed interface. For each relevant contract, seek a counterexample rather than another design opinion:

- **Boundary values and state:** Empty/duplicate/oversized inputs; valid-but-unexpected ordering; state transition from partially initialized to visible; stale snapshots and caches.
- **Behavior under failure:** Error before/after a side effect; partial commit; retry after ambiguous success; cancellation; rollback that itself fails.
- **Compatibility:** An older producer/newer consumer pair; backwards-compatible schema or serialized encoding; persisted data from a previous release; previously legal API calls that now behave differently.
- **Security boundaries:** Authorization is checked at the correct resource/action boundary, not just an upstream handler; identity and tenant context survive nested calls; errors and logs do not leak sensitive fields.
- **Evidence:** Cite where the precondition is checked (or demonstrably is not), the reachable entry point, and the observable violation. The existence of multiple code paths alone is not a bug.

Do not infer a specification solely because an implementation looks odd. If the contract is an inference, label it **assumed** and seek corroboration.

## Test quality

- Identify the invariant/contract that could regress, then verify that tests exercise the critical observable behavior.
- Consider failure injection, boundary inputs, concurrency interleavings, and backward compatibility when they are material.
- Avoid requesting one test per implementation detail or a fixed test count. A small number of behavioral tests may be sufficient.
- Distinguish missing proof from a demonstrated bug: missing tests without a concrete regression risk usually merits an advisory, not a critical finding.
- Report actual test/tool execution status. Never infer passing checks from configuration files.

## Spec lens (run as a distinct pass only when an authoritative spec exists)

Compare changed behavior against user-provided requirements, issue/PR description, ADR, or verifiable local spec. For each requirement, record evidence of coverage, a mismatch, or why inspection was impossible. Check missing scenarios and scope creep. Cite the source and exact requirement. **Do not infer an unwritten requirement from reviewer taste.** If no spec is available, report that this lens was not evaluated; do not declare a spec pass.

## Prioritizing findings

- A project-specific *documented rule* normally supersedes a generic style preference. Concrete safety/correctness issues can still override a local habit.
- Mandatory policy (e.g., production panic-producing `unwrap()` under ReviewLens defaults) may be recorded as a low severity standards issue even when a reachable crash is not demonstrated; a real crash requires a path and impact.
- Contextual advice (a new dependency, abstraction choice, naming, clone) becomes a finding only if it materially harms a stated requirement or shown behavior.
- Make comments terse, constructive, and directly linked to the changed line(s). Do not praise for padding.

Inspiration: Matt Pocock's separate Spec/Standards reviews and Google's engineering review guidance. The language here is independently written; see repository `docs/SOURCES.md`.
