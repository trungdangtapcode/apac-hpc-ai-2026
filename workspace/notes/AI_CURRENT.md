# Current AI / Qwen research handoff

Updated 2026-10-24T20:05:00Z. This GPU fork (`01a166eb-33cb-7ce0-9699-ec65de26689a`) continues the AI parent `01a15dd3-3094-7712-a991-8ce55b15cbfe`. It owns AI/Qwen only. The separate worker owns HPC/OpenFOAM. English artifacts, Vietnamese chat. No background Codex, schedules or automatic notification.

## Latest AI result and actual H200 queue

H200 full-protocol frontier remains **3,044.400475 good output tokens/s** at N64 (jobs 25366, 25373 and 25487; 60/120/30-second protocol). It has not increased. Official full-set accuracy ≥99% of the reference remains UNKNOWN.

The newly reviewed fast-default short pair **25947/25948** does not replace that frontier. Both used N64, 4,000/200 tokens, seed 2026, 20/40/30-second protocol, and 16 H200 GPUs:

| Job | Arm | Good output tokens/s | Joint latency success | Mean TTFT | Mean ITL | Finding |
|---|---|---:|---:|---:|---:|---|
| 25947 | Target-only control | 2,757.36 | 95.24% | 1,311.60 ms | 14.833 ms | Short-protocol control passed |
| 25948 | EAGLE3 on all workers | 2,443.00 | 83.49% | 2,631.95 ms | 7.820 ms | ITL improved; TTFT gate failed |

Both arms had zero profiled request errors/cancellations, 7/8 output sanity and 12/12 retrieval. The candidate increased raw output throughput 1.07% and lowered ITL 47.24%, but mean TTFT roughly doubled and good output throughput fell 11.40%. Job 25948 is terminal FAILED 1:0: its post-run checker had a control-review schema mismatch, and independent replay also confirmed the actual 83.49% SLA failure. The 20/40/30 screen cannot be ranked directly against the 60/120/30 incumbent. See [paired review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25947-25948-20261024/REVIEW.md).

## Current H200 job

**Job 25988 (S61 decode-only EAGLE3)** was actually submitted on 24 October at 20:04:27 UTC. At the 20:05:50 UTC query it was PENDING for Resources: two H200 nodes, 16 GPUs, 17-minute limit, no dependency. Two one-node jobs 25982/25983 from apacsc37 were RUNNING on g1/g4; the displayed pending queue placed 25988 above the other pending jobs, including APACSC01 jobs. Test-only IDs 25987 and 25985 are virtual and are not submitted jobs. A prior dry-run estimated 20:20:55 as a start time; that is a scheduler estimate, not a guarantee. [Definite receipt and root review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-decode-only-20261024/slurm-receipt.json).

S61 is based on a specific difference in retained native arguments: the full N64 target-only incumbent has speculative settings off on prefill and decode; S60 enabled EAGLE3 on both prefill workers and decode. S61 keeps prefill target-only and enables EAGLE3 only on decode. Its bounded gate is the same short N64 profile with zero errors/cancellations, at least 90% joint SLA, the 7/8 output-sanity floor, both P/D semantic paths and 12/12 retrieval. If it misses the SLA, close this EAGLE3 branch. This is a feasibility run, not an official score or quality evaluation. [Plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-decode-only-20261024/PLAN.md).

Three pre-admission guard attempts stopped before actual sbatch because of a review-path mismatch and two differences in Slurm test-only output handling. All were preserved and corrected before the definite job 25988 receipt; those attempts consumed no allocation. The submitted bundle and each completed review/receipt milestone were committed and pushed separately.

H100/PBS state has **not** been refreshed in this session. The latest prior observation was H100 job 224561 terminal; do not treat its old queue snapshot as live. The local VPN helper currently reports no live session. H200 Slurm admission does not spend PBS SU.

Latest H100/PBS credit record remains a dated admission-ledger snapshot, not a live balance: site label 24 October 22:20:02, used 47,327.78 SU, balance 16,330.887 SU, In Doubt 341.333 SU and conservative headroom 14,037.553 SU after retained maxima. The H200 Slurm job does not change that PBS ledger. [Ledger](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

## Earlier retained evidence

The sections below preserve the cache, topology, source corrections and failed runs that led to the current hypothesis. Their job states are historical unless a fresh scheduler query above confirms otherwise.

### Cache comparison and five-rank topology

Corrected FP8-KV screen **25920 completed 0:0** in 536 s. Fresh BF16 control **25863** and FP8 candidate use the same H200 N64 short 20/40/30-second protocol, fixed 4,000/200 tokens and seed 2026.

| Metric | BF16 control 25863 | FP8 candidate 25920 |
|---|---:|---:|
| Good output tokens/s | 2,796.146461 | 2,697.655265 |
| Requests meeting both latency limits | 95.283019% | 95.114007% |
| Profiling requests | 636 | 614 |
| Profiling errors / cancellations | 0 / 0 | 0 / 0 |

The FP8 result is **3.522390% lower**, so the prospective gain-above-1% condition is false. Do not repeat unchanged or run full confirmation. Both semantic paths, all 16 FP8 allocation records, the known 7/8 smoke floor and 12/12 retrieval checks pass. A failed pre-scoring warmup response is retained; zero errors above refers to profiling. Official accuracy remains unknown and KV scales remain source-inferred, not observed per layer. [Complete paired review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25920-20261024/README.md).

Sparse role metrics were inspected beyond the score. Sampled decode KV token occupancy peaked at 12% for BF16 and 6% for FP8; decode queue length was zero at captured instants. FP8 roughly doubles cache token capacity while the allocator still consumes a similar byte budget. This is not a VRAM reduction or proof of a causal bottleneck. The 5-second outer-client sampling envelope includes warmup, scoring and grace. Successful server polls use `server_http_status=200` with a `server_metrics` list; failed polls have `server_metrics_status=URLError`. Do not look for a nonexistent success value `ok`. Sixteen distinct, disjoint role GPU UUIDs were verified. [Paired server metrics](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25920-20261024/paired-server-metrics.json).

**25864 failed** before semantic/performance stages because our inherited checker insisted on BF16 despite all actual allocations being FP8. New S52 fixed only validation/storage-description metadata. That failed job is not a performance observation. Full dependent jobs **25875/25877 were cancelled pending** and supply no measurements. An expired terminal Slurm dependency rejected the first S52 submission; scheduler rejection was preserved and the independently passing control was replayed before actual submission 25920. [Failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25864-20261024/README.md), [correction and admission](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-kv-h200-screen-rank-fix-20261024/README.md).

## Five-rank topology: numerical prerequisite passed, complete startup still unproven

Native R3 primitive **224468 passed**, exit 0, 82 s. EP5/oracle relative L2 is 0.623731%, below the original 2% gate; EP5/EP1 is 0.232612%, copy-map error zero. Five virtual partitions ran serially on one H100. This proves neither five-GPU communication nor Qwen accuracy/performance. The source-corrected oracle includes native BF16 intermediate stores and FP8 requantization. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224468-20261024/README.md).

First H200 D5 **25921 failed before model loading** because our source-provenance metadata mistyped one SHA character. Direct extraction proves the retained source and immutable image match, with 12 other digests also matching. Pending H100 parent **224552 was cancelled before allocation** to avoid the same known error. Frozen parents remain unchanged. [Correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp5-source-hash-correction-20261024/README.md).

Corrected R2 **25923 failed 1:0 / 128 s** and **224553 failed exit 1 / 157 s**. Both prove five assigned unique GPUs, TP5/DP5 with attention TP1, EP5, 130 physical expert slots, 26 local slots and matching pre-load maps. Both then fail the LM head at **151936 is not divisible by 5**. No loaded weights, health pass, output, accuracy or score exists. Attention and expert partition checks were necessary but insufficient: the vocabulary is a third constraint. [H200 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25923-20261024/README.md), [H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224553-20261024/README.md).

New R3 uses the pinned runtime's native **`--enable-dp-lm-head`**, selecting the effective attention TP1 group for the LM head. It changes no vocabulary or model weights. All actual rank observers must verify that flag plus the previous map, loaded duplicate weights/scales, BF16 KV and health gates. This is a source-backed proposed correction, not an established GPU fix. [Explanation and source](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp5-lm-head-correction-20261024/README.md).

## Queue-order correction and preserved failures

During a queue adjustment intended to let the five-GPU probe fit before the long-waiting 16-GPU request, original **224466 became terminal** with no recorded allocation start/resources/exit status. `qrls` returned 35. The exact PBS transition cause is not established. Do not report 224466 as still queued or as a completed transport experiment. The new five-GPU job was released and actually ran. A separately sealed, same-experiment replacement **224554** was submitted after it and is now running. Original payloads, partial command audit, terminal query and conservative old maximum remain retained. [Audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp5-source-hash-correction-20261024/h100-r2-order-adjustment.json), [replacement](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-serial-init-r6-replacement-20261024/RESUBMISSION.md).

## EAGLE: keep token identity and benchmark quality separate

**25862 failed its strict exact-target-ID gate** after successful deterministic runtime, native geometry and both P/D semantic paths. Both candidate repeats are stable but all four differ from accepted deterministic target 25855. All 1,600 candidate IDs and native counters are retained. No official quality failure or pass follows from that diagnostic. Shape-dependent verification-versus-decode numerics are plausible, not proven. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25862-20261024/README.md).

A separate **unranked performance-feasibility pair S55/S56 is being prepared**. It preserves the exact-ID failure as a known limit and does not turn that gate into a pass. It would match target-only and EAGLE settings except speculation, retain runtime/geometry/semantic checks and the same smoke/retrieval floor, and record official quality as UNKNOWN. This revises our local experiment sequence transparently: collect performance feasibility separately while full task quality remains unresolved. No promotion or qualified speedup may follow from one pair. Check actual new receipts before claiming the pair is queued. [Prospective plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-unranked-performance-20261024/PLAN.md).

A frozen 128-question stratified public MMLU-Pro local-screen protocol is CPU prepared, **not run**. Exact tokenizer/template preflight and prompt fit remain unverified. It cannot certify the official full-set 99% requirement. An upstream checkout exceeded that preparation's 50 MB download cap; the overrun and cleanup are recorded, not hidden. [Protocol and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/mmlu-pro-local-quality-20261024/README.md).

## Credit, frontier and preservation

Latest admission-time AI report: **64,000 SU grant; 46,937.772 used; 17,062.228 balance; 0 In Doubt**, as of site label 24 October 21:20:08. It may lag the running allocation. Conservative headroom after all retained maxima is **15,131.561333 SU**; older terminal/cancelled reservations have not all been uniquely reconciled. Do not subtract In Doubt twice or treat a maximum as actual spend. The owner authorizes remaining H100 credit before their 30 October planning deadline; the account's separate expiration metadata is not reinterpreted. CPU project unchanged. Shared PBS cap 3, one running AI allocation, at most 16 GPUs/45 min; Slurm cap 5 and 17 min/job. Admission requires fresh CPU and AI queues under CPU-before-AI locks. [Ledger](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

Reproduced H200 N64 remains **3,044.400475 good output tokens/s** (25366/25373/25487). H100 N54 **2,433.019859** (222048) stays separate. Official full-set accuracy remains unverified; no global SOTA is claimed. Packaged primary remains N62 pending reviewed promotion. Submission, slides and HPC payloads were not changed this turn.

Edit active sources once, capture safe explicit checkpoints, verify, commit with actual dates and push promptly. Git stores safe sources/reports and external-object recovery manifests; large corpus bytes still require off-host artifact backup. [Learning journey](../reports/ai-research-learning-journey-20261023/README.md), [research journal](../reports/research-journey-20261019/journal/README.md), [previous handoff](history/20261024-ai-before-cache-result-and-dp-lm-head.md).
