# TripleU AI task — final research report

The current presentation is an [engineering investigation](FEEDBACK_RESPONSE.md): 16 main AI slides and 16 hidden backups, with complete technical stories and explicit evidence limits. [The 24-page main-talk PDF](../../submission-review/ai-investigation-update-20261030/TripleU_APAC2026_Main_Talk.pdf) goes directly from AI to the eight unchanged HPC pages. Both bilingual guides are remapped; no new scientific result is introduced.

Prepared 30 October 2026, Vietnam time (UTC+7). This report covers the Qwen AI task. The independent HPC task is outside its scope. Research and new job submissions are stopped.

## Result and submission choice

**Recommended submission:** replicated target-only N64 serving on 16 H200, with two TP4/EP1 prefill workers and one TP8/EP8 decode worker. Three historical full runs average **3,044.400475 good output tokens/s**. A later native-runtime full observation reproduces that level at **3,045.501509**; it is a separate series.

**Highest complete local full pass:** job **27378**, **3,048.446289 good output tokens/s**. Its prefill ChunkCache treatment is only **0.240921%** above fresh native control 27376, below the prospective 1% useful-gain threshold. P95 TTFT also worsens. It is an isolated higher point, not a confirmed improvement, so it does not replace the replicated configuration.

**Highest recovered portable raw observation:** job **27145**, **3,055.330517 good output tokens/s**. Both semantic P/D routes and the official GPU client completed, but the original job failed in result-reader path handling. Corrected readers passed actual compute-only job 27152 on both retained datasets. Original failed states remain; a whole-allocation end-to-end replay after the repair is not claimed.

Official full-set model accuracy, requiring at least 99% of the organiser's reference score, remains **UNKNOWN**. Local latency/output checks are not official competition acceptance or a global-optimum claim.

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
- Portable reader repairs preserve the original failed GPU allocations and their recovered raw observations. Compute postprocessing verification is a separate proof.
- Five-second hardware/server samples use a request-start envelope with uncalibrated clocks and incomplete final-drain coverage. GPU activity, sampled VRAM and KV token occupancy measure different things. Missing kernel, hot-thread, Xid/throttle and authoritative generated-token data are not zero or healthy.
- Earlier lower valid replays remain retained. Their difference from later approximately 3k runs is not automatically a causal launcher gain.

## H100 results are separate

The retained H100 individual peak is **2,433.019859 good output tokens/s** at N54; a fresh H100 full control scored **2,399.186728**. H100 uses different hardware and an independently tuned prefill configuration. These values are not directly comparable algorithmic treatments of the H200 peak.

A historical same-configuration N52 calibration produced an observed system ratio of 1.188096805. One held-out N50 check was within the predeclared 2% tolerance, but outside the earlier incomplete sensitivity range. This does not establish a universal hardware conversion factor or an extrapolation to other configurations.

## Delivery and reproducibility

The package retains the portable N64 entry and the corrected result readers. The official model/client command, serving implementation and latency limits are unchanged in this report update. Recent configurations, raw profiling exports, requests, runtime logs and independent reviews accompany the report.

Submission artifacts and slides are in English; the owner-requested Vietnamese learning transcript is a separate exception. The existing theme, gradients and distinct background photographs are retained. The eight HPC slides and their 68 transitive OOXML parts remain protected. Current live HPC files and the existing ZIP's HPC contents are preserved independently because another worker has unpublished folder changes; this AI update does not silently package them.

No organiser upload or new research job is performed. Large artifact recovery metadata is backed up through the private research repository; Git does not upload the sibling external object bytes.

- [Updated presentation](../../submission-review/ai-investigation-update-20261030/TripleU_APAC2026_Presentation.pptx)
- [Review PDF](../../submission-review/ai-investigation-update-20261030/TripleU_APAC2026_Presentation.pdf)
- [Speaker notes](../../submission-review/ai-investigation-update-20261030/PRESENTER_NOTES.md)
- [Current detailed metrics and configuration](../../VNUHCM%20-%20TripleU/AI_Task/logs/measured/latest-results.md)
- [Publication verification](../../submission-review/ai-investigation-update-20261030/publication-validation.json)


## Presentation readiness

The current compact AI route targets about 10:40, with a proposed 12-minute rehearsal stop and direct handoff to the independent OpenFOAM presenter. The official combined time and Q&A inclusion remain awaiting clarification; earlier 15–20-minute AI-only planning is historical. Three evidence cards cover request-scoped KV transfer, the repeated backend interaction and full-protocol N64 selection. Each separates observation, hypothesis, supported conclusion and missing evidence.

The revised slides make previously compressed reasoning explicit: transport recovery and output rejection, reverse-order startup confirmation, role-aware EAGLE debugging, source-guided tokenization/collective tests, controlled regime recovery, and defects exposed by real portable replay. The full shared journal contains independent HPC and administrative records as well as scientific arcs. It is not presented as a count of successes.

- [Journal-to-slide coverage and supporting entry index](JOURNEY_COVERAGE.md)
- [Compact speaking plan and protected OpenFOAM handoff](PRESENTATION_PLAN.md)
- [Three technical evidence cards](EVIDENCE_CARDS.md)
- [Panel Q&A, with observation/hypothesis/unknown distinctions](PANEL_QA.md)


## Final queue and terminal-result reconciliation — 31 October 2026

Read-only query at **09:54:58 Vietnam time (UTC+7)**: the H200 Slurm queue has no job for this account. All 13 AI allocations in the fresh accounting window starting 29 October UTC are terminal; the latest is 27510. H100/PBS state remains **UNKNOWN** because this machine's existing VPN path is unavailable. No fresh login, DUO request or new job is initiated. [Snapshot and hardware-separated audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-status-audit-20261031/README.md).

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
smoke 7/8 non-regression and retrieval 12/12; official full-set quality remains
UNKNOWN. Actual wave 12.671111 GPU-hours, no PBS SU.

The panel-facing lesson is measured: H100 screened compatibility and tradeoffs;
we validated selected alternatives against a fresh H200 control, and retained
the H200-specific recipe after the H100-selected recipe lost. Do not pool GPU
scores, quote a universal conversion multiplier, or attribute this coupled
runner/chunk comparison to one factor. These new results are added to this
working report; the published PowerPoint and ZIP have not been regenerated.

[Complete four-job evidence and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md).
