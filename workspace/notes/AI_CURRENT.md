# Current AI / Qwen handoff

Updated 29 October 2026, 21:33:55 Vietnam time (UTC+7). AI fork `01a166eb-33cb-7ce0-9699-ec65de26689a` of parent `01a15dd3-3094-7712-a991-8ce55b15cbfe`. Preserve the independent HPC worker and its payloads, queue and budget. English artifacts; Vietnamese chat. No background Codex or schedules.

## Current work

**27365 is actually submitted**: one exploratory full N64 trial changes decode running-request cap 256→64, with separate transfer/preallocation headroom and all graph/model/workload/output gates retained. Maximum 16 H200, two nodes, 17 minutes, 4.533334 GPU-hours, no PBS SU. Low expected upside: only about 6 MiB request-map reduction per decode GPU and no demonstrated queue/memory pressure. No automatic 128 sweep. Require actual requested and final scheduler cap 64. [Receipt and exact plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-cap64-20261029/STATUS.md). Source/configuration is captured in 71e30c64; receipt backup follows promptly.

**27340 completed 0:0 in 97 seconds**, a positive one-H200 tiny BF16 compile observer/PyTorch graph fixture. Batch shapes 1/52/64 each show positive Dynamo graphs and Inductor kernels, with successful captures/replays and prospective synthetic numerical checks. It does NOT prove Qwen/HPC-Ops, eight-rank startup, performance or official accuracy. Original 27338 remains FAILED before compilation due the contextmanager source-location bug. [Actual prerequisite result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-compile-observer-probe-r2-20261029/RESULTS-27340.md). A source-pinned real-model compile observer/startup gate is being prepared independently before any scored compile client; default compile cap32 misses observed high-load shapes, and cap54 startup fit is still unknown.

**27274 completed 0:0 in 11:34** at 3016.700285 good output tokens/s (1861/1887 good, 98.622152%, zero errors/cancellations, smoke7/8 and retrieval12/12). Independent full local checker passes; full beyond-score review is finishing. Interval 4 loses versus fresh interval 1 control 27270=3039.053386 and joins interval 2's 3028.279635 loss. Close unchanged polling intervals 2/4 after final evidence review; no automatic extra sweep. Earlier pending and combined node-reason snapshots are historical, not live outage claims.

A distinct source review of disabling prefill radix prefix caching under the unchanged cold workload is underway. Actual control prefills initialize RadixCache on all four ranks each, while decode uses ChunkCache on all eight. This lead is independent of the pending compile work and must establish real flag/cache-class selection and native P/D safety before admission. Preserve own cap5 and queue positions. Full jobs retain 16 H200/two nodes/17 minutes; no blind duplicates or repeated losing settings.

The existing H100 SSH helper this turn reports no live VPN session. No DUO prompt or qsub; both queues and current credit UNKNOWN. The historical grant/balance below is not live spendable credit. This does not block authorised H200 work.

New token-accounting source review confirms AIPerf uses local text tokenization rather than server usage. Raw input counts3986/3987 and a few reported199 output counts do not prove physical truncation; exact per-row cause is unknown without actual IDs/authoritative usage. Canonical requested4000/200 configuration and official Goodput×200 formula remain. [Source and tutorial](../tutorial/20-requested-and-reported-token-counts.md). Preserve the new failed exact-count diagnostic separately from original prospective protocol gates.

The shallow EAGLE 27238 full local pass lost2.080318% against matched26949; that exact one-step/two-token setting is closed. Continuous decode steps has no Python consumer in the pinned image and is closed. Earlier graph/admission tests concerned prefill limits; this new decode cap64 arm is distinct. [Prior detailed handoff](history/20261029-ai-before-cap64-and-compile-positive.md).

## Retained results and delivery

| H200 observation | Good output tokens/s | Interpretation |
|---|---:|---|
| Historical 25366/25373/25487 mean | 3044.400475 | Three full local passes |
| Native 26766 | 3045.501509 | Retained best reproduced native individual |
| Fresh full control 26949 | 3034.761104 | Matched control for newest arms |
| Tokenizer 200µs 26951 / 2ms 26953 | 3040.591887 / 3042.963988 | +0.192% / +0.270%; close unchanged |
| FlashInfer prefill 27077 | 2841.004107 | −6.385%; retain FA3 |
| Prefill MNNVL 27138 | 3038.093484 | +0.109807%; close unchanged |
| Portable 27136 recovered raw | 3050.225487 | Original job FAILED 1:0 |
| Portable 27145 recovered raw | 3055.330517 | Original job FAILED 1:0; fixed readers confirmed on compute |
| Shallow EAGLE 27238 | 2971.628430 | −2.080318%; close unchanged |
| Fresh polling control 27270 | 3039.053386 | Full local pass |
| Polling interval 2, 27272 | 3028.279635 | −0.354510%; close unchanged |

Actual **27152 completed 0:0 in 3 seconds on compute g1, using zero GPUs**. It reproduces the old mount-alias exception, then both corrected postprocessors pass both retained real datasets. This proves the reader tail on compute, not a new single-allocation GPU success. Original 27136 and 27145 remain FAILED. Their recovered raw observations are not retroactively successful original jobs. Portable allocations did not collect separate smoke/retrieval or hardware time series. Actual prerequisite 27153 completed 0:0 in 72 seconds on one H200: native argument resolution only, without model or distributed inference. [Compute result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-postprocess-compute-check-20261029/RESULTS.md).

The team folder and ZIP contain both reader fixes and positive compute evidence. Current ZIP SHA256 is **d3686c36a0262301f8733214740a44ebac4135eb514a831f5ea2ef87a31dd88e**, 78,621,011 bytes. All 265 HPC files, modes, ZIP attributes and complete PPTX bytes are unchanged. Slides remain the 28 October delivery; no organiser upload. [Repair record](ai-artifact-path-fix-20261029.md). Older pending labels and ZIP hashes are historical.

Good output tokens/s = raw AIPerf Goodput requests/s × 200. Joint SLA requires TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms for at least 90% of ALL requests, including errors. Official accuracy ≥99% of reference remains UNKNOWN; local output checks do not prove it. Strict token-ID failures 25797/25862 are retained. Small recovered gains are not established optimizations.

Larger chunks 10240/12288, N62/N66, graph/admission tuning, old QK/RoPE fusion and the old two-step/three-token draft are closed unchanged. Page diagnostics 27075/27141 completed constructed cases but did not pass all strict numerical criteria. Identical page1/page16 pairs do not qualify full-model page16 transfer; actual role metadata and native P/D proof remain prerequisites. Preserve exact existing exceptions. [Detailed prior snapshot](history/20261029-ai-before-shallow-full-handoff.md).

## H100 access and preservation

The existing SSH helper at about 16:03 Vietnam time on 29 October reports no live VPN session. No DUO prompt or authentication change occurred. Both PBS queues and current credit are UNKNOWN. Historical 27 October project 59010042 balance 15686.158 SU is not a live spendable balance. The owner removed discretionary buffers and uses 30 October as the planning deadline. Before qsub, refresh both CPU/AI queues and selected-project credit under CPU-before-AI locks; combined cap 3 and at most one running AI. Prepared equal-TP R2, 8 H100/one node/30 minutes/max 512 SU, is unsubmitted. H100 results 222048 = 2433.019859 and 225227 = 2399.186728 are separate-platform measurements.

Completed safe checkpoints: 2f21dbd4 for S98 admission, 166dc684 for actual prerequisites, and 30f438eb for the compute-confirmed publication. The full shallow loss and journal are captured in 066f282e; polling source/configuration/fixtures are captured in 9ba8aaf2. Actual three-job admission is captured in 5fe8c648. The pair review is captured in 522c336a. Pinned source findings and the token-count tutorial are captured in b6b8b12b; the frozen observer prerequisite is captured in 924dd6ce. Actual first-probe admission is captured in 88a50c71; its source-location failure is captured in eddd84d5 and the derived source fix in 21b03713. Actual corrected admission is captured in 53fd4996; later terminal/admission milestones follow separately. Commit and push small explicit selections with actual dates; preserve frozen payloads and original failures. Git stores recovery manifests but does not upload sibling external object bytes. [Research journal](../reports/research-journey-20261019/journal/README.md).
