# Current AI / Qwen handoff

Updated 29 October 2026, 13:05 Vietnam time (UTC+7). AI fork `01a166eb-33cb-7ce0-9699-ec65de26689a` of parent `01a15dd3-3094-7712-a991-8ce55b15cbfe`. Preserve the independent HPC worker and its payloads, queue and budget. English artifacts; Vietnamese chat. No background Codex or schedules.

## Current work

At 12:57:34 Vietnam time on 29 October, the actual own Slurm queue is empty. **27238 completed 0:0 in 13:12 on g1/g4**. Its full shallow EAGLE3 trial passes independent raw, runtime, KV, semantic-route and local output gates, but loses **2.080318%** to matched target-only control 26949. Close this unchanged setting. [Full result and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-shallow-eagle-full-20261029/RESULTS.md).

S98 enables EAGLE3 only on decode: one step, top-k 1, two draft tokens, unquantized BF16 draft. The control retains P4+P4 / D8 with TP8/EP8, DeepGEMM prefill chunk 8192 and breakable graphs, HPC-Ops/FlashInfer/MNNVL decode, full decode graphs 1..64, FP8 target weights, BF16 activation and KV, page size 1 and tokenizer batching off. Workload is fixed N64, cold 4000/200 tokens, seed 2026 and full 60/120/30 seconds. Actual receipts confirm 188 prefill and 190 decode KV regions across all 16 ranks. The existing page1 missing-head exception is unchanged; explicit layer identity and decode head counts remain uncollected.

The result is **2971.628430 good output tokens/s**, 1825/1851 good requests (98.595354%), zero errors/cancellations, 26 TTFT and zero ITL breaches, smoke 7/8 and retrieval 12/12. Mean/p95 ITL worsens from 14.979/15.147 to 15.776/17.084 ms; TTFT improves from 1128/1423 to 1056/1386 ms. Sparse decode samples show 52.25 mean running requests, zero queued, 0.12 KV token usage, 93.76% GPU activity and 131.875 GiB VRAM per GPU. All 72 server polls return HTTP 200. Unweighted displayed draft acceptance averages 1.2464 over 196 log entries with at least 48 running requests; these include warmup and profiling and are not token weighted. No heavy kernel profile or exact generated token IDs were collected. Allocation occupancy is 3.52 GPU-hours, versus a maximum reservation of 4.533334; no PBS SU.

The complete pinned SGLang Python package declares continuous decode steps but has no consumer; the active overlapping decode loop does not read it. Close that lead for this image. [Source report](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-continuous-decode-source-20261028/followup-20261029/REPORT.md). A distinct transfer/admission source investigation is underway, informed by roughly 12 in-transfer requests and no sampled decode queue. Do not repeat the historical receive-worker-count 2 loss unchanged. Source review is not submission. Preserve cap 5; full serving jobs use 16 H200, two nodes and 17 minutes. Check the actual queue and required gates before admission.

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

Actual **27152 completed 0:0 in 3 seconds on compute g1, using zero GPUs**. It reproduces the old mount-alias exception, then both corrected postprocessors pass both retained real datasets. This proves the reader tail on compute, not a new single-allocation GPU success. Original 27136 and 27145 remain FAILED. Their recovered raw observations are not retroactively successful original jobs. Portable allocations did not collect separate smoke/retrieval or hardware time series. Actual prerequisite 27153 completed 0:0 in 72 seconds on one H200: native argument resolution only, without model or distributed inference. [Compute result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-postprocess-compute-check-20261029/RESULTS.md).

The team folder and ZIP contain both reader fixes and positive compute evidence. Current ZIP SHA256 is **d3686c36a0262301f8733214740a44ebac4135eb514a831f5ea2ef87a31dd88e**, 78,621,011 bytes. All 265 HPC files, modes, ZIP attributes and complete PPTX bytes are unchanged. Slides remain the 28 October delivery; no organiser upload. [Repair record](ai-artifact-path-fix-20261029.md). Older pending labels and ZIP hashes are historical.

Good output tokens/s = raw AIPerf Goodput requests/s × 200. Joint SLA requires TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms for at least 90% of ALL requests, including errors. Official accuracy ≥99% of reference remains UNKNOWN; local output checks do not prove it. Strict token-ID failures 25797/25862 are retained. Small recovered gains are not established optimizations.

Larger chunks 10240/12288, N62/N66, graph/admission tuning, old QK/RoPE fusion and the old two-step/three-token draft are closed unchanged. Page diagnostics 27075/27141 completed constructed cases but did not pass all strict numerical criteria. Identical page1/page16 pairs do not qualify full-model page16 transfer; actual role metadata and native P/D proof remain prerequisites. Preserve exact existing exceptions. [Detailed prior snapshot](history/20261029-ai-before-shallow-full-handoff.md).

## H100 access and preservation

The existing SSH helper at about 12:59 Vietnam time on 29 October reports no live VPN session. No DUO prompt or authentication change occurred. Both PBS queues and current credit are UNKNOWN. Historical 27 October project 59010042 balance 15686.158 SU is not a live spendable balance. The owner removed discretionary buffers and uses 30 October as the planning deadline. Before qsub, refresh both CPU/AI queues and selected-project credit under CPU-before-AI locks; combined cap 3 and at most one running AI. Prepared equal-TP R2, 8 H100/one node/30 minutes/max 512 SU, is unsubmitted. H100 results 222048 = 2433.019859 and 225227 = 2399.186728 are separate-platform measurements.

Completed safe checkpoints: 2f21dbd4 for S98 admission, 166dc684 for actual prerequisites, and 30f438eb for the compute-confirmed publication. Capture the current result and journal next. Commit and push small explicit selections with actual dates; preserve frozen payloads and original failures. Git stores recovery manifests but does not upload sibling external object bytes. [Research journal](../reports/research-journey-20261019/journal/README.md).
