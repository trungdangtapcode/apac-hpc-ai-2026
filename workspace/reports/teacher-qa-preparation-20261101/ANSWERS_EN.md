# Teacher Thanh's questions: prepared AI answers

Prepared 1 November 2026 from retained measurements and the current 42-slide presentation. These are proposed answers, not an official question list, a transcript of delivered answers or a completed mock. This companion supplements the released slide-by-slide guides; it does not change the published deck or ZIP.

Start with [how the hypotheses and decisions developed](THINKING_PROCESS_EN.md). The emphasis is the evidence available before testing, the expected mechanism, a way the idea could fail, and the decision after measurement. This explanation is written retrospectively from retained records; missing original motives are not invented.

Use the quoted answer first, then stop. Expand only when asked. Each answer should identify the observation, the comparison, the supported decision and its limit. All performance numbers below are **good output tokens/s**, unless another unit is printed. H200 means 16 GPUs across two Firmus nodes. N is client concurrency, not GPU count or instantaneous server batch size.

## Find the teacher's question

| Question raised by the teacher | Prepared answer | Main / backup slide |
|---|---|---|
| Why choose 2×TP4 prefill + TP8/EP8 decode? | Q1 | 3–4; 18, 26 |
| What was the bottleneck and how was it identified? | Q2 | 5–8, 12 |
| Is the N48 profile representative of N64? | Q3 | 8, 12 |
| What was wrong with KV transfer, which component was affected, and why prioritise descriptors? | Q4 | 5–6; 20 |
| How much end-to-end performance came from the descriptor optimisation? | Q5 | 7; 21 |
| Can individual optimisation gains be isolated? What evidence supports the gain? | Q6 | 9–11; 32 |
| Why can concurrency increase TTFT or reduce throughput? Queueing or computation? Was GPU usage inspected? | Q7 | 11–12; 29 |
| How far was model quality validated? | Q8 | 16 |
| Why use H100? Which results were actually verified on H200? | Q9 | 14; 17, 22, 26, 33–34 |
| Which result is selected, and is it reproducible? | Q10 | 13, 16; 31 |
| What failed and what was learned? | Q11 | 15; 24–25, 28–31 |
| Does the result scale to more nodes or larger workloads? | Q12 | 4, 14, 16; 17, 33–34 |
| What did the team contribute rather than reuse? | Q13 | 2, 5–10 |
| What exactly was measured and how is the score computed? | Q14 | 1, 11–12; 27 |
| Why 128 MPI ranks/node for OpenFOAM? Why did its performance vary? | HPC handoff | Preserved HPC 35–42; answer owner must confirm |

The broad panel prompts — why this problem, why this choice, what proves the gain, what scales, what was verified and what failed — map to Q2/Q4, Q1/Q6, Q6/Q10, Q12, Q8/Q9 and Q11 respectively.

## Q1. Why choose two TP4 prefills and one TP8/EP8 decode worker?

**Say first:**

> We considered this split because prefill and decode perform different work and may benefit from different worker shapes. Two TP4 prefills and one TP8/EP8 decode worker fit the two-node allocation while keeping each TP group inside a node. The counter-risk was added KV transfer and an unbalanced pipeline. We therefore used compatibility and real-request gates, then full-run repeats to retain the operating point; we did not know its final score beforehand.

**If pressed:** The first node has two TP4/EP1 prefill workers; the second has one TP8/EP8 decode worker. Prefill processes the long prompt; decode repeatedly generates tokens. Splitting them permits different implementations but introduces cross-role KV transfer through NIXL. More replicas versus wider workers is a resource tradeoff, not an automatic improvement.

**Evidence:** slides 3–4; [selected early topology 22415](../../../2026-APAC-HPC-AI/qwen-experiments/runs/22415/config.json), [recovery results](../../../2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md), [later N64 review](../../../2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md).

**Do not say:** “We proved it was the best of all possible topologies.” Early N32, N40 and N48 scores are not a common-load topology ablation. TP8/EP2 recovery belongs to a separate historical branch.

## Q2. What was the most significant bottleneck, and how did you identify it?

**Say first:**

> We first asked where progress stopped. Ready workers followed by failed pair warmup pointed to setup, rather than a scored steady-state bottleneck. Source inspection then gave us a narrow avoidable-work hypothesis to test. On later working deployments we checked which request deadline failed before proposing another fix. That is how observations narrowed the next question; they did not establish one universal bottleneck for the whole journey.

**If pressed:** Job 22271 timed out at 360 seconds during P/D warmup. Separate full N64 job 26766 had 1,875/1,902 qualifying requests: 27 TTFT misses, zero request-mean ITL misses and zero scored request errors/cancellations. These are different jobs and phases. The later service did not inherit a proven bottleneck diagnosis from the earlier failed branch.

**Evidence:** slides 5, 7–8, 12; [22271 warmup log](../../../2026-APAC-HPC-AI/qwen-experiments/runs/22271/pair-warmup.log), [26766 request records](../../../2026-APAC-HPC-AI/qwen-experiments/runs/26766/confirm/n64/artifacts/profile_export.jsonl).

**Do not say:** “KV bandwidth was the dominant bottleneck” or “high GPU activity proves compute saturation.” We did not measure the causal request-time decomposition needed for either conclusion.

## Q3. Does profiling at N48 represent the selected N64 point?

**Say first:**

> Not quantitatively. N48 profiling gave us diagnostic leads: GEMM, collective-plus-normalisation and attention were visible components. Their percentages are shares of summed recorded kernel durations, which can overlap. N64 has separate request-level and sampled runtime evidence. We therefore do not transfer the N48 percentages into an N64 wall-time budget or claim that the profile proved which optimisation would work.

**If pressed:** N48 named shares were 21.642%, 23.479% and 15.064%. They are neither GPU utilisation nor exclusive fractions of request latency. A representative N64 diagnosis would need the same operating configuration and correlated phase/request timing; heavy profiling should remain separate from ranked timing or its overhead should be controlled.

The subsequent N60 backend comparison is a **separate controlled probe** of a supported implementation. Its control and repeat establish its observed value; the N48 percentages do not.

**Evidence:** slide 8; [24819 diagnostic profile](../../../2026-APAC-HPC-AI/qwen-experiments/runs/24819/diagnostic-profile/), [N64 observability and limits](../../../2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/observability.md).

**Do not say:** “23% communication means eliminating communication would make the service 23% faster.”

## Q4. What was wrong with KV transfer, and why try descriptors before bandwidth, layout or scheduling?

**Say first:**

> The failure occurred before scoring, and the source built metadata for the reserved KV pool although a request needed only a subset. That gave us a specific hypothesis: remove request-irrelevant setup work without changing the transferred ranges. We chose it because equivalence was cheap to check in 720 CPU cases before a GPU trial. We expected less metadata work; bandwidth, layout and scheduling remained possible competing causes.

**If pressed — answer the teacher's five causal prompts:**

- **What failed?** Model workers became ready, then the P/D pair warmup timed out before AIPerf scoring.
- **Which component was suspect?** Host-side construction of source/destination metadata describing KV memory ranges on a heterogeneous-TP transfer path. A descriptor identifies a memory range; it is not the KV data itself.
- **What made it worth checking?** The source constructed whole-pool range lists even though one request needs only a subset. This was a concrete avoidable-work hypothesis, not a measured ranking of all possible bottlenecks.
- **What changed?** Build descriptors for the request's pages and coalesce adjacent byte ranges, preserving mapping, offsets and strides. Seven hundred twenty CPU equivalence cases passed; real transport was checked separately through actual serving.
- **What did it establish?** Read Q5: patched-path feasibility, not a descriptor-only speedup.

The approximately **403.8 million source entries per rank for the reserved pool** and **188 coalesced ranges for a single contiguous 4,000-token request** have different scopes. They are not bytes, bandwidth or a speedup multiplier. NIXL carries KV between roles; MNNVL concerns GPU collectives and is a different communication layer.

**Evidence:** slides 5–7; [KV reasoning audit](../ai-final-report-20261030/KV_TRANSFER_REASONING_AUDIT.md), [patch](../../../2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/nixl-ondemand.patch), [geometry fixtures](../../../2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/geometry-test.json).

**Do not say:** “The counts prove descriptor construction dominated request latency.” There is no isolated old/new descriptor timer in this comparison.

## Q5. How much did the descriptor change improve end-to-end performance?

**Say first:**

> Our hypothesis was that constructing only the request ranges would remove unnecessary setup work and could make the failing path usable. We checked range equivalence, then tested real serving. The patched path completed warmup and a full N32 run at 1,422.96 good output tokens per second. That supports the engineering change, but no successful unpatched scored control exists, so a descriptor-only throughput improvement is still unknown.

**If pressed:** The observed failure and successful patched run motivate retaining the implementation for that branch. They do not isolate all startup/bootstrap/transport changes or prove descriptors were the sole cause. CPU range equivalence establishes a mapping property, not production GPU correctness on its own. A stronger attribution would require a viable matched unpatched control or a separately instrumented matched initialisation comparison.

**Evidence:** slide 7, backup 21; [22294 warmup](../../../2026-APAC-HPC-AI/qwen-experiments/runs/22294/pair-warmup.log), [22294 scored export](../../../2026-APAC-HPC-AI/qwen-experiments/runs/22294/confirm/n32/artifacts/profile_export_aiperf.json).

**Do not say:** “360 divided by 0.7 is the speedup.” One number is a timeout limit; the other is successful request warmup after workers are ready.

## Q6. Can you isolate the contribution of each optimisation to goodput?

**Say first:**

> We did not assume an implementation had one fixed effect. Earlier results and the changed prefill runner and chunk gave us a new interaction to test. We compared decode choices with the same load and serving setup, then repeated the promising candidate. The full N60 comparison gained about 5.30%, with worse TTFT and better ITL. That supports the tested interaction; it does not let us add independent kernel speedups.

**If pressed:** Topology, DeepGEMM prefill/chunk 8192, attention/collective choices, precision and the full workload were held at the intended same settings. Mean TTFT worsened from 822.29 to 947.63 ms while mean ITL improved from 16.58 to 14.93 ms. Treatment 24913 was about 0.033% below original treatment 24738. Generated engine seeds and deployment variability limit exact causal attribution.

The later full N62→N64 pair gave +1.083%; it tests client load on a selected service, not a separate additive kernel contribution. The historical bars span changing loads/configurations and must not be treated as an ablation.

**Evidence:** slides 9–11; [24912 control](../../../2026-APAC-HPC-AI/qwen-experiments/runs/24912/), [24913 repeat](../../../2026-APAC-HPC-AI/qwen-experiments/runs/24913/), [25365 control review](../../../2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md), [25366 load review](../../../2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md).

**Do not say:** “FlashInfer contributed X%, MNNVL Y% and descriptors Z%, so they sum to the final gain.” We do not have that complete factorial isolation.

## Q7. Why did more concurrency increase TTFT? Queueing or computation? Did you inspect GPU usage?

**Say first:**

> After improving the service configuration, we rechecked the load instead of assuming the old concurrency remained best. More in-flight requests could improve pipeline work, but could also increase waiting. We used bounded full tests and repeats: N64 gained about 1.08% over N62, while N68 added only 0.083% and raised mean TTFT substantially. We therefore kept N64; sparse monitoring does not isolate the queue-versus-compute cause.

**If pressed:** Jobs 25487/25488 are the matched full N64/N68 pair. TTFT misses increased 26→30; ITL misses stayed zero. The small gain was below the team's prospective >1% useful-gain gate, so N68 was not promoted. This is a team decision rule, not an organiser requirement.

For **the separate N64 repeat pair** 25366/25373, phase-aligned samples show decode GPU activity averaging 100%, about 50–51 running requests per labelled series, and sampled decode queue zero. Prefill activity means were approximately 92–97% depending on worker/run. These measurements establish what was sampled; they neither prove a compute bottleneck nor exclude transient queues. Do not substitute these particular samples for the N68 pair.

The observability review also records diagnostic profiler-stop HTTP 500 responses separately from zero scored-request errors. Missing trace analysis, incomplete phase timing and diagnostic failures are not silently called healthy.

**Evidence:** slides 11–12; [N64/N68 comparison](../../../2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md), [N64 repeat telemetry](../../../2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/observability.md).

**Do not say:** “We measured an N8→N16 collapse” merely because the teacher used that as an example. Use the actual N64/N68 evidence. A causal queueing explanation requires aligned per-request enqueue, prefill, KV-transfer and first-decode spans.

## Q8. How far has model quality been verified? Could FP8 change the answers?

**Say first:**

> Official model quality remains unverified by our team. The criterion is at least 99% of the organiser's reference score on the official accuracy evaluation; it is not 99% request success or exact answer-string equality. We used the supplied FP8 target and retained small smoke and retrieval checks as regression screens. Those checks do not replace the full official evaluation, so we do not claim quality certification or official ranking acceptance.

**If pressed:** Recent reviewed runs report smoke 7/8 with no new regression and retrieval 12/12. Neither is the official full-set score. Keeping weights fixed reduces one source of change but does not prove output equivalence across kernels, numeric paths or decoding. Exact generated token IDs were not retained in the performance runs; client-retokenized lengths do not by themselves establish physical truncation.

**Evidence:** slide 16; [current report and validation limits](../ai-final-report-20261030/REPORT.md), [current packaged metrics](../../VNUHCM%20-%20TripleU/AI_Task/logs/measured/latest-results.md).

**Do not say:** “FP8 retained all parameters, therefore quality is identical,” or “98.6% SLA success passes the 99% model-quality gate.” They are different metrics and evaluations.

## Q9. Why run H100 experiments? How can they tell you what is better on H200?

**Say first:**

> H100 supplied hypotheses, not a prediction of H200 performance. We tested the full recipe on H200; it lost, but runner and chunk changed together. That prompted a narrower test: keep HPC-Ops and match the larger chunk. It recovered part of the losing branch but stayed below the H200 incumbent. The tests refined the explanation and supported retaining the H200-specific recipe rather than converting scores between GPUs.

**If pressed:** All nine final allocations ran on 16 H200. Eight are N64; job 27781 is N54. The controls are 27777 for the native/recipe/FA3/chunk branch and 27826 for phase modes. The four additional distinct ports are 27804, 27806, 27828 and 27830; they are not four proven H100 wins or nine unique candidates. The full-recipe transfer changes a coupled prefill runner/chunk choice, so its loss is not one isolated backend effect.

Main AI scores are H200; H100-only results are separately labelled in backups. Running on the allocated platform means team-measured there, not organiser-scored or quality-certified. The historical one-point forecast in backup 33 is a bounded check, not a universal GPU conversion factor.

**Evidence:** main 14 and backup 34; [complete final nine-job ledger](../../VNUHCM%20-%20TripleU/AI_Task/logs/research-20261101/final-nine-run-ledger.csv), [full-recipe review](../../../2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md), [chunk review](../../../2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/RESULTS.md), [mode review](../../../2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md).

**Do not say:** “H100 is slower, so multiply every H100 result by 1.1881.” Different GPU, driver, network, launcher and runtime conditions limit that inference.

## Q10. Which result should we defend, and how reproducible is it?

**Say first:**

> We wanted an improvement attributable to a repeatable setting rather than one lucky run. That is why a candidate needed its own fresh control, a useful margin and a repeat. Historical N64 runs averaged about 3,044.40 good output tokens per second. The higher cache point gained only 0.241% against its control and worsened p95 TTFT, so it did not displace the repeated operating choice.

**If pressed:** Historical jobs are 25366/25373/25487; native 26766 is a separate series. Highest complete reviewed local full pass 27378 is not a promoted recipe. Portable raw 27145 reached 3,055.33 but the original job failed in postprocessing; CPU 27152 verified repaired readers on saved datasets. A new complete GPU deployment replay after repair has not occurred.

Independent deployment/repeat means a new launch/allocation, not necessarily different physical GPUs. There is no broad hardware-diversity study, formal confidence interval or global-optimum proof. A lower valid legacy replay at 2,830.92 remains unexplained by one isolated factor.

**Evidence:** slides 13 and 16; backups 29 and 31; [current result classes](../ai-final-report-20261030/REPORT.md), [cache comparison](../../../2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/RESULTS.md), [reader verification](../../../2026-APAC-HPC-AI/qwen-experiments/portable-postprocess-compute-check-20261029/RESULTS.md).

**Do not say:** “Independent repeats prove any H200 deployment will reproduce this exactly” or “the repaired reader makes the original FAILED allocation successful.”

## Q11. What did not work, and what did you learn?

**Say first:**

> We used failures to reject assumptions. Smaller graph capture memory looked promising as a resource change, but the full workload did not gain goodput. A functional shallow EAGLE path also lost throughput. Those observations told us that lower resource use and feature support were insufficient selection criteria. We closed the tested settings and kept the evidence, instead of accumulating optimisations that had not improved the actual objective.

**If pressed:** The sparse comparison is 27510 versus earlier control 27376, with one candidate observation and engine-seed/time limitations. It does not prove total VRAM or capacity improved. The shallow EAGLE comparison is 27238 versus 26949, not a rejection of every speculative method. Full-model compile 27383 failed before scoring on a native RoPE/fused-KV interface; that is a compatibility failure with no throughput result. The final H100-derived tests also preserved losses rather than extrapolating a hardware conversion.

**Evidence:** slide 15 and backups 25, 28, 30–31; [sparse result](../../../2026-APAC-HPC-AI/qwen-experiments/h200-sparse-decode-compile-20261029/RESULTS-27510.md), [EAGLE result](../../../2026-APAC-HPC-AI/qwen-experiments/h200-shallow-eagle-full-20261029/RESULTS.md), [compile failure](../../../2026-APAC-HPC-AI/qwen-experiments/h200-decode-compile-full-20261029/FAILURE-27383.md).

**Do not say:** “Speculation is always bad,” “FA3 is universally slower,” or “a terminal failed job is a valid performance measurement.”

## Q12. How would this behave on more nodes, GPUs or a different workload?

**Say first:**

> We have not measured that scaling, so we do not claim linear improvement beyond sixteen GPUs or beyond the fixed 4,000/200-token workload. More nodes would change the balance between replicas, model parallelism and cross-node KV or collective traffic. A different prompt/output ratio would also change prefill and decode demand. The H100-to-H200 tests already show why a configuration should be revalidated on its target system.

**If pressed:** A future plan would use platform-specific controls, fixed workload and cold-prefix settings, then vary one resource/layout factor at a time and inspect useful goodput, latency tails, errors and phase-aligned diagnostics. Such measurements are proposals, not jobs already executed or authorisation to restart research. No >16-GPU scaling curve or larger-workload claim is in the presentation.

**Evidence:** slides 4, 14 and 16; [scope of completed verification](../../../2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md).

**Do not say:** “Thirty-two GPUs should double the score.”

## Q13. Which contributions are actually yours?

**Say first:**

> Our work is the engineering investigation: selecting a usable topology and operating load, implementing and checking request-scoped heterogeneous-TP descriptor construction, validating actual runtime paths, and comparing candidates with controls and repeats. FlashInfer, DeepGEMM, HPC-Ops, MNNVL and the serving runtime are reused implementations. We distinguish our integration and experimental evidence from the kernels developed by their authors.

**If pressed:** The KV implementation supports bounded geometry/serving feasibility claims, not an isolated speedup. The backend comparison supports its tested service configuration and latency tradeoff. Failed trials, real reader defects and the resulting correction of claims are part of the contribution rather than hidden unsuccessful work.

**Evidence:** slide 2; [contribution classification](../ai-final-report-20261030/investigation-contributions.json), [research coverage](../ai-final-report-20261030/JOURNEY_COVERAGE.md), [KV patch](../../../2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/nixl-ondemand.patch).

**Do not say:** “We developed FlashInfer/HPC-Ops kernels” or credit an existing runtime feature to the team.

## Q14. What does the benchmark score actually mean?

**Say first:**

> AIPerf runs closed-loop at our selected concurrency, replacing completed requests with new ones rather than imposing a fixed arrival rate. Requested lengths are 4,000 input and 200 output tokens, with seed 2026 and cold prefixes. A request qualifies only if TTFT is at most 3,000 milliseconds and its mean ITL is at most twenty milliseconds. At least ninety percent of all requests must jointly qualify. The displayed score is exported Goodput in requests per second multiplied by 200.

**If pressed:** The full campaign protocol is 60 seconds warmup, 120 seconds profiling and 30 seconds grace. Errors remain in the request denominator. The 90% latency eligibility rule and ≥99%-reference model-quality requirement are separate. Do not replace exported Goodput with total output throughput multiplied by a good fraction unless equivalence is established for that export and accounting window.

**Evidence:** slides 1, 11–12; [retained organiser clarification](../../notes/official-goodput-clarification-20261020.md), [example exact final export](../../VNUHCM%20-%20TripleU/AI_Task/logs/research-20261101/jobs/27830/profile_export_aiperf.json).

**Do not say:** “It passed because the average TTFT was below three seconds.” The gate is applied per request, jointly with ITL.

## HPC handoff: do not invent these two answers

The teacher also asks **why 128 MPI ranks per node** and **what caused OpenFOAM variability**. Those are the independent HPC speaker's measured claims. The AI worker has not certified the rank-count choice or a variability diagnosis.

**Prepared handoff:**

> Those questions concern our independent OpenFOAM investigation. I will hand over to the member who owns the CPU configuration and repeated solver measurements, so we can show the actual rank placement, timing and variability evidence.

The HPC owner should bring the comparison that justified the rank count, physical-core/SMT and affinity details, per-case solver/wall times, repeated-run variation and controls for placement, I/O, contention and convergence. These are evidence to confirm, not explanations already established here. The AI preparation changes no HPC payload, notes or claims.

## Rehearse the questions, not a memorised defence

1. Ask Q1–Q8 without opening a terminal. Give the short answer and one precise evidence limit.
2. Ask follow-ups: “Is that observed or causal?”, “Which control?”, “Same hardware and load?”, “What was not measured?”
3. Open the named main/backup slide or source only when pressed. Keep the nine-job ledger available for H100/H200 questions.
4. Ask the speaker to explain N, TP, EP, KV, TTFT and ITL in plain language. Do not assume memorising an abbreviation means understanding it.
5. Rehearse Q9–Q14 and the handoff with the actual HPC presenter. Fit the combined 15–20-minute talk, leaving the separate 10-minute Q&A.
6. Record real timing, listener confusion and unanswered questions after the mock. This document does not claim those checks happened.

For the current deck and short talk scripts, start with the [release route](../../submission-review/ai-final-update-20261101/README.md). The older [general mock Q&A](../ai-final-report-20261030/MOCK_QA_EVIDENCE.md) remains supporting material; this companion explicitly maps the teacher's questions and current answer boundaries.
