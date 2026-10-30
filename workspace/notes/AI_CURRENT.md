# Current AI / Qwen handoff

**Presenter learning guides:** [bilingual transcripts for all 40 slides](ai-bilingual-transcripts-20261030.md), now with a 10–20 second spoken brief before every slide's purpose. Briefs explain the main point, standout result and necessary terms, including what repeated measurements mean. Detailed technical explanations remain below. The Vietnamese companion remains a narrow requested exception; deck and HPC payloads are unchanged.

**Hardware reminders:** every transcript slide now starts with H200/Firmus, H100/NSCC, shared/mixed evidence, or CPU attribution. Slides 16–18 are H100; the approximately 3044-good-token/s series is H200. Mixed slides 19/20/26/27/31 also identify each result's platform. This is a guide update, not a new measurement or deck change.

**Latest presentation:** [journey coverage and panel preparation](ai-journey-presentation-20261030.md), following the owner’s 15–20 minute AI allowance. No research resumed.

**Final report and delivery:** [30 October update](ai-final-delivery-20261030.md). Report-only work is complete; research remains stopped.

**STOPPED by owner on 30 October 2026.** Read [stop handoff](ai-stop-20261030.md) first for the newer accepted jobs, CPU result, exact uncaptured drafts and actual scheduler snapshot. The dated sections below are historical. Do not submit or resume research without new owner steering.

Updated 2026-10-29T23:04:43.349902+07:00, Vietnam time (UTC+7). AI fork 01a166eb-33cb-7ce0-9699-ec65de26689a of parent 01a15dd3-3094-7712-a991-8ce55b15cbfe. Preserve independent HPC payloads, queues and budget. English artifacts; Vietnamese chat. No background Codex or schedules.

## Actual queue and next decisions

The former queued jobs 27383 and 27387 are now terminal failures, with no new performance score. Independent sparse compile-off graph preparation and a revised CPU prerequisite are active; neither has an acceptance receipt yet. Query the actual queue before admission; own active/pending cap remains 5.

| Job | Hypothesis | Actual reviewed/observed state |
|---|---|---|
| 27365 | Decode running-request cap 256 to 64 | COMPLETED 0:0, 11:43; full local pass, 3046.890454 good output tokens/s; +0.257879% versus 27270, below useful gate |
| 27376 | Fresh native control, prefill RadixCache | REVIEWED full local pass, 3041.119598 good tokens/s; COMPLETED 0:0, 12:39 |
| 27378 | Disable prefill prefix caching, require ChunkCache | REVIEWED full local pass, 3048.446289 good tokens/s; COMPLETED 0:0, 11:41; +0.240921% versus 27376, close unchanged |
| 27383 | Actual Qwen decode compile cap 54 | FAILED 1:0, 3:35; native RoPE/fused-KV interface assertion, no AIPerf |
| 27387 | Cold native C++ radix build and CPU metadata fixtures | FAILED 124:0, 1:33; 76-second extraction consumed most of 90-second process window; fixtures did not complete |

The actual queried queue is retained in [cap review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-cap64-20261029/RESULTS.md) and the admission records. Query fresh scheduler state before acting. Each full job is 16 H200/two nodes/17 minutes maximum, 4.533334 GPU-hours; no new PBS SU. No prior job was cancelled/requeued, no dependency chain or submit service created.

**27365 decision:** close unchanged cap 64 sensitivity, with no 128 sweep or default/submission promotion. It has 1877/1903 good requests (98.633736%), zero errors/cancellations, 26 TTFT and zero ITL breaches, smoke 7/8 without regression and retrieval 12/12. Actual requested/final scheduler cap is 64; transfer/preallocation headroom remains separate. The request-map saving is only about 6 MiB per rank and the control did not demonstrate capacity pressure. The result is only +0.045606% over the separate prior native individual 26766, not an established optimization. [Complete measured result and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-cap64-20261029/RESULTS.md).

Cap64 decode mean GPU activity 95.833% is one idle sample at 0.161 seconds after first profiling-request start, with the other 23 samples at 100%; do not interpret this average as causal efficiency. Mean running requests 49.625, maximum 56, sampled queue zero, KV token usage 0.1146. All 72 server polls return HTTP 200 and no selected transport error/Python traceback is found. Sparse samples/uncalibrated host clocks/request-start envelope and missing hot-thread/Xid/throttle/kernel data limit interpretation. Engine random seeds vary across launches while workload seed remains 2026.

**27376/27378:** compare native RadixCache against prefill-only ChunkCache, retaining decode cap 256/polling 1 and all other factors. Pinned native factory and successful-transfer release lifecycle support the test. Require exact flags and actual cache class on all ranks, physical KV buffers, both semantic P/D routes and original raw/output gates. No cap 64 combination. [Source, plan and definite receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/STATUS.md).

**27383 actual result:** FAILED 1:0 after 3:35, before AIPerf. The first enabled compiled shape 54 reaches Qwen RoPE forward_native and asserts that fused_set_kv_buffer_arg is unsupported. This is an interface incompatibility, not a 600-second startup timeout. Eight current distributed/source-bound receipts and all raw startup/cleanup logs are sealed. Close unchanged S105 and block unchanged sparse compile S108; fewer graph buckets do not fix this error. Source-supported remedy needs its own qualification and a new matched control if fusion behavior changes. Independent compile-off sparse graph S107 remains a distinct startup/memory/padding hypothesis. [Failure review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-decode-compile-full-20261029/FAILURE-27383.md).

Compare only complete local passes to reviewed fresh control 27376. Require >1% useful gain and acceptable tails before independent matched confirmation; otherwise close unchanged settings. No new optimum, official ranking or accuracy claim.

**27376 fresh control** is reviewed:3041.119598 good output tokens/s,1874/1900good(98.631579%),zero errors/cancellations,26TTFT/0ITL breaches,smoke7/8 without regression,retrieval12/12. Native RadixCacheP/ChunkCacheD all-rank flags/classes,physicalKV and both semantic routes pass. This same-setting repeat is only+0.068% above27270, not an optimization. [Complete control review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/CONTROL_RESULTS.md).

**27378 final pair decision:** close the unchanged prefill ChunkCache arm. It passes 1879/1905 good requests (98.635171%), zero errors/cancellations, 26 TTFT and zero ITL breaches, smoke 7/8 without regression and retrieval 12/12. The +0.240921% score difference is below the prospective 1% useful-gain gate. Mean/p95 TTFT is 1102.185/1380.071 ms; mean/p95 request-mean ITL is 15.028/15.226 ms. P95 TTFT worsened while average TTFT improved. No repeat, cap64 combination, default or submission promotion. All-rank actual caches, physical KV and both semantic paths pass; only the intended prefill flag and generated engine seeds differ. [Full comparison, diagnostics, cost and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/RESULTS.md).

**27387 CPU prerequisite failed its process limit**, not a C++ compatibility assertion. Container creation took 76 seconds; Torch import 2.142 seconds; the fixed 90-second process window left too little for cold C++ JIT. Cases are empty and no native cleanup-end receipt was seen. S106 remains unsubmitted and blocked; offline fixtures are not actual CPU evidence. A separate R2 preparation proposes zero GPUs, four CPUs, 16 GiB and six minutes, with a 300-second internal deadline and 60-second cleanup allowance. It will preserve source/fixture scope and explicitly review any exact old rootfs cleanup. This revises an agent-created stage envelope under existing Slurm authorization, not the owner's budget. No old payload is extended or silently retried. [Original accepted trial](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cpp-radix-cpu-probe-20261029/STATUS.md).

A separate prefill-delayer source review is complete. Its queue trigger requires running requests; current pure-prefill logs show0 and slot capacity4096 is far above observed batch≤4. Max-delay passes are loop counts, not milliseconds. No active batching trigger is established, so no GPU run is justified for this topology. This is a local source/topology decision, not a universal claim. [Source evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-prefill-delayer-source-20261029/REPORT.md).

## Closed branches and retained evidence

Polling interval 1/2/4 full bracket is complete: 27270 = 3039.053386, 27272 = 3028.279635 (−0.354510%), 27274 = 3016.700285 (−0.735528%) good output tokens/s. All full local gates pass; differences are below 1% and each setting has one run. Keep interval 1 and close 2/4 without widening the sweep. [Final runtime/hardware/output/cost review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-transfer-poll-final-20261029/RESULTS.md). Actual engine seeds differ; configured workload seed 2026 is separate, so no deterministic/causal claim.

Tiny compile observer 27340 completed 0:0/97 seconds on one H200. Shapes 1/52/64 all show compiler activity and PyTorch captures/replays inside prospective synthetic tolerances. It does not prove Qwen/HPC-Ops, distributed startup, accuracy or speed. Original 27338 remains FAILED before compilation due source-location introspection; both are sealed. Its positive fixture permits the actual production startup qualification above, not bypassing it. [Result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-compile-observer-probe-r2-20261029/RESULTS-27340.md).

Shallow EAGLE 27238 = 2971.628430, −2.080318% versus matched 26949; close that one-step/two-token arm. Continuous decode steps has no Python consumer in this pinned image and is closed. Earlier tokenizer/collective/chunk/load/graph/old-QK-RoPE/old-draft branches remain closed unchanged. Page16 primitives remain diagnostic, not full-model correctness acceptance; preserve exact page1 exceptions. [Detailed previous handoff](history/20261029-ai-before-final-four-job-handoff.md).

## Retained performance and scoring

| H200 observation | Good output tokens/s | Limit |
|---|---:|---|
| Historical N64 three-run mean | 3044.400475 | Retained baseline series |
| Native baseline individual 26766 | 3045.501509 | Retained baseline, not global optimum |
| Fresh control 27270 | 3039.053386 | Full local pass |
| Exploratory cap 64 individual 27365 | 3046.890454 | +0.258%, no confirmed useful gain or promotion |
| Portable 27145 recovered raw | 3055.330517 | Original job FAILED after GPU client; readers fixed and later verified |

Official good output tokens/s = exported AIPerf Goodput requests/s × 200. Require TTFT ≤3000 ms and request-mean ITL ≤20 ms jointly on ≥90% of ALL requests including errors. Model accuracy ≥99% of reference remains UNKNOWN; local smoke/retrieval is not certification. Strict token-ID comparison failures 25797/25862 remain retained.

AIPerf defaults to client text tokenization here. Reported input 3986/3987 and occasional output 199 do not establish physical model truncation; actual generated IDs/authoritative per-request usage are uncollected. Do not redefine official multiplier 200 or silently change frozen gates. [Source and beginner explanation](../tutorial/20-requested-and-reported-token-counts.md).

## Access, submission and preservation

Existing H100 SSH reuse at 22:53:59 Vietnam time on 29 October failed; transport availability remains unknown/unusable. No DUO prompt or auth-state change was initiated; PBS queues/current credit UNKNOWN. Historical 27 October project 59010042 balance 15686.158 SU is not live spendable credit. Owner removed discretionary buffers and uses 30 October planning deadline. Before qsub refresh both CPU/AI queues and selected-project credit under CPU-before-AI locks, combined cap 3/max 1 running AI. Prepared equal-TP R2 (8 H100/one node/30 minutes/max 512 SU) remains unsubmitted.

This turn did not change published submission or slides, and preserved HPC. Last AI publication record is the compute-confirmed reader repair (ZIP SHA d3686c36a0262301f8733214740a44ebac4135eb514a831f5ea2ef87a31dd88e; all 265 HPC files and whole PPTX preserved at that publication). It is a dated AI publication record, not an audit of concurrent HPC work. No organiser upload. [Repair record](ai-artifact-path-fix-20261029.md).

Preparation/admission checkpoints: 71e30c64/d4d1112d for cap 64; 248a201d/7f3e4336 for cold-cache pair; 7874e9c4/3c8286d3 for compile qualification. Final polling review is captured in e3acdb31. Cap64 final review/raw seal/handoff is captured and pushed in e68e7261. Fresh queue handoff follows as its own checkpoint. Preserve frozen payloads, all failed/losing data and actual dates. Git stores recovery manifests but does not upload sibling external object bytes. No automatic mirror or background Codex.
