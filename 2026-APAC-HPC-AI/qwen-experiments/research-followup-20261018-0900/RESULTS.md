# Progress and next controlled trials — 18 October 2026, 08:56 UTC

## A promising H100 decode result

Job **221263.pbs111** reaches **2,308.308 good output tokens/s**, compared with the immediately preceding matched control **221262.pbs111** at **2,245.534**: **+2.7955%**. Both use concurrency 50, the same prefill weight prefetch, complete native FP8 checkpoint, BF16 key/value cache, routing, topology, transport patch and full benchmark. Only the decode MoE runner changes from auto to HPC-Ops. Prefill remains on the auto runner. The inherited speculative runner setting follows the main runner, but speculative decoding remains disabled.

| Metric | Fresh control 221262 | HPC-Ops decode 221263 |
|---|---:|---:|
| Good output tokens/s, higher is better | 2,245.534 | 2,308.308 |
| Joint latency success, at least 90% required | 98.5075% | 98.7526% |
| Mean time to first token (ms), lower is better | 457.898 | 678.908 |
| Mean inter-token latency (ms), lower is better | 19.448 | 17.804 |

This trades higher first-token waiting for faster token generation and greater qualifying throughput. Mean latency alone does not prove the joint gate: each qualifying request must satisfy TTFT at most 3,000 ms and its own mean ITL at most 20 ms. Errors remain in the denominator. Good output throughput is the exported qualifying request rate multiplied by 200 tokens.

Both allocations finished with exit 0. Review checks terminal evidence seals, exact predeclared payload hashes, full 60-second warmup / 120-second scoring / 30-second grace, no errors/cancellations, short-output nonregression and all 12 long retrieval checks. Runtime logs verify all three roles, BF16 cache, unchanged TP/EP layout, all eight decode ranks' MNNVL and FlashInfer attention, HPC-Ops preflight and exactly the intended runner change. See the frozen `*-gates.json` and `*-review.json` files beside this report. This is one matched observation; independent replication is pending. Organiser full-set accuracy at 99% of reference evaluation score remains unverified.

## H200 control and remaining work

Fresh DeepGEMM chunk 4096 control **24526** passes full local review at **2,715.832 good tokens/s**, joint SLA **98.8201%**, mean TTFT **751.280 ms**, mean ITL **16.443 ms**. It matches the previous stable controls. The provisional peak remains job 24425 at 2,722.281 with chunk 8192; the approximately 0.20% gain is not independently confirmed.

Jobs 24527 (chunk 8192 repeat), 24528 (chunk 6144) and24529 (HPC-Ops prefill) remain pending. Keep their queue positions. Their results are required before promoting a larger chunk or the prefill backend. No failed graph-off branch is reopened.

## H100 profile is valid

Control 221262 has **16 nonzero rank traces** covering 4+4+8 ranks, and **360/360 successful diagnostic requests**. The diagnostic runs after scoring at concurrency 48, four prefill / 32 decode capture steps; it is not ranked or mixed into score. The PBS model-path portability fix works.

The corrected classifier gives MoE-associated shares of **42.72% / 42.38%** in the two prefill groups and **28.31%** in decode. Collective shares are **21.95% / 22.67%** in prefill and **24.31%** in decode. These are shares of summed kernel duration, not wall time or predicted speedups. Batch/shape differences prevent causal phase comparisons with H200. The decode MoE share supports investigating an alternative MoE implementation; the measured full score, not an Amdahl extrapolation, determines whether it helps. See h100-profile.json and review-h100-profile.py. Original traces and controller warnings are preserved.

## Submitted followups

| Platform | Job | Change and hypothesis |
|---|---|---|
| H100 | **221274.pbs111** | Independent HPC-Ops decode repeat at concurrency 50; confirm the observed gain |
| H100 | **221275.pbs111** | Fresh auto decode control at concurrency 50; same prefetch and no diagnostic profile |
| H100 | **221276.pbs111** | HPC-Ops decode at concurrency 52; test whether lower ITL permits a better operating point |
| H200 | **24538** | HPC-Ops decode only with the confirmed DeepGEMM prefill, chunk 4096, concurrency 56; compare fresh 24526 |

The PBS jobs form a verified strict afterany chain, at most one 16-GPU allocation running, three pending/running jobs maximum. Each retains a 45-minute cap. N52 is one bounded operating-point trial after N50 has passed all local gates; no automatic N54. Require exact runtime differences, full protocol and output quality for every result. A runner, SLA or output failure closes the affected branch; do not repeat unchanged just to fill the queue. Do not transfer H100 gains into H200 predictions: 24538 measures the effect on H200 directly. It does not combine the pending HPC-Ops prefill trial with the new decode runner.

New bundles preserve scoring, output checks and transport payload byte for byte from their source. The profile-only switch is disabled on the fresh H100 score control to avoid collecting another identical diagnostic after scoring. HPC-Ops early GPU checks remain present on the changed role. Frozen file hashes and shell/Python syntax validation are in next-validation.json. The existing non-AI Slurm submission function ran once under its lock and recorded 24538 in the registry; no background Codex, schedule or watcher was started.

## Cost

The previous H100 pair used walltimes **13:56** and **13:10**, together **925.013 SU** at 128 SU/GPU-hour for 16 GPUs. This exactly reconciles the ledger increment within rounding. Their old reservations are released. Fresh ledger as of 18 October 16:40:02 SGT: grant 64,000 SU, Used **21,580.231 SU**, Balance **42,419.769 SU**, In Doubt 0.

The new three-job batch reserves at most **4,608 SU**. Remaining headroom under the unchanged internal 51,000 SU planning cap is **24,811.769 SU**. The retained 13,000 SU buffer is our planning choice, not an organiser quota. Do not subtract any In Doubt prepayment twice. Before another qsub, refresh scheduler/credit and reconcile under budget.lock. Never retry an uncertain submission.

## Reports

The all-history metric report was regenerated with the new observed record holders, full metric units and job configuration cards. The top results are separated by GPU platform; neither plot nor report applies the old frozen calibration to this new backend. The previous presentation remains a dated snapshot and was not changed. No official-script promotion, HPC_Task content or organiser upload occurred.
