# Independent review: bounded full-shard continuation

**Review status: source review passed for creating the final code guard and running pre-admission fixtures. Chained admission remains conditional on root integration: final source hashes, reviewed first pair, and frozen candidate bytecode dependencies.** No jobs were submitted and no scheduler/authentication commands were run during this review. The source files under review were not edited.

## What passed

- The callback resolves the actual reference and candidate evaluation directories produced by the frozen full-shard drivers. It checks the frozen role/shard plan, prepared corpus and manifest hashes, exact selected IDs, complete coverage, concurrency 64, pinned generation settings, zero service errors/deadline skips, retained response bodies, and the measurement-validity receipt.
- It recomputes each answer from the raw OpenAI response body using the pinned parser and checks the stored answer, finish reason, prompt/token hashes, shot count, category, and expected label against the prepared corpus. The full aggregator independently verifies non-overlapping shards and the complete 12,032-ID set for both roles; it sums item-level correctness and reports the candidate/reference accuracy ratio. A local quality-gate failure is retained as a completed measurement.
- Reference paths resolve to `jobs/full-ref-NNof08/runs/JOB/reference/evaluation`. Candidate paths resolve to `jobs/full-cand-NNof08/AI_Task/logs/full-shards/JOB/evaluation`. Generated Slurm stdout/stderr parents exist for the tested shard directories.
- The wrapper copies the original frozen submit script's resource headers into `sbatch --wrap`, runs that unchanged script from the same submit working directory, captures the driver's exit code, invokes the callback after the driver's cleanup trap, and returns the driver error before the callback status. The wrapper has valid POSIX shell syntax. The existing drivers reserve two nodes, 16 GPUs, exclusive access, and a 17-minute limit. The fill path uses the shared admission lock, current queue count, own five-job cap, fixed 16-job ledger limit, and definite receipts; it does not cancel or retry jobs.
- All 11 finite-event fixtures passed, including ambiguous-admission timeout cleanup and malformed-ledger fail-closed STOP persistence. Dispatch starts a new process group, kills it on callback timeout, marks submission ambiguity, and requires reconciliation rather than retry. The 5 full-aggregate fixtures passed. Generated reference/candidate launch shell and Python syntax checks passed. Static construction of both role wrappers passed `sh -n`, and their Slurm output directories resolved correctly.
- The current reference event for job 28373 is recorded `VALID`: 1,504 items, 1,200 correct, 13 invalid parses, 187 outputs ending at the generation limit, and zero service errors. Candidate job 28375 was still running at the time of this review, so this is not yet a paired quality result.

## Required before continuation

1. The source review permits creating `workflow/CODE_GUARD.json` now from final reviewed sources. The guard may hash `workflow/finite_event.py`, `workflow/test_finite_event.py`, `workflow/README.md`, and `admit_full.py` without self-reference; wrapper receipts should record the guard's own hash as implemented. Then rerun pre-admission guard and fixture checks.
2. The first-pair qualification file remains a required gate until candidate job 28375 completes and is reviewed. The fill script appropriately refuses to continue without a passing reviewed qualification.
3. Freeze and verify both `.pyc` files named in each candidate package's `SHA256SUMS` (`artifact_paths.cpython-39.pyc` and `warmup_semantic.cpython-312.pyc`). They are runtime checksum dependencies despite their `__pycache__` location. Include their exact hashes in the full-shard capture, as planned by the owner.

## Failure-containment review

1. **Resolved: timed-out admission cleanup.** `dispatch_fill()` now runs `admit_full.py` in its own process group and kills that group on timeout; `admit_full.cmd()` bounds scheduler CLI calls at 60 seconds and preserves ambiguous `sbatch` results without retry. The new fixture verifies process-group cleanup and ambiguity recording. A scheduler submission already accepted before timeout still requires manual reconciliation, as the code documents.
2. **Resolved: unexpected callback exceptions fail closed.** The CLI's outer exception handler attempts to persist immutable STOP, incident, and state records under the workflow lock; it reports an explicit persistence failure if that cannot be done. New fixtures verify malformed-ledger and unexpected validation exceptions both persist STOP and do not dispatch. Admission must remain stopped if persistence itself fails, which the callback enforces by returning nonzero and not attempting admission.

## Scope and limits

This review checked local code and fixtures only. It did not query Slurm, contact the model endpoint, authenticate, submit, cancel, or change the active source or frozen scientific payload. A code review cannot establish future cluster behavior; the first actual concurrency-64 reference/candidate pair still needs the separate elapsed-time, coverage, error, and response review required by the plan.
