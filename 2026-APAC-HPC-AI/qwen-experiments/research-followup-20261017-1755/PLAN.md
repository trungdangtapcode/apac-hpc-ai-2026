# Equal-TP transport repair and prefill graph ablation

Prepared and submitted 17 October 2026, 17:50–17:54 UTC. Pending allocations are not benchmark results.

## New submissions

| Platform | Job | Hypothesis / change | Load | Maximum allocation |
|---|---|---|---:|---|
| H200 | 24375 | Repair equal-TP transfer using the exact previously validated TP8→TP8 patch | 56 | 16 GPUs, 17 minutes |
| H200 | 24376 | Disable CUDA graphs only in prefill; retain decode graphs and kernels | 56 | 16 GPUs, 17 minutes |
| H100 | 221181.pbs111 | Same prefill-only graph ablation, versus fresh control 221151 | 50 | 16 GPUs, 45 minutes |

H100 dependency chain is verified: prefetch 221153 → DeepGEMM readiness repair 221177 → graph ablation 221181. At most one 16-GPU PBS allocation runs at once. The existing non-AI Slurm watcher holds at most five active jobs. It submitted both new H200 bundles after shell and hash checks.

## What failed in job 24321

TP8/EP2 fixed the FP8 loading geometry: both workers became ready and ALL_WORKERS_READY was reported after 280 seconds. The single P/D warmup request then timed out after its bounded 480-second client wait. The job ended FAILED after 13:32, with an empty summary and no benchmark export. Later AbortReq/abort notifications are cancellation effects, not a demonstrated original root cause.

The submitted bundle reused the heterogeneous-TP NIXL patch (SHA256 912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f). Source inspection shows it retains whole-pool prepared descriptor setup for equal-TP paths. This layout is TP8→TP8, so it should have used the separate guarded equal-TP on-demand patch. Reusing the heterogeneous baseline was a preparation mistake. The process was not profiled during the stall, so descriptor setup as the sole cause is not directly established by this run.

The exact equal-TP patch (SHA256 e979738ef1681b793b09e3b81d2d4e4563535c1a354bf2e7ac76da14f73c856c) was previously GPU-validated in job 22809: every prefill rank logged skipped pool descriptors, workers were ready at 269 seconds and the P/D path was warm at 303 seconds. That older job used different serving settings and does not predict a new N56 result.

Re-ran the actual CPU equivalence test in an isolated copy: 936 byte-range cases and five fallback guards passed. Original artifacts were not modified. New job 24375 changes the transport patch and its associated metadata only relative to 24321. TP8/EP2, decode backends, load, full protocol, output checks, startup limits and model precision stay fixed. Require the exact patch hash and equal-TP activation on all eight prefill ranks. If it still fails warmup, preserve the failure and inspect its actual transfer path before another retry. Do not increase the client timeout blindly.

## Why test prefill CUDA graphs?

Exact staged server_args.py exposes --disable-prefill-cuda-graph and maps it only to the prefill graph backend. The decode phase has a separate switch. Actual control 24320 reported 106.51 seconds of prefill graph startup; DeepGEMM 24291 reported 144.91 seconds, and the failed H100 trial reported 161.62 seconds. These are engine startup diagnostics, not scored benchmark time.

The hypothesis is that bypassing prefill graph capture can reduce startup time and allocated GPU cost. It may also reduce scored throughput because graph replay saves launch overhead. Both outcomes must be measured. Each new ablation uses the auto prefill MoE backend of its fresh combo control; it is not combined with DeepGEMM. The only execution change is the prefill graph switch. Retain chunk4096, two TP4/EP1 prefills, TP8/EP8 decode, MNNVL, FlashInfer, dense decode graphs, model weights, KV precision and client protocol.

Compare H200 24376 with fresh N56 control 24320 and H100 221181 with fresh N50 control 221151. Loading time, filesystem cache, node and ordering can confound total startup savings, so inspect per-phase startup diagnostics as well as allocation walltime. A faster startup does not justify promoting a slower ranked configuration. Close the throughput branch on failed SLA or a material goodput loss; reserve startup-only conclusions separately. Require no request errors/cancellations, exact runtime activation, short-output nonregression and 12/12 long checks. A useful gain requires independent confirmation. Official full-set accuracy remains unverified.

## Budget and current queue

Fresh H100 ledger as of 18 October 01:40:02 SGT: used 17,075.200 SU, balance 46,924.800 SU, In Doubt 0. This turn adds a maximum 1,536 SU reservation. Total outstanding reservations for 221153, 221177 and 221181 are 4,608 SU. Headroom within the existing internal 51,000 SU planning limit after reservations is 29,316.800 SU. The 13,000 SU reserve and internal limit are planning buffers, not organiser restrictions.

H200 24322, 24327, 24352, 24375 and 24376 are pending at this snapshot. H100 221153 is queued; 221177 and 221181 have dependency holds. No new score is claimed. Do not promote pending configurations, resubmit the failed 24321 unchanged, or create new Codex scheduling. Existing AI autopilot remains disabled.

## Evidence

- Failed allocation: ../runs/24321/ (terminal manifest, worker logs and warmup timeout).
- Exact previous equal-TP patch and GPU validation: ../nixl-equal-ondemand/.
- Geometry rerun: equal-geometry-test.json; frozen bundle hashes: validation.json.
- Source of the graph switch: ../serving-tuning-10/next-evidence/staged-source/sgl-workspace/sglang/python/sglang/srt/server_args.py.
- H100 queue/ledger, upload, qsub receipt and verified dependency: files in this directory.
- Strict source-bound H200 reviewer: review-slurm.py. It returns WAITING for pending jobs and requires new terminal evidence before accepting results. H100 runtime review must also verify the prefill graph phase is disabled and decode settings retained; older MNNVL-only runtime proof is insufficient.
