# Sources, attribution, and licensing

ReviewLens uses **independently written prompts** informed by review *ideas and techniques* from the projects below. None of their SKILL.md contents, scripts, prompts, agents, or binary artifacts are vendored or copied. References are provided for traceability, not endorsement, and their licenses continue to govern their respective original works.

| Source | Ideas used by ReviewLens | Upstream license | Primary link |
| --- | --- | --- | --- |
| Trail of Bits `rust-review` | Capability-guided auditing, independent candidate verification, unsafe/FFI/concurrency coverage | CC BY-SA 4.0 (upstream repository) | https://github.com/trailofbits/skills/tree/main/plugins/rust-review |
| NVIDIA-NeMo Switchyard `switchyard-rust-review` | Practical Rust and async review questions, memory/backpressure/streaming/FFI, comment hygiene; *project-only* preferences deliberately not imposed | Apache-2.0 | https://github.com/NVIDIA-NeMo/Switchyard/blob/main/.agents/skills/switchyard-rust-review/SKILL.md |
| Matt Pocock `code-review` | Keep requirements/Spec findings independent from repo-standards findings | MIT | https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md |
| Google Engineering Practices (archived) | Design, functionality, complexity, tests, and code-health review criteria | CC BY 3.0 (documentation) | https://google.github.io/eng-practices/review/reviewer/looking-for.html |
| obra Superpowers | Providing precise Git scope to a reviewer; critically validating review feedback | Verify upstream per-file licenses before any verbatim reuse | https://github.com/obra/superpowers/tree/main/skills |

**ReviewLens additions:** minimal six-file portable skill organization, conditional selection of Rust/Systems lenses, evidence thresholds for memory/performance, database visibility/durability/recovery checks, policy distinctions (`unwrap`/`expect`, contextual `parking_lot`, repository-specific logging), and bilingual installation documentation.

**ReviewLens license:** MIT applies only to ReviewLens's original material. It is **not** a relicensing of Trail of Bits's CC BY-SA 4.0 text, Google's CC BY 3.0 guide, or NVIDIA's Apache-2.0 implementation. If downstream contributors copy substantial upstream expressive text, they must separately honor the corresponding license and attribution obligations (including ShareAlike where applicable). This file is an attribution of intellectual inspiration, not evidence of official affiliation or approval.
