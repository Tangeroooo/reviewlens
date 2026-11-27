# Requested change

Centralize the retry eligibility rule used by the status API and queue selection.
Keep both public function signatures and outputs unchanged, preserving input order.
A job is retryable exactly when its state is "failed" and attempts is below retry_limit.
Callers provide lists of jobs with id/state/attempts present, nonnegative integer attempts,
and a nonnegative integer retry_limit. Input validation is outside this change.
These are small in-memory job lists; no persistent/wire record format, plugin API,
or requirement for future configurable rules is involved. No dependencies are needed.
