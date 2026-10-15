# Attention-DP architecture pilot

Job **23780** was submitted2026-10-15, after verifying normal QoS allows five
pending/running jobs per user. It fills the fifth account slot alongside the
N53 repeat and three wave7 kernel experiments. Those jobs retain their IDs and
queue positions. This is a Qwen-only research deployment; it changes no contest
submission artifacts.

The [public history analysis](../research-public-slurm-2026-10-15/README.md)
identified a gap: our topology sweep and earlier DeepEP test did not enable
attention DP. Labels from another team motivated the hypothesis; their results
are unknown. The exact staged SGLang arguments explicitly support Qwen2/3 MoE
with DP attention, and its NIXL common connection code maps attention TP ranks
and attention DP ranks separately.

## Pilot23780

- Source: confirmed round-robin N52 bundle23576.
- Retain16 H200,8+8 P/D split, prefill2×TP4/EP1, decodeTP8/EP8 group on one node,
  official FP8 checkpoint, BF16 KV, round-robin prefill routing, chunk4096,
  decode graph list1–64, existing request-scoped NIXL patch.
- Decode flags: `--enable-dp-attention --dp-size 8 --moe-runner-backend deep_gemm
  --moe-a2a-backend deepep --deepep-mode low_latency
  --deepep-dispatcher-output-dtype fp8`.
- The decode attention group changes fromTP8 to eightDP groups with attentionTP1.
  Attention work is distributed by request; experts remain distributed across
  eight GPUs. These are not eight full235B model replicas.
- DP attention also changes engine scheduling/communication and disables the
  auto fused-allreduce path. This is an architecture-package comparison; any gain
  cannot be attributed to one kernel flag.
- Model, client and full60/120/30 benchmark remain unchanged at N52. Never copy
  the competitor's N128 load before establishing a passing latency point here.

## Validation and decisions

Frozen payload checksums, shell syntax and actual-image CLI fields pass.
Because attention TP changes4→1 across P/D, the CPU byte-mapping test covers
all eight physical decode DP GPUs, all four prefill head slices, and contiguous
and scattered token slots:96 cases match both the image's original descriptor
algorithm and an independently constructed expected source/destination mapping.
This proves descriptor geometry only, not GPU transport or output correctness.

The first run must provide complete measured exports and output diagnostics.
Compare against controls23576/23607 and current single-run best23616. SLA failures
remain valid negative measurements; a failed deployment remains incomplete.
Inspect effective DP/EP and transport metadata before attributing a speedup.

As in wave7, at least2% gain over both N52 controls with SLA≥90%, zero errors
and cancellations, and output research eligibility triggers one independent N52
repeat. Only a reproduced gain with SLA≥95% and mean ITL≤19.3ms triggers N54.
At most three deployments in this bounded wave, excluding recorded budget retries.
The shared active-plan limit is five pending/running jobs, including diagnostics.

Before selecting a contest candidate, require long-context output/transport
validation and organiser full-set accuracy. Eight-case sanity checks and CPU
geometry are insufficient for the99% accuracy gate. No promotion is automatic.

Next architecture branches are lossless EAGLE3, reconsidering12+4 P/D with
attention DP, and a separately validated vLLM baseline. These are research
priorities, not claimed measurements or already submitted jobs.

- [Prepared pilot](prepared-pilots.json)
- [CPU validation](cpu-validation.json)
- [KV geometry validation](geometry-validation.json)
- [Shared queue validation](controller-validation.json)
- [Automatic follow-ups](followup-plan.json)
- [Live results](../SERVING_TUNING_RESULTS.md)


## Completed pilot review, 2026-10-15 19:17 UTC

Job23780 completed with exit0 after10m18s. Its full60/120/30 N52 export
records2549.1966 good tokens/s,98.8708% SLA (1576/1594 requests), mean
ITL16.9623ms and TTFT596.4419ms, zero errors/cancellations. This is one
architecture-package observation; independent repeat23859 was
PENDING(Resources) at the19:17UTC check (historical). The existing2% repeat/N54 gates are unchanged.

Effective decode arguments confirm DP8/TP8/EP8, DP attention enabled,
DeepGEMM+DeepEP low_latency with FP8 dispatcher output, and fused allreduce
disabled. All eight DP ranks initialize NIXL UCX. The engine also automatically
adjusts decode-side chunked-prefill size8192→1024; the two prefill workers retain
chunk4096. Treat scheduling, expert dispatch precision and backend changes as a
package, with no individual kernel-speedup attribution.

Goodput exceeds fresh N52 control23607 by6.22% and repeated N53 job23773 by4.54%,
but trails MNNVL23778 by1.66%. Relative to23607, mean ITL falls2.57ms while
TTFT rises249.60ms. Eight-case output diagnostic remains7/8 with only the known
reverse failure; full organiser accuracy and long-context transport remain
unverified. No configuration is promoted to the contest submission.
[Independent export, runtime fields and source hashes](../nscc-pbs/inspection/wake-20261015-1915UTC/dpa8-review.json).

## Repeat runtime audit, 2026-10-15 22:07 UTC

23859 now RUNNING since22:02:26UTC. Frozen/submitted payload seals and actual
Slurm stored launcher pass;12operational files match23780, config differs only
experiment/purpose. Effective decode DP8/TP8/EP8, DeepEP and chunk1024 match;
no full export or smoke at22:06 snapshot. See [repeat review](REPEAT_REVIEW.md)
for exact existing N54 gate, matched table and final result checklist. No new
submission/controller change or performance result.
