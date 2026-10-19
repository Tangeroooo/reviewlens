# Rust lens — language safety, correctness, and idioms

Use for changed Rust code. Combine the language-safety emphasis inspired by Trail of Bits with practical Rust guidance inspired by NVIDIA Switchyard. The checklist is **risk-directed**: establish real paths and invariants, not syntax-pattern violations alone.

## Safety and representation

- **Ownership/lifetimes:** Are borrowed values valid through all uses? Does shared ownership unintentionally retain large objects? Inspect self-referential patterns, pins, interior mutability, and lifetime assumptions at FFI boundaries.
- **`unsafe` invariants:** For each changed unsafe block/unsafe impl/API, identify the claimed preconditions, caller obligations, and proof for pointer validity, alignment, initialization, aliasing, provenance, and length/capacity. Look at both the unsafe implementation and *safe* callers that may make invalid states reachable.
- **Memory safety:** Check raw-pointer/`Vec::from_raw_parts`/`set_len` usage, drop exactly once, allocation/deallocation layout agreement, slice bounds, `MaybeUninit`, and validity of externally provided buffers. Mere presence of `unsafe` is not itself a finding.
- **`Send`/`Sync` and atomics:** Scrutinize manual impls, ordering, publication/visibility invariants, ABA where relevant, condition synchronization, and thread migration of non-thread-safe resources. Demand a concrete interleaving for asserted races.
- **FFI:** Check ABI, `repr`, ownership transfer, error/unwind boundaries, pinned addresses, callback lifetime, foreign-thread invocation, and GIL behavior if PyO3 is actually used.

## Rust behavior and failure safety

- **Production `unwrap()` / `expect()` policy — REQUIRED:** ReviewLens defaults to forbidding both in non-test production paths. Prefer `?`, explicit error mapping, safe pattern matching, or a justified invariant that cannot panic. Flag a use as a *standards violation* even when failure seems impossible; classify as a runtime bug only when a reachable failure and impact are established. Allow test/example-only code; classify generated or external vendor code by project ownership and policy.
- Handle `panic!`, `assert!`, and indexing similarly **when they can reach untrusted inputs or threaten a service**, but do not mechanically ban assertions or safe indexing in every context.
- **Errors:** Use explicit recoverable errors when the caller can act. Check `?` conversions, context, retry behavior, swallowed `Result`s, and partially applied side effects. Respect the repository's chosen `anyhow`/`thiserror`/custom error strategy.
- **Resource lifetime:** Verify `Drop`/RAII releases locks, memory maps, FDs, temp files, handles, and partially initialized state. Check order of teardown, cancellation and panics; do not rely solely on manual cleanup in the success path.
- **APIs:** Enforce meaningful type/ownership contracts, object-safety/lifetime constraints, trait bound appropriateness, and semver behavior for public crates.

## Efficient, idiomatic Rust — CONTEXTUAL

- **Copies:** Trace `clone`, `to_vec`, `collect`, `Arc`, `Box`, and temporary `String`/`Vec` on meaningful hot paths. Propose a borrow/move/reference-counted representation only where it actually reduces measured or clearly bounded allocation/copy cost without complicating lifetime safety.
- **Synchronization choice:** **Never require `parking_lot` just because `std::sync::Mutex` or `RwLock` appears.** Compare scope duration, workload/contention, fairness, poisoning policy, compatibility, dependency cost, and behavior during panic. `parking_lot` lacks poisoning; this can be a semantic difference. `tokio::sync` primitives allow asynchronous acquisition; synchronous locks may be appropriate for short, `.await`-free sections. Do not block executor threads waiting on contended synchronous locks, and do not hold synchronous guards across `.await`.
- **Pointer/sync complexity:** Do not prescribe `Arc<Mutex<T>>` or remove it without verifying ownership and concurrent access. Avoid gratuitous atomic lock-free rewrites.
- **Idioms:** Favor transparent control flow, correct `Result` handling, predictable types, and minimal boilerplate. Preserve established naming, lint, and dependency standards. Avoid mass renaming for taste.

## Adversarial Rust probes (high-risk changes)

- **Unsafe proofs:** List preconditions and postconditions for each modified unsafe boundary. Attempt one counterexample for aliasing, pointer provenance/alignment, initialization, length/capacity, panic/unwind, or lifetime as applicable. Also inspect whether a *safe public API* allows a caller to break the unsafe preconditions.
- **Publication and synchronization:** Distinguish concurrent execution from an actual race. Write a concrete ordering showing which store/load/lock establishes the required visibility. Examine stale generation, lost wake-ups, ABA, double-release, and teardown races only where the code makes them plausible.
- **Panic and cancellation:** Follow ownership of resources when an async future is dropped, a task is aborted, or a callback panics. Check whether `Drop` restores invariants or whether partial state becomes externally visible.
- **Boundary/control:** A passing borrow check, `Send`/`Sync` inference, clippy, or Miri run is evidence about certain classes of behavior, **not** proof of overall API or storage correctness. Never claim UB solely from a suspicious primitive.
- **`unwrap()` / `expect()` defaults remain REQUIRED:** A changed production use can be reported as a standards issue even if impossibility of failure has been established; demonstrate a reachable error path before claiming a crash. Respect genuine test-only or generated-code exceptions.

## Targeted validation (only if available and appropriate)

- `cargo fmt --check`, `cargo clippy`, `cargo test` according to repo instructions; do not silently modify files or fetch packages. Request permission before costly checks.
- Miri when an appropriate runnable test exists for UB or unsafe code; Miri does not prove the absence of all memory/concurrency bugs.
- Focused regression tests for panic paths, failed allocations, partial initialization, FFI contracts, atomic publication, and cancellation.

Cross-check with [systems.md](systems.md) only when async, I/O, concurrency, resource pressure, storage, or distributed behavior is materially changed. Keep the Rust lens focused on language contracts; systems lens covers behavior under load/failure.

Sources of ideas: Trail of Bits `rust-review` and NVIDIA Switchyard `switchyard-rust-review`. This text is newly written and is not a copy of their prompt files.
