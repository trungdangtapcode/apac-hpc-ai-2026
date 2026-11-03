# TripleU AI task — final research report

The current delivery is an engineering investigation with **16 main AI slides, 18 hidden AI backups and eight unchanged HPC slides**. The [24-page main-talk PDF](../../submission-review/ai-quality-update-20261103/TripleU_APAC2026_Main_Talk.pdf) presents AI 1–16, then hands directly to HPC 35–42. Backup 33 keeps the bounded historical forecast, backup 34 gives the nine final H200 verification jobs, and backup 31 retains the exact portable-entry failure and repair. English and Vietnamese scripts provide the AI reasoning and spoken transitions. The HPC content remains owned by its independent presenter.

Updated 3 November 2026, Vietnam time (UTC+7). **Submission posture: preserve the official Qwen FP8 checkpoint and optimise the serving path.** The checkpoint and model weights are preserved; experiments changed the serving configuration. Exact-package deployment and performance acceptance completed in job 28197. A separate full-set local MMLU-Pro comparison now passes the predeclared 99% reference-retention point gate. This is our measured local check, not BTC certification or an organiser evaluation result.

## Result and submission choice

**Basic submission serving configuration:** N64 on 16 H200, with two TP4/EP1 prefill workers and one TP8/EP8 decode worker; DeepGEMM prefill/chunk 8192 and HPC-Ops decode with FlashInfer attention/MNNVL transport. The official Qwen FP8 model remains intact with BF16 KV; the work changes serving implementation and runtime configuration, without skipping model layers or requantizing the checkpoint. This is the measured operating choice within the tested two-node budget.

**Historical repeated target-only series:** three full H200 runs average **3,044.400475 good output tokens/s**. Native full job 26766 measured **3,045.501509** in a separate series. Highest complete individual before portable acceptance, job 27378, measured **3,048.446289**, but its cache treatment was only +0.240921% versus its fresh control, below the team's prospective 1% usefulness threshold. It was not a confirmed optimization.

**Final exact packaged-entry acceptance:** the initial attempt, 28194, failed before AIPerf because `/health` returned 200 while asynchronous registration was incomplete; `/v1/models` then returned 503. The fix changed only readiness: wait for a valid registered Qwen model and live workers under the original deadline. Five local readiness/liveness fixtures passed before submitting the exact corrected entry as job 28197. That full run completed successfully in **611 seconds on 16 H200 at N64**, passed both P/D semantic routes, corrected result readers, the performance gate and cleanup. It measured **3,051.518173 good output tokens/s**. Of **1,907 requests, 1,881 passed both latency limits (98.636602%)**; 26 missed TTFT, none missed ITL, and there were zero errors or cancellations. Mean/p95 TTFT was **1,100.315/1,285.996 ms**; mean/p95 request-mean ITL was **15.009828/15.185750 ms**.

This is a complete portable deployment-acceptance observation, not a new serving recipe or a matched speedup. Its value is numerically above the prior highest complete individual 27378, but it has no contemporaneous matched control and establishes no optimisation gain. Keep it separate from the historical three-run mean 3,044.400475, native job 26766 at 3,045.501509, prior highest complete configuration 27378 at 3,048.446289, and recovered raw observation 27145 at 3,055.330517 whose original job FAILED during postprocessing.

### Answer-quality verification

A separate local full-set check compared the stock official FP8 deployment with the accepted serving configuration on the same 16 H200 GPUs and the same 12,032 MMLU-Pro questions. The reference answered 9,460 correctly (78.623670%); the candidate answered 9,452 (78.557181%), retaining **99.915433%** of reference accuracy and passing our predeclared local 99% point gate. Both roles had zero service errors; invalid answers and answers reaching the generation limit remained in the denominator. The paired outcomes differ on 876 questions, for a net eight fewer correct answers on the candidate. Computer science retention was 97.971014% and philosophy retention 98.966408%; no per-category gate was declared. This is one local benchmark comparison, not statistical equivalence or BTC certification. All sixteen full-study allocations completed; total allocated cost was 51.533333 H200 GPU-hours including pilots (47.32 for the full set), not active compute time or money. The separate N16 pilot remains a failed point result at 98.076923%; it was not combined with the full-set score.

The 28197 value of 98.636602% remains the fraction of performance-benchmark requests that met both latency limits. It is not answer accuracy. Performance and quality are separate measurements. See [full quality results](../ai-quality-verification-20261103/FULL_RESULTS.md) and [methodology](../ai-quality-verification-20261103/METHODOLOGY.md).

[Full 28197 review and failure-to-fix evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/REVIEW.md), [actual job status/receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/STATUS.md), [current presentation package](/home/apacsc42/workspace/submission-review/ai-quality-update-20261103/).

## Workload and score

AIPerf sustains a team-selected closed-loop concurrency of 64, with requested 4,000 input and 200 output tokens, seed 2026 and cold prefixes. The full protocol uses 60 seconds of warmup, 120 seconds of profiling and 30 seconds of grace.

A request is good only if both its time to first token (TTFT) is at most 3,000 ms and its average interval between generated tokens (request-mean ITL) is at most 20 ms. At least 90% of all requests must satisfy both, with errors included in the denominator.

The official displayed throughput is:

    good output tokens/s = exported AIPerf Goodput (good requests/s) × 200

Do not substitute aggregate output throughput or divide completed counts by an assumed window length. Client-retokenized lengths can differ from requested lengths; actual generated token IDs are not retained.

## How performance developed

1. **Find a workable topology.** The early 07 layout scored about 1,297 good tokens/s at N32, then 09 about 1,666 at N40. Widening prefill and selecting TP8/EP8 decode established the current split. These historical points change more than one factor; they are not a cumulative causal ablation.
2. **Make transport practical.** Request-scoped NIXL descriptors avoid constructing whole-pool transfer metadata. Source, byte-range, KV-geometry and semantic checks support the patch. Descriptor-count reduction is not an inference speedup multiplier.
3. **Combine phase-specific backends.** FlashInfer decode attention, MNNVL collectives, DeepGEMM prefill and HPC-Ops decode produced useful interactions. At N60, an independent HPC-Ops repeat improved 5.295% against its matched auto-decode control, with the repeat only about 0.033% below the original treatment.
4. **Increase load and replicate.** The full N62-to-N64 pair improved 1.082867%. Independent N64 observations established the historical 3,044.400475 mean. The later N68 difference was only 0.083056%, below the useful-gain gate, and was not promoted.
5. **Inspect beyond the headline score.** Per-request tails, errors, actual runtime activation, KV ownership, both P/D routes, GPU/host samples and source bindings distinguish a valid measurement from a terminal job. Initial TTFT misses remain in the score.
6. **Close losing or unsupported branches.** Recent cache, request-cap, tokenization, polling, speculative and graph trials did not displace the reproduced operating choice. Full Qwen compile exposed a real RoPE/KV interface incompatibility. A successful small C++ fixture remains only an integration prerequisite.

The complete historical reasoning, including failed attempts and corrected interpretations, remains in the [research journal](../research-journey-20261019/journal/README.md). The presentation illustrates the topology, transfer change, backend interaction, replication, cross-platform calibration and later negative results.

## Recent measured decisions

| Question | Jobs | Good output tokens/s or matched change | Decision |
|---|---|---:|---|
| Dynamic prefill tokenizer | 26951 / 26953 vs 26949 | +0.192% / +0.270% | No promotion |
| Prefill FlashInfer, page 1 | 27077 vs 26949 | −6.385% | Retain FA3 prefill |
| Shallow decode EAGLE3 | 27238 vs 26949 | 2,971.628430; −2.080318% | Close tested arm |
| Transfer polling 1 / 2 / 4 | 27270 / 27272 / 27274 | 3,039.053 / 3,028.280 / 3,016.700 | Retain interval 1 |
| Decode request cap 64 | 27365 vs 27270 | 3,046.890454; +0.257879% | No promotion |
| Prefill ChunkCache | 27378 vs 27376 | 3,048.446289; +0.240921% | No promotion |
| Sparse decode graphs | 27510 vs earlier 27376 | 3,029.861122; −0.370208% | Retain dense graphs |

Job 27378 has 1,879/1,905 good requests (98.635171%), zero errors/cancellations, TTFT mean/p95 1,102.185/1,380.071 ms and request-mean ITL mean/p95 15.028/15.226 ms. It passes local smoke 7/8 without new regression and retrieval 12/12.

Job 27510 completed 0:0 with 1,870/1,896 good requests (98.628692%). Twelve sparse buckets reduced native logged graph-capture memory from 1.15 to 0.36 GB per decode rank, but capture time changed only from 101.46–101.49 to 95.98–96.05 seconds. Lower capture memory did not improve serving throughput. Different times, generated engine seeds and candidate startup instrumentation limit causal interpretation.

## Failures and limits that remain visible

- Full-model compile 27383 failed before AIPerf when native RoPE rejected a fused KV argument. It has no performance score; fewer capture buckets alone cannot repair the interface.
- CPU C++ trial 27387 ran out of its short process window after 76 seconds of container creation. Its replacement 27506 completed in 95 seconds, with a 26.605-second cold JIT, two CPU fixtures and native cleanup. That establishes neither Qwen integration nor serving speed.
- Portable reader repairs preserve the original failed GPU allocations and their recovered raw observations. Compute-only postprocessing was a separate proof; the later complete corrected-entry GPU acceptance is job 28197, while failed 28194 remains a separate retained failure.
- Five-second hardware/server samples use a request-start envelope with uncalibrated clocks and incomplete final-drain coverage. GPU activity, sampled VRAM and KV token occupancy measure different things. Missing kernel, hot-thread, Xid/throttle and authoritative generated-token data are not zero or healthy.
- Earlier lower valid replays remain retained. Their difference from later approximately 3k runs is not automatically a causal launcher gain.

## H100 results are separate

The retained H100 individual peak is **2,433.019859 good output tokens/s** at N54; a fresh H100 full control scored **2,399.186728**. H100 uses different hardware and an independently tuned prefill configuration. These values are not directly comparable algorithmic treatments of the H200 peak.

A historical same-configuration N52 calibration produced an observed system ratio of 1.188096805. One held-out N50 check was within the predeclared 2% tolerance, but outside the earlier incomplete sensitivity range. This does not establish a universal hardware conversion factor or an extrapolation to other configurations.

## Delivery and reproducibility

The accepted 28197 delivery copy retains the exact portable N64 entry and corrected result readers. Its readiness-only repair waits for real model registration and live workers. The model, serving implementation, both semantic routes, official client command and latency limits are unchanged. Frozen code and raw profiling exports, requests, runtime logs, reviews and cleanup evidence accompany the run.

Submission artifacts and slides are in English; the owner-requested Vietnamese learning transcript is a separate exception. The existing theme, gradients and distinct background photographs are retained. The eight HPC slides and their 68 transitive OOXML parts remain protected. Current live HPC files and the existing ZIP's HPC contents are preserved independently because another worker has unpublished folder changes; this AI update does not silently package them.

No organiser upload receipt or organiser quality-evaluation result is recorded here. The local full-set quality comparison is documented above; it does not claim BTC certification. Large artifact recovery metadata is backed up through the private research repository; Git does not upload the sibling external object bytes.

- [Updated presentation](../../submission-review/ai-quality-update-20261103/TripleU_APAC2026_Presentation.pptx)
- [Review PDF](../../submission-review/ai-quality-update-20261103/TripleU_APAC2026_Presentation.pdf)
- [Speaker notes](../../submission-review/ai-quality-update-20261103/PRESENTER_NOTES.md)
- [Current detailed metrics and configuration](../../VNUHCM%20-%20TripleU/AI_Task/logs/measured/latest-results.md)
- [Publication verification](../../submission-review/ai-quality-update-20261103/publication-validation.json)


## Presentation readiness

The current compact AI route targets about 10:50, with a proposed 12-minute rehearsal stop and direct handoff to the independent OpenFOAM presenter. The public rules provide 15–20 minutes for the combined AI/HPC talk plus a separate 10-minute Q&A; earlier AI-only planning is historical. Agree the split with the HPC speaker and test it in a real timed mock. Evidence cards cover request-scoped KV transfer, the repeated backend interaction, N64 selection, direct H100-derived tests on H200 and the accepted packaged-entry replay. Each separates observation, hypothesis, supported conclusion and missing evidence.

The revised slides make previously compressed reasoning explicit: transport recovery and output rejection, reverse-order startup confirmation, role-aware EAGLE debugging, source-guided tokenization/collective tests, controlled regime recovery, and defects exposed by real portable replay. The full shared journal contains independent HPC and administrative records as well as scientific arcs. It is not presented as a count of successes.

- [Journal-to-slide coverage and supporting entry index](JOURNEY_COVERAGE.md)
- [Compact speaking plan and protected OpenFOAM handoff](PRESENTATION_PLAN.md)
- [Three technical evidence cards](EVIDENCE_CARDS.md)
- [Panel Q&A, with observation/hypothesis/unknown distinctions](PANEL_QA.md)


## Historical queue snapshot and terminal-result reconciliation — 31 October 2026

This is the dated 31 October snapshot retained for audit; it is not a live queue statement. Read-only query at **09:54:58 Vietnam time (UTC+7)**: the H200 Slurm queue has no job for this account. All 13 AI allocations in the fresh accounting window starting 29 October UTC are terminal; the latest is 27510. H100/PBS state remains **UNKNOWN** because this machine's existing VPN path is unavailable. No fresh login, DUO request or new job is initiated. [Snapshot and hardware-separated audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-status-audit-20261031/README.md).

The two final jobs were already included in this report, so there is no omitted winning result:

- **27510 (H200):** completed 0:0/13:15; 3029.861122 good output tokens/s, -0.370208% versus 27376. Keep dense graphs. The experiment admission note and main ledger were stale; they now point to the reviewed terminal result.
- **27506 (CPU only):** completed 0:0/95 seconds, zero GPUs/four CPUs; JIT 26.605 seconds, both CPU fixtures pass and native cleanup observed. It is not a Qwen integration or inference score. A terminal review and canonical source-path seal are added. Hashes confirm the four raw artifacts already had byte-identical captured copies in the final delivery.

No selected configuration or slide/submission result changes. H100 2433.019859 and H200 3044.400475 remain separate historical series, not one combined score. Inaccessible newer PBS results cannot be excluded without restored read-only access. [CPU terminal review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cpp-radix-cpu-probe-r2-20261029/RESULTS-27506.md), [sparse GPU review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-sparse-decode-compile-20261029/RESULTS-27510.md).


## Additional H200 verification after the panel's cross-hardware question

31 October 2026: the owner authorised four same-H200 measurements to validate
H100-derived choices. All four completed and passed the full local protocol on
16 H200 / g1,g4. Fresh control 27777 scored 3038.022907 good tokens/s; FA3 decode
27779 scored 2999.245473 (-1.276404%). H100 both-HPC-Ops/chunk 4096 recipe port 27781
at N54 scored 2738.940099; same-load N64 port 27783 scored 2721.815800 (-10.408319%
versus control). Keep the existing H200 DeepGEMM/chunk 8192 prefill plus HPC-Ops/
FlashInfer/MNNVL decode at N64. This does not replace the historical repeated
H200 series or claim a global optimum.

On the transferred recipe, N54->N64 gives no goodput gain while mean TTFT rises
896.156->1591.493 ms and sampled prefill queues increase. Direct per-request
queue/compute/transfer decomposition is absent; the added latency cannot be
causally assigned to one kernel. All four have zero scored errors/cancellations,
smoke 7/8 non-regression and retrieval 12/12. At this 31 October checkpoint, the full-set
quality study had not yet been run. Actual wave 12.671111 GPU-hours, no PBS SU.

The panel-facing lesson is measured: H100 screened compatibility and tradeoffs;
we validated selected alternatives against a fresh H200 control, and retained
the H200-specific recipe after the H100-selected recipe lost. Do not pool GPU
scores, quote a universal conversion multiplier, or attribute this coupled
runner/chunk comparison to one factor. These results are now represented in main slide 14 and the complete final-run ledger in backup 34 of the 1 November edition.

[Complete four-job evidence and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md).


## Additional chunk interaction after the H100 recipe transfer

31 October 2026: native H200 N64 HPC-Ops prefill variants 27804 (chunk 6144) and
27806 (chunk 8192) both pass full local gates at 2821.884862 and 2900.606831 good
output tokens/s. Relative to prior HPC 4096 port 27783, gains 3.676555%/6.568815%
partially recover the earlier loss. Relative to DeepGEMM 8192 control 27777 they
still lose 7.114431%/4.523207%. Keep the H200 incumbent; no new winning score.
The 8192 comparison holds chunk and graph settings fixed and differs in prefill
runner, inactive fallback metadata and generated engine seeds; this narrows the
engineering choice, but it is not a per-kernel causal profile.

Both have zero scored errors/cancellations, 30 TTFT/0 ITL breaches, smoke 7/8
non-regression and retrieval 12/12. Larger chunks coincide with lower prefill
queue means and TTFT; direct queue/compute/transport time is uncollected. At this
31 October checkpoint, the full-set quality study had not yet been run; actual pair 6.062222 GPU-hours, zero PBS SU. At this historical chunk-stage checkpoint only two additional distinct ports had completed; the later phase results below complete the four-intervention set. Raw artifacts, runtime/source checks and cost are preserved. The final deck summarises the decision in main slide 14 and preserves the complete nine-job ledger in backup 34.

[Complete evidence and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/RESULTS.md).


## Final phase-mode transfer results and completed candidate count

31 October 2026: all three native H200 N64 phase jobs completed and replay the
full local source/runtime/KV/semantic/raw/output gates. Explicit no_grad control
27826 scores 3039.167093 good tokens/s; decode-only 27828 scores 3039.356215
(+0.006223%); prefill-only 27830 scores 3043.141258 (+0.130765%). None clears the
prospective 1% useful-gain gate. Keep the current H200 recipe and native default
provider; no unchanged repeat, combined sweep or publication promotion.

Actual common/scheduler hashes and per-role native mode/context/restoration
preflights pass; workers differ only in phase flag exports and resolved native
arguments only in engine seeds. Do not describe the role-launch receipt as a
per-rank steady-state mode or kernel trace. Prefill-only TTFT p95 improves in
one observation, but each arm retains 26 TTFT/0 ITL breaches and the score effect
is small. Zero scored errors/cancellations, smoke 7/8 non-regression and retrieval
12/12. At this 31 October checkpoint, the full-set quality study had not yet been run. Actual phase cost 9.604444 GPU-hours,
zero PBS SU.

Four distinct additional H100-derived interventions have now been reviewed on
H200: 27804/27806 chunk settings and 27828/27830 phase settings; extra 27826 control
is not counted as a candidate. These are intervention transfers into documented
H200-specific bases, not four H100 winners or exact full-recipe reproductions.
Raw data, controls and accounting are preserved. The 1 November presentation update incorporates this final decision and all nine allocations without promoting a subthreshold result.

[Final phase evidence and completed register](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md).
