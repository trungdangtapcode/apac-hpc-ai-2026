# Mock panel Q&A: evidence and answer boundaries

Updated 2 November 2026 after full portable acceptance job 28197 from retained AI run reviews and the current reasoning outline. This is rehearsal material, not an official question list and not a record that a mock interview has occurred. Slide references follow [reasoning-plan.json](../../submission-review/ai-acceptance-update-20261102/reasoning-plan.json): AI slides 1–16 are the main route and AI slides 17–34 are backup slides; the slideshow hides those backups, then hands off from main slide 16 to unchanged HPC slides 35–42.

| Main slide | Exact title in the current plan |
|---:|---|
| 1 | Fast tokens count only when requests meet both latency limits |
| 2 | Three investigations support three different kinds of claim |
| 3 | Replica count and parallel width compete for the same 16 GPUs |
| 4 | Two TP4 prefills feed one TP8 decode within the two-node budget |
| 5 | Ready workers still failed before the first usable benchmark |
| 6 | Request-scoped descriptors remove work unrelated to the request |
| 7 | The patched path became usable; descriptor-only speedup is unknown |
| 8 | Profiles identify candidates for investigation, not a proven time budget |
| 9 | Test the decode implementation while holding the serving setup fixed |
| 10 | Higher goodput came with slower first tokens and faster streaming |
| 11 | N64 survives a full repeat; N68 loses its short-test advantage |
| 12 | The remaining latency failures are first-token tails |
| 13 | Repeated evidence supports N64 more strongly than an isolated peak |
| 14 | Direct H200 tests decide which H100 ideas transfer |
| 15 | Better proxy metrics did not always improve qualifying throughput |
| 16 | Deployment acceptance passes; official model quality remains unverified |

## Answer pattern

In about 30 seconds: state the observed problem, name the comparison or intervention, give one or two numbers, and end with the limit. If pressed, add the exact run/source record and say what was not measured. Keep observations, hypotheses, causal conclusions, and unknowns separate.

## Core AI questions

### 1. Why split prefill and decode this way, and why did the earlier N48 result lead to N64?

**30-second answer:** “We selected two TP4/EP1 prefill workers on the first H200 node feeding one TP8/EP8 decode worker on the second. This kept each tensor-parallel group within a node, used a measured FP8-compatible layout, and let the two phases use different implementations. The early N48 result showed that this layout could serve; it was not a repeated N48-versus-N64 experiment. We later raised client concurrency under the same fixed workload: a matched full N62-to-N64 comparison improved good output throughput by 1.083%, and an independent N64 deployment repeated the result. This is a measured operating choice, not a proof of global optimality.”

**Cross-examination:** “What was N48?” Explain that it is the client-concurrency point in an early topology/recovery series, around 1,912 good output tokens/s, not the number of GPUs or a matched N64 control. The topology record includes multiple layouts with differing history and factors. FP8 shard geometry and actual prefill/decode response checks constrain feasibility; they do not by themselves rank every layout.

**Retained evidence:** main slides 3–4; selected N48 layout job 22415 is documented in [RECOVERY_RESULTS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md), with its [configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22415/config.json) and [summary](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22415/summary.json). The separate heterogeneous-TP recovery layout is in [TOPOLOGY_REVIEW.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_REVIEW.md). For the later load decision, see [25365 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md), [25366 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md), and [25373 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/REVIEW.md). Job 22415 supports the chosen P8-TP4 / D8-TP8-EP8 topology at N48; jobs 25365→25366 are a later, separate N62→N64 concurrency pair, and 25373 repeats N64.

**Still missing:** an exhaustive, same-protocol comparison of all feasible layouts; broad hardware diversity; a demonstrated optimum beyond the tested 16-GPU envelope. The N48 pilot and later full-load results are not one matched pair.

### 2. Did the KV descriptor repair solve the end-to-end problem?

**30-second answer:** “It made the tested heterogeneous-TP path feasible, but it did not establish a descriptor-only speedup. Job 22271 loaded workers and then timed out during pair warmup before scoring. Source analysis found whole-pool descriptor enumeration; the patched path builds request-scoped descriptors. CPU geometry checks matched original byte ranges in 720 cases, and patched job 22294 warmed both real P/D routes in 0.68–0.70 seconds per request after servers were ready, then scored 1,422.96 good output tokens/s at N32. We have no successful unpatched scored control for that exact topology.”

**Cross-examination:** “Is 403.8 million to 188 a speedup?” No. Those are source descriptor counts for different scopes: approximate whole-pool entries per rank versus coalesced ranges for one contiguous 4,000-token request. They are not bytes, bandwidth, elapsed time, or an inference-speed multiplier. The 360-second timeout and 0.68–0.70-second patched warmup are not comparable timed measurements.

**Retained evidence:** main slides 5–7; [KV reasoning audit](KV_TRANSFER_REASONING_AUDIT.md); [NIXL source note](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/README.md), [720-case geometry result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/geometry-test.json), and [patch](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/nixl-ondemand.patch); [22271 warmup log](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22271/pair-warmup.log); [22294 warmup log](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22294/pair-warmup.log) and [N32 AIPerf export](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22294/confirm/n32/artifacts/profile_export_aiperf.json); [topology](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_REVIEW.md) and [recovery results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md).

**Still missing:** a successful unpatched end-to-end control on the same layout; separately timed old-versus-new descriptor construction; attribution of the warmup change among descriptor work, bootstrap, transport and other run differences; a measured bandwidth explanation. The geometry test is CPU-only and explicitly does not prove real GPU transfer correctness by itself.

### 3. What did profiling say was the bottleneck, and did you prove that the named components caused the gain?

**30-second answer:** “The N48 diagnostic profile made GEMM, collectives/RMSNorm, and attention sensible places to investigate: their shares of summed kernel duration were 21.642%, 23.479%, and 15.064%. Those are profile observations, not percentages of wall-clock latency. We then tested an integrated decode-backend interaction at full N60: a fresh AUTO-decode control scored 2,838.853 good tokens/s, while an HPC-Ops treatment repeat scored 2,989.175, about 5.295% higher. That supports the tested configuration at N60; it does not isolate one kernel or let us add component gains.”

**Cross-examination:** “Which components were held fixed?” The comparison retained DeepGEMM prefill and chunk size 8192, plus the same full 60/120/30-second protocol; the decode backend was the intended treatment. The treatment repeat 24913 is about 0.033% below original treatment 24738. Still, an integrated backend change can alter interactions and scheduling, so do not call this a kernel-only causal decomposition. Continuous hardware data dedicated to 24913 are absent.

**Retained evidence:** main slides 8–10; [N48 diagnostic profile](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24819/diagnostic-profile/) and [profile log](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24819/diagnostic-profile.log); [24912 fresh control](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24912/), [24913 treatment repeat](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24913/), and [24738 original treatment](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24738/); [RUNS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RUNS.md) entries for 24912–24915; [evidence cards](/home/apacsc42/workspace/reports/ai-final-report-20261030/EVIDENCE_CARDS.md).

**Still missing:** wall-clock phase decomposition, a single-component intervention for each profile share, and dedicated continuous hardware sampling for treatment repeat 24913. Kernel-duration shares may overlap across ranks and must not be presented as exclusive end-to-end time fractions.

### 4. Why choose N64? Did more concurrency improve service, and what happened to TTFT?

**30-second answer:** “The full N62 control 25365 scored 3,011.875 good output tokens/s; N64 candidate 25366 scored 3,044.490, a 1.083% matched gain. Mean TTFT rose from 1,037.6 to 1,110.5 ms, while the joint good-request fraction stayed about 98.6%; an independent N64 repeat 25373 differed by only −0.014%. N68 then added just 0.083% over a fresh N64 control and worsened mean TTFT from 1,113.6 to 1,347.1 ms, with TTFT breaches increasing from 26 to 30. We retained N64 and stopped the unchanged N68 branch.”

**Cross-examination:** “Does client concurrency equal batch size or prove queueing caused TTFT?” No. It sets target in-flight client requests; actual running batches, queueing, prefill, transfer and compute are separate. We observed role-specific gauges and sparse samples, but did not reconstruct each request's phase timing. Mean ITL and TTFT alone cannot split queue wait from computation.

**Retained evidence:** main slide 11; [25365 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md), [25366 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md), [25373 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/REVIEW.md), and [25487/25488 pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md); [serving results index](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md); [25373 observability review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/observability.md).

**Still missing:** correlated per-request enqueue/dequeue, prefill, KV-transfer and first-decode spans on aligned clocks; a controlled decomposition of the TTFT change. Sampled zero queue is not proof that the queue was always empty. N68 remains a valid local full result, but its gain misses the 1% practical repeat gate.

### 5. Which score is “best,” and what do you claim as the selected result?

**30-second answer:** “Our recommended operating choice remains replicated target-only N64: historical full runs 25366, 25373 and 25487 average 3,044.400 good output tokens/s, and separate native run 26766 at 3,045.502 is a distinct observation. The later exact-packaged-entry acceptance 28197 scored 3,051.518, but it had no matched control and changes no serving recipe, so it is not an optimisation gain. Before that, the highest complete full benchmark was 27378 at 3,048.446; its cache pair was only +0.241% versus fresh control 27376. Recovered raw 27145 is 3,055.331, but its original job failed postprocessing; compute-only 27152 verified readers, not a full rerun.”

**Cross-examination:** “Why not claim the largest number?” Because evidence class and matched controls matter. A recovered raw measurement from a failed job is not a successful deployed run; a one-off treatment below the prospective useful-gain gate is not a confirmed optimization. The selected three-run historical mean, later native observation, cache comparison, and portable replay are distinct series.

**Retained evidence:** main slides 13 and 16; [final AI report](REPORT.md); [25366 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md), [25373 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/REVIEW.md), and [25487/25488 pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md); [27376 control](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/CONTROL_RESULTS.md) and [27378 treatment review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/RESULTS.md); [native chunk review for 26766–26770](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-native-chunk-review-20261028/REVIEW.md); [27145 alias correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-artifact-path-fix-20261029/ALIAS_CORRECTION.md) and [27152 compute-only result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-postprocess-compute-check-20261029/RESULTS.md).

**Still missing:** a statistical confidence interval or broad hardware diversity; complete single-allocation portable success after the reader repair. Do not call 3,048.446 the new optimum or 3,055.331 a successful job.

### 6. How do you know answer quality is acceptable?

**30-second answer:** “We do not yet know that the official quality gate passes. The contest requires at least 99% of the reference on the full accuracy set; that evaluation remains UNKNOWN. Small local smoke and retrieval checks are useful regression screens, but they are not substitutes for the full evaluation. We report the measured local latency/goodput result and do not claim official quality certification.”

**Cross-examination:** “Then can you claim the official result is valid?” We can claim measured goodput from our assigned-cluster runs under the stated workload and local protocol checks, with their limits. We cannot claim official ranking acceptance or certified model accuracy. Do not reinterpret exported request lengths as proof of truncation or exact token-ID equality.

**Retained evidence:** main slide 16; [final AI report](REPORT.md); [25366 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md), [25373 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/REVIEW.md), and [25487/25488 pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md); [AI handoff](/home/apacsc42/workspace/notes/AI_CURRENT.md); [latest packaged results](</home/apacsc42/workspace/VNUHCM - TripleU/AI_Task/logs/measured/latest-results.md>).

**Still missing:** the full organizer accuracy evaluation and authoritative generated token IDs for the performance runs. A whole-allocation portable replay after the reader correction is also not claimed.

### 7. What does the N64 request-level scatter tell you about the SLA misses?

**30-second answer:** “The request-level view for full N64 job 26766 shows 1,875 of 1,902 requests meeting both latency limits. The other 27 all breached TTFT; none breached request-mean ITL, and there were zero request errors or cancellations. This tells us which part of the joint gate failed in that run. It does not reveal whether any slow first token came from queueing, prefill, transfer or compute.”

**Cross-examination:** “Does the scatter prove the server saturated?” No. Request points and aggregate tails characterize outcomes, not the internal causal stage. Client concurrency is not batch size. Sparse server/hardware samples and uncalibrated cross-host clocks do not join each request to its phase timings.

**Retained evidence:** main slide 12; [26766 native full-load review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-review-20261026/review-26766.json), [N64 raw AIPerf export](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/26766/confirm/n64/artifacts/profile_export_aiperf.json), and [N64 request records](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/26766/confirm/n64/artifacts/profile_export.jsonl). For optional load-context comparisons only: [25365 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md), [25366 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md), and [25487/25488 pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md). The 26766 run-specific review governs the main answer's counts and units.

**Still missing:** aligned per-request queue, prefill, KV transfer and first-decode spans, plus continuous sufficiently sampled diagnostics for the same request interval. Do not infer a bottleneck from the shape of the score distribution alone.

### 8. What did the final H100-to-H200 checks change?

**30-second answer:** “H100 helped us screen settings, then we ported four distinct H100-derived interventions onto the same 16 H200 base and compared them with fresh H200 controls. The transferred full H100 recipe at N64 scored 2,721.816 good tokens/s versus fresh control 3,038.023, a 10.408% loss. HPC-Ops prefill at chunk 6,144 and 8,192 remained 7.114% and 4.523% below that control. Decode-only and prefill-only inference-mode ports changed goodput only +0.006% and +0.131%. None cleared our prospective 1% usefulness gate, so we retained the H200 recipe.”

**Cross-examination:** “Are these four full H100 recipe replays?” No. They are four distinct source-intervention ports into the stronger current H200 base; 27826 is an explicit control and is not counted as a candidate. The selected H100 full recipe is a separate coupled runner/chunk comparison. These measurements do not establish universal library rankings or a GPU conversion ratio.

**Retained evidence:** main slide 14 and backup 34; [final H100 transfer review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md), [chunk interaction review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/RESULTS.md), [phase-mode review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md).

**Still missing:** repeated independent runs of these losing/small-effect ports are not justified by their margins; no cross-platform conversion law or official quality certification follows.

### 8a. What does the one-point H100-to-H200 forecast prove?

Only a bounded held-out check. A frozen N52 calibration predicted 2,642.244 good tokens/s on H200; measured job 24272 reached 2,601.629 (−1.537%), inside the team's ±2% practical tolerance but outside an earlier incomplete sensitivity range. It is backup slide 33, not the latest transfer result and not a universal hardware multiplier. Source: [frozen calibration and held-out run](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md) and [job 24272](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24272/).

### 9. What did the final full portable acceptance prove?

**30-second answer:** “Job 28197 ran the exact packaged entry after we corrected the readiness race found in 28194. The old gate saw `/health` return 200 before asynchronous model registration finished; `/v1/models` then returned 503. We changed only the readiness gate so it checks for the registered Qwen model and live workers within the original deadline. The full entry then completed in 611 seconds on 16 H200 and passed the corrected readers, both P/D semantic paths, performance gate and cleanup. It scored 3,051.518 good output tokens/s; 1,881 of 1,907 requests passed both latency limits (98.6366%), with 26 TTFT misses and zero ITL misses or errors. This accepts the packaged deployment path; with no matched control it does not prove a performance improvement.”

**Cross-examination:** “Did you change the model or optimize serving?” No. The fix only waits for the API's actual model-registration response and checks the worker PIDs under the original job-start-plus-600-second readiness deadline. It changes no model, serving parameters, semantic criteria or official client flags. A performance score from this run is an acceptance observation, not a matched treatment effect.

**Retained evidence:** slide 16 and backup 31; [28197 acceptance review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/REVIEW.md), [actual scheduler receipt and state](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/STATUS.md), [preserved 28194 failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/delivery/VNUHCM%20-%20TripleU/AI_Task/logs/reruns/28194/summary.json) and [portable performance gate](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/delivery/VNUHCM%20-%20TripleU/AI_Task/logs/reruns/28197/performance-gate.json).

**Still missing:** the official model-quality ratio against the organiser reference. The acceptance run is a performance/deployment check, not that full accuracy evaluation.

### 10. What does the “quality score” say, and can we submit without it?

**Answer:** “We have no measured official quality number. The 98.6366% value from 28197 is the fraction of performance requests that met both latency limits; it is not model accuracy. The official ≥99%-of-reference evaluation is organiser-run. The published Basic submission procedure asks for the stack instructions, single-job deployment and benchmark script, and slides; it does not list our possession of the unpublished reference score as a pre-upload requirement. We can submit the Basic package while stating that organiser quality validation is pending. This does not guarantee it will pass that later quality evaluation.”

**Retained evidence:** [exact requirement and careful interpretation](/home/apacsc42/workspace/notes/ai-quality-threshold-clarification-20261102.md), [official Qwen rules snapshot](../submission-review/submission-readiness-20261102/official-rules/1.%20Qwen3%20AI%20Task%20Rules.md).

### 11. Did the latest acceptance replace the historical best or improve the model?

No. Job 28197's 3,051.518173 is the latest complete exact-package acceptance observation and is numerically above the earlier 3,048.446289 individual 27378 result. It has no matched concurrent control and changes no serving recipe, so do not call the difference an optimisation gain. Keep the historical three-run mean 3,044.400475, separate native job 26766 at 3,045.501509, highest complete individual 27378, and previously recovered raw value from failed job 27145 at 3,055.330517 as separate evidence classes. The acceptance run confirms the deployment and scoring path after reader repair; it does not rewrite those historical records or provide official accuracy.

### 12. Did a lower resource proxy or speculative decoding improve the service?

**30-second answer:** “No tested branch displaced replicated N64. Sparse decode graphs reduced logged capture memory from 1.15 to 0.36 GB per decode rank, but job 27510 scored 3,029.861 good tokens/s, 0.370% below the earlier control 27376. The shallow EAGLE3 full arm 27238 scored 2,971.628, 2.080% below matched 26949. These examples show why a favorable resource or short diagnostic is not enough: the complete service objective and quality gates still decide.”

**Cross-examination:** “Does lower graph memory mean lower total VRAM or better capacity?” Not by itself. It is the logged capture-memory measure, not total VRAM or KV occupancy; capture time changed only slightly. Also, one candidate/control observation and different engine seeds limit causal strength. EAGLE's result closes the tested arm, not every speculative decoding design.

**Retained evidence:** main slide 15 and backups 24, 28, 30; [sparse graph result for 27510](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-sparse-decode-compile-20261029/RESULTS-27510.md) and [result JSON](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-sparse-decode-compile-20261029/result-27510.json); [EAGLE3 full result 27238](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-shallow-eagle-full-20261029/RESULTS.md) and [feasibility review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-shallow-eagle-feasibility-20261029/REVIEW.md); [evidence cards](/home/apacsc42/workspace/reports/ai-final-report-20261030/EVIDENCE_CARDS.md) and [panel Q&A notes](/home/apacsc42/workspace/reports/ai-final-report-20261030/PANEL_QA.md).

**Still missing:** total-memory attribution, a repeat of the sparse candidate under identical sampling, and evidence for untested speculative methods. These local interventions do not establish official accuracy.

## Team handoff and HPC questions

If asked about the HPC section, keep the answer to ownership and handoff: “Slides 35–42 cover the independent OpenFOAM CPU track. I can hand over to its owner for the solver, scheduler and measured CPU results; I will not attribute those results to the AI experiments.” The AI speaker should not improvise HPC measurements, alter its payload, or merge the two tracks' budgets and evidence. Allow the HPC speaker their separately agreed time; no HPC timing is inferred here.

## Proposed final mock rehearsal

This is a rehearsal procedure, not a claim that the team has rehearsed. Run one compact timed 16-slide AI main route with a 10–11 minute target inside the official combined 15–20 minute AI/HPC talk; the separate Q&A is 10 minutes. Then ask the questions and follow-ups above without opening a terminal. Use hidden backups 17–34 only when prompted, and preserve the time assigned to the independent HPC speaker. Record whether each answer states (1) the measured observation and unit, (2) why that test followed, (3) what the comparison held fixed, (4) the supported conclusion, and (5) one specific missing measurement. Cut detail before removing an evidence boundary.

At the end, hand the microphone and slide control to the independent HPC presenter. Keep an explicit unknown/contingency sentence ready: “Official full-set quality is still unverified; we are presenting the result measured by our team on the assigned cluster and its limits.” If a number or source is not immediately available, state the boundary and point to the named retained review rather than searching a command line live. Afterwards assess whether the answers were clear to a non-specialist, whether each explained the technical reasoning rather than reciting chronology, whether every causal claim was defensible against its control, and whether timing left the promised HPC handoff intact. Record actual timings and feedback only after a real rehearsal.

No rehearsal outcome, timing result, panel question, HPC explanation, research job, authentication action, or new measurement is asserted by this document.
