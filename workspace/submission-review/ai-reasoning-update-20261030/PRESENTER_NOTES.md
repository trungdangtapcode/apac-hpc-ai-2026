# TripleU presenter notes — 30 October 2026

AI slides updated; original HPC notes retained unchanged.

## Slide 1

Reasoning role: RQ1–4 · Problem & constraints. Introduce four research questions and the reasoning cycle used to answer them, rather than a chronology of runs.

We ask how to distribute the GPUs, what performance evidence identifies, which changes help qualifying throughput, and whether the result survives repeated deployment. The recurring cycle is problem, observation, analysis, hypothesis, intervention, causal assessment, and decision.

Observation: The work progressed from resolving the two-node serving topology and KV transfer to phase-specific backend experiments and repeated full-protocol measurements.
Hypothesis: Reliable performance depends on making the deployment and measurement path work end to end before tuning individual kernels.
Conclusion: The presentation will support a reproduced operating point and selected configuration, while distinguishing that evidence from isolated peaks and official accuracy verification.
Unknown: Official full-set model accuracy remains unverified, and the local result is not an official contest ranking.

Speaking brief: We studied four questions: how to divide sixteen H 200 GPUs, what limits the service, which changes improve goodput, and whether results are reproducible. The contribution is the evidence behind our decisions, including failed hypotheses and unresolved quality checks.

The title also states the argument: the distributed system must function correctly before its speed comparisons are meaningful.
Reproduction here means similar results on another run; it does not establish all-platform or all-workload performance.

Research sources: Problem-driven presentation plan; retained research journey

## Slide 2

Reasoning role: RQ1 · Problem & constraints. Define the fixed model, hardware envelope, workload and latency objective before comparing configurations.

Qwen 3-235 B FP 8 runs within two nodes of eight H 200 GPUs. The workload requests 4000 input and 200 output tokens. More raw output is useful only if each request qualifies under both latency limits and the total qualifying fraction is at least 90%.

Observation: The benchmark fixes the request size and applies a joint per-request latency rule; errors count against the service. Goodput is based on requests passing both limits.
Hypothesis: A system that produces more raw tokens can still be worse if too many requests violate first-token or token-spacing requirements.
Conclusion: We judge candidates by qualifying throughput together with the latency and output gates, not by a single mean or raw token count.
Unknown: The table defines the protocol but contains no candidate measurement; it does not show any configuration's actual latency distribution.

Speaking brief: Our fixed problem is Qwen 3-235 B on two eight-H 200 nodes. Requests contain 4000 input and 200 output tokens. At least 90% must meet both first-token and token-gap limits. We optimize qualifying output tokens per second, not unrestricted aggregate throughput.

Read each arrow as the preferred direction: latency down, qualifying share and goodput up.
Both TTFT and mean ITL limits must pass on the same request for it to count as qualifying.
The 90% threshold applies to the proportion of all evaluated requests, not just successful requests.

Research sources: Qwen task rules and 25 September addendum

## Slide 3

Reasoning role: RQ1 · Baseline & observation. Use the topology campaign as evidence for a feasible resource decision, not as the storyline.

A wider tensor-parallel worker divides one model over more GPUs, reducing the number of replicas that fit into a fixed GPU budget. More replicas can serve independent requests, but each has less GPU memory and a different communication cost. Candidates must load compatible FP 8 shards, complete transfer and answer correctly before scores matter.

Observation: The selected split reached 1912.30 good tokens/s at N48 in this early topology sample, after displayed N32 and N40 configurations reached 1297.02 and 1666.01. Overall, the recovery ledger counted 14 original layouts plus three EP2 replacements.
Hypothesis: A balanced allocation of prefill replication and decode parallelism could better serve the chosen request concurrency.
Conclusion: These trials established a usable architecture to develop. They are initial operating points, not a clean causal ranking because load and transport history varied.
Unknown: The slide does not show all 17 configurations or confidence intervals; it cannot isolate which topology change caused the score differences.

Speaking brief: Seventeen usable configurations support the topology decision. The selected split reached about 1912 qualifying tokens per second at 48 concurrent requests. Because loads differ across layouts, the evidence identifies a feasible choice rather than a globally optimal topology.

Compare rows horizontally across role topology, concurrency N, and good output tokens per second.
N rises from 32 to 40 to 48 across these illustrative rows; the measurements also differ in load and transport history.
The summary counts usable measured configurations; it does not say all attempted originals passed.

Research sources: 22197; 22219; 22415; prior topology campaign

## Slide 4

Reasoning role: RQ1 · Conclusion from topology evidence. Explain the technical tradeoff behind retaining two TP 4 prefills and one TP 8/EP 8 decode, without inventing a one-factor topology speedup.

The first node holds two prefill workers of four GPUs each; the second has one eight GPUdecode worker. All tensor-parallel groups stay within a node. Separating phases lets each use a suitable implementation, but requires KV transfer. This is a measured usable split; the historical layout table alone does not isolate the contribution of each architectural change.

Observation: The selected layout allocates two TP4/EP1 prefill workers on Node 0 and one TP8/EP8 decode worker on Node 1; the request's KV state must cross between roles.
Hypothesis: Separating prompt processing from generation can let each phase use a fitting topology, but adds a correctness- and startup-sensitive transfer path.
Conclusion: Round-robin routes requests to a prefill worker, and decode produces all generated tokens. The diagram defines the experiment's architecture, not a measured performance benefit by itself.
Unknown: The drawing does not quantify network bandwidth, transfer latency, utilization or the causal advantage over a unified deployment.

Speaking brief: We retain two four-GPU prefill workers and one eight-GPU decode worker. This keeps tensor-parallel groups within nodes and allows phase-specific implementations. KV transfer must work correctly; the historical scores do not isolate a one-factor architectural speedup.

Read from left to right: requests are processed for prefill on either P0 or P1, then KV data moves to D0 for generated output.
Each prefill worker is TP4/EP1; the decode worker is TP8/EP8. The TP groups stay within their node.
Orange squares and arrows are visual role cues in this slide, not a general chart color key or evidence of traffic volume.

Research sources: Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents

## Slide 5

Reasoning role: RQ1 · Observation → validity check. Establish the observed failure before explaining the proposed fix. Workers had loaded, but the actual heterogeneous prefill-to-decode path had not become ready for a benchmark request. This separates a startup/transfer symptom from an assumed steady-state performance problem.

Tell the audience this slide represents the baseline stage of the seven-step reasoning chain: symptom, job evidence, and failure boundary. The title's contrast is literal: model workers were ready, while pair warmup was not. No numeric chart or axes are implied.

Observation: Job 22271 loaded the model workers but its heterogeneous P/D warmup request timed out after 360 seconds. The retained log ends in HTTP TimeoutError; AIPerf did not run, so there is no score.
Hypothesis: The immediate failure lies somewhere in cold P/D bootstrap or transfer readiness; a specific descriptor bottleneck is not yet established by this symptom alone.
Conclusion: Treat this as a pre-benchmark readiness failure and preserve the exact topology and terminal evidence. Do not call it a throughput regression.
Unknown: The timeout alone does not locate the stalled work, quantify transfer latency, or rule out other bootstrap and placement causes.

Speaking brief: In job 22271, H200 workers loaded, but the P-to-D pair warmup timed out after 360 seconds. No AIPerf benchmark ran, so this is a transfer-readiness failure, not a throughput measurement.

Step 1 — Symptom: the client could not complete pair warmup, even though workers had loaded.
Step 2 — Evidence and boundary: job 22271 timed out after 360 seconds with HTTP TimeoutError; no AIPerf export or throughput score exists.
The topology is heterogeneous TP: P8 TP8/EP2 to D8 TP4/EP4. It is not the two-TP4 prefill plus TP8/EP8 decode topology selected later.
The contemporaneous review says bootstrap/transfer was not yet proven. It does not identify bandwidth saturation or a measured slow KV copy.

Research sources: TOPOLOGY_REVIEW.md; 22271 pair-warmup.log; 22294; recovery ledger

## Slide 6

Reasoning role: RQ2 · Bottleneck analysis. Put observations before optimizations and separate suspected performance limits from a proven bottleneck.

The separate N 48 profile records matrix work, communication/normalization and attention. Their summed kernel durations suggest trial targets; they are not wall-time shares because kernels can overlap. A later N 64 run has TTFT-only failures, but no complete queue/prefill/transfer breakdown explains them. These evidence types concern different runs.

Observation: Three named groups account for stated shares of recorded kernel duration.
Hypothesis: Large recorded groups may guide next experiments.
Conclusion: Use profile as a hypothesis source, not an end-to-end explanation.
Unknown: Wall-time shares, overlap effects, FLOP saturation and causality are unknown.

Speaking brief: The separate N48 profile assigns about 23.48% of summed kernel duration to communication and normalization. That suggests experiments, not a wall-time bottleneck percentage. Later N64 first-token failures also lack a complete causal time breakdown.

Named decode groups are HPC group GEMM 21.642%, MNNVL collective/RMSNorm 23.479%, and FlashInfer paged attention 15.064% of summed recorded kernel duration. These percentages are descriptive sums, not shares of end-to-end wall time: kernels can overlap and the trace covers only recorded activity. Terms: GEMM is matrix multiplication; MNNVL is a communication backend; RMSNorm normalizes hidden activations; rank is one distributed process. The three groups suggest questions about MoE implementation, communication strategy, and phase-specific attention backend. They do not predict equivalent speedups, prove FLOP saturation, or causally explain N58/N60 service results. Keep the N48 diagnostic distinct from the N58 repeat. Hypothesis: large recorded groups deserve follow-up. Conclusion: use traces to design a controlled full-service test. Unknown: per-request phase attribution and causal latency shares.
A profile is instrumentation: it records selected activity while a workload is running. The percentages sum kernel durations across recorded ranks/GPUs. Because kernels overlap and because queueing, CPU work, communication gaps, and unrecorded activity also consume elapsed time, those percentages cannot be read as the fraction of a request spent in each component. The N48 diagnostic was separate from the N58 deployment repeat.

Research sources: 24819 sealed traces; H200_PROFILE.md; observability correction

## Slide 7

Reasoning role: RQ2 · Prioritisation & hypothesis. Explain the prioritization decision: the symptom occurred before scoring, and source inspection exposed a large amount of descriptor setup work aligned with the cold-warmup failure. This is a reason to test the setup hypothesis, not proof that other bottlenecks were absent.

Present the evidence chain as seven-step flow steps 3 and 4: identify the affected component, then state why its setup cost was prioritized. The two counts have different scopes—whole pool per rank versus one request—so they must not be shown as a timing ratio or speedup.

Observation: Source-backed geometry showed a very large whole-pool enumeration signal—about 403.8 million descriptors per source rank—compared with 188 coalesced ranges for one representative request.
Hypothesis: Building descriptors only for the pages of the current request could reduce cold setup work and help pair warmup complete.
Conclusion: Descriptor setup was a rational first target because it matched a pre-benchmark symptom and had a concrete source-level cost signal. This is prioritization, not diagnosis of the sole cause.
Unknown: No old-code initialization duration was measured. Bandwidth utilization, KV layout, scheduling/placement, and other bootstrap work remain possible contributors.

Speaking brief: Source review found about 403.8 million whole-pool descriptors per source rank, versus 188 for one contiguous 4,000-token request. That justified testing setup work first, but did not rule out bandwidth or placement causes.

Step 3 — Component: source inspection located the affected work in heterogeneous-TP NIXL KV descriptor preparation and transfer.
Step 4 — Evidence to prioritize: source notes derive about 403.8 million descriptors for the full pool per rank, while CPU geometry gives 188 descriptors for one contiguous 4,000-token request.
Those values count descriptors, not bytes, seconds, bandwidth, or speed. Their scopes differ and they do not quantify setup time.
Because the failure was pre-score and the proposed work targeted setup, this was more directly supported than first tuning steady-state bandwidth, KV layout, or scheduler placement. These alternatives were not experimentally ruled out.

Research sources: nixl-ondemand/README.md; nixl-ondemand.patch; metadata.json; geometry-test.json;22271

## Slide 8

Reasoning role: RQ3 · Hypothesis → intervention. Ask whether attention and collective-communication choices work better together than separately at a fixed H200 load. The comparison is a motivation for a combination, not proof that independent component gains add up.

Interpret the N52 observations as separate backend configurations at one load: FlashInfer alone 2,440.386, MNNVL alone 2,592.162, the combined choice 2,631.085, and a later MNNVL control 2,594.028 good tokens/s. Compare the combination with the later same-load MNNVL control: about +1.43%.

Observation: The combined observation exceeds the later MNNVL control by about 1.43% at H200 N52; standalone FlashInfer and MNNVL observations are lower.
Hypothesis: The attention and communication choices may interact favorably when used together.
Conclusion: The measured combination is promising at this load and merits comparison as a complete serving setting.
Unknown: The result does not quantify component-level causal gains or establish behavior at another load, model, or hardware setup.

Speaking brief: At H200 N52, combining attention and communication measured about 1.43 percent above a later MNNVL control. This supports the combined setting at this load, not additive component gains or a universal rule.

Question: does choosing both an attention implementation and a communication backend improve the service? At H200 N52, the standalone and combined observations are 2,440.386, 2,592.162, and 2,631.085 good tokens/s. A later MNNVL control at the same load is 2,594.028; the combined observation is approximately 1.43% higher than that control.
The evidence supports testing or retaining the combined operating point for this configuration. It does not establish a general interaction law, isolate each backend's causal contribution, or permit adding the standalone differences as if the components were independent.

Research sources: 23777; 23778; 23904; 23974

## Slide 9

Reasoning role: RQ3 · Matched measurement → causal limits. Evaluate a decode-runner change using complete-service outcomes. A matched control asks whether the treatment changed goodput at this configuration; the latency rows show the cost of that gain.

Compare fresh auto-decode control 24912 with HPC-Ops decode repeat 24913 at the same full N60 configuration. Goodput rises from 2,838.853 to 2,989.175 tokens/s; mean TTFT rises 822.292→947.627 ms, mean request-mean ITL falls 16.579→14.934 ms, and joint SLA changes 98.7599%→98.8178%.

Observation: Goodput rises 5.295% and ITL improves, but mean TTFT increases about 125 ms; a separate treatment deployment reproduces nearly the same goodput.
Hypothesis: The decode-runner change may improve useful throughput in this configuration while changing the latency balance between first token and later tokens.
Conclusion: The matched full result and independent treatment repeat support this H200 N60 operating point.
Unknown: Exact kernel-level cause, queue/compute attribution, broad hardware generalization, and official full-set model quality remain unverified.

Speaking brief: At H200 full N60, the decode change raises goodput 5.295 percent and lowers ITL, but mean TTFT rises about 125 milliseconds. A treatment repeat is close; the claim remains specific to this setup.

The control-to-treatment goodput increase is 5.295%. Mean TTFT increases 125.335 ms, while mean request-mean ITL decreases 1.644 ms. The joint SLA rate changes only slightly upward. The treatment repeat 24913 is 0.033% below original treatment 24738 at 2,990.151 tokens/s.
The result supports a repeatable interaction between the decode runner and this H200 N60 service setting. It does not establish a universal HPC-Ops advantage. The older 24913 extended inspection lacks a dedicated continuous hardware telemetry series; a separate N48 kernel profile cannot causally explain this N60 result.

Research sources: 24912/24913 full reviews; 24738 original treatment

## Slide 10

Reasoning role: RQ3 · Intervention & full measurement. Choose a useful concurrency point with a full-protocol control and an independent N64 repeat, while resisting a larger but unconfirmed short-screen result.

Read three columns: N62 control 25365; N64 candidate 25366; N64 repeat 25373. Goodput is 3,011.875 / 3,044.490 / 3,044.075 tokens/s. The full N64 gain over N62 is 1.082867%; the N64 repeat is only 0.013634% below the candidate. TTFT rises modestly, ITL is nearly stable, SLA is slightly lower, and errors/cancellations are zero.

Observation: N64 gains about 1.083% goodput over N62 and repeats within 0.014%; TTFT rises modestly, SLA dips slightly, and ITL is nearly unchanged.
Hypothesis: Moderately higher client concurrency may increase pipeline utilization enough to improve throughput.
Conclusion: Keep N64 as a reproduced operating point; do not choose the short-screen N68 result over full evidence.
Unknown: These runs do not separate queueing, transfer and compute effects, establish a confidence interval, or find a global optimum.

Speaking brief: N64 improves full goodput 1.083 percent over N62 and repeats within 0.014 percent. TTFT rises modestly. N68’s short-screen advantage shrinks to 0.083 percent in a full pair, so N64 is the supported stopping point.

Full N62 control 25365 versus N64 candidate 25366 gains 1.082867%. Independent N64 run 25373 reaches 3,044.075 tokens/s, 0.013634% below the candidate. The two N64 runs sampled the same GPU UUID set, limiting hardware diversity and not providing a confidence interval.
Mean TTFT is 1,037.630 ms at N62 and 1,110.463 ms at N64; mean ITL changes from 14.958 to 15.003 ms. Joint SLA is 98.7227% versus 98.6330%, with zero errors/cancellations. N68's favorable short screen did not persist: the full pair gain is only 0.083056%.

Research sources: 25365/25366 matched full proof; 25373 replication and telemetry

## Slide 11

Reasoning role: RQ3 · Evidence & unresolved cause. Move from averages to request-level acceptance. The scatterplot reveals that every observed miss is on TTFT, while explicitly preserving the distinction between an association near admission and a causal explanation.

Each point is one request: x is time to first token (TTFT, ms), y is that request's mean inter-token latency (ITL, ms). Red vertical/horizontal thresholds are 3,000 ms TTFT and 20 ms ITL. Dark teal #23373B (may appear blue-green) jointly passes; orange #EB811B (may appear yellow) misses at least one. Pale green marks TTFT only, not joint acceptance. Dark overlap is alpha rendering, not a separate class.

Observation: 1,875/1,902 requests jointly pass; all 27 misses are TTFT-only, with no request errors/cancellations.
Hypothesis: Requests arriving at the beginning of the scored profile may face a distinct startup/admission effect.
Conclusion: The distribution shows the remaining acceptance gap is first-token tail behavior in this run.
Unknown: The timing association does not identify whether queueing, prefill, KV transfer, or computation caused the TTFT misses.

Speaking brief: This H200 N64 scatterplot shows 1,875 of 1,902 requests pass both limits. The remaining 27 miss TTFT only. Their timing near profile admission is a clue to investigate, not proof of the cause.

The full native-runtime job 26766 produces 3,045.501509 good output tokens/s. Of 1,902 profiled requests, 1,875 (98.580%) meet both limits. The 27 failures miss TTFT; none miss request-mean ITL, and there are zero request errors or cancellations.
Mean/p95 TTFT is 1,108.869/1,311.693 ms; mean/p95 ITL is 15.0075/15.1930 ms. All 27 misses start within 13.004085 ms of profiling admission. This timing is an initial-cohort association, not proof that startup, queueing, prefill, transfer, or compute caused the misses.

Research sources: 26766 raw profile, independent full review and sealed native-runtime payload

## Slide 12

Reasoning role: RQ3 · Evidence → keep or reject. This is a decision table, not a single experiment or a hardware comparison. It brings together three independent H200 intervention results and one separate H100 attention result. Each row compares the tested change with its own control and applies the useful-gain rule.

Read four evidence groups independently: H200 prefill cache 27376→27378 gains 0.240921%, below the prospective 1% useful threshold; H200 sparse decode graphs reduce capture memory 1.15→0.36 GB/rank but lose 0.370208% goodput; a separate H100 N54 FlashInfer→FA3 decode pair lowers TTFT 118.922 ms but loses 0.812% goodput. Do not compare their raw throughputs as one experiment.

Observation: The cache result is +0.240921%, sparse graphs save capture memory but lose 0.370208% goodput, and H100 FA3 reduces TTFT while losing 0.812% goodput.
Hypothesis: Cache, graph capture, or attention changes might improve one resource or latency metric without damaging the service objective.
Conclusion: Keep the replicated N64/cache setting; retain dense graphs and FlashInfer decode for the measured settings. None of these interventions meets its adoption criterion.
Unknown: The three results do not share a control or hardware; their effects cannot be added, ranked by raw score, or generalized beyond each setup.

Speaking brief: Three separate interventions improve a secondary metric but fail their service adoption rule: H200 cache gain is below 1%, sparse graphs lose goodput, and H100 FA3 loses goodput despite faster TTFT. Their results cannot be combined.

H200 cache pair: fresh control 27376 scores 3,041.119598; candidate 27378 scores 3,048.446289, a +0.240921% difference. Candidate passes local request/output gates (1,879/1,905 joint requests; zero errors), but does not pass the prospective >1% useful-gain decision threshold.
H200 sparse graph job 27510 scores 3,029.861122 versus control 27376 at 3,041.119598, or −0.370208%. Decode graph-capture memory falls from 1.15 to 0.36 GB per rank; this resource reduction does not improve goodput. Separately, H100 N54 FA3 lowers mean TTFT by 118.922 ms but raises ITL and mean request latency; goodput falls 0.812%. These are distinct trials on distinct hardware, with separate controls.

Research sources: 27376/27378;27510;H100222027/222028

## Slide 13

Reasoning role: RQ3 · Failed hypothesis → revised test. Trace the full EAGLE3 reasoning chain: a placement hypothesis, a validator defect, a corrected short retry, and a separate full test. Repairing a measurement tool makes a rerun valid; it does not turn a losing performance result into a win.

Read stages in order: all-worker draft 25948 fails the joint latency gate; decode-only attempt 25988 is rejected because the validator expects draft KV regions on target-only prefill; repaired short run 25998 passes its limited protocol but loses 4.74% goodput; separate shallow full run 27238 loses 2.080318% versus control 26949.

Observation: After validator repair, the short decode-only retry loses 4.74%, and the distinct shallow full trial loses 2.080318% goodput.
Hypothesis: Restricting draft execution to decode or using a shallow draft may reduce TTFT without sacrificing total service throughput.
Conclusion: The tested variants do not solve this workload; close them while preserving the tooling failure and repair history.
Unknown: The observations do not explain precisely which service phase causes the slowdown, nor rule out every possible speculative configuration.

Speaking brief: EAGLE3 placement missed latency; a validator bug was repaired; the short retry and separate full shallow trial both lost goodput. The tested method therefore did not help this workload, although other configurations remain untested.

The initial all-worker trial 25948 misses the joint latency gate. Moving the draft to decode-only was hypothesized to reduce first-token delay. Attempt 25988 is then rejected by a validator that wrongly applies draft KV-region counts to target-only prefill; the role-aware repair preserves the original failure.
Short retry 25998 passes its limited protocol but loses 4.74% goodput against its own target-only control. Later full shallow run 27238 reaches 2,971.628430 versus control 26949 at 3,034.761104, a 2.080318% loss. Low draft acceptance is descriptive telemetry, not a causal timing explanation.

Research sources: 25948;25988 role-aware KV repair;25947/25998 short review;26949/27238 full shallow review

## Slide 14

Reasoning role: RQ4 · Reproducibility & selection. Distinguish replicated operating points from isolated peaks and from a later software-runtime series. Selection rests on repeatability and the declared useful-gain rule, not the largest number on the slide.

Three historical complete N64 runs 25366/25373/25487 average 3,044.400475 good tokens/s. Native-runtime job 26766 is a separate complete result at 3,045.501509 and 98.580442% joint SLA. Cache candidate 27378 is numerically higher at 3,048.446289, but its matched fresh control 27376 is 3,041.119598, making the gain only +0.240921%, below the >1% useful threshold.

Observation: Historical N64 repeats average 3,044.400475; native job 26766 is similar but separate; cache job 27378 is only +0.240921% above its own fresh control.
Hypothesis: A repeated point is a more defensible selection basis than the highest isolated observation.
Conclusion: Retain replicated N64 and do not select the small cache difference as a useful gain.
Unknown: No result establishes a global optimum, cross-runtime causality, organiser ranking, or official model quality.

Speaking brief: Three H200 full N64 runs average 3,044.40. The native-runtime result is separate. A higher cache score gains only 0.24 percent against its own control, below the useful threshold; recovered raw output from a failed job is not a complete successful repeat.

The three historical N64 full runs average 3,044.400475 good tokens/s and support choosing N64 for replication. Native-runtime 26766 separately reaches 3,045.501509 and 98.580442%; do not pool it with the historical trio because the server runtime path differs.
The highest complete cache candidate 27378 reaches 3,048.446289, but relative to its own fresh control 27376 at 3,041.119598 the gain is +0.240921%, below the >1% useful threshold. The numerical high is not a confirmed useful improvement. A recovered portable raw score of 3,055.330517 came from job 27145, whose scheduler job failed during postprocessing; it is not a successful whole-allocation repeat.

Research sources: 25366/25373/25487;26766;27376/27378

## Slide 15

Reasoning role: RQ4 · Robustness & confounder checks. Investigate a discrepancy rather than explain it with a convenient single flag. The evidence identifies changed settings and measurement context, but the completed comparison does not isolate one sufficient cause.

The question is why historical full N64 averaged 3,044.400475 while a newer short control was about 2,560. Show that ServerArgs differ in prefill graph policy and max-running-request cap, and that harness/observation protocol also differs. Exact legacy replay 26313 reaches 2,830.923547; new native run 26766 reaches 3,045.501509. These rows are different runtime/protocol series, not a clean single-factor ladder.

Observation: Scores vary across the historical full series, short control, legacy replay, and native runtime; several settings and measurement conditions changed together.
Hypothesis: Changed graph policy, server admission cap, runtime, or measurement harness could contribute to the observed drift.
Conclusion: Retain the lower valid result and label its protocol/runtime; no single-factor explanation was established.
Unknown: The factorial evidence did not isolate one causal factor sufficient to explain the historical-to-new score difference.

Speaking brief: Historical full N64 averaged 3,044.40 while a newer short control was about 2,560. Graph policy, server admission cap and measurement procedure changed. The completed tests did not isolate one cause, so we retain the drift without attributing it to one flag.

The historical full N64 mean is 3,044.400475, while a later short control is approximately 2,560. Actual ServerArgs show a changed prefill graph policy and max-running-request cap; harness and observation conditions also differ.
An exact legacy operational replay 26313 reaches 2,830.923547, and native-runtime full run 26766 reaches 3,045.501509. The completed graph/admission factorial did not identify one useful cause. Therefore neither restoring one flag nor changing the launcher alone can be credited for the whole score difference.

Research sources: Incumbent recovery plan;26313 legacy full result;graph/admission factorial;26766 native full review

## Slide 16

Reasoning role: RQ4 · Frozen forecast → held-out evidence. Evaluate one cross-platform forecast without changing it after seeing the test result. The evidence supports a single nearby operational check, while exposing that the earlier sensitivity range omitted a source of predictive uncertainty.

At the same N52 combo, the H100 mean is 2,215.460 good tokens/s from two allocations and the H200 mean is 2,632.181 from four; ratio H200/H100 = 1.188096805. This ratio was used with the H100 N50 mean to freeze an H200 N50 prediction of 2,642.244. Held-out job 24272 measures 2,601.629, signed error −1.5371%, within a predeclared team tolerance of ±2% but outside the earlier input-only sensitivity range.

Observation: One held-out H200 N50 result is 1.5371% below prediction: within ±2% tolerance but outside the incomplete sensitivity range.
Hypothesis: The N52 ratio may transfer well enough to forecast a nearby N50 H200 operating point.
Conclusion: This single prospective check passes the team's operational tolerance; retain the missing-model-error limitation.
Unknown: Prediction accuracy across more loads/configurations, complete uncertainty, and any universal H100-to-H200 conversion remain unknown.

Speaking brief: The N52 H200/H100 ratio is 1.1881. A forecast frozen before H200 N50 measured −1.5371 percent error, inside the team’s ±2 percent tolerance but outside an incomplete sensitivity range. One check does not validate a universal conversion.

At N52, H100 averages 2,215.460 tokens/s across two allocations and H200 2,632.181 across four. Their ratio, 1.188096805, is a local system association for the same combo, not a universal hardware multiplier. Allocation repeats do not prove unique physical hardware.
Before H200 N50 job 24272 was available, the prediction was frozen at 2,642.244 good tokens/s. The measured result is 2,601.629, signed error −1.5371%, within the team-set ±2% operational tolerance. However, the result falls outside the earlier sensitivity range because that range varied inputs but omitted model error. The factor is not refit, and broad predictive reliability is not established.

Research sources: H100221052/221058;H20023904/23973/23975/24174;frozenforecast;held-out24272

## Slide 17

Reasoning role: RQ4 · Quality boundary. Separate service performance from model quality. Meeting request latency criteria answers whether the service responds quickly enough; it does not establish whether generated answers meet the organiser's full-set quality threshold.

Read three evidence levels: H200 job 26766 joint latency success 98.580442%; team-run smoke checks 7/8 with no new regression and retrieval checks 12/12; official quality requirement at least 99% of reference remains unverified. The local checks are small regression probes, not the required full quality evaluation.

Observation: Latency acceptance and small regression checks pass at their stated scope; official full-set quality was not verified.
Hypothesis: Keeping model changes separate from serving changes helps measure throughput without conflating it with answer-quality effects.
Conclusion: Report service latency and official model quality as separate questions; claim only the measured latency result.
Unknown: Whether the system reaches at least 99% of reference on the official full evaluation remains unknown.

Speaking brief: H200 N64 passes its joint latency rule on 98.580 percent of requests. Small checks do not verify the separate official requirement of at least 99 percent of reference, so model quality remains unknown.

Full N64 job 26766 reaches 98.580442% joint latency success. The team-run smoke suite is 7/8 with no newly detected regression; retrieval is 12/12. These small suites do not estimate the organiser's full-set score.
The required quality gate is at least 99% of reference on the official evaluation, and it remains unknown. The selected primary retains FP8 weights and BF16 activation/KV; it does not use quantized KV or speculative decoding. No organiser-issued accuracy certificate or ranking follows from this latency result.

Research sources: 26766 full gate; official Qwen rules and goodput clarification

## Slide 18

Reasoning role: RQ4 · Real replay & failure analysis. Distinguish successful GPU inference from successful end-to-end packaging. Two real portable allocations completed serving but failed while readers located and interpreted result files; a later CPU-only replay verified the reader repair, not a repaired full allocation.

Trace the pipeline in order: real portable jobs 27136 and 27145 ran the official GPU client and both semantic P/D routes, then failed in result processing. First repair handled exports nested in an immediate child directory; second canonicalized the input root where /scratch/home and /home paths referred to the same files. Actual zero-GPU compute job 27152 passed both repaired readers on both real datasets. Keep original scheduler states FAILED.

Observation: Two real GPU jobs completed inference and client work but failed in result reading; CPU-only job 27152 verified both reader fixes on real outputs.
Hypothesis: The deployment's remaining failure was caused by file-layout and path-alias assumptions in post-processing, rather than serving execution.
Conclusion: The precise reader defects were repaired and verified against actual datasets; the full post-repair deployment remains unverified.
Unknown: Whether a complete new allocation would pass launch, inference, export, reading, and all gates after the fixes is unknown.

Speaking brief: Two real H200 portable jobs completed serving but failed during result reading. A zero-GPU job verified reader fixes on real exports. This does not establish a successful full deployment after repair; the original jobs remain failed.

Real H200 portable jobs 27136 and 27145 completed both serving routes and the official client, but the scheduler jobs failed during post-processing. In 27136, AIPerf 0.12 placed exports in an immediate child directory; the first fix handled that layout. In 27145, lexical /home and canonical /scratch/home paths caused an alias mismatch; canonicalizing the root fixed the second issue.
Zero-GPU job 27152 then ran the corrected readers on both real datasets and passed. Raw 27145 score 3,055.330517 is recoverable evidence from the failed original job, not a successful whole-allocation rerun after repair. No post-repair full GPU deployment is claimed.

Research sources: 27136 nested export failure;27145 canonical alias failure;27152 actual compute reader verification

## Slide 19

Reasoning role: Conclusion · Answer the research questions. Answer the four questions with decisions and the boundary of their supporting evidence.

The layout is a usable 16 H 200 decision, profiles suggest rather than prove universal limits, matched useful service gains are retained, and repeatedN 64 measurements support an operating point. Unknown quality, limited hardware diversity and unfinished full portable replay keep robustness claims bounded.

Observation: Historical N64 mean is replicated; cache point gains 0.240921%; native path is separate.
Hypothesis: A reproduced point is a safer selection basis than isolated peak.
Conclusion: Retain N64; do not select for the main configuration the small cache gain.
Unknown: Global optimum, official quality and causal runtime differences are unknown.

Speaking brief: Our four decisions follow evidence: keep a usable layout, test suspected limits, retain measured service improvements, and require repeat results. Historical N64 averages about 3044 qualifying tokens per second; official quality and complete repaired deployment validation remain open.

Later native-runtime job 26766 independently reaches 3,045.501509 and 98.580442% joint SLA; keep it separate because runtime path differs. Highest full cache result 27378 reaches 3,048.446289, only +0.240921% over fresh control 27376, below useful-gain gate. Lower valid replays around 2,802–2,831 remain retained. Replication supports choosing N64, not a global optimum. No speculative speedup, official quality certificate, or causal native-runtime speedup is claimed.
Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
The historical mean and the native-runtime score are both team-run, fully reviewed measurements on the assigned accelerator cluster; “reviewed” means raw request/runtime checks were inspected, not that the organiser certified a ranking or quality score. The native runtime is the software execution environment, not a new GPU generation. Keep its 3,045.501509 separate from the three-run historical mean because the runtime paths differ. A numerically higher cache result is not selected when its gain is below the predeclared useful-change threshold.

Research sources: Four research questions; matched full runs; independent reviews

## Slide 20

Reasoning role: Conclusion & next iteration. Make future validation follow the unresolved claims, rather than suggesting more trials merely to raise the headline score.

Official full-set quality would establish whether the accuracy requirement holds. A fresh complete portable replay would test deployment after reader repair. A compatible model path and bounded phase timing would be required before claiming compilation or bottleneck improvements. These are proposals, not accepted jobs.

Observation: The selected N64 service has repeated full-run evidence; several optimization trials did not show useful gain. Accuracy and post-repair portable replay remain open.
Hypothesis: Path-specific runtime and output checks can prevent unsupported deployment claims.
Conclusion: Keep the reproduced service and treat the listed validation as future work, not as completed or queued research.
Unknown: Official accuracy, full deployment behavior after reader repair, and a compatible compiled RoPE/KV path remain unknown.

Speaking brief: The next iteration should close evidence gaps: official model quality, a complete packaged replay after reader repair, and phase timing before another bottleneck claim. We retain the repeated 64-request service meanwhile. These are proposed validation tasks; no new experiment is being launched as part of this report.

Retain the replicated target-only N64 configuration rather than the highest isolated score. Cache, cap, and polling changes showed no useful gain; the tested shallow EAGLE configuration lost; sparse graph candidate goodput was 0.370208% below the earlier control.
Any new implementation should show the intended backend active, correct KV movement, and valid outputs before its performance score is interpreted. CPU fixtures or source inspection alone do not satisfy that standard.

Research sources: Reviewed research journey through30October2026; exact source and terminal-run audits

## Slide 21

Reasoning role: Backup · Environment. Set the comparison boundary for all later platform results: a shared model and client make experiments more comparable, but do not erase differences in hardware or deployment stack.

The table contrasts allocation, scheduler, container launcher, serving/client software, and model. Matching rows are useful controls: both systems have two eight-GPU nodes and use the same staged artifacts and Qwen3-235B FP8 checkpoint. Different rows are potential influences on latency and throughput. Slurm and PBS schedule resources; they do not execute model inference. Pyxis/Enroot and Singularity provide different container launch paths, while SGLang serves requests and AIPerf generates and measures client traffic. Therefore a score needs its platform, topology, backend, and load attached.

Observation: Both sites provide sixteen GPUs across two nodes and share staged images and model checkpoint, while GPU family, scheduler, launcher, and host environment differ.
Hypothesis: Matching the model and request workload is necessary, but platform differences may still affect serving measurements.
Conclusion: Report each platform's results separately and name its deployment conditions.
Unknown: This table does not isolate the effect of any one platform difference or define an H100-to-H200 score multiplier.

Speaking brief: Both systems allocate sixteen GPUs and use the same Qwen checkpoint and staged workload. Firmus uses H200s; NSCC uses H100s. Different hardware, schedulers, containers, and node conditions mean their scores are separate measurements, not a direct GPU conversion.

Common controls are the two-node, sixteen-GPU allocation, the staged serving and client artifacts, and the Qwen checkpoint.
Platform differences include H200 versus H100 GPU generation, Slurm versus PBS, and different container launchers. CPU, driver, network, node cache, and process placement can also differ.
The table establishes context; it does not provide a controlled performance result or quantify each site's contribution.

Research sources: Qwen rules; NSCC asset contract; matched-anchor audit

## Slide 22

Reasoning role: Backup · Compatibility mechanism. Teach a concrete compatibility failure from the model's weight geometry and distinguish a layout that can load from a deployment that has passed service tests.

Start with the MoE intermediate dimension, 1,536 elements, then divide by the effective tensor-parallel split. TP8/EP1 gives 1,536 ÷ 8 = 192. The tested kernel needs whole 128-element FP8 blocks, so 192 becomes one full block plus 64 unusable remainder elements. TP8/EP2 changes effective MoE tensor parallelism to four: 1,536 ÷ 4 = 384, exactly three full blocks. The red remainder marks a load-time compatibility failure, not lost output tokens. The arithmetic explains why the old shape failed and why the replacement shape is compatible; it is not a benchmark chart.

Observation: TP8/EP1 yields a 192-element partition, not divisible into 128-wide blocks; TP8/EP2 yields 384 elements, exactly three blocks.
Hypothesis: Changing expert partitioning can make the existing FP8 weights compatible with the kernel while retaining the model contents.
Conclusion: EP2 corrects the tested block geometry and makes a compatible deployment attempt possible; this combined layout change is not an isolated TP speedup.
Unknown: Alignment alone does not establish successful full startup, request SLA, output quality, or improved throughput.

Speaking brief: The failed TP8/EP1 partition had 192 elements, which leaves a 64-element remainder against a 128-wide FP8 block. EP2 changes the effective split to 384 elements, or three full blocks. That fixes this shape mismatch; it does not prove serving speed or quality.

The two equations are the key evidence: TP8/EP1 produces 192 elements; TP8/EP2 produces 384.
The 64-element remainder is why the first tested path failed during loading. EP2 removes that remainder by changing expert distribution, not precision or model size.
The footer lists evidence still required after compatibility: successful startup, service-level latency checks, and output-quality checks.

Research sources: Exact staged SGLang source; failed job 24282; corrected trial 24321

## Slide 23

Reasoning role: Backup · Chronology as supporting evidence. Use the historical chart as context for the research questions: it shows which operating points motivated later controlled tests, while teaching why a rising sequence is not a cumulative causal experiment.

The horizontal axis lists named milestones, not dates or equal time intervals. The vertical axis is good output tokens per second, so taller bars mean more requests meeting the latency limits under that milestone's workload. Gray marks early layouts, teal marks backend specialization, and orange marks later tuning and repeat points. The chart progresses from 1,297 at N32 and 1,666 at N40, through 1,912 at N48 and 2,631 at N52, to a rounded historical N64 mean of 3,044. Since concurrency, worker layout, backends, and runtime conditions change along the way, the chart shows the team found stronger measured configurations; it does not show how much any one change caused.

Observation: Measured good output throughput rises across named operating points from 1,297 at N32 to a rounded 3,044 at historical N64.
Hypothesis: Recovering a usable split and transfer path, then specializing attention, collective, prefill, and decode backends, helped identify stronger configurations.
Conclusion: The chart is a map of milestones and later replication targets; it is not evidence the named optimizations add up to the full rise.
Unknown: Loads, topology, runtime settings, and observation conditions vary; individual causal contributions and a global optimum are not established.

Speaking brief: The H200 chart rises from 1,297 good tokens/s at N32 to a 3,044 N64 mean. It shows better measured operating points over the campaign, but each milestone changes load or configuration, so the bars do not assign a causal gain to each optimization.

The milestones are 1,297 (initial 07/N32), 1,666 (initial 09/N40), 1,912 (split/N48), 2,631 (FlashInfer plus MNNVL/N52), 2,716 (DeepGEMM prefill/N56), 2,939 (DeepGEMM plus HPC-Ops/N58), 2,989 (repeated N60), 3,023 (repeated N62), and 3,044 (three historical N64 runs). Labels are rounded.
Later N62 runs measured 3,022.034919 and 3,023.072304; later N64 repeats measured 3,044.489701 and 3,044.074628. These support repeatability at those settings, not a universal optimum or causal explanation for every step.
Colors group phases of work; they are not pass/fail marks. Bar height is a score, not a confidence interval.

Research sources: Historical retained milestones; 24724/24737/24819; 24738/24913; 24915

## Slide 24

Reasoning role: Backup · Intervention & correctness. Describe the intervention precisely and put its correctness evidence at the right level. The patch changes descriptor scope and coalescing in heterogeneous-TP transfer while retaining the relevant mapping behavior; CPU equivalence is not the same as validating real transport on GPUs.

This is step 5 and the first half of step 6 in the seven-step chain: exact change, then the correctness gate that was actually run. Keep the distinction between address-range equivalence and real GPU transfer visible.

Observation: The patch implements request-only descriptor preparation and contiguous-range coalescing; retained CPU tests pass 720 range-equivalence cases, including the representative count of 188 for the contiguous request.
Hypothesis: If the mapping is preserved while irrelevant pool ranges are omitted, setup can do less descriptor work without changing the KV bytes required by the request.
Conclusion: The CPU fixture supports address and byte-range equivalence for its tested geometries. It is a correctness gate for the mapping, not a full deployment validation.
Unknown: The fixture does not validate real GPU transport. It does not time old and new descriptor creation or establish that this change alone resolves the earlier timeout.

Speaking brief: The patch builds descriptors for requested KV pages and coalesces contiguous ranges while preserving mapping and stride. CPU tests passed 720 geometry cases; the fixture explicitly did not validate real GPU transport.

Step 5 — Intervention: replace full-pool source and destination descriptor enumeration with request-scoped descriptors, then coalesce contiguous ranges.
The patch scope retains equal-TP behavior, weights, precision, KV-head mapping, per-token stride where a head slice is sent, and notifications.
Step 6, correctness part: 720 original-versus-patched CPU geometry cases pass byte-range equivalence.
The fixture records real GPU transport validation as false. Therefore CPU mapping checks do not prove GPU transfer, server readiness, or valid responses.

Research sources: nixl-ondemand/{README.md,nixl-ondemand.patch,metadata.json,geometry-test.json}

## Slide 25

Reasoning role: Backup · End-to-end evidence & limits. Close the seven-step chain with real end-to-end evidence and an explicit limit. The patched heterogeneous topology completed P/D warmup and a full N32 confirmation, but the absence of an equivalent successful no-patch run prevents causal speedup attribution.

This is steps 6 and 7: real path/result, then decision and unknowns. State the warmup duration, benchmark score, joint SLA, and zero errors as results of patched job 22294, not as a directly matched speedup over 22271.

Observation: Patched job 22294 completed P/D warmup in 0.68–0.70 seconds per request after server readiness, then scored 1422.96 good tokens/s at N32 with 95.87% joint SLA and zero errors/cancellations.
Hypothesis: Request-scoped descriptor setup may have helped the previously blocked topology reach a serving state, but differences between attempts could also explain the contrast.
Conclusion: The supported claim is patched-path feasibility and an end-to-end result for this P8 TP8/EP2 to D8 TP4/EP4 run. The patch's speedup is unmeasured.
Unknown: There is no successful matched unpatched run for this exact topology; old-versus-new setup time, network utilization, causal warmup decomposition, and the patch's independent goodput contribution remain unknown. Bandwidth, KV layout, placement, and other bootstrap explanations were not ruled out.

Speaking brief: On patched job 22294, pair warmup took 0.68–0.70 seconds per request and full N32 goodput was 1,422.96 with 95.87% joint SLA and zero errors. No matched unpatched control measures speedup.

Step 6, end-to-end part: patched job 22294 completed both real prefill/decode warmup paths in 0.68–0.70 seconds per request after workers were ready.
It then completed a full N32 confirmation: 1,422.96 good output tokens/s, 95.87% joint SLA, zero errors and zero cancellations.
Step 7 — Decision: the run establishes feasibility of the patched heterogeneous topology and that this run served requests under the local benchmark protocol.
It does not establish the patch's independent speedup: no successful no-patch end-to-end control exists for the same topology, and no old/new descriptor setup timer or causal latency decomposition was collected.

Research sources: 22271/pair-warmup.log;22294/pair-warmup.log;22294/confirm/n32/artifacts/profile_export_aiperf.json

## Slide 26

Reasoning role: Backup · Platform-specific tradeoff. Explain why evaluating only time to first token can select the wrong decode backend: latency over a long answer and qualifying throughput also matter.

The pair changes decode attention from FlashInfer to FA3 while holding H100, N54 load, and the rest of the tested path matched. Read across each metric: FA3 lowers mean time to first token by 118.922 ms, but raises mean inter-token latency by 0.773 ms. Repeated over roughly 199 token intervals, that adds about 154 ms. Mean request latency rises from 4,337.853 to 4,372.813 ms, and goodput falls 0.812%. Thus the early response improves while the full answer becomes slower on average and fewer requests qualify per second. This is one pair for this H100 decode setting, not a general ranking of attention libraries.

Observation: FA3 improves mean TTFT by 118.922 ms but worsens mean ITL by 0.773 ms and mean request latency by 34.960 ms; goodput falls 0.812%.
Hypothesis: Changing decode attention can move startup and per-token costs in opposite directions.
Conclusion: Keep FlashInfer for this tested H100 decode setting; FA3 remains used for prefill.
Unknown: One matched pair does not rank attention backends generally or isolate exact kernel-level causality.

Speaking brief: In one matched H100 N54 pair, FA3 cut mean TTFT from 713.199 to 594.276 ms, but goodput fell from 2,420.945 to 2,401.284 tokens/s, about 0.812%. A faster first token did not improve the full request objective.

FlashInfer → FA3: good output tokens/s 2,420.945 → 2,401.284; mean TTFT 713.199 → 594.276 ms; mean ITL 18.214 → 18.988 ms; mean request latency 4,337.853 → 4,372.813 ms.
Both runs passed team-reviewed protocol, runtime, and output checks on the assigned cluster, and FA3 was confirmed active on all eight decode ranks. That establishes the tested intervention actually ran, not that it improved the service.
The historical H100 individual peak of 2,433.019859 and fresh N54 control of 2,399.186728 are context, not the two arms of this matched pair. They do not provide an H100/H200 hardware conversion.

Research sources: 222027/222028 matched fullH100N54pair;222048historicalpeak;225227freshcontrol

## Slide 27

Reasoning role: Backup · Cost hypothesis & confirmation. Teach why a favorable first pair is not enough for adopting a startup optimization: execution order, cache state, nodes, and the predeclared cost threshold affect interpretation.

Compare the first pair with the reversed-order confirmation. In the first pair, off/read-first walltime was 934/759 seconds, a reported 18.74% saving, while goodput fell 0.659%. In the reverse-order pair, walltime was 854/770 seconds, a 9.84% saving, and goodput changed −0.326388%. The planned rule required at least 10% walltime saving and at most 2% goodput loss. The reverse pair meets the throughput tolerance but misses the walltime requirement. Scheduler walltime includes startup and cleanup; it is not the 120-second steady-state score window.

Observation: Read-first saved 18.74% walltime in the first order but 9.84% after reversing the order; goodput changed −0.659% and −0.326388%, respectively.
Hypothesis: Reading prefill weights before measured startup may reduce startup walltime.
Conclusion: The reverse-order confirmation missed the predeclared 10% saving threshold, so the team did not adopt the change.
Unknown: Unverified OS cache state and node differences prevent a causal cold-storage explanation.

Speaking brief: Read-first initially reduced scheduler walltime by 18.74%, but the reversed-order confirmation saved only 9.84%, below the predeclared 10% threshold. Goodput changed slightly in both pairs; unknown cache state prevents a cold-storage causal claim.

The first pair looked favorable for startup time but had a 0.659% goodput loss. The reversed pair cut the apparent saving below the 10% decision threshold.
The reverse pair's 0.326388% goodput change is within the stated 2% tolerance, but that alone cannot rescue the branch because the walltime threshold was missed.
Node differences and unverified file-cache state mean the result cannot be assigned to cold storage. A cold prefix is a model KV-cache condition and is not the same as cold filesystem pages.

Research sources: Startup-prefetch original and reverse-pair reviews; static locality222412

## Slide 28

Reasoning role: Backup · Negative measured interventions. Show how the team used source inspection, runtime activation checks, matched controls, and output review to decide whether small interventions deserved adoption.

The rows are independent hypotheses, not pieces of one cumulative optimization. Source review first identified a setting the runtime could consume; logs then confirmed activation; full serving runs measured the result. A small positive goodput change can fall below a useful threshold or worsen p95 first-token latency. Negative and neutral results therefore answer the research question: functionality is necessary, but only improvement in the service objective justifies changing the retained configuration.

Observation: Changes had source/runtime checks and full serving observations, but measured gains were small, negative, or mixed with worse tail latency.
Hypothesis: Changes in tokenization, collective, cache, request cap, polling, or attention might improve goodput.
Conclusion: Keep a change only when the intended path ran and a controlled service comparison improves the objective enough to matter.
Unknown: Small single-run differences may reflect run variation; these rows do not establish a CPU bottleneck or universal feature ranking.

Speaking brief: Several H200 changes were activated and measured, but gains were small, negative, or worse in a tail metric. For example, a prefill attention change lost 6.385% goodput. A working flag is not enough to replace the selected configuration.

Tokenizer wait changes measured +0.192% and +0.270%; the team kept tokenizer batching off. Switching the auto-selected prefill collective from TRT-LLM to MNNVL activated on all eight prefill ranks but gained only +0.109807% in full run 27138.
Prefill RadixCache to ChunkCache gained +0.240921%, but p95 TTFT worsened, so RadixCache stayed. Request-cap and polling comparisons were +0.26% or negative and did not demonstrate useful gain.
Prefill FlashInfer page 1 reduced ITL but lost 6.385% goodput. Percentages belong to separate branches; do not add them as if they were components of one run.

Research sources: 26949/26951/26953;27138 actual collective source/activation;27077;27365;27376/27378;27270/27272/27274

## Slide 29

Reasoning role: Backup · Diagnostics versus full serving. Answer what kernel names, profiles, and source inspection can establish, and prevent a component result on one hardware family from being mistaken for full-model evidence on another.

Read each row as an evidence boundary. The N52 H200 attention package is a real serving score but has coupled changes. H100 Triton probes test selected kernel shapes, not every model shape. SM budgets are bounded kernel/runtime checks, not model-level speed results. NCCL logs corrected an earlier interpretation: the label LL did not mean the tested control used that low-latency protocol for all messages. The real Qwen compile reached a native RoPE/fused-KV assertion before scoring. C++ CPU fixtures and source findings are narrower still. Mixing these rows would mix H200, H100, and CPU evidence.

Observation: Evidence ranges from one H200 serving score through H100 kernel/resource probes to CPU-only helpers and source review; their scopes differ.
Hypothesis: Alternative kernels, communication protocols, resource budgets, or APIs might improve a specific part of serving.
Conclusion: Use component evidence to select a full-model test only when the code path and hardware support it; do not claim service improvement from probes or source alone.
Unknown: Untested shapes and configurations may differ. The failed Qwen compile and CPU tests leave full-model compatibility and performance unresolved.

Speaking brief: The 2,549.20 N52 attention package changed several factors; representative Triton probes, CPU fixtures, and source review answer narrower questions. Full Qwen compilation stopped at a RoPE/KV assertion. None alone proves a full-model serving gain.

The H200 N52 attention-DP plus DeepGEMM/DeepEP package scored 2,549.20, below the retained MNNVL point; coupled settings block one-factor attribution.
Representative H100 FP8 Triton probes lost to DeepGEMM in tested shapes. H100 SM budgets 80/96/120 were mixed or below consistency criteria; 132 was retained without claiming a model gain.
The small 0.2315% NCCL point did not justify adoption after logs showed the control already selected Simple for large messages. Qwen compile failed before score; CPU fixtures did not test serving.

Research sources: JOURNEY stages15,29-31;DeepGEMM representative probes;NCCL source correction;27383;27506

## Slide 30

Reasoning role: Backup · Exact deployment settings. Provide exact deployment context so earlier results can be interpreted without mixing platform settings or treating configuration labels as performance evidence.

Read columns within each platform, not across H200 and H100 as if they were a matched benchmark. Both use target-model FP8 weights, BF16 activations and KV state, TP8/EP8 decode, FlashInfer decode attention, MNNVL collectives, and round-robin routing to two prefill workers. The H200 choice is N64 with DeepGEMM prefill, chunk 8,192, and dense decode graph buckets 1–64. H100 is N54 with HPC-Ops prefill and chunk 4,096. The table defines the operating points; it does not claim equal capacity or rank hardware performance.

Observation: The retained configurations share some decode and precision settings but differ in hardware, concurrency, prefill backend, and chunk size.
Hypothesis: Explicit platform-specific settings make the replicated operating points reproducible and interpretable.
Conclusion: Use the H200 N64 settings for the selected primary and report H100 N54 independently.
Unknown: This table does not establish that the settings are optimal or that performance transfers between platforms.

Speaking brief: The retained H200 setup uses N64, two TP4 DeepGEMM prefill workers with chunk 8,192, and TP8/EP8 HPC-Ops decode. H100 is separate: N54, HPC-Ops prefill with chunk 4,096, and its own measured settings.

H200: client concurrency 64; two TP4/EP1 prefill workers; DeepGEMM; chunk 8,192; one HPC-Ops TP8/EP8 decode worker.
H100: client concurrency 54; two TP4/EP1 HPC-Ops prefill workers; chunk 4,096; TP8/EP8 HPC-Ops decode. Keep H100 point separate from H200 scores.
Both use the listed weight/activation/KV precision and shared decode attention, collective, routing, and request-quality rules. Official full-set accuracy is not certified by this configuration table.

Research sources: 26766 frozen worker/runtime; 25487 operational settings; staged portable deployment validation

## Slide 31

Reasoning role: Backup · Fixed protocol & negative result. Explain the benchmark protocol behind the chunk table so its negative result is interpreted as a controlled, bounded comparison rather than a claim about all workloads.

The table compares three full runs with the same target concurrency, requested prompt/answer lengths, seed, cold-prefix setting, model, precision, and runtime path. Only prefill chunk size changes: 8,192, 10,240, or 12,288 input tokens handled together. Read good output tokens/s as qualifying throughput, joint SLA as the fraction meeting both limits, and p95 TTFT as the slow-response tail. Goodput and the tail both worsen at larger chunks. One run per setting supports retaining 8,192 for this configuration, but cannot identify a general optimum.

Observation: Goodput decreases from 3,045.50 to 3,020.94 tokens/s and p95 TTFT increases from 1,311.69 to 1,624.12 ms as chunk grows from 8,192 to 12,288.
Hypothesis: A larger prefill chunk might increase throughput by handling more input tokens per scheduling batch.
Conclusion: Retain 8,192 for this service configuration; the tested larger chunks did not improve the objective.
Unknown: One run per chunk makes the comparison bounded; it does not establish a global optimum or rule out order/seed variation.

Speaking brief: Under the same full N64 workload, increasing prefill chunk from 8,192 to 12,288 reduced goodput from 3,045.50 to 3,020.94 tokens/s and worsened p95 TTFT. Each setting has one reviewed H200 run; this does not establish a global optimum.

At chunk 8,192, job 26766 scored 3,045.501509 good output tokens/s, 98.580% joint SLA, and 1,311.69 ms p95 TTFT. At 10,240, job 26768 scored 3,034.088251, 98.524%, and 1,518.87 ms.
At 12,288, job 26770 scored 3,020.943099, 98.310%, and 1,624.12 ms. All three were full N64 runs with the same 60/120/30 schedule and requested 4,000/200 workload; each chunk setting was observed once.
The runs passed team protocol, runtime, latency, and output checks with zero profiling errors/cancellations. That is a reviewed result on the assigned cluster, not organizer quality certification.

Research sources: 4000/200seed2026closedloop;26766/26768/26770 fullreviews

## Slide 32

Reasoning role: Backup · Resource metric versus objective. Explain why a lower resource metric is not automatically a service improvement, and separate capture memory from total GPU memory and end-to-end throughput.

Compare dense control 27376 with sparse candidate 27510. The candidate stores 12 decode graph buckets instead of 64 and reduces logged graph-capture memory per rank, but goodput is 3,029.861122 versus 3,041.119598, 0.370208% lower. Mean request ITL rises from 14.991 to 15.136 ms; TTFT improves. Fewer buckets may force requests into less exact padded shapes, which can add work, but padding was not isolated or measured here. The reported capture memory excludes other GPU allocations such as model weights and KV cache, so it is not a VRAM capacity figure. The service score, not the smaller capture number, determines whether this is useful.

Observation: Sparse capture reduced logged per-rank graph memory from 1.15 to 0.36 GB and slightly shortened capture, while goodput fell by 0.370208% against the earlier control.
Hypothesis: Fewer captured shapes might save resources while maintaining service throughput; padding was a possible mechanism but not measured.
Conclusion: The service objective did not improve, so the team retained dense graphs for this deployment.
Unknown: There is one earlier control and generated seeds differ; total VRAM use and any padding effect were not measured by the capture-memory metric.

Speaking brief: Sparse capture cut logged memory from 1.15 to 0.36 GB per decode rank, but goodput fell 0.370208% and mean ITL worsened. Padding was not measured as a cause. The team retained dense graphs; this pair does not prove a causal effect.

The dense control has 64 buckets, 1.15 GB capture memory per rank, 101.46–101.49 s capture time, 3,041.119598 good output tokens/s, and 14.991 ms mean ITL.
The sparse candidate has 12 buckets, 0.36 GB/rank, 95.98–96.05 s capture time, 3,029.861122 good output tokens/s, and 15.136 ms mean ITL. Captures were confirmed on all eight decode ranks with model compilation off.
Candidate mean/p95 TTFT was 1,102.404/1,240.481 ms and improved, while mean/p95 ITL was 15.136/15.324 ms and worsened. One earlier control, different engine seeds, and candidate-only startup instrumentation limit causal interpretation.

Research sources: 27510 terminal raw/runtime/capture review;27376 prior control

## Slide 33

We optimize execution of the official OpenFOAM v2512 car-flow case, not its mathematics. The mesh contains 65,334,765 cells. The job completes the prescribed preparation and 150 solver iterations on four nodes. The measured metric is the solver's average wall-clock seconds per time step, beginning with the second solver iteration; lower is better. The retained final drag coefficient is a physical sanity signal, not the performance score.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/FOUNDATIONS.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/equinix-private-ai-dgx/hybrid-ai-infrastructure-m460-d.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/dgx-superpod/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 34

MPI means Message Passing Interface: separate solver processes exchange information about cells at partition boundaries. Mesh decomposition assigns cells to ranks; CPU affinity maps ranks to CPUs. These are different decisions. A complete run includes mesh decomposition, renumbering, potential-flow initialization, boundary-layer setup, and the 150-step simpleFoam solve. Skipping preparation or solver work would not be a valid comparison.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/FOUNDATIONS.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/dgx-superpod/Automotive-Collaboration-6701.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/dgx-superpod/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 35

The NUMA-aware decomposition hypothesis was that grouping work by memory locality might reduce communication and improve speed. Its graph cut fell by 10.63%, but the solver mean worsened from 13.881 to 14.359 seconds per step, a 3.4416% slowdown. The comparison also changed other partition properties, so the cut alone cannot explain the runtime. We closed the unchanged branch. A separate offline mapping reduced a graph cut by 4.5741% but has no measured solver result.

Research sources: /home/apacsc42/workspace/reports/hpc-research-journey-20261023/JOURNEY.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/figures/research-journey.png
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/nvidiaweb/networking/infiniband-switching/nvidia-infiniband-switch-ndr-400gbs-2c50-d-2x.jpeg", "reference_page": "https://www.nvidia.com/en-us/networking/infiniband-switching/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 36

These are separately allocated observations at 128 ranks per node, not an identical-work strong-scaling experiment. Endpoints are 40, 80 and 150 solver steps. Hierarchical led the two-node pair at 7.169996913 seconds per step versus Scotch at 7.462835189. At four nodes, Scotch led at 3.677906731 versus hierarchical at 3.819929017. Different allocations and endpoint lengths limit causal claims.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/RESULTS.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/figures/observed-scaling.png
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/networking/spectrumx/spectrum-x-og-2.jpg", "reference_page": "https://www.nvidia.com/en-us/networking/spectrumx/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 37

The six reviewed four-node logs all complete 150 steps with 149 timed samples. At 64 and 96 ranks per node, hierarchical has the lower observed mean; at 128, Scotch is lower. Requested CPU counts differ across some configurations, and these are separate allocations. We therefore describe measured candidate means, not a causal effect or a universal best method. The lowest mean is 3.677906731 seconds per step for Scotch-128.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/networking/spectrumx/spectrumx-multiplane-ari-1920x1080.jpg", "reference_page": "https://www.nvidia.com/en-us/networking/spectrumx/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 38

Scotch-128 has a median of 3.298742 seconds, p95 of 3.795740 seconds, and maximum of 35.883552 seconds at solver Time 119. All 149 timed samples remain in the arithmetic mean. The review did not collect enough hardware counters to attribute the spike to MPI, CPU scheduling, memory or I/O. The sample-size warning motivates independent repeats; it does not authorize removing the slow point or changing the prescribed endpoint.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/figures/iteration-spikes.png
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/ai-homepage/inference/inferencemax-promo-reference/dgx-press-gb300-1920x1080.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 39

The best reviewed four-node native mean is a candidate observation, not an accepted official score. The independent confirmation job 25940700 was submitted on 23 October at 12:51 UTC. A fresh scheduler query at 15:06 UTC still showed Q/q5 with the comment Not Running: Insufficient amount of resource: node_pool. No result is available. The job is configured to re-run the full preparation and 150-step solve on four exclusive nodes. Its fresh 54-file bundle requires source/mesh identity, explicit stage returns, startup 512-physical-core/four-host proof, and zero-field seals. These are required proofs, not completed checks.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/scheduler-status.json; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-four-node-confirm-20261023/submission.json
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/technologies/blackwell-architecture/nvidia-gb200-nvl72-1920-1080.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 40

The research has narrowed choices, rejected the unchanged NUMA-aware branch, and identified Scotch-128 as the lowest mean among six reviewed four-node native observations. This is not a proven global optimum or accepted score. At 15:06 UTC on 23 October, job 25940700 was still Q/q5; PBS reported Not Running because node_pool resources were insufficient. No result was available. Next review its complete terminal proof and all iteration tails, then use bounded matched sampling to investigate stability before choosing another configuration.

Research sources: /home/apacsc42/workspace/reports/hpc-research-journey-20261023/JOURNEY.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/TALK_TRACK.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/scheduler-status.json; /home/apacsc42/workspace/notes/HPC_CURRENT.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/h100/hpc-web-gtc23-h100-2560x1440.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/h100/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}
