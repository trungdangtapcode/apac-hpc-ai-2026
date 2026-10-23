# Prospective H100 EAGLE3 prefill geometry probe

## Question and hypothesis

The small NIXL registration probes show that buffers can be registered and
transferred, while the full-size serving path has not yet recorded the actual
KV region geometry passed to native registration. A single TP4 H100 EAGLE3
prefill can answer whether the production-sized target and draft allocations
produce a complete, stable four-rank registration inventory.

The hypothesis is that the existing uniform-eager-prefill readiness recipe
will reach native readiness while the derived observer records one before and
one after receipt for each of the four prefill ranks. The observer wraps the
existing native `register_buffer_to_engine()` call and leaves its arguments,
registration order, calls, and return value unchanged.

## Controlled run

The prospective PBS allocation is one node, four H100 GPUs, 56 CPUs, 940 GB
host memory, project `59010042`, normal queue, 20 minutes, with a hard startup
timeout of 1,100 seconds. The maximum charge ceiling is 170.666667 SU. No
reservation has been made and no job has been submitted.

The base is the verified single-prefill readiness job 223005. It keeps the
official FP8 target, pinned BF16 draft, TP4/EP1, 8,192 context, 4,096-token
prefill chunks, HPC-Ops, disabled prefill CUDA graphs, native NIXL, original
container, draft and graph-source checks, private writable `HOME` and `/tmp`,
and the tested CUDA library path. The only serving-code mount change is the
read-only derived NIXL module plus its read-only geometry helper. The expected
derived module SHA256 is
`45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8`.
The diagnostic sets the exact role `prefill-0` and creates a fresh experiment ID from the PBS job ID plus a random UUID at batch start. The ID is explicitly passed through the clean-environment container launch, verified by entry and receipt helpers, and stored in both the run directory and copied submitted context. The copied worker only adds explicit
cleanup for its existing background samplers and observer.

There is no decoder, router, explicit user-serving client or generation workload, AIPerf run, score, or cross-role transport test. The only health call is `/health`; the native health path may internally execute a token-level check.

## Acceptance gate

An accepted diagnostic needs HTTP 200 health, the server-ready marker, exact
native graph-source verification, four devices named H100 with Hopper
capability, the pinned draft digest, the derived NIXL digest, and resolved
runtime arguments matching the recorded TP4 EAGLE3 prefill recipe. Each of
TP0–TP3 must log two BF16 KV allocations, two disabled-prefill-graph messages,
and one NIXL initialization. No prefill graph capture or fatal runtime marker
may appear.

The independent receipt gate uses the shared strict field/value validator,
then requires exactly eight JSON files: before and successful after receipts
for `prefill-0`, engine ranks 0–3, PP rank 0, TP size 4. It rejects every extra
file, missing or duplicate phase, malformed value, failed registration,
identity mismatch, or geometry change across registration. The scheduler exit
code alone cannot make the diagnostic pass.

All deadlines derive from the same recorded T0 rather than from time after setup. The startup loop and container timeout share T0 + 1,100 seconds. The semantic checker has its own absolute T0 + 1,140-second bound. Cleanup starts before T0 + 1,170 seconds and is bounded: the worker TERM/KILLs and waits for its server, resource sampler, and locality observer, then the allocation wrapper terminates/reaps the timeout/container process. The design leaves at least 30 seconds before the 1,200-second allocation limit.

## Interpretation limits

This captures sanitized allocator/NIXL region lengths, memory kinds, layer and
head metadata, and arithmetic page geometry. It never serializes pointers.
Actual tensor dtype and tensor strides remain `not_collected`; the BF16 KV log
messages are a separate runtime observation. The reused helper's schema name
contains `h200` because it was derived and validated in the H200 proposal; this
prospective run itself is explicitly H100.

Instrumentation and receipt writes may add startup and shared-filesystem cost.
Those costs have not been measured. A successful result would establish only
single-prefill readiness and full-size registration geometry. It cannot prove
full P/D correctness, output equivalence, EAGLE3 speedup, scored latency, or the
competition's 99% reference-accuracy requirement.

## Source trail

- Base runtime and verified result: `../eagle3-prefill-graph-gate-20261021/REVIEW.md`
  and the retained evidence for job `223005.pbs111`.
- Native geometry derivation and strict value validator:
  `../eagle3-h200-geometry-20261022/PLAN.md`.
- Exact source and copied-file digests: `SOURCE_PROVENANCE.json` and
  `payload/SHA256SUMS`.
- CPU gates and shell syntax result: `validation.json`.

This directory is a mutable proposal for review. Freezing, uploading, budget
reservation, and submission are separate actions.
