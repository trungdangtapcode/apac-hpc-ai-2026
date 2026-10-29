# Current AI / Qwen handoff

Updated 2026-10-29T22:04:04.846938+07:00, Vietnam time (UTC+7). AI fork 01a166eb-33cb-7ce0-9699-ec65de26689a of parent 01a15dd3-3094-7712-a991-8ce55b15cbfe. Preserve the independent HPC worker, payloads, queue and budget. English artifacts; Vietnamese chat. No background Codex, schedules or automatic notifications.

## Actual queue and next decisions

Four full H200 jobs were admitted this turn. Cap64 job 27365 has already completed; the other three remain queued at the dated observation. Preserve their positions and own cap 5.

| Job | Hypothesis | Actual reviewed/observed state |
|---|---|---|
| 27365 | Decode running-request cap 256→64 | COMPLETED 0:0/11:43; full local pass, 3046.890454 good output tokens/s; +0.257879% versus 27270, below useful gate |
| 27376 | Fresh native control, prefill RadixCache | PENDING Resources |
| 27378 | Disable prefill radix prefix cache, require ChunkCache | PENDING Resources |
| 27383 | Real Qwen decode compile cap54 and startup proof before conditional N64 | PENDING Resources |

The actual queried queue is retained in [cap review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-cap64-20261029/RESULTS.md) and the admission records. Query fresh scheduler state before acting. Each full job is 16 H200/two nodes/17 minutes maximum, 4.533334 GPU-hours; no new PBS SU. No prior job was cancelled/requeued, no dependency chain or submit service created.

**27365 decision:** close unchanged cap64 sensitivity, with no 128 sweep or default/submission promotion. It has 1877/1903 good requests (98.633736%), zero errors/cancellations, 26 TTFT and zero ITL breaches, smoke 7/8 without regression and retrieval 12/12. Actual requested/final scheduler cap is 64; transfer/preallocation headroom remains separate. The request-map saving is only about 6 MiB per rank and the control did not demonstrate capacity pressure. The result is only +0.045606% over the separate prior native individual 26766, not an established optimization. [Complete measured result and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-cap64-20261029/RESULTS.md).

Cap64 decode mean GPU activity 95.833% is one idle sample at 0.161 seconds after first profiling-request start, with the other 23 samples at 100%; do not interpret this average as causal efficiency. Mean running requests 49.625, maximum 56, sampled queue zero, KV token usage 0.1146. All 72 server polls return HTTP 200 and no selected transport error/Python traceback is found. Sparse samples/uncalibrated host clocks/request-start envelope and missing hot-thread/Xid/throttle/kernel data limit interpretation. Engine random seeds vary across launches while workload seed remains 2026.

**27376/27378:** compare native RadixCache against prefill-only ChunkCache, retaining decode cap256/polling1 and all other factors. Pinned native factory and successful-transfer release lifecycle support the test. Require exact flags and actual cache class on all ranks, physical KV buffers, both semantic P/D routes and original raw/output gates. No cap64 combination. [Source, plan and definite receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/STATUS.md).

**27383:** enable compile only on decode, cap54 covering observed high-load shapes 50–54, while retaining ordinary full graph batches 1..64. Startup may not fit. The unchanged 600-second startup, 720-second warmup and 1020-second hard stop remain. Before any official client, require exact eight-rank current job/experiment/role/source-bound receipts, actual calls/captures for target shapes and per-rank Dynamo/FX/Inductor activity, plus original runtime/KV/semantic checks. Missing proof or timeout is a failed diagnostic, not a scored run. System sitecustomize is preserved; unsupported memory-saver mode is rejected. Independent raw receipt replay is required after measurement. [Plan, guards and acceptance](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-compile-full-20261029/STATUS.md).

Compare only complete local passes to fresh control 27376 once reviewed. Require >1% useful gain and acceptable tails before independent matched confirmation; otherwise close unchanged settings. No new optimum, official ranking or accuracy claim.

## Closed branches and retained evidence

Polling interval 1/2/4 full bracket is complete: 27270 = 3039.053386, 27272 = 3028.279635 (−0.354510%), 27274 = 3016.700285 (−0.735528%) good output tokens/s. All full local gates pass; differences are below 1% and each setting has one run. Keep interval 1 and close 2/4 without widening the sweep. [Final runtime/hardware/output/cost review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-transfer-poll-final-20261029/RESULTS.md). Actual engine seeds differ; configured workload seed2026 is separate, so no deterministic/causal claim.

Tiny compile observer 27340 completed 0:0/97 seconds on one H200. Shapes 1/52/64 all show compiler activity and PyTorch captures/replays inside prospective synthetic tolerances. It does not prove Qwen/HPC-Ops, distributed startup, accuracy or speed. Original 27338 remains FAILED before compilation due source-location introspection; both are sealed. Its positive fixture permits the actual production startup qualification above, not bypassing it. [Result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-compile-observer-probe-r2-20261029/RESULTS-27340.md).

Shallow EAGLE 27238 = 2971.628430, −2.080318% versus matched 26949; close that one-step/two-token arm. Continuous decode steps has no Python consumer in this pinned image and is closed. Earlier tokenizer/collective/chunk/load/graph/old-QK-RoPE/old-draft branches remain closed unchanged. Page16 primitives remain diagnostic, not full-model correctness acceptance; preserve exact page1 exceptions. [Detailed previous handoff](history/20261029-ai-before-final-four-job-handoff.md).

## Retained performance and scoring

| H200 observation | Good output tokens/s | Limit |
|---|---:|---|
| Historical N64 three-run mean | 3044.400475 | Retained baseline series |
| Native baseline individual 26766 | 3045.501509 | Retained baseline, not global optimum |
| Fresh control 27270 | 3039.053386 | Full local pass |
| Exploratory cap64 individual 27365 | 3046.890454 | +0.258%, no confirmed useful gain or promotion |
| Portable 27145 recovered raw | 3055.330517 | Original job FAILED after GPU client; readers fixed and later verified |

Official good output tokens/s = exported AIPerf Goodput requests/s × 200. Require TTFT ≤3000 ms and request-mean ITL ≤20 ms jointly on ≥90% of ALL requests including errors. Model accuracy ≥99% of reference remains UNKNOWN; local smoke/retrieval is not certification. Strict token-ID comparison failures 25797/25862 remain retained.

AIPerf defaults to client text tokenization here. Reported input3986/3987 and occasional output199 do not establish physical model truncation; actual generated IDs/authoritative per-request usage are uncollected. Do not redefine official multiplier200 or silently change frozen gates. [Source and beginner explanation](../tutorial/20-requested-and-reported-token-counts.md).

## Access, submission and preservation

Fresh existing H100 SSH helper at 22:01:51 Vietnam time on 29 October reports no live VPN session. No DUO prompt or auth-state change; PBS queues/current credit UNKNOWN. Historical 27 October project59010042 balance15686.158 SU is not live spendable credit. Owner removed discretionary buffers and uses 30 October planning deadline. Before qsub refresh both CPU/AI queues and selected-project credit under CPU-before-AI locks, combined cap3/max1 running AI. Prepared equal-TP R2 (8 H100/one node/30 minutes/max512 SU) remains unsubmitted.

This turn did not change published submission or slides, and preserved HPC. Last AI publication record is the compute-confirmed reader repair (ZIP SHA d3686c36a0262301f8733214740a44ebac4135eb514a831f5ea2ef87a31dd88e; all265 HPC files and whole PPTX preserved at that publication). It is a dated AI publication record, not an audit of concurrent HPC work. No organiser upload. [Repair record](ai-artifact-path-fix-20261029.md).

Preparation/admission checkpoints: 71e30c64/d4d1112d for cap64; 248a201d/7f3e4336 for cold-cache pair; 7874e9c4/3c8286d3 for compile qualification. Final polling review is captured in e3acdb31. Capture the cap64 final review/handoff next, verify and push promptly. Preserve frozen payloads, all failed/losing data and actual dates. Git stores recovery manifests but does not upload sibling external object bytes. No automatic mirror or background Codex.
