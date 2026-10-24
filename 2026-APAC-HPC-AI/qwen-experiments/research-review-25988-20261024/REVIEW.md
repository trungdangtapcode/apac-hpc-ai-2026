# Job 25988 review: EAGLE3 decode-only startup stopped at KV geometry validation

## Question and hypothesis

Job 25988 tested whether keeping both prefill workers target-only while enabling EAGLE3 only on the TP8 decode worker could recover TTFT relative to the earlier all-worker EAGLE3 short screen. The matched short control was job 25947. The expected performance outcome was not measured because the run stopped before the AIPerf client started.

## Exact run and terminal state

- Platform: two H200 nodes, 16 GPUs, Slurm partition `hpcai`.
- Bundle: `serving-tuning-10/s61-h200-eagle3-decode-only`; submitted 2026-10-24 20:04:27 UTC.
- Workload planned: N64, fixed 4,000 input and 200 output tokens, seed 2026, cold prefix cache, 20/40/30-second short protocol.
- Actual scheduler result: `FAILED`, exit code `1:0`, elapsed 6:15 of a 17-minute limit. The 16-GPU allocation ended before any AIPerf profile was created.
- This was a failed run, not a completed performance measurement. Goodput, TTFT, ITL, request fraction, request errors and output checks for the candidate are therefore **not measured**.

## What did run

The submitted bundle hash and copied payload are retained under `runs/25988/submitted-payload`. Preflight and the checksum-bound control review passed. All three model workers reached HTTP health 200 and emitted `worker_ready` markers. The independent candidate gates recorded:

- Draft fingerprint on decode-0: PASS, matching the reviewed Nebius EAGLE3 artifact revision.
- Runtime readiness: PASS. Both prefill workers were target-only with four BF16 KV and four NIXL rank records each; decode-0 had eight target BF16 and eight NIXL rank records, plus its draft KV registration records. Resolved fast defaults were collected.
- Worker startup: PASS for prefill-0, prefill-1 and decode-0.
- Semantic prefill/decode warmup: **not reached**.
- AIPerf: **not started**.
- Resource telemetry files and NIXL/KV geometry receipts were retained. No profiler was run.

## Failure and root cause

The fail-closed geometry checker stopped on a real role-specific layout difference. All 16 prefill before/after receipts had 188 KV regions per rank. All eight decode ranks had 190. The older checker used one constant (190) for every empty-layer-ID MHA receipt and therefore rejected target-only prefill geometry before P/D semantic warmup.

This is a checker defect, not evidence that the prefill KV allocation was malformed. The role-aware runtime report independently counted four BF16 KV and four NIXL records for each prefill TP4 worker, and eight target BF16 and eight NIXL records for the decode TP8 worker. The current raw geometry shows 188 target-model regions per rank and two additional decode-side draft regions per rank. Empty layer IDs remain an explicit observability limitation: the receipts do not establish semantic layer order.

The incorrect shared count is also explained by the previous comparison: S59 target-only had 188 regions across roles, while S60 placed EAGLE3 on all workers and used the 190-region expectation on all roles. S61 changed draft placement to decode-only, so a single shared count was no longer valid.

## Broader inspection

- Request errors and cancellations: not applicable; there was no AIPerf request profile.
- TTFT tail, ITL, queue/inflight behavior and goodput: not collected for a benchmark; no profile exists.
- Startup and role-specific model/KV state: inspected as above.
- GPU utilization, sampled VRAM series and kernel-time profiles: not inspected as performance evidence. The retained sampler records are available for later diagnostic review; they do not substitute for a profile.
- Cost: the reservation was 16 H200 GPUs for at most 17 minutes. The scheduler reports 6:15 elapsed. This is Slurm allocation time, not PBS SU.
- Official accuracy and the full-task 99% gate remain UNKNOWN.

## Assessment and next decision

The decode-only placement hypothesis remains untested. Preserve job 25988 as a validation failure and keep the 3,044.400475 good output tokens/s full-protocol H200 frontier unchanged. Refine the checker to validate the observed topology explicitly: 188 target-model regions for each target-only prefill rank, and 188 target plus two draft registrations for each EAGLE3 decode rank. Replay the corrected checker against the retained 32 raw receipts before submitting a fresh, separately frozen retry. Do not edit the submitted payload in place and do not infer a performance gain from readiness.

## Raw evidence

- Scheduler stdout/stderr: `runs/25988.out`, `runs/25988.err`.
- Frozen submitted payload: `runs/25988/submitted-payload/`.
- Runtime and draft receipts: `runs/25988/runtime-readiness.json`, `runs/25988/draft-worker-headcheck.json`.
- Raw KV geometry: `runs/25988/kv-geometry/` (32 before/after rank receipts).
- Worker, router and resource logs: remaining files under `runs/25988/`.
- Slurm accounting at review: batch `FAILED 1:0`, elapsed 00:06:15; steps 25988.1 through 25988.4 were cancelled by batch cleanup after the validator exited.

Full run artifact directory: `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/25988/`.
