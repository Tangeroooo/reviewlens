# Systems lens — asynchronous services, performance, storage, and failure

Read this only for changes affecting runtime scheduling, concurrent work, performance-sensitive paths, memory pressure, I/O, distributed behavior, or data storage. For a simple library change, do not invoke this lens automatically just because it uses Rust.

## Async/concurrency and resource budgets

- **Blocking:** Identify synchronous disk/network waits, CPU-heavy tasks, and blocking locks on executor threads. Verify bounded offload strategies and shutdown behavior where relevant.
- **Tasks:** Examine spawning, cancellation, result/error observation, panic propagation, join/abort semantics, and shutdown/drain. A dropped future/task does not guarantee underlying side effects were rolled back.
- **Backpressure:** Trace end-to-end admission, bounded queues/channels, fan-out, streams, and downstream slow-consumer behavior. If unbounded structures exist, show the input rate/time condition for unbounded growth rather than calling every allocation a leak.
- **Locks:** Find lock-order inversions, reentrancy, lock lifetime across await/IO, starvation, contention and fairness. Distinguish a demonstrated deadlock from a speculative lock contention concern.
- **Memory:** Track per-request and global buffering, peak allocation, sharing, decompression amplification, caches, retained references, mmap vs anonymous RSS, and allocator retention. Note that high RSS after `free`/drop may reflect allocator retention and is not necessarily a live leak. Check cgroup budget, admission accounting coverage, and OOM paths.
- **I/O:** Review streaming vs whole-buffer fallbacks, short reads/writes, file synchronization, partial transfers, retries, checksums/integrity, idempotency, and cleanup of orphaned temporary objects.
- **Observability:** Determine whether the repository uses `tracing`, `log`, OpenTelemetry, custom logging, or another approach. **Never demand `tracing` simply because a different crate is present**; require useful context, sensitive-field protection, appropriate levels and sane high-volume costs. When `tracing` is already standard, assess spans and propagation.

## Storage/database (apply only to affected code paths)

- **Visibility/consistency:** Identify the linearization/visibility point. Can readers observe an incompletely published segment, catalog version, manifest, or index? Check snapshot isolation assumptions, write/read races, and generation checks.
- **Durability:** Compare acknowledgment order with WAL/journal persistence, object-store commit/flush semantics, metadata publication, checkpoints, and restart behavior. Explicitly describe the crash point that could lose acknowledged data.
- **Recovery/idempotency:** Inspect interrupted writes, partial uploads, replay, deduplication, compaction, deletion, rollback, retry, and lease/epoch invalidation. Can a replay duplicate records or expose an invalid segment?
- **Lifecycle/cache:** Check segment state machine transitions, pin/unpin, cache eviction, mmap lifetime, remote/local tier transitions, close/unload with active readers, generation fences, and GC safety.
- **Query correctness:** Verify filtering, projection, delete/update visibility, ordering, pagination, cancellation of distributed scans, limits, and planner/executor semantic alignment. Prefer functional counterexamples to algorithmic opinions.
- **Concurrency/operations:** Check bounded in-flight RPCs, pool exhaustion, queue growth, metadata/cache invalidation, partition moves, partial replica failures, and concurrent migrations.
- **Performance:** Separate correctness from advice. Review meaningful complexity, batching, copying, lock contention, disk/network amplification, locality, resource budgets, and p99 risks with explicit workloads and available measurements.

## Evidence threshold

For every issue identify: (1) changed path, (2) input or interleaving, (3) violated invariant, (4) actual observable outcome, (5) missing mitigation, and (6) test/repair. A path that *might* allocate a buffer is not sufficient to claim an OOM. A multi-step write is not automatically non-atomic if metadata publication or version fencing provides a safe commit point. Treat those designs as needing examination, not automatic findings.

Ideas are informed by NVIDIA Switchyard's systems-oriented review guidance. Database-specific criteria are ReviewLens original additions; see `docs/SOURCES.md`.
