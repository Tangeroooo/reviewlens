# Performance lens — work amplification and safe reuse

Apply in any language or application when a change affects repeated work, external operations, data processing, resource lifetime, or scheduling. A correctness, security, or durability fix can introduce a performance regression. Derive costs and safety contracts from the target code; do not assume a particular database, framework, hardware, or universal latency threshold.

## Establish the cost before judging it

Trace the entry point through changed helpers and their consumers. Compare the resolved base and target for the **same input, configuration, and required semantics**. Record the operation, invocation unit (request, batch, item, retry, etc.), call count, data processed, and reuse lifetime. Inspect callees: a cheap slice or wrapper can hide repeated parsing, allocation, I/O, or synchronization.

Establish expected workload from accessible repository evidence such as README, deployment configuration, limits, benchmarks, and actual consumers. Cite the sources and distinguish documented expectations from reviewer assumptions; if unavailable, record the unknown instead of inferring load solely from the application category. Record workload evidence separately for each independent path.

Distinguish total work from elapsed time. Useful models include `calls × setup cost + items/bytes processed × unit cost` and the number of serial external waits. Two O(n) implementations can differ materially when one repeats expensive setup per item. A larger operation count does not by itself establish a latency multiplier or an outage.

Inspect relevant earlier optimizations, callers, configuration defaults, and cost regression tests where accessible. Keep this history search local to affected behavior. An old optimization is evidence to examine, not authority to remove a new safety requirement. In blind evaluations, never read future fixes or answer keys.

## Checks and affected paths

Keep P1–P8 as separate coverage items for each independent affected path; use the coordinator's existing statuses and evidence rules. An absent trigger may be `not applicable` with a reason. A trigger whose cost or consumer cannot be traced remains `not inspected`, not a clean bill of health. These checks supplement correctness, Spec, Rust, and Systems coverage; they do not replace it.

| ID | Check | Trace and compare |
| --- | --- | --- |
| **P1** | Batching and vectorization | Batch-to-item/run/chunk changes; repeated kernel dispatch, parser/regex setup, temporary arrays, or transactions. Count setup calls as well as processed items; zero-copy slicing does not make repeated evaluation free. |
| **P2** | Expensive operation frequency | Database/API/RPC calls, file open/stat, decode, checksum, persistence barriers, and acknowledgments. Count per entry point including fan-out, retries, pool work, and wrapper fallbacks. Separate logical calls, physical operations, and network round trips. |
| **P3** | Repeated computation and safe reuse | Rebuilt plans, parsed constants/documents, counts, masks, lookups, and metadata. Identify already available results and the smallest valid sharing scope; check identity, inputs, options, freshness, invalidation, and error semantics. |
| **P4** | Processing and complexity amplification | Full scans for small selections, repeated sort/lookup, nested traversal, and read/decode/validation before filtering or limits. Account for total bytes and unrelated objects, not only returned items. Include hidden work in helpers. |
| **P5** | Allocation, copying, and retention | Clone-before-filter, concatenation, serialization, buffer growth, and large backing buffers retained by small views. Check peak coexistence and lifetime across concurrent requests; reuse may save CPU while increasing retained memory or admission pressure. |
| **P6** | Serial waits and contention | Await-inside-loop changes, lost bounded parallelism, locks covering scans/I/O/destructors, executor blocking, and queue/connection pressure. Separate ordering that the contract requires from independent work; preserve backpressure and resource bounds. |
| **P7** | Workload shape and fallback | Relevant size, fragmentation/distribution, selectivity, batch width, payload width, cache warmth, and concurrency. Exercise both sides of changed thresholds and fallback paths. A fast common case does not close a newly expensive reachable path. |
| **P8** | Evidence and regression protection | Existing tests of calls, processed bytes, allocations, or bounds; measured build/ref and workload; result/error equivalence; and what remains unmeasured. Output-only tests can miss performance-only regressions. Match the suggested check to the alleged cost. |

Choose workload dimensions from the actual trigger rather than taking the Cartesian product of every dimension. For example, filtering invalid records into many tiny valid runs can repeat setup despite reducing evaluated records; one contiguous invalid range is not an adequate control for fragmented input.

## Preserve the reason for the change

- **Safety work:** For newly repeated validation, authorization, integrity checks, durable writes, or acknowledgments, identify the guarantee and required observation/commit point. Look for equivalent batching or reuse without weakening it. Never recommend skipping required checks solely to match baseline speed.
- **Reuse:** A value valid within one request or immutable version may be stale across requests, tenants, mutable state, or later observations. Cache hits must preserve per-consumer options, limits, and error timing. Concurrent call sharing must define who may join and what happens on cancellation or failure.
- **Batching:** Check partial failure, order, transaction/replay boundaries, conflicts, cancellation, and peak memory before proposing coalescing. Evaluating excluded inputs may raise errors or effects that filtering previously suppressed. Larger batches and more concurrency are not universally better.
- **Tradeoffs:** Distinguish avoidable repeated work from a necessary or explicitly accepted cost. Report a documented tradeoff accurately; do not convert it into a defect unless its assumptions, bounds, or claimed impact are contradicted. Do not invent an SLA or demand a new cache/index/abstraction when existing results or bounded batching suffice.

## Evidence and finding threshold

For each candidate, supply this cost evidence alongside the normal trigger, path, and counterevidence:

```text
Workload and invocation unit: <input shape, size, concurrency, relevant configuration>
Base -> target work: <calls, traversals, bytes, allocations, or serial waits; cite both>
Safety/reuse boundary: <required guarantees, available result, validity and invalidation>
Mitigations checked: <batching/cache/bounds/fallbacks/caller behavior>
Impact and evidence: <source-derived amplification / executed operation count / measured timing>
Minimal correction or check: <preserve semantics; verify the alleged cost>
```

- Reachable, material work amplification can support a performance defect without a timing benchmark when the source proves the cost and workload. State what is established: for example, one remote read becoming one per item. Do not infer a wall-clock ratio from call counts, or raise severity based only on hypothetical saturation.
- A plausible expense without a base comparison, reachable workload, or material impact remains `needs-more-evidence`. An unrelated pre-existing optimization opportunity belongs outside defect findings. Necessary safety costs and minor optional optimizations are not automatically defects.
- Validate **every performance defect candidate in both modes**, including low severity. Try to disprove it using existing reuse, amortization, bounds, fast paths, compiler/library behavior, and semantic constraints. A cost-only regression need not violate output correctness; identify the demonstrated cost change instead of inventing a correctness invariant.
- Prefer deterministic operation/byte/allocation checks for the specific mechanism. If counters miss it (for example, a vectorized implementation replaced by an element loop), use an authorized focused measurement or record the limit. Avoid wall-clock thresholds on shared CI and tests that merely repeat implementation details.
- For timing evidence, record baseline/target refs, build mode, data and cache state, resources, concurrency, repetitions, and the measured boundary. Preserve error/result checks. Do not present a microbenchmark as end-to-end throughput or measurements of an earlier revision as final-head results. Suggested tests are not executed tests; costly or external runs still require authorization.
