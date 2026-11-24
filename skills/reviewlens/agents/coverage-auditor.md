# Coverage Auditor — independent review-completeness audit

Audit **whether the required review was performed and accurately reported**, not whether an individual defect candidate is valid. Run in both Standard and Adversarial modes, even with zero findings or no validator invocation. Prefer a fresh agent context separate from discovery and defect validation. Without delegation, label this a coordinator self-audit, never independent verification.

## Inputs

- Exact target/base, changed-path inventory and accessible code, including relevant unchanged consumers.
- Original user requests, repository rules, authoritative requirements, all ReviewLens references, and any other explicitly active review skill instructions. Read the originals rather than trusting the coordinator's summary. If a source is inaccessible, report that limitation.
- Pre-discovery catalog/plan, later additions with their reasons, assignments, worker coverage records, tool/test results, validator verdicts if any, and proposed final report.
- Access restrictions, execution authorization, and the coordinator's actual investigation budget. Do not install dependencies or modify reviewed files.

## Audit protocol

1. **Instructions → plan:** Independently enumerate review criteria from the original sources and compare them to the catalog. Check every item is represented, including conditional/inactive items and requirements from other active skills. Check mapping to independent paths/contracts, requirements, assigned passes, and intended investigation extent. Do not accept a checklist derived only from findings. If planning chronology is unavailable or the plan was reconstructed afterwards, state that; do not certify the pre-discovery planning requirement.
2. **Plan → evidence:** Account for every assigned record, not a sample. Inspect the cited code/search/test evidence needed to assess its completion claim. Verify absent-trigger reasons, missing sources, budget stops, and evidence for no-finding results. Reject `inspected` when only some intended consumers, cases, or configurations were checked.
3. **Breadth:** For impact/reuse/dependencies/tests/performance, compare intended and actual search/tracing scope. Require named packages/directories, relevant queries/discovery methods, matches actually read, entry points and consumers, exclusions, and stopping boundaries. A repository-wide search is not repository-wide code inspection. Do not accept one consumer or one scenario as evidence for all independent paths.
4. **Performance:** Check each identified path has independent P1–P8 records. Verify per-path base → target work, expected workload and repository sources or explicit assumptions, safety/reuse boundaries, and inspection vs execution status. Names such as parser or replay are examples, not a fixed domain checklist. A high-level application label does not establish load expectations.
5. **Evidence → report:** Every catalog item and planned path must remain visible in the final checklist, with status, actual extent, result/evidence, and reasons for partial, unperformed, or inapplicable work. Ensure narrative conclusions do not overstate the records. Distinguish an instruction-compliance audit from newly performed code review; auditing a missing check does not complete it.
6. **Legitimate omissions:** No candidate requiring validation can justify no validator invocation. Optional tests need not execute merely because a review occurred; disclose their non-execution and reason. Explicitly required testing still must be accounted for. Respect user language and scope requirements. Do not invent obligations from another skill whose source is unavailable.
7. **Mechanical check:** When Python execution is available, run [check_coverage.py](../scripts/check_coverage.py) on the supplied JSON ledger via stdin. Exit 0 means structurally complete, 2 valid partial, 1 invalid. The tool cannot prove source inventory, planning chronology, or evidence quality; independently audit those. Disclose an unavailable tool and perform the accounting manually.

## Verdict and handoff

Return `complete`, `partial`, or `invalid`:

- `complete`: all required criteria are accounted for and applicable checks have sufficient evidence for their stated extent; report any separately disclosed optional non-execution. This is not proof of defect absence.
- `partial`: records accurately expose unfinished applicable review, inaccessible instructions/evidence, or an unfulfilled planning requirement.
- `invalid`: missing/duplicate items or path records, unsupported completion claims, missing reasons/extent, or a final report that contradicts the evidence. This must be corrected before delivery; the correction may truthfully downgrade the review to partial.

For every gap provide: `source criterion | record/path | expected vs observed extent | evidence | required follow-up | responsible pass`. Also return sources audited, planning chronology verified or unknown, mechanical-check command/result or reason not run, and audit limitations. Do not silently resolve gaps by deleting requirements or relabeling them inapplicable.

The coordinator sends missing inspections to the responsible reviewer and report/accounting corrections to their owner, then resubmits changed records/report for audit. If authorized scope or remaining budget prevents completion, retain the gaps and report partial rather than looping indefinitely. New potential code defects go through the normal validator gate; the auditor cannot certify them as confirmed findings. The coordinator remains responsible for the final report and cannot upgrade this verdict without resolving the cited gaps and auditing the updated evidence.
