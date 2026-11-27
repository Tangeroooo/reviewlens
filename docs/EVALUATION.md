# Evaluating ReviewLens: Standard vs Adversarial

This guide measures whether Adversarial review **actually finds more real bugs**, rather than merely writing more findings. The distribution tests do not measure model review quality.

## Assemble a blind, balanced review set

Use **at least 20 independently fixed real defects** from representative repositories (pre-fix commits) and **at least 20 clean/accepted diffs** as negative controls. Cover public contracts, boundary inputs, error behavior, reuse and package dependency direction. Add domain-specific cases when evaluating a specialized lens. Keep each historical bug's fix, issue answer, and benchmark label *out of the reviewer's context*. Do not expose private source outside the approved execution environment.

For each case, independently document: review base and head, changed-line location, validated root cause, realistic triggering sequence, actual fix, and scoring criteria. Record whether an authoritative specification exists. This ground truth must be created **before** running any review.

## Paired cases for impact, reuse, and structure

Use separate, blind reviews for both variants of each pair. Keep the answer key and the paired variant out of the review context. Compare baseline, Standard, and Adversarial at the same review scope and budget. These case designs can be implemented in any language.

| Case | Change with an issue | Control change | What counts as a useful finding |
| --- | --- | --- | --- |
| Consumer contract | An API returns an empty value instead of the documented missing-value sentinel. An unchanged consumer now skips its fallback. | The same internal representation changes, but an adapter preserves the public sentinel. | Trace the public path to the consumer in the first case and recognize the adapter in the control. |
| Repeated validation | Two new entry points independently implement an existing inclusive bound. One accidentally rejects the exact limit. | Both use the same existing validator; one adds a documented entry-point-specific check. | Identify the boundary input, both new sites, and the reusable definition. Preserve the distinct precondition in the control. |
| Dependency direction | A shared package imports an application package to reuse a pure conversion despite an explicit dependency rule; both already depend on the package owning the converted type. | Similar-looking conversions belong to separate adapters with different rounding contracts and no shared policy. | Cite the actual edge and rule in the first case. Check the contracts before recommending extraction in the control. |

Record confirmed defects, actionable design suggestions, false positives on controls, and cross-package paths inspected. Track the time and token cost. For each unique finding added or rejected at final review, record whether adjudication supports that decision.

## Code-quality advisory/control pairs

Evaluate Q1–Q5 separately from bug recall: correct outputs do not establish maintainability, and a supported advisory must not inflate defect counts. Freeze the changed scope, current maintenance task/contract, counterevidence, and acceptable correction tradeoffs before review. Use blind separate contexts for each variant; do not provide the expected advisory or its control.

| Case | Potentially actionable change | Control | What to assess |
| --- | --- | --- | --- |
| Readability/control flow | A current decision is spread through opaque flags and indirect branches across actual callers. | A local explicit branch expresses the same rule, even if longer. | Trace the decision and explain the present reading cost; no line-count verdict. |
| State/interface | A new positional record requires producers and consumers to coordinate undocumented indices and derived fields. | A direct predicate or existing named value carries only the needed contract; or an explicit stable wire format requires positional fields. | Cite producer/consumer sites and constraints; prefer the smallest compatible representation. |
| Abstraction | Unused extension hooks route a single current policy through configuration and wrapper layers. | A superficially similar boundary protects a documented compatibility or test contract. | Check real callers and the reason for the boundary before recommending removal. |
| Change locality | One current policy is now scattered across independent edits with no owner. | Similar code implements intentionally different policies with incompatible errors or dependencies. | Explain actual edit sites and sharing costs; do not force reuse. |
| Testability | Pure policy now reads hidden global/environment state, requiring unrelated integration setup. | An existing explicit seam or integration test already exercises the policy reliably. | Verify the claimed obstacle and the available tests; keep test-gap and quality advice distinct. |

Record Q1–Q5 coverage, supported/deduplicated advisories, unsupported advice on controls, invented runtime defects, and whether corrections preserve contracts. Include no-advisory and zero-defect-with-advisory outcomes in the validator/auditor acceptance cases. Check that a missing quality inspection remains partial even if all bug hypotheses were rejected. A supported advisory alone is not a merge blocker without an applicable requirement. These cases are evaluation designs, not executed measurements or a mandate for a new review pass.

## Performance regression/control pairs

Evaluate Performance across languages and applications, independently of Systems activation. Use the same frozen inputs to compare the previous skill and the candidate in each mode; keep model, tools, budget, and other checks fixed. Track existing correctness findings as well as performance detection so added coverage cannot hide losses elsewhere.

| Case | Change with an issue | Control change | What counts as a useful finding |
| --- | --- | --- | --- |
| Fragmented batches | A validation fix evaluates each valid run separately, rebuilding the same parser or regex for every run. | Preparation is shared within a valid scope; excluded records still cannot raise errors. | Count setup calls under scattered and contiguous exclusions, and preserve the validation guarantee. |
| Web/API fan-out | A page replaces one bulk lookup with an awaited remote read for each displayed item. | A bounded bulk read preserves per-item authorization and result order. | Trace actual backend calls and waits through the adapter; do not bypass authorization. |
| Repeated parsing | An importer reparses a constant format or the same immutable document for each consumer. | Preparation/document reuse is scoped by input identity and options, with bounded lifetime. | Identify duplicate work and its valid reuse scope; reject cross-user or stale reuse. |
| File/cache cleanup | Removing each matched object rescans and clones the whole registry. | A bounded selection pass preserves active users and replacement identities, with disposal outside the lock. | Show the product of removals and registry size, copying, and contention without breaking lifetime safety. |
| Serial persistence | Independent already-durable items are reread and verified sequentially on every request despite an equivalent pinned proof. | Fresh verification or a persistence barrier is required by the actual acknowledgement contract. | Distinguish unnecessary repeated work from required freshness/durability; do not recommend weaker guarantees. |
| Lifetime and selectivity | A small selected result now retains a huge backing buffer, or all payloads are decoded before a selective filter. | A bounded copy or selective decode preserves errors, ordering, and resource limits. | Explain reachable bytes/lifetime, including concurrent requests and fallback paths. |

Freeze base/head, realistic workload dimensions, required semantics, and expected cost evidence for each case before review. Include tiny/bounded inputs, necessary safety costs, and explicit accepted tradeoffs as negative controls. Check clean outcomes as carefully as positive findings; a loop, allocation, cache miss, or missing benchmark alone is not a defect.

Prefer reproducible operation/byte/allocation counts where they capture the mechanism. For performance-only mutations that preserve output and counts (such as losing vectorization), use authorized controlled timing or mark them unmeasured. Record measured refs and distinguish local kernels from end-to-end behavior. No universal QPS or timing threshold is implied.

Score P1–P8 coverage per independent path, correctness retention, performance recall, false positives on controls, and review cost. Separate source-derived amplification, executed counts, and measured timing. Synthetic smoke cases establish protocol behavior only; these case designs are not completed benchmarks or evidence of improved real-world recall.

## Run a controlled comparison

For every identical case:

1. Run the base agent without the skill, ReviewLens `Standard`, and ReviewLens `Adversarial`. Rotate run order across cases to reduce ordering bias. Use isolated agent sessions with no shared candidate findings.
2. Keep model/version, code access, allowed commands, budget, tools, diff scope, and spec identical. Record whether independent subagents **actually** ran, and whether tests executed.
3. Have a reviewer who can read the code match each Finding to the ground-truth defect (exact root cause, not shared keywords). Mark unsupported claims and duplicate findings; do not treat unverified hypotheses as confirmed positives.
4. Save reproducible case artifacts: inputs/scope, mode, final findings, coverage limitations, run wall-time and tokens when available. Never include secrets in reports.

Suggested request:

```text
$reviewlens Review the changes between <BASE> and <HEAD> in Adversarial mode.
Use the available source code only. Do not read future commits or external fix discussions.
Report each candidate's execution path, defenses checked, and whether any tests actually ran.
```

## Record results

| Metric | Definition |
| --- | --- |
| Bug recall | Distinct ground-truth bugs detected / total known bugs in applicable positive cases |
| Finding precision | Matched real defects / all reported substantive defect findings |
| False positives per clean PR | Unsupported confirmed defect findings / clean-control PRs |
| High-severity miss rate | High/critical ground-truth defects not detected / all high/critical defects |
| Evidence quality | Fraction of findings with accurate trigger, execution path, mitigating guards checked, and corrected impact |
| Coverage candor | Fraction of reviews accurately distinguishing inspected/tested/uninspected paths |
| Cost | Wall-time, tokens, and number of subagents per case |

Also track `needs-more-evidence` separately: it is **not** a confirmed Finding. Treat severe but well-calibrated uncertainty as a useful follow-up, not automatic success or failure. Report full per-case results; small sets do not justify sweeping accuracy claims.

## Release gate

Use a release candidate only when distribution tests pass, Claude/Codex packaging checks pass **where those CLIs are available**, and adversarial mode shows meaningful benefit on the same frozen set **without unacceptable increases in false positives or cost**. Prefer paired comparisons and inspect regressions individually. These case designs do not establish detection performance.

## Coverage-audit acceptance cases

Evaluate the auditor separately from defect discovery: provide original instruction sources, initial plan/history, code evidence and a draft report. Keep expected verdicts out of its context. Include omitted catalog items, absent independent P1–P8 paths, unsubstantiated workload assumptions, missing investigation boundaries, and a retrospectively reconstructed plan presented as original. The auditor should identify each gap, its source, and remaining work; merely writing a fuller table does not complete omitted inspection. Negative controls include no validation candidates and optional tests explicitly not run. They must not be reported as mandatory missing work. Also evaluate a complete no-finding review and a truthful partial review.

Record false completion verdicts, false omission claims, instruction-to-plan reconciliation, and fidelity of stated breadth to actual evidence. The coverage-checker tests validate JSON accounting only; they do not establish that an agent follows instructions or that its inventory is complete.

## Language and delivery acceptance cases

Use the same review evidence with different user requests and draft deliverables; do not change the defect or coverage facts. Include a Korean request with English source/skill text, an English request with Korean comments, a mixed-language follow-up with an established preference, and an explicit output-language override. Expect explanatory text in chat, detailed review, audit, and coverage reasons to follow the resolved request language, while identifiers, quotations, JSON keys and canonical status values remain intact. A Korean chat answer with an English audit file must be corrected.

Contrast links/counts-only answers with self-contained summaries covering material trigger/impact/action, actual breadth, test execution/gaps, audit basis and remaining work. Include no-finding and partial reviews, an explicitly requested terse answer, and a summary whose verdict/counts disagree with the files. Check that presentation corrections do not invent new code defects, imply unexecuted tests passed, erase checklist items from the detailed report, or upgrade a partial review. These are evaluation designs, not executed language-detection or model-behavior tests; the JSON checker does not validate prose language or summary adequacy.

A bounded [Q1–Q5 advisory/control trial](evals/code-quality/report.md) preserves two synthetic inputs and fresh-context worker reports. It tests the quality-pass component only, not full review accuracy or improvement over the previous skill.
