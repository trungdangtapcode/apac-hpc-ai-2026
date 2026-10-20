# H100 placement evidence: local threads, asymmetric CPU envelopes

**222435.pbs111** passes sealed full local serving/runtime/output gates at **2413.341139 good output tokens/s**, joint SLA **98.416887%**, mean TTFT **719.763703 ms**, mean ITL **18.207979 ms**. This is a placement-observation baseline, not a new individual peak or official accuracy certification. Reported walltime 828 s corresponds to 471.040000 SU before posted-ledger reconciliation. [Per-job review](222435.pbs111-review.json), [sealed gates](222435.pbs111-gates.json).

All three one-time captures complete before the official client, with unambiguous namespace PID→GPU UUID mapping across **4/4/8 schedulers, 16 unique GPUs**, known PCI/sysfs locality and no truncation. All captured GPU-scheduler thread masks are **already NUMA-local**. The one-GPU static mismatch did not establish that full-serving workers were remotely bound; this actual observation corrects that interpretation. There is no evidence here that native SGLang needs its NUMA binding disabled.

| Worker group | Launch CPU mask | Actual scheduler CPU masks | Shared local CPU IDs |
|---|---|---|---:|
| Prefill0, four NUMA0 GPUs |0–31 |0–31 |32 |
| Prefill1, four NUMA1 GPUs |32–63 |56–63 |8 |
| Decode NUMA0, four GPUs |0–63 |0–55 |56 |
| Decode NUMA1, four GPUs |0–63 |56–63 |8 |

These are **logical CPU ID counts**, not a measured CPU utilisation or a verified physical-core count on this allocation. Native SGLang intersects the outer task mask with GPU-local CPUs, explaining why a 32–63 launcher does not imply remote GPU scheduling. Eight local CPU IDs are shared by four scheduler processes in the affected groups. Prefill GPU-worker threads total 561 at mask 0–31 versus 369 at 56–63; decode threads 713 at 0–55 and 324 at 56–63. Many threads can sleep; counts do not prove contention. Observer capture durations are 0.426/0.413/0.457 seconds for the two prefills/decode, outside scored traffic. [Exact process/UUID/mask tables](locality-review.json).

The wrapper's ordinal CPU slicing is a plausible cause of the envelope asymmetry: it chooses available[offset×8 : offset×8+requested], without GPU PCI locality. This is a hypothesis about an actionable setting, not a causal performance bottleneck claim. Host averages and near 100% sampled GPU activity do not resolve CPU launch stalls, memory-bandwidth limits or the scored critical path. Scored per-thread demand and host memory placement are not collected.

## Next controlled experiment

Keep the same total 32/64 logical CPU budget per prefill/decode task, native per-GPU NUMA binding, official FP8 target, GPU layout, kernels, context, N54, full benchmark and all observers. Compare a replay of the legacy envelope with a deterministic envelope assembled from GPU-local CPU partitions, using actual CUDA UUIDs matched to NVML PCI locality and the real scheduler-allowed mask. Do not assume CUDA and NVML ordinals match, request CPUs outside the allocation, pin host memory or disable native NUMA binding. Prefer one allowed hardware thread per core when the actual lscpu mapping provides enough; record the selected IDs and fallback/failure. Compute both envelope options in the common prelaunch helper and keep metadata-query overhead identical in the pair.

A positive outcome needs full local protocol/runtime/output gates, no errors/cancellations, intended and complete worker mapping changes, and a useful goodput improvement against the matched new control. A single pair remains provisional; only a useful valid signal warrants an independent confirmation. If available local CPUs are insufficient, fail before loading weights; if the helper/common infrastructure fails, diagnose instead of unchanged repeats. Locality being correct does not imply load is evenly provisioned, and a more symmetric envelope does not guarantee speedup.

## Other inspection and limitations

[Full raw tails/role logs and 16 sealed post-score traces](222435.pbs111-inspection.json), [scored server gauges](222435.pbs111-server-state.json) and [hardware sampling](222435-resources.json) are retained separately. Resource samples cover 16 unique UUIDs and 25/24/24 scored samples for decode/prefill0/prefill1. Inspect these as five-second samples, not exact peaks or causal kernel shares. Profiles are outside the ranked interval and retain known stop_profile HTTP 500; missing inflight/per-thread-demand/memory-placement fields stay uncollected. Request errors and 12/12 long-context checks pass; local short-output eligibility remains distinct from organiser quality evaluation.

The copied reviewer successfully wrote the per-job PASS, then its generic pair-summary tail failed on this single-pilot experiment. [Local bookkeeping correction](REPORT_TAIL_CORRECTION.md) preserves the first stderr, fixes the role/length guard and separates serving summaries from predeclared cost gates. CPU fixtures execute only that summary tail; the immutable per-job review SHA remains unchanged. This is not a failed model or an excuse to count an unvalidated run as passing.

The header-only EAGLE3 source work now identifies a gateway token-ID interface for non-streaming diagnostics, but its actual runtime/draft/P-D/greedy equivalence remains separate work. H200's five pending jobs preserve their positions. Neither this H100 observation nor its possible CPU benefit is transferred numerically to H200. No new binding or speculative GPU submission is implied by writing this review.
