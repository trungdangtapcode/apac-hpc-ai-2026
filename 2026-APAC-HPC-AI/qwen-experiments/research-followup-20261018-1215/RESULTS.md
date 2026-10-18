# Completed reviews and next hypotheses — 18 October 2026, 12:19 UTC

## Results that change the next experiment

| Platform / job | Configuration change | Good output tokens/s | Joint latency success | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
| H200 24528 | DeepGEMM prefill, chunk 6144, concurrency 56 | **2737.011** |98.9437%|720.378|16.477|
| H200 24529 | HPC-Ops prefill, chunk 4096, concurrency 56; decode unchanged |**2732.459**|98.9424%|715.071|16.531|
| H100 221276 | HPC-Ops decode, concurrency 52, chunk 4096 |**2314.735**|98.5537%|824.582|17.787|
| H100 221284 | HPC-Ops decode, concurrency 50, chunk 4096; profile after scoring |2309.229|98.6851%|664.620|17.848|
| H100 221285 | Same HPC-Ops decode at concurrency 50, prefill chunk 8192 |2251.931|98.3039%|835.922|17.443|

All five allocations finished with exit 0 and pass terminal seals, frozen payload hashes, full 60-second warmup / 120-second score / 30-second grace, intended runtime and layout, short-output nonregression and 12/12 long retrieval checks. No request errors/cancellations are accepted. Decode MNNVL and FlashInfer attention are verified on all eight ranks. The predeclared role-specific changes and inherited speculative runner fields are explicitly checked; speculative decoding remains disabled. Raw evidence and frozen reviewer JSON are retained beside this report. Official full-set accuracy at 99% of the reference evaluation score remains unverified.

Good output tokens/s is the exported rate of requests passing both latency limits multiplied by 200. Per-request limits remain TTFT ≤ 3,000 ms and mean ITL ≤ 20 ms, with at least 90% joint success and errors in the denominator. Table means alone do not establish that gate.

**H200:** chunk 6144 is **+0.7798%** versus fresh DeepGEMM chunk 4096 control 24526 (2715.832). HPC-Ops prefill is **+0.6122%** versus that same control. Both improve mean TTFT slightly, while mean ITL is similar/slightly higher. They are single observations; the size is small enough that replication and a fresh control are essential. Do not combine two provisional gains yet. The prior chunk 8192 peak 24425 (2722.281) is no longer the highest observation; its repeat 24527 (2718.692) still documents a much smaller chunk gain.

**H100:** concurrency 52 adds only **0.2384%** versus the newly scored N50 point 221284, while TTFT increases by about 160 ms. That is a load comparison, not an isolated backend gain. It is worth one independent repeat; no automatic N54. The review JSON also includes a descriptive comparison to the older N50 auto control 221262; its percentage mixes load and backend and must not be described as a same-load backend speedup.

The H100 chunk 8192 change **loses 2.4813%** versus the immediately preceding HPC-Ops N50 score 221284 and raises mean TTFT. Close this branch; do not repeat unchanged or transfer the tiny H200 chunk gain into a H100 prediction.

## What the new profile shows

The separate post-score diagnostic of 221284 contains **16 nonzero rank traces**, complete 4+4+8 coverage, and **371/371 successful requests**. It uses concurrency 48, four prefill and 32 decode capture steps. The profiler did not overlap scoring. Original traces, controller warnings, hashes and ranked kernel durations are in hpc-profile-kernels.json.

The two unchanged auto-runner prefills still show fused_moe_kernel at about 42.15%/41.71% of aggregated kernel duration, with explicit MoE sum/reduce kernels around 6.4% separately. That supports trying an alternative prefill MoE implementation. These named categories do not exhaust all MoE-related work.

Decode now contains real HPC-Ops group_gemm_blockwise_fp8 kernels (largest named kernel 23.39%), HPC activation/blockwise quantisation 7.04% and reduction 3.55%. FlashInfer paged attention is 16.33%; two leading MNNVL collectives contribute 11.68% and 11.29%. A per-token group quantisation kernel is 10.09%, but its ownership across dense and MoE paths is not established, so do not attribute all of it to MoE. These values aggregate summed durations across ranks, not wall time, and do not imply additive speedup opportunities. New kernel names make the old MoE-only name matcher incomplete; no claim of MoE disappearing or a direct phase-speedup comparison is made.

## Six new jobs: hypotheses, controls and stop rules

| Job | Trial | Reason / comparison |
|---|---|---|
| **24573** | H200 DeepGEMM chunk 6144, concurrency 56, independent repeat | Confirm provisional 0.78% gain; compare new 4096 control 24575 |
| **24574** | H200 HPC-Ops prefill chunk 4096, concurrency 56, independent repeat | Confirm provisional 0.61% gain; compare fresh DeepGEMM control 24575 |
| **24575** | H200 confirmed DeepGEMM chunk 4096, concurrency 56 | Detect time/node drift before interpreting sub-percent improvements |
| **221314.pbs111** | H100 replicated HPC-Ops decode, auto prefill, chunk 4096, concurrency 50 | Fresh score control; no repeated diagnostic capture |
| **221315.pbs111** | Same H100 configuration with HPC-Ops prefill added | Only prefill runner changes; compare 221314 directly. Prefill profile and passing H200 prefill trial motivate the test, not an assumption of hardware gain transfer |
| **221316.pbs111** | H100 HPC-Ops decode with auto prefill, concurrency 52 | Independent repeat of the small N52 advantage; compare fresh N50 control 221314 and prior N52. Do not combine the pending prefill change with the load trial |

The PBS chain 221314 → 221315 → 221316 was verified. Each 16 H100 / 45 minutes, maximum 1,536 SU, at most three active jobs and only one running allocation. Source worker preflight is retained for decode and added identically before model loading on the changed prefill role. Both HPC-Ops kernels must pass actual runtime and output gates; source compatibility alone is insufficient.

Existing H200 pending 24538 (HPC-Ops decode with DeepGEMM prefill) and 24544 (DeepGEMM chunk 8192 N58) retain their positions. The three new jobs bring the own queue to five active jobs; no sixth. Each 16 H200 / 17 minutes. Existing non-AI submission function invoked once under its lock; no background watcher or AI process started.

Require full terminal payload/runtime/protocol/latency/output gates for every new result. If a branch loses or produces backend/quality failure, retain evidence and do not retry unchanged. A useful small gain requires an independent repeat and fresh-control context; no official-script promotion from a single peak. N52 repeat must improve enough to justify extra TTFT before preferring it over N50; no automatic increase beyond 52. A passing prefill change still needs replication before adoption.

## Credit reconciliation

The four newly terminal PBS jobs 221275/221276/221284/221285 used 14:25/13:00/15:10/14:46. At 128 SU/GPU-hour for 16 GPUs, total **1,957.547 SU**, exactly matching the ledger increment within rounding. All old reservations are now reconciled and released.

Ledger as of 18 October 20:00:02 SGT: Used **24,030.436 SU**, Balance **39,969.564 SU**, In Doubt 0. New three-job chain reserves **4,608 SU maximum**. Headroom under the unchanged internal 51,000 SU planning cap after reservations is **22,361.564 SU**. The 13,000 SU project buffer is an internal planning choice, not an organiser quota. Never deduct prepayment twice. New reservations and each actual returned ID were saved under budget.lock; uncertain submissions must retain their reservations and never be blindly retried.

No slides, official job scripts, HPC_Task content or organiser upload changed. Codex autopilot remains disabled. Reviewers, frozen payloads, scheduler receipts, raw collected artifacts and profile analysis are preserved.
