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
