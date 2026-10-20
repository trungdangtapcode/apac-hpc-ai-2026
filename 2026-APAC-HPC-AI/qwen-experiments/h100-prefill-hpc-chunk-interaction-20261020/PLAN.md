# Missing H100 HPC-Ops prefill/chunk interaction

## Evidence and distinct question

Native dense-kernel screens now pass all numerical/source/activation gates but fail their predeclared useful-consistency criteria. Retain DeepGEMM at132 SMs; do not carry the isolated M54 QKV improvement into a model change. Close the tested Triton and96/120/80 scheduler-budget branches. The next comparison is independent of these micro settings.

The H100 incumbent uses two TP4/EP1 prefill workers and one TP8/EP8 decode worker, both MoE phases HPC-Ops, chunk4096, N54. The earlier h100-hpc-chunk8192-29 worker uses chunk8192 plus checkpoint prefetch for prefill but **no prefill MoE override**; only decode sets hpc_ops. A bounded scan of retained H100 configuration files found no both-HPC-Ops/chunk8192 candidate. That previous auto-prefill8192 loss does not answer this missing interaction. Preserve its negative result; do not relabel it as untested or erase it.

H200 evidence shows runner/batch-size interactions: DeepGEMM-prefill8192 plus HPC-Ops decode reproduces around2990 good output tokens/s. H200's separate HPC-Ops-prefill8192 pair is still queued. This motivates direct testing, not a hardware score conversion or assumed H100 speedup. Native HPC-Ops wrapper source documents fused blockwise FP8 gather/GEMM/activation/reduction on Hopper and the H20 tuning caveat. Previous successful H100 HPC-Ops-prefill4096 deployments establish support; the larger actual batch still needs runtime/memory/output validation.

Hypothesis: HPC-Ops benefits from a larger prefill work batch through its fused path sufficiently to improve fixed-load goodput. Counterhypothesis: larger batches increase first-token latency/memory pressure or make its Hopper scheduling worse. Do not diagnose a bottleneck from TTFT or mean GPU activity alone.

## Matched full-model pair

| Pilot | Prefill MoE | Prefill chunk | Decode | Load | Uniform sampler |
|---|---|---:|---|---:|---|
| h100-hpc-prefill-4096-n54-control-68 | HPC-Ops |4096| HPC-Ops, TP8/EP8 |54| On |
| h100-hpc-prefill-8192-n54-candidate-69 | HPC-Ops |8192| Identical |54| On |

Both derive from fully reviewed observed control222049's frozen bundle h100-hpc-n54-observer-on-58. The new control worker is byte-identical to it. Inverse-diff the candidate worker by8192→4096 and it is byte-identical to the control: **only prefill chunk changes**. Config and job labels reflect the pair. Benchmark, output checks, client timeout, 60-second warmup/120-second measure/30-second grace, synthetic4000/200 workload, telemetry, phase markers, separate diagnostic profiler, topology/NIXL patch, official FP8 checkpoint, BF16 KV, attention, decode graphs1–64, MNNVL, receive interval1, native dense auto/132 SM default and inference-mode policy stay unchanged. No native scheduler micro patch is deployed. Freeze both before submission; validate hashes, shell/Python syntax, inverse diff and all shared execution bytes.

## Review and decisions

Require terminal evidence seals/submitted hashes, intended runtime on every role/rank, full protocol, joint TTFT/ITL success>=90%, zero errors/cancellations, short-output nonregression and all12 long-context retrieval checks passing. A scheduler exit0 alone is not accepted. Retain failed/deferred results honestly. Validate source versus submitted config and runtime chunk values, HPC-Ops preflights, BF16 KV and unchanged decode paths. Existing reviewer must allow exactly4096→8192 for the candidate, not silently waive other runtime differences.

Compare only the equally observed fresh pair for the chunk effect. Historical observed222049 and unobserved222048/222179 remain context, not a substituted control or observer-overhead correction. Inspect all raw per-request tails/errors, admission/batch/KV logs and five-second hardware/server samples: disjoint UUIDs, phase coverage, GPU/memory activity, sampled VRAM, power/clocks, node CPU/memory/interfaces and whitelisted server metrics. Deduplicate node counters and retain uncalibrated cross-node clock/efficiency limits. Profiles are separate post-score diagnostics with expected16 rank traces; never count their traffic as scored work or summed kernel durations as wall-time shares.

A >=1% goodput gain with all local gates and useful latency tails warrants an independent controlled confirmation before adoption. Smaller effects remain inconclusive; a clear loss, SLA/error/output/runtime failure closes this exact interaction without an unchanged retry or blind chunk/load growth. This full-model comparison does not verify the organiser's >=99%-reference full-set accuracy. Keep H100 and H200 results separate.

## Bounded resource and submission

Two serial PBS jobs, each two8-H100 nodes/16 GPUs and at most45 minutes, maximum1536 SU each/3072 SU total. Submit control first, candidate afterany control; verify the dependency. No simultaneous allocation, cap three active PBS jobs. Fresh empty own queue and ledger under budget.lock; reconcile completed micro222279 only when published Used delta matches its estimated allocated-walltime charge, otherwise retain its entire maximum reservation in addition to3072. Stay below51000 SU campaign cap and retain13000 project buffer. Record definite receipts before/after each qsub; do not repeat uncertain submissions. Do not increase the budget or change scheduler policy.

H20024990/24928/24962/24964/24965 remain untouched and fill cap five. No official package edit, model weights copied, authentication restart, automatic background Codex or schedule.
