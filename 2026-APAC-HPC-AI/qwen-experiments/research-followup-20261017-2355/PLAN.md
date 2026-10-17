# Submit the remaining H200 slots; retain the existing H100 queue

Prepared 17 October 2026, 23:55 UTC. This is a research-job submission, not an upload to the organisers.

## Why these two jobs?

The DeepGEMM prefill gain at N56 is independently confirmed: 2,715.842 and 2,716.787 good tokens/s, mean 2,716.315. N58 reached only 2,718.080 with higher first-token waiting. The earlier auto-runner load optimum need not remain optimal after changing prefill computation.

1. **DeepGEMM N54:** bracket the useful-load region from below while retaining the confirmed topology, chunk4096, graph-on, decode backends and full protocol. It changes only client concurrency from N56 to N54. Compare throughput and latency against N56/N58 operating points; use same-load auto-runner control 24189 for backend context, with time-drift caveats. A useful optimum requires independent confirmation. Do not increase to N60 automatically.
2. **DeepGEMM N56 with a separate post-measurement profile:** the old 24263 trace describes the earlier prefill backend. The new kernel choice warrants fresh diagnosis rather than assuming that the old ~43% MoE kernel share still applies. Preserve the full N56 score before profiling. Then run the exact existing diagnostic: 48 concurrent requests, four prefill steps, 32 decode steps, 4+4+8 expected rank traces. The prompt is separate from the benchmark dataset and seed. No profile traffic overlaps the scored window.

Both jobs use 16 H200 with a 17-minute allocation cap. Existing three Slurm jobs keep their queue positions; adding these two respects the five-job active cap. Both bundles retain all execution files from the confirmed DeepGEMM candidate except job exports for load or profiling. The diagnostic script, client and launcher are byte-identical to the previous audited profiler. The initial preparation check used an incorrect source anchor, failed before arming, and was corrected to the actual run_benchmark call; no GPU job was submitted by that failed check.

## Acceptance and interpretation

Require terminal sealed artifacts, exact frozen payload, intended runtime, full 60/120/30 benchmark, no request errors/cancellations, joint SLA at least 90%, short-output nonregression and 12/12 long retrieval checks. Keep all requests, including the initial burst. Official full-set accuracy remains unverified.

For profiling require nonzero kernel traces for all 16 ranks and inspect traffic success. Kernel fractions are shares of summed kernel durations, not shares of wall time or a predicted speedup. Equal diagnostic concurrency and capture counts do not guarantee identical batches or kernel shapes. Do not infer absolute phase speedups by comparing unequal work. Retain control warnings; do not repeat an allocation merely to remove harmless HTTP/JSON warnings when trace evidence is valid. Profile may be deferred if the bounded allocation lacks time; never sacrifice the scored protocol or silently drop output checks.

## H100 and credit

The three existing H100 jobs remain queued in their verified chain: 221181 (graph-off) → 221194 (prefetch repeat) → 221195 (control). No fourth PBS job is submitted.

The latest ledger as of 18 October 07:40:01 SGT reports Used **18,482.062 SU**, Balance **45,517.938 SU**, In Doubt **0**. The terminal charge for 221177, 869.262 SU, now reconciles with Used. Its old full reservation was released. Three pending jobs retain **4,608 SU maximum** total; headroom under the existing internal 51,000 SU planning limit is **27,909.938 SU**. No prepaid credit is deducted twice. These planning limits are not organiser quotas.

## Next action

Record the actual Slurm IDs from the existing non-AI watcher before reporting the two jobs as submitted. Use returned results and the existing graph/chunk tests to choose the next trial. Keep the invalid equal-TP8/EP2 branch closed. No new AI scheduling or official-submission promotion is enabled.

## Confirmed scheduler receipts

- **24428**: DeepGEMM prefill N54.
- **24429**: DeepGEMM N56 score followed by separate N48 profile.

Both were verified in the live Slurm queue with pending Resources state at 23:55 UTC. The own queue now contains five pending jobs.
