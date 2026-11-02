# TripleU presenter notes — 2 November 2026

AI slides updated; original HPC notes retained unchanged.

## Slide 1

Reasoning role: Problem · success criterion. Define the service objective before discussing optimizations. The system has a fixed model, GPU budget, request shape, and per-request latency gate. Every later topology or backend decision is judged against qualifying service output, not the largest unfiltered token count.

Problem: Choose how to serve the specified model within sixteen H200 GPUs while sustaining the fixed synthetic request workload.
Why It Matters: Latency failures make output unusable for the stated objective even when the system emits many raw tokens.
Why This Test: Fix the request shape and require both TTFT and mean ITL limits on each request, then aggregate only qualifying service as goodput.
What We Learned: The study optimizes useful, latency-qualified output and requires at least 90% of all requests to pass both limits.
Next Logic: With success defined, the next slide separates which conclusions are engineering choices, direct team contributions, and measured backend findings.

Explain the intended metric pipeline from one request to the final service score: the request enters with a fixed prompt and requested output; TTFT and mean ITL are checked for that request; passing requests contribute to goodput; goodput is multiplied by 200 requested output tokens to report good output tokens per second. Errors remain in the evaluated set. There are no unspecified chart glyphs or decorative encodings to interpret.

Observation: The task fixes a 4,000-token prompt, 200 requested output tokens, two per-request latency limits, and a minimum 90% joint pass share.
Hypothesis: A configuration with high raw output can still be a poor service if too many individual requests miss either latency limit.
Conclusion: Use qualifying throughput under the joint gate as the objective for later engineering and experimental decisions.
Unknown: This definition does not by itself establish official model accuracy or a contest ranking; full-set quality remains a separate validation question.

Speaking brief: We serve Qwen3-235B FP8 on sixteen H200 GPUs. A request contributes only if it meets both latency limits; at least 90% must qualify. We report qualifying output tokens per second, not raw throughput.

Follow a request through both latency checks; passing only one limit is insufficient.
The 90% requirement is a share of all evaluated requests, including errors in the denominator.
Good output tokens per second is a derived service metric. It is not simply all generated tokens divided by run time.

Research sources: Qwenrules;officialGoodputclarification

## Slide 2

Reasoning role: Contribution map · ownership and scope. Map the presentation's contribution and prevent evidence from one type of claim being used to overstate another. Engineering decisions select a workable design; the KV patch is a specific team implementation; backend comparisons are measured findings that require their own controls and repeats.

Problem: Present a long systems investigation without conflating topology choices, a code change, and performance experiments.
Why It Matters: Evidence that supports feasibility may not support speedup; a measured backend effect cannot automatically validate a separate transfer patch.
Why This Test: Assign each claim its own evidence gate and preserve the platform and configuration associated with each observation.
What We Learned: The team has an engineering selection, a direct KV-transfer implementation with bounded validation, and backend findings based on separate comparisons.
Next Logic: First inspect the fixed sixteen-GPU topology tradeoff; then show the retained layout and the distinct historical branch where the KV failure occurred.

Describe three claim lanes joined by a common objective. The architecture lane is supported by feasible layout records; the KV-transfer lane by source change, geometry checks, and a real patched run; the backend lane by controlled benchmark observations and replication. Each lane points toward the same success criterion but retains its own evidence gate. H100 observations stay in a separately labeled platform lane. This is a claim map, not three additive percentages.

Observation: The research contains layout decisions, a specific request-scoped transfer change, and separate backend trials; each has a different evidence trail.
Hypothesis: Separating claim types will make it possible to explain what the team implemented, what it measured, and what remains only an engineering selection.
Conclusion: Report each contribution at the level its evidence supports and keep H100 results distinct from the H200 primary series.
Unknown: This contribution map does not make all findings causal, combine them into one gain, or establish official accuracy.

Speaking brief: We separate architecture choices, the team’s request-scoped KV patch, and backend measurements. These claims use different evidence: layout records, source plus transfer validation, and controlled experiments; H100 remains separate from H200.

Read the three lanes independently: architecture choice, direct KV implementation, and backend experiments.
A successful engineering deployment does not alone prove a speedup; a source patch does not alone prove a GPU transfer; a backend score does not prove model accuracy.
All lanes are evaluated against slide 1's latency-qualified goodput objective, but their evidence is not interchangeable.
The H200 primary and H100 observations must retain their platform labels.

Research sources: investigation-contributions.json;ownerfeedback

## Slide 3

Reasoning role: Engineering decision · compare feasible layouts. Explain the actual decision rule behind the retained topology. The choice was made from feasible model-compatible layouts that use the fixed two-node budget, can complete disaggregated requests and support a latency-qualified operating point that was later repeated. Historical scores at N32, N40 and N48 motivated the choice but cannot rank topology independently because load and trial conditions differ.

Problem: Allocate sixteen H200 GPUs across prefill and decode, balancing the number of worker replicas against the GPUs assigned to each worker.
Why It Matters: Too few replicas can limit prompt-side admission, while overly narrow workers may not process their share efficiently; decode also has different parallelism needs.
Why This Test: Apply the constraints in order: allocation and FP8 compatibility first, successful real P/D transfer second, then full latency-qualified performance and repeatability. Use historical different-load points only to understand the search.
What We Learned: The retained split is feasible and its N64 operating point is repeatable. Because the topology scores shown were measured at different concurrency settings, we cannot say the split beat all alternatives under the same load.
Next Logic: After stating why this layout was retained, examine a separate heterogeneous-TP recovery branch. That branch teaches us about transfer readiness; it is not a topology comparison against this selected layout.

The left column lists four selection gates: fit two nodes of eight H200, pass FP8 parallel-shape compatibility, complete the real prefill/decode KV path, and establish a full-run SLA-qualified operating point with later repeats. The right column gives three historical layout observations at N32, N40 and N48. Orange highlights the retained split and the repeat requirement; it does not mark a controlled topology winner. There are no chart axes; the throughput unit is good output tokens/s. P means prefill workers and D means decode workers. Different loads prevent a topology-only causal ranking.

Observation: Seventeen usable measured topology configurations were recovered, including three EP2 replacements. Displayed examples use N32, N40 and N48, so they are not a common-load ranking.
Hypothesis: A feasible phase-specialized split can provide a working transfer path and a repeatable latency-qualified service point within two nodes.
Conclusion: Retain the documented two-TP4-prefill plus TP8/EP8-decode layout because it fits the allocation, is model-compatible, serves across the split and supports later repeated N64 measurements. This is a practical evidence-based selection, not a proven global optimum.
Unknown: No matched, repeated comparison of every feasible topology at a shared load establishes the causal performance winner.

Speaking brief: The topology trials exposed a tradeoff between more prompt workers and wider workers. We retained a split that fits two eight-GPU nodes, has a working transfer path and survives later full N64 repeats. The different-load scores do not prove it is globally best.

The resource constraint is exactly two nodes of eight H200 GPUs; each candidate must fit those resources.
The model’s FP8 block geometry rules out some nominal parallel shapes before performance comparison.
A split is useful only if real requests complete the prefill-to-decode KV transfer and the service meets the joint latency gate.
The retained operating point later has full N64 repeats around 3,044 good output tokens/s; these repeats support the operating point, not its causal advantage over every topology.
The older N32/N40/N48 values are shown to explain the search, not to claim increasing topology-only performance.

Research sources: topologyrecoveryledger;22197/22219/22415

## Slide 4

Reasoning role: Engineering decision · retained architecture. State the retained architecture clearly as an engineering decision within the two-node GPU budget. Explain how phase specialization uses replicas for prompt processing and wider parallelism for decode, while naming the additional KV transfer path as a cost of disaggregation.

Problem: Turn topology candidates into a two-node serving architecture that uses the full sixteen-H200 allocation.
Why It Matters: The two service phases have different resource needs, and the chosen split determines both worker capacity and whether KV must move across nodes.
Why This Test: Retain two TP4/EP1 prefill workers and one TP8/EP8 decode worker as a feasible phase-specialized layout, then validate its actual transfer path.
What We Learned: The architecture fits the node budget and offers separate prefill and decode roles, but introduces a required inter-role KV transfer.
Next Logic: A separate historical heterogeneous-TP recovery branch exposed a failure in that transfer warmup; its topology differs from this retained layout.

Show Node 0 containing P0 and P1, each with four GPUs and TP4/EP1. Show Node 1 containing D0 with eight GPUs and TP8/EP8. Route a request to a prefill worker, then show its KV state crossing to decode, where output generation occurs. The layout sums to sixteen GPUs. This schematic represents roles and placement, not measured utilization or data volume.

Observation: The retained H200 layout places two TP4/EP1 prefill workers on Node 0 and one TP8/EP8 decode worker on Node 1, using all sixteen GPUs.
Hypothesis: Specializing allocation by phase can match prompt processing and generation to different replica and parallel-width needs.
Conclusion: This is the retained engineering architecture for the selected service; it is not proof that this exact split causally beat every alternative at a matched load.
Unknown: The diagram does not quantify the performance benefit of phase specialization or the transfer cost; request KV transfer must work for the architecture to serve.

Speaking brief: The retained split uses two four-GPU TP4/EP1 prefill workers on one node and one eight-GPU TP8/EP8 decode worker on the other. This fits sixteen H200s but adds KV transfer between roles.

The two P workers are replicas to receive prompt work; the D worker uses a wider TP/EP configuration for generation.
The split respects the two-node budget and keeps each worker's TP group within its node.
Unlike a single co-located worker, this design must transfer request KV state between prefill and decode.

Research sources: Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents

## Slide 5

Reasoning role: Technical contribution · observed transfer failure. Establish the observed transfer-readiness failure before describing a fix. This is a historical recovery branch with heterogeneous tensor parallelism, not the architecture retained on slide 4. The timeout happened before a usable benchmark result.

Problem: A historical heterogeneous-TP deployment had loaded workers but could not warm the prefill-to-decode path for a client request.
Why It Matters: Without pair readiness, there is no usable benchmark and no service result to optimize.
Why This Test: Inspect the retained job and warmup log to identify which stage failed before any performance interpretation.
What We Learned: Job 22271 waited 360 seconds and ended in HTTP TimeoutError; it produced no AIPerf score. The evidence is a readiness symptom, not a measured bandwidth diagnosis.
Next Logic: Because failure occurred before scoring, the next step is to inspect the cold setup path and prioritize a source-backed hypothesis without claiming other causes are excluded.

Show the request path from a ready prefill worker toward decode, then mark the pair-warmup request timing out at 360 seconds. Label job 22271 and explicitly mark that AIPerf did not run and no score exists. Do not represent this as a low point on a performance chart or as measured transfer latency.

Observation: Job 22271 loaded model workers on the heterogeneous-TP branch, then pair warmup timed out after 360 seconds with HTTP TimeoutError. AIPerf did not run.
Hypothesis: The issue lies in cold P/D bootstrap or transfer readiness, but the symptom does not isolate descriptor construction as the cause.
Conclusion: Classify 22271 as a pre-benchmark readiness failure and preserve the topology and log evidence. It has no baseline throughput value.
Unknown: The timed-out phase was not decomposed. Descriptor setup, other bootstrap/transfer work, bandwidth, KV mapping, and placement were not individually measured or ruled out.

Speaking brief: In job 22271, the P8 TP8/EP2 to D8 TP4/EP4 workers loaded but pair warmup timed out after 360 seconds. AIPerf never ran, so there was no baseline score.

The model workers loaded, but an actual request through the P/D pair did not finish warmup.
The retained log ends in HTTP TimeoutError after 360 seconds; there is no AIPerf export and no benchmark score.
This establishes a cold readiness/bootstrap failure in this attempt, not steady-state bandwidth saturation or a slow KV copy measurement.
Keep this historical branch distinct from the selected two-TP4 prefill plus TP8/EP8 decode layout.

Research sources: 22271/pair-warmup.log;TOPOLOGY_REVIEW.md

## Slide 6

Reasoning role: Technical contribution · intervention and checks. Explain why descriptor construction was the first intervention. After the pre-score warmup failure, source inspection showed that heterogeneous-TP setup enumerated pool metadata unrelated to the current request. Restricting descriptors to request pages had a narrow correctness check in CPU fixtures and did not require assuming that network bandwidth, KV layout or scheduling had already been ruled out.

Problem: Full-pool descriptor enumeration appeared in the cold heterogeneous-TP path after pair warmup had failed.
Why It Matters: Preparing metadata for pages the request will not transfer could add setup work before the service can handle its first request.
Why This Test: The source exposed a concrete setup action that included data irrelevant to the request. Restricting that work had a clear correctness invariant and a cheap CPU check, so it was the lowest-cost discriminating first intervention. We did not first prove bandwidth, KV layout or scheduling innocent.
What We Learned: The 720 range checks support byte-range equivalence. They justify attempting the patched distributed path, but cannot identify the timeout’s cause or prove a performance bottleneck.
Next Logic: The next run asks whether the patched branch can actually warm up and complete a full benchmark. Since the old branch has no successful scored control, interpret that result as feasibility evidence only.

The preceding slide supplies the failed warmup context. Here the left grid illustrates the whole reserved KV pool, with orange pages representing the small requested subset. The right orange range illustrates selecting request pages and coalescing adjacent ranges. The labels compare representative pool-source entries per rank (403.8 million) with coalesced ranges for one 4,000-token request (188). These scopes differ; no axis or speed ratio exists. The heading explains why this bounded source-visible setup hypothesis was chosen first. The bottom note reports 720 CPU checks and says bandwidth and scheduling were not ruled out; CPU checks do not validate GPU transport.

Observation: A heterogeneous-TP worker pair loaded, but the warmup timed out before a scored benchmark. Source showed whole-pool metadata enumeration; 720 CPU equivalence cases passed after the narrow patch.
Hypothesis: Avoiding request-irrelevant descriptor construction may make this bootstrap path usable; a cheap exact-range check can reject an incorrect patch before spending another distributed allocation.
Conclusion: Descriptor scoping was a sensible first engineering intervention because it was directly visible in source, bounded, and inexpensive to validate. Existing evidence does not establish that it was the dominant performance bottleneck.
Unknown: No successful unpatched scored run, initialization timer, bandwidth profile, KV-layout comparison, or scheduling comparison exists for this branch. Which component caused the timeout and the descriptor-only end-to-end gain remain unknown.

Speaking brief: Workers reached ready state but pair warmup timed out before AIPerf. Source inspection found request-independent enumeration of a large reserved KV pool. We tried request-scoped ranges first because this setup hypothesis was narrow and cheaply testable.

The motivating symptom was a 360-second pair-warmup timeout before AIPerf, with no scored requests.
Source review found descriptor setup traversing the whole registered pool even though the immediate request references only a subset of pages.
The first intervention was deliberately narrow: build descriptors for request pages and merge adjacent byte ranges while preserving offsets and strides.
720 CPU fixtures checked range equivalence, making this a cheap correctness gate before another distributed GPU attempt. They do not validate real NIC/GPU transfer behavior.
Bandwidth, KV layout and request scheduling remain competing explanations not isolated by these counts.

Research sources: nixl-ondemand/README.md;nixl-ondemand.patch;metadata.json;geometry-test.json

## Slide 7

Reasoning role: Technical contribution · end-to-end evidence boundary. Report the end-to-end result of the patched recovery branch and define its evidence boundary. The path became usable and completed a full local N32 benchmark, but this does not measure the descriptor patch's independent contribution because there is no successful matched unpatched control.

Problem: Determine whether the source change was followed by a usable service path, not just a passing CPU fixture.
Why It Matters: Only a real end-to-end request and benchmark can show the patched recovery topology became usable; CPU address checks alone cannot do that.
Why This Test: After a successful byte-range check, the necessary next gate was a real distributed request through both roles, followed by the complete benchmark protocol. This tests feasibility of the patched path, while the missing successful unpatched control limits causal comparison.
What We Learned: The patched branch warmed up and completed a full N32 run with 95.87% joint SLA and zero scored errors. That establishes a usable example path. It does not quantify descriptor-only speedup because the original run timed out before scoring.
Next Logic: With a working path available, performance experiments become possible. The separate diagnostic profile on the next slide identifies candidates, not a proven bottleneck.

Show before and after as two distinct job records, not a conventional speedup chart. Before: 22271 loaded workers, then timed out during pair warmup at 360 seconds; no AIPerf result. After: 22294 with the patch completed real P/D warmup in 0.68–0.70 seconds per request, then a full N32 benchmark produced 1,422.96 good tokens/s, 95.87% joint SLA, zero errors and cancellations. Place a clearly separate “not measured” callout for descriptor-only speedup and causal attribution.

Observation: Job 22294's patched path completed both P/D warmup routes in 0.68–0.70 seconds per request after servers were ready, then scored 1422.96 good tokens/s at N32 with 95.87% joint SLA and zero errors/cancellations.
Hypothesis: Request-scoped descriptors may have helped make the recovery path usable, but other run differences or bootstrap work could also explain why this attempt succeeded.
Conclusion: The evidence supports patched-path feasibility and a complete local benchmark result for this recovery topology. Descriptor-only speedup and causal attribution are unknown.
Unknown: There is no successful unpatched end-to-end control for this exact topology, no old-versus-new descriptor setup time, and no controlled warmup decomposition. Network utilization, KV layout, placement, other bootstrap work, and the patch's independent goodput contribution remain unmeasured.

Speaking brief: Patched job 22294 completed warmup in 0.68–0.70 seconds per request and scored 1,422.96 good tokens/s at N32, with 95.87% joint SLA and zero errors. This proves feasibility, not isolated speedup.

Before: job 22271 had a 360-second pair-warmup timeout and no AIPerf score.
After: patched job 22294 completed real P/D warmup in 0.68–0.70 seconds per request after server readiness, then completed an N32 benchmark.
The full result was 1,422.96 good tokens/s, 95.87% joint SLA, and zero errors or cancellations.
The comparison establishes feasibility of the patched topology in that run. It is not a speedup ratio: there is no successful no-patch control, no isolated old/new setup timer, and no causal latency decomposition.

Research sources: 22271;22294pairwarmup;22294/confirm/n32/artifacts/profile_export_aiperf.json

## Slide 8

Reasoning role: Experimental evidence · prioritise what to test. Use instrumentation to prioritize a follow-up without mistaking recorded GPU activity for an end-to-end time budget or merging evidence from different runs.

Problem: The campaign needed to choose which performance questions to test without claiming a bottleneck from a profile.
Why It Matters: Summed GPU kernel time can overlap and excludes other elapsed-time sources, so its percentages cannot be read as request-latency shares.
Why This Test: Collect a diagnostic N48 profile and separate N64 request-tail observations to identify candidate areas and symptoms. Kernel-duration sums cannot assign request wall time or select one causal fix, so the next backend comparison is described as a separate controlled probe, not the proven consequence of this profile.
What We Learned: Compute, collectives, attention and first-token queueing are plausible investigation areas, but none has a measured per-request time share here. The evidence does not tell us that HPC-Ops decode was the profile-selected remedy.
Next Logic: We next report an independently motivated, supported decode-implementation probe with its own fresh control and repeat. Its measured effect stands on that control pair, not on the N48 kernel percentages.

The profile's categories are matrix operations, communication/normalization, and attention. The displayed percentages divide each category's recorded kernel duration by the sum of recorded kernel durations across profiled ranks. GPU kernels can overlap; queues, CPU work, gaps, and unrecorded activity also contribute to elapsed request time. Separate N64 requests later missed TTFT but passed ITL, which identifies the failed latency condition, not its cause. The N48 profile and N64 request outcomes are different observations.

Observation: Three kernel groups account for the listed shares of recorded kernel duration; a separate N64 observation has TTFT-only failures.
Hypothesis: Communication, matrix work, or attention could be useful targets for controlled follow-up; early request-tail timing could also merit investigation.
Conclusion: Treat the profile as a prioritization clue. Keep its N48 scope separate from N64 service outcomes.
Unknown: Per-request phase timing, total wall-time attribution, and a causal explanation for the N64 TTFT failures are unavailable.

Speaking brief: The separate N48 diagnostic assigns about 23.48% of summed recorded GPU-kernel duration to communication and normalization. This motivates a controlled test; it does not establish that communication consumes the same share of request latency or limits N64.

The N48 profile attributed 21.642% to GEMM, 23.479% to MNNVL collective plus RMSNorm, and 15.064% to FlashInfer paged attention, as shares of summed recorded kernel duration.
A separate N64 run had 27 requests fail TTFT, zero fail ITL, and zero request errors among 1,902 profiling requests. This says which service limit was missed; it does not connect that tail to the N48 profile.
The evidence motivates measuring phase-specific queueing and timing. It does not show that optimizing the largest kernel share yields an equal request-latency reduction.
The horizontal bar lengths show each named group’s share of summed recorded kernel durations, in percent; the printed labels give the values. Colors identify/emphasize groups, not pass or failure. There is no per-request time axis or exclusive wall-time partition.

Research sources: 24819profile;26766requests;observabilityreview

## Slide 9

Reasoning role: Experimental method · hypothesis and control. Present a separate, supported test of a decode implementation after profiling raised several possible areas to investigate. This comparison asks whether the decode implementation changes end-to-end service performance with the rest of the measured setup held fixed. It is not a claim that the N48 profile identified HPC-Ops as the bottleneck or prescribed this intervention.

Problem: A backend change is only useful if a measured service objective improves under comparable workload conditions.
Why It Matters: Without a control and fixed prefill/load settings, observed score changes could come from other configuration differences.
Why This Test: The diagnostic profile did not identify a unique bottleneck. We therefore use a distinct, practical intervention with an available supported implementation and matched full-run control: change decode implementation, hold the serving topology, prefill, transport, workload and protocol fixed, then repeat the treatment.
What We Learned: The comparison can estimate the effect of this whole decode-setting change on the tested H200 service under the stated conditions. It cannot turn the prior profile into causal evidence or isolate an individual GPU kernel mechanism.
Next Logic: The next slide reports goodput together with TTFT and ITL, then checks the treatment against its independent repeat.

The setup diagram should be read as two otherwise matching full N60 runs: fresh automatic decode control 24912 and HPC-Ops decode treatment/repeat 24913. Both use sixteen H200 GPUs, DeepGEMM prefill, and chunk size 8,192 under the 60-second warmup, 120-second scoring, and 30-second grace protocol. The intended difference is the decode runner. Job 24913 also serves as an independent treatment repeat relative to original treatment 24738. Equal settings reduce confounding; they do not make all runtime randomness identical.

Observation: Jobs 24912 and 24913 used the matched H200 N60 setup; 24913 independently repeated the HPC-Ops treatment.
Hypothesis: Replacing automatic decode with HPC-Ops may improve goodput while altering the balance between first-token delay and later-token spacing.
Conclusion: This design isolates the intended decode choice more cleanly than historical mixed-configuration milestones.
Unknown: Generated engine seeds and uncollected phase-level telemetry prevent a fully deterministic or kernel-causal account.

Speaking brief: We compared automatic decode with HPC-Ops on the same full H200 N60 setup, holding DeepGEMM prefill and chunk 8,192 fixed. The hypothesis was that decode execution could improve useful throughput; a separate treatment repeat checks consistency.

The experiment holds hardware, load, prefill backend, and chunk size constant. The changed choice is automatic versus HPC-Ops decode.
The full protocol is 60 seconds warmup, 120 scored seconds, and 30 seconds grace. This allows the comparison to include first-token and streaming behavior under the same workload window.
The repeat addresses reproducibility of the treatment, not whether every request-level difference or mechanism has been explained.

Research sources: 24912/24913fullreview;24738;runtimeactivation

## Slide 10

Reasoning role: Experimental finding · matched result and repeat. Interpret the decode intervention as a multi-metric tradeoff rather than a single score change, and distinguish evidence of reproducibility from a universal backend claim.

Problem: A higher throughput score alone can hide a worse first response or fail to repeat.
Why It Matters: Users experience both the wait for the first token and the pace of later tokens; the SLA checks both.
Why This Test: Compare the matched full N60 control/treatment on goodput, TTFT, request-mean ITL, and then check a separate treatment repeat.
What We Learned: Goodput rose 5.295%; TTFT slowed about 125 ms; ITL improved about 1.64 ms; the repeat was 0.033% below original.
Next Logic: Carry this measured tradeoff to the load-selection question without generalizing the backend beyond N60.

The three metric arrows show opposing movements: goodput increases, mean time to first token increases (worse), and mean request-mean inter-token latency decreases (better). The result is from control 24912 versus treatment/repeat 24913 at full N60. Joint SLA changed only slightly, from 98.7599% to 98.8178%. Treatment 24913 measured 2,989.175 good tokens/s, just 0.033% below original treatment 24738 at 2,990.151. This is the observed service outcome; it does not say why each latency component moved.

Observation: The treatment increased goodput and improved ITL but worsened TTFT; the independent treatment run was close to the original score.
Hypothesis: The decode runner may shift work between startup and per-token streaming costs.
Conclusion: The complete service result supports this H200 N60 configuration with an explicit first-token tradeoff.
Unknown: The comparison does not isolate kernel-level causes, queue/compute timing, or behavior on other loads and hardware.

Speaking brief: The decode change improves qualifying throughput by about 5.30% on H200, and a separate deployment repeats the result closely. First-token wait gets worse while streaming gaps improve. We retain this measured tradeoff, not a claim that everything became faster.

Goodput rose 5.295%, from 2,838.853 to 2,989.175 tokens/s.
Mean TTFT rose 125.335 ms, from 822.292 to 947.627 ms. Mean request-mean ITL fell 1.644 ms, from 16.579 to 14.934 ms.
The separate treatment repeat was 0.033% below the original treatment. That supports repeatability of this operating point, while the slower first token remains a real tradeoff.

Research sources: 24912/24913;24738;fullreview

## Slide 11

Reasoning role: Engineering decision · choose the operating load. Choose an operating load using complete-protocol evidence and a repeat, while rejecting a larger-load claim that did not survive full measurement.

Problem: The team needed an operating load that improves useful throughput without trusting a short-test peak.
Why It Matters: Higher concurrency can create more work but also increase queueing and latency failures, so the full service objective may stop improving.
Why This Test: Compare full 60/120/30 N62 control with N64 candidate and repeat N64; use the full N68 pair to check its earlier short-screen signal.
What We Learned: N64 gained 1.082867% and repeated within 0.013634%; N68's short +2.27% became only +0.083056% full.
Next Logic: Inspect request-level latency failures at the selected N64 load.

Follow the load decision, not a bar-height ranking. Full N62 control 25365 scored 3,011.875 good tokens/s; N64 candidate 25366 scored 3,044.490, a 1.082867% gain. Independent N64 repeat 25373 scored 3,044.075, 0.013634% below the candidate. A short N68 screen appeared 2.27% higher, but the later full N68 comparison reduced the difference to 0.083056%. The load decision is therefore based on N64's full gain and repeatability, not the short N68 signal.

Observation: N64 gained 1.082867% over full N62 and repeated closely; N68's apparent short gain shrank to 0.083056% in the full comparison.
Hypothesis: Increasing client load may raise qualifying throughput until latency costs erase the gain.
Conclusion: Retain N64 as the supported operating load; do not promote N68 from its short screen or negligible full difference.
Unknown: The observed load points do not define a universal maximum concurrency or performance curve.

Speaking brief: Full N64 beat N62 by 1.082867% and repeated within 0.013634%. N68 looked 2.27% better in a short screen, but the full pair showed only 0.083056%, below the useful-gain gate. N64 is the supported load choice.

Full N64 increased goodput from 3,011.875 at N62 to 3,044.490 tokens/s, +1.082867%.
N64 repeat 25373 scored 3,044.075, only −0.013634% versus candidate 25366.
N68's +2.27% short-screen result became +0.083056% in full measurement, so it did not establish a useful improvement over N64.

Research sources: 25365/25366/25373;fullN68pair

## Slide 12

Reasoning role: Experimental finding · request-level evidence. Move from aggregate throughput to individual request evidence, showing exactly which SLA condition the remaining failures crossed without assigning an unsupported cause.

Problem: A mean score can hide which requests fail and which latency constraint they violate.
Why It Matters: The service rule requires each good request to meet both TTFT and ITL limits; aggregate goodput alone does not explain failures.
Why This Test: Plot each of the 1,902 scored requests against the two latency limits and classify requests that satisfy both inclusive boundaries.
What We Learned: There are 1,875 joint passes and 27 TTFT-only failures, with zero ITL misses and zero errors.
Next Logic: Keep the cause unknown unless phase-level timing is collected; assess robustness separately from this request-level diagnosis.

Each point represents one profiling request. The horizontal position is that request's time to first token in milliseconds; the vertical position is its request-mean inter-token latency in milliseconds. Teal points meet both inclusive limits: TTFT ≤3,000 ms and mean ITL ≤20 ms. Orange points fail at least one limit. The displayed evidence has 1,875 teal passes and 27 orange failures; all 27 are to the right of the TTFT boundary and none exceed the ITL boundary. This shows a first-token tail. It does not show whether queueing, prefill, transfer, or another phase caused the delay.

Observation: The N64 service has 98.580442% joint success; every one of its 27 SLA failures is TTFT-only.
Hypothesis: A startup-side phase such as admission, queueing, prefill, or KV transfer may contribute to the late first tokens.
Conclusion: The scatter localizes which latency metric fails but does not establish the responsible phase.
Unknown: Per-request queue/prefill/transfer phase timing and a causal account of the 27 misses are not available.

Speaking brief: Of 1,902 requests, 1,875 met both latency limits; all 27 misses were TTFT-only. No request missed ITL, and there were zero request errors. The scatter identifies the failed condition, not why those first tokens were late.

Job 26766 contains 1,902 profiling requests; 1,875 pass both conditions, or 98.580442%.
The 27 failures all miss TTFT. Zero miss request-mean ITL; request errors and cancellations are zero.
The threshold lines classify pass/fail. Point position shows measured latency, but the plot does not include phase timing needed to explain the tail.

Research sources: 26766 raw profile, independent full review and sealed native-runtime payload

## Slide 13

Reasoning role: Robustness · historical and accepted deployment series. Assess repeatability across distinct deployment paths without pooling them as one homogeneous series. The newly completed portable run used the repaired result readers and a genuine full H200 allocation. It supports the retained operating level and closes the previous post-reader-fix GPU acceptance gap, while leaving unexplained drift and single-run uncertainty visible.

Problem: The earlier portable GPU jobs failed in result reading, so CPU-only reader checks did not establish that a complete packaged deployment worked after repair.
Why It Matters: A good benchmark score is useful for submission only if the actual portable package can pass readiness, serve both roles, run the client, read results and clean up in a real allocation.
Why This Test: After one exact-ZIP attempt failed before scoring because the gateway health check returned HTTP 200 while model registration still returned 503, change only the deployment readiness wait and checksum. Keep workers, official client, readers and semantic paths unchanged, then run a complete 16-H200 N64 entry.
What We Learned: Job 28197 completed the full portable entry in 611 seconds, passed both P/D semantic paths and summary gates, and scored 3051.518173 good tokens/s with 98.6366% joint SLA and zero errors/cancellations. This closes the post-reader-fix GPU acceptance gap.
Next Logic: The package has one complete post-fix GPU acceptance run. Keep its scope separate from historical performance repeats, then close with the remaining official model-quality requirement.

Use three separately labelled evidence cards: (A) historical three-run N64 full-run mean 3044.400475 good tokens/s; (B) separate native job 26766 at 3045.501509; (C) new complete portable job 28197 at 3051.518173. Show its 1881/1907 joint SLA passes (98.6366%), zero errors/cancellations, mean/p95 TTFT 1100.315/1285.996 ms and request-mean ITL 15.010/15.186 ms. Footer: older valid low replay 26313 at 2830.923547 remains unexplained; earlier cache 27378 at 3048.446289 was the highest complete individual before 28197, not current peak. No axes: these are distinct measured series, not a continuous trend or error-bar plot.

Observation: 28197 scored 3051.518173 good tokens/s with 1881/1907 jointly passing, zero errors/cancellations, mean/p95 TTFT 1100.3153/1285.9962 ms and ITL 15.009828/15.185750 ms. It completed the full portable entry after the exact-ZIP readiness attempt failed before benchmark.
Hypothesis: Independent native and portable paths should reproduce the retained operating level if the fixes address packaging/readiness rather than changing model semantics or server/client behavior.
Conclusion: The complete portable acceptance run supports the deployment path and is consistent with the prior roughly 3044–3046 operating series. It is one acceptance run, not a fresh matched performance treatment or proof of a global optimum.
Unknown: A lower valid legacy replay remains unexplained; run-to-run variation and broader statistical repeatability are not resolved. Official model quality remains a separate unknown.

Speaking brief: Three evidence series now meet: historical N64 mean 3,044.40, separate native run 3,045.50, and complete portable run 28197 at 3,051.52 good tokens/s. This confirms the packaged path once; lower valid replays still have no identified cause.

The historical three-run mean (3044.400475) summarizes its own series; do not mix it with later runtime paths.
Native job 26766 at 3045.501509 is a separate complete run, not an additional replicate in that historical mean.
Portable job 28197 is a full 16-H200 N64 package run at 3051.518173 good output tokens/s after the reader and gateway-readiness fixes.
Its 1881/1907 requests jointly pass both SLA thresholds (98.63660199265862%); 26 miss TTFT, none miss ITL, and errors/cancellations are zero.
Mean/p95 TTFT is 1100.3153/1285.9962 ms. Mean/p95 request-mean ITL is 15.009828/15.185750 ms.
The earlier complete cache candidate 27378 scored 3048.446289, only +0.240921% over its own fresh control; 28197 is now higher, but these are different deployment series.
Valid lower replay 26313 scored 2830.923547; its cause remains unresolved. This spread warns against claiming all drift is explained.

Research sources: 28197raw/gate/terminalreview;N64historicalseries;26766

## Slide 14

Reasoning role: Robustness · direct cross-hardware verification. Answer the panel’s cross-hardware question using direct H200 measurements, not a conversion factor. A fresh H200 control lets us test selected H100-derived interventions on the target system. The runs show which tested ideas transfer, which lose, and why hardware-specific tuning remains necessary.

Problem: The H100 and H200 results cannot be compared as if only GPU type changed, so we needed to verify H100-derived ideas directly on target H200 hardware.
Why It Matters: A setting that wins or appears promising on H100 can lose on H200 because the hardware and deployment stack differ. Adopting it from cross-platform score ratios could degrade the actual H200 service.
Why This Test: Run four distinct H100-derived interventions on 16 H200 at N64 against fresh or explicit matched H200 controls. Check full protocol, joint SLA, runtime/source and output gates; keep each port’s changed factors visible.
What We Learned: FA3 and the H100 full recipe lost; HPC-Ops chunks recovered part of that branch’s loss but remained below the H200 incumbent; both inference-mode changes were below 0.14%. No transferred setting cleared the 1% usefulness gate.
Next Logic: These tests close the current cross-hardware transfer question. We retain the H200-specific recipe, report the open official-quality limit, then hand over to the OpenFOAM speaker.

Three cards show target-hardware evidence, not a mixed H100/H200 score chart. All displayed throughput values are full N64 measurements on 16 H200. Teal is fresh control 27777 at 3,038.02 good output tokens/s. Red is the transferred full H100 recipe 27783 at 2,721.82, a 10.41% loss. Gray is HPC-Ops prefill with chunk 8192, job 27806 at 2,900.61, still 4.52% below that control. The smaller line summarises the FA3 loss and phase-mode changes; those mode gains use their separate 27826 control. There are no plot axes. Backup 34 provides the complete nine-job ledger, including N54, and the control for every delta.

Observation: The direct H200 ports yielded losses for FA3, the H100 full recipe and both HPC-Ops chunk variants relative to their relevant H200 references. Phase-mode candidates were effectively flat against their explicit control.
Hypothesis: Hardware-specific implementations or settings may not transfer as a complete recipe; test selected components on H200 under a matched target-system base before adopting them.
Conclusion: Retain the H200 DeepGEMM/chunk-8192 prefill and HPC-Ops/FlashInfer/MNNVL decode recipe at N64. None of these tested ports improves goodput by the prospective 1% gate; this is the best-supported measured H200 recipe in this evidence set, not a claimed global optimum.
Unknown: Each candidate is a single run; full official model accuracy is UNKNOWN. The H100 full-recipe port changes coupled settings, and chunk runner comparisons retain generated-seed and run-order limitations. These tests do not establish universal transferability.

Speaking brief: We ported four distinct H100-derived settings onto the current H200 base. Every candidate stayed below the fresh H200 control: chunk 8192 lost 4.52%, while phase-mode changes gained at most 0.13%. Keep the H200 recipe.

All listed measurements ran on 16 H200 at N64, so the target-hardware comparisons use the H200 system rather than comparing H100 and H200 scores directly.
Fresh control 27777 measured 3038.022907 good output tokens/s. FA3 decode 27779 measured 2999.245473 (−1.276404%).
H100 full-recipe port 27783 measured 2721.815800 (−10.408319%). It changes a coupled prefill runner/chunk recipe, so its loss is not attributable to one factor.
HPC-Ops prefill chunk 8192 job 27806 measured 2900.606831 (−4.523207%); chunk 6144 job 27804 measured 2821.884862 (−7.114431%). Larger chunks improved that losing branch versus chunk 4096, but did not beat the DeepGEMM incumbent.
Phase-mode control 27826 measured 3039.167093; decode inference mode 27828 gained 0.006223%, and prefill inference mode 27830 gained 0.130765%. Both are below the team’s 1% usefulness gate.
Four distinct additional H100-derived interventions are represented by jobs 27804, 27806, 27828 and 27830. Job 27826 is their explicit phase-mode control, not another candidate. The broader nine-job final verification also includes 27777, 27779, 27781 and 27783.
MNNVL is the decode-side GPU collective communication path; NIXL transfers request KV state between the separate prefill and decode roles.

Research sources: 27777/27779/27781/27783;27804/27806;27826/27828/27830 final reviews

## Slide 15

Reasoning role: Experimental findings · reject tested alternatives. Compare two proposed improvements that optimize a proxy or subcomponent, and explain why the team retained the existing serving choices after full-service outcomes did not improve.

Problem: Optimizations can improve an attractive proxy while making the actual request-level objective worse.
Why It Matters: Resource savings and fewer decode steps matter only if they increase requests meeting both latency limits.
Why This Test: Place the sparse-graph control/candidate pair and the separate full EAGLE/target-only pair side by side, preserving each comparison's own baseline.
What We Learned: Sparse capture saved logged memory but reduced goodput 0.370208%; shallow EAGLE lost 2.080318% in its full pair.
Next Logic: Keep the selected settings and avoid universal claims; any new variant needs its own matched full-service evidence.

Read the two evidence cards separately because they use different controls and answer different questions. Sparse-graph job 27510 compared with earlier control 27376: capture memory fell from 1.15 to 0.36 GB per rank, while goodput fell 0.370208%. This is a lower resource proxy, not a service win; the pair has one earlier control and differing seeds. The full shallow EAGLE run 27238 compared with target-only control 26949: 2,971.628430 versus 3,034.761104 good tokens/s, −2.080318%. The tested speculative configuration lost in its full workload. Neither card is a universal rejection of graph sparsity or speculative decoding; each closes the exact tested setting pending different evidence.

Observation: Sparse capture memory improved while goodput fell slightly; the full shallow EAGLE treatment lost goodput to its target-only control.
Hypothesis: Less graph storage or draft-token speculation might improve useful serving throughput.
Conclusion: Retain dense graphs and target-only serving for the tested configurations because the full service objective did not improve.
Unknown: The results do not establish that all sparse graphs or all speculative methods fail; padding cost, other shapes, and alternative draft settings were not tested here.

Speaking brief: Sparse graphs reduced capture memory but goodput fell 0.370208% versus control 27376. Full shallow EAGLE scored 2.080318% below target-only control 26949. These separate results reject neither idea universally; they bound the tested settings.

Sparse graph card: 64 to 12 buckets and 1.15 to 0.36 GB capture memory per rank, but goodput is 0.370208% below earlier control 27376.
EAGLE card: full 27238 reached 2,971.628430 versus target-only 26949 at 3,034.761104 good tokens/s, a 2.080318% loss.
Each card supports keeping the tested alternative out of the selected configuration. The controls, mechanisms, and uncertainty differ; do not compare the two percentages as one experiment.

Research sources: 27510/27376;27238/26949

## Slide 16

Reasoning role: Conclusion · claim boundaries and OpenFOAM handoff. Conclude with the distinction between local deployment acceptance and official model-quality acceptance. The full portable GPU path now passes once after the readiness fix; this validates execution and scoring integrity under the team’s gates, but not the model’s full-set accuracy against the organiser reference.

Problem: The prior package jobs failed after inference in result readers, and one exact-ZIP retry stopped before scoring when gateway health preceded asynchronous model registration.
Why It Matters: A team needs to distinguish “the service is fast” from “the actual packaged deliverable completes its official-client acceptance path,” and both from official quality certification.
Why This Test: For 28197, change only the deployment readiness wait/checksum following the 28194 gateway health race. Preserve worker, client, reader, and both semantic paths, then run one complete allocation with cleanup and the existing scoring gates.
What We Learned: All deployment stages passed in 611 seconds; the run scored 3051.518173 good tokens/s, with 1881/1907 joint passes and zero request errors/cancellations. This closes the package replay acceptance gap once.
Next Logic: Finish by stating that package execution and measured service acceptance pass, while full-set official model-quality evaluation remains unknown; then hand over to OpenFOAM.

Two panels: VERIFIED—job 28197 full 16-H200/N64 portable entry, 611 seconds, both P/D semantic paths, official client, reader/summary gate and cleanup passed; 3051.518173 good output tokens/s, 1881/1907 joint SLA (98.6366%), 26 TTFT misses, zero ITL misses/errors/cancellations. OPEN—organiser full-set accuracy ≥99% of reference is UNKNOWN. Label these as deployment acceptance versus model-quality validation. MNNVL is the decode GPU collective path; NIXL carries request KV between prefill and decode roles. The next visible physical slide is unchanged OpenFOAM 35.

Observation: A full portable 16-H200/N64 entry passed in 611 seconds at 3051.518173 good output tokens/s and 98.6366% joint SLA with zero scored errors/cancellations.
Hypothesis: Fixing the gateway model-readiness race while preserving the official client, server workers and result readers should let the package pass the full acceptance path.
Conclusion: The portable package now has one complete post-fix GPU acceptance pass. Retain the N64 H200 recipe; the measured performance is supported, while official quality is not yet established.
Unknown: Organiser full-set accuracy ≥99% of reference remains UNKNOWN. One portable acceptance does not establish statistical repeatability of this package path.

Speaking brief: Portable job 28197 passed the complete 611-second H200 deployment entry, scoring 3,051.52 good tokens/s with 98.64% joint SLA. The organiser’s full-set ≥99%-reference quality result remains unknown.

28197 used 16 H200 at N64 and completed the whole portable entry in 611 seconds, including startup readiness, semantic checks for both roles, the official client, reader/summary gates and cleanup.
The exported score is 3051.518173 good output tokens/s; 1881/1907 requests met both latency thresholds jointly (98.63660199265862%).
Latency: mean/p95 TTFT 1100.3153/1285.9962 ms; mean/p95 request-mean ITL 15.009828/15.185750 ms; 26 TTFT misses, zero ITL misses and zero scored errors/cancellations.
This closes the complete portable post-reader-fix GPU acceptance gap with one successful entry. It is not a new matched optimization experiment or a global-optimum proof.
Official full-set model accuracy against the organiser reference remains UNKNOWN; portable execution does not establish that score.
HPC slides and claims are unchanged; handoff is physical slide 35.

Research sources: 28197gate/summary/semantic/cleanup;officialQ1

## Slide 17

Reasoning role: Backup · Environment. Set the comparison boundary for all later platform results: a shared model and client make experiments more comparable, but do not erase differences in hardware or deployment stack.



The table contrasts allocation, scheduler, container launcher, serving/client software, and model. Matching rows are useful controls: both systems have two eight-GPU nodes and use the same staged artifacts and Qwen3-235B FP8 checkpoint. Different rows are potential influences on latency and throughput. Slurm and PBS schedule resources; they do not execute model inference. Pyxis/Enroot and Singularity provide different container launch paths, while SGLang serves requests and AIPerf generates and measures client traffic. Therefore a score needs its platform, topology, backend, and load attached.

Observation: Both sites provide sixteen GPUs across two nodes and share staged images and model checkpoint, while GPU family, scheduler, launcher, and host environment differ.
Hypothesis: Matching the model and request workload is necessary, but platform differences may still affect serving measurements.
Conclusion: Report each platform's results separately and name its deployment conditions.
Unknown: This table does not isolate the effect of any one platform difference or define an H100-to-H200 score multiplier.

Speaking brief: Both systems allocate sixteen GPUs and use the same Qwen checkpoint and staged workload. Firmus uses H200s; NSCC uses H100s. Different hardware, schedulers, containers, and node conditions mean their scores are separate measurements, not a direct GPU conversion.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
Common controls are the two-node, sixteen-GPU allocation, the staged serving and client artifacts, and the Qwen checkpoint.
Platform differences include H200 versus H100 GPU generation, Slurm versus PBS, and different container launchers. CPU, driver, network, node cache, and process placement can also differ.
The table establishes context; it does not provide a controlled performance result or quantify each site's contribution.

Research sources: Qwen rules; NSCC asset contract; matched-anchor audit

## Slide 18

Reasoning role: Backup · Compatibility mechanism. Teach a concrete compatibility failure from the model's weight geometry and distinguish a layout that can load from a deployment that has passed service tests.



Start with the MoE intermediate dimension, 1,536 elements, then divide by the effective tensor-parallel split. TP8/EP1 gives 1,536 ÷ 8 = 192. The tested kernel needs whole 128-element FP8 blocks, so 192 becomes one full block plus 64 unusable remainder elements. TP8/EP2 changes effective MoE tensor parallelism to four: 1,536 ÷ 4 = 384, exactly three full blocks. The red remainder marks a load-time compatibility failure, not lost output tokens. The arithmetic explains why the old shape failed and why the replacement shape is compatible; it is not a benchmark chart.

Observation: TP8/EP1 yields a 192-element partition, not divisible into 128-wide blocks; TP8/EP2 yields 384 elements, exactly three blocks.
Hypothesis: Changing expert partitioning can make the existing FP8 weights compatible with the kernel while retaining the model contents.
Conclusion: EP2 corrects the tested block geometry and makes a compatible deployment attempt possible; this combined layout change is not an isolated TP speedup.
Unknown: Alignment alone does not establish successful full startup, request SLA, output quality, or improved throughput.

Speaking brief: The failed TP8/EP1 partition had 192 elements, which leaves a 64-element remainder against a 128-wide FP8 block. EP2 changes the effective split to 384 elements, or three full blocks. That fixes this shape mismatch; it does not prove serving speed or quality.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The two equations are the key evidence: TP8/EP1 produces 192 elements; TP8/EP2 produces 384.
The 64-element remainder is why the first tested path failed during loading. EP2 removes that remainder by changing expert distribution, not precision or model size.
The footer lists evidence still required after compatibility: successful startup, service-level latency checks, and output-quality checks.

Research sources: Exact staged SGLang source; failed job 24282; corrected trial 24321

## Slide 19

Reasoning role: Backup · Chronology as supporting evidence. Use the historical chart as context for the research questions: it shows which operating points motivated later controlled tests, while teaching why a rising sequence is not a cumulative causal experiment.



The horizontal axis lists named milestones, not dates or equal time intervals. The vertical axis is good output tokens per second, so taller bars mean more requests meeting the latency limits under that milestone's workload. Gray marks early layouts, teal marks backend specialization, and orange marks later tuning and repeat points. The chart progresses from 1,297 at N32 and 1,666 at N40, through 1,912 at N48 and 2,631 at N52, to a rounded historical N64 mean of 3,044. Since concurrency, worker layout, backends, and runtime conditions change along the way, the chart shows the team found stronger measured configurations; it does not show how much any one change caused.

Observation: Measured good output throughput rises across named operating points from 1,297 at N32 to a rounded 3,044 at historical N64.
Hypothesis: Recovering a usable split and transfer path, then specializing attention, collective, prefill, and decode backends, helped identify stronger configurations.
Conclusion: The chart is a map of milestones and later replication targets; it is not evidence the named optimizations add up to the full rise.
Unknown: Loads, topology, runtime settings, and observation conditions vary; individual causal contributions and a global optimum are not established.

Speaking brief: The H200 chart rises from 1,297 good tokens/s at N32 to a 3,044 N64 mean. It shows better measured operating points over the campaign, but each milestone changes load or configuration, so the bars do not assign a causal gain to each optimization.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The milestones are 1,297 (initial 07/N32), 1,666 (initial 09/N40), 1,912 (split/N48), 2,631 (FlashInfer plus MNNVL/N52), 2,716 (DeepGEMM prefill/N56), 2,939 (DeepGEMM plus HPC-Ops/N58), 2,989 (repeated N60), 3,023 (repeated N62), and 3,044 (three historical N64 runs). Labels are rounded.
Later N62 runs measured 3,022.034919 and 3,023.072304; later N64 repeats measured 3,044.489701 and 3,044.074628. These support repeatability at those settings, not a universal optimum or causal explanation for every step.
Colors group phases of work; they are not pass/fail marks. Bar height is a score, not a confidence interval.

Research sources: Historical retained milestones; 24724/24737/24819; 24738/24913; 24915

## Slide 20

Reasoning role: Backup · Intervention & correctness. Describe the intervention precisely and put its correctness evidence at the right level. The patch changes descriptor scope and coalescing in heterogeneous-TP transfer while retaining the relevant mapping behavior; CPU equivalence is not the same as validating real transport on GPUs.



This is step 5 and the first half of step 6 in the seven-step chain: exact change, then the correctness gate that was actually run. Keep the distinction between address-range equivalence and real GPU transfer visible.

Observation: The patch implements request-only descriptor preparation and contiguous-range coalescing; retained CPU tests pass 720 range-equivalence cases, including the representative count of 188 for the contiguous request.
Hypothesis: If the mapping is preserved while irrelevant pool ranges are omitted, setup can do less descriptor work without changing the KV bytes required by the request.
Conclusion: The CPU fixture supports address and byte-range equivalence for its tested geometries. It is a correctness gate for the mapping, not a full deployment validation.
Unknown: The fixture does not validate real GPU transport. It does not time old and new descriptor creation or establish that this change alone resolves the earlier timeout.

Speaking brief: The patch builds descriptors for requested KV pages and coalesces contiguous ranges while preserving mapping and stride. CPU tests passed 720 geometry cases; the fixture explicitly did not validate real GPU transport.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
Step 5 — Intervention: replace full-pool source and destination descriptor enumeration with request-scoped descriptors, then coalesce contiguous ranges.
The patch scope retains equal-TP behavior, weights, precision, KV-head mapping, per-token stride where a head slice is sent, and notifications.
Step 6, correctness part: 720 original-versus-patched CPU geometry cases pass byte-range equivalence.
The fixture records real GPU transport validation as false. Therefore CPU mapping checks do not prove GPU transfer, server readiness, or valid responses.

Research sources: nixl-ondemand/{README.md,nixl-ondemand.patch,metadata.json,geometry-test.json}

## Slide 21

Reasoning role: Backup · End-to-end evidence & limits. Close the seven-step chain with real end-to-end evidence and an explicit limit. The patched heterogeneous topology completed P/D warmup and a full N32 confirmation, but the absence of an equivalent successful no-patch run prevents causal speedup attribution.



This is steps 6 and 7: real path/result, then decision and unknowns. State the warmup duration, benchmark score, joint SLA, and zero errors as results of patched job 22294, not as a directly matched speedup over 22271.

Observation: Patched job 22294 completed P/D warmup in 0.68–0.70 seconds per request after server readiness, then scored 1422.96 good tokens/s at N32 with 95.87% joint SLA and zero errors/cancellations.
Hypothesis: Request-scoped descriptor setup may have helped the previously blocked topology reach a serving state, but differences between attempts could also explain the contrast.
Conclusion: The supported claim is patched-path feasibility and an end-to-end result for this P8 TP8/EP2 to D8 TP4/EP4 run. The patch's speedup is unmeasured.
Unknown: There is no successful matched unpatched run for this exact topology; old-versus-new setup time, network utilization, causal warmup decomposition, and the patch's independent goodput contribution remain unknown. Bandwidth, KV layout, placement, and other bootstrap explanations were not ruled out.

Speaking brief: On patched job 22294, pair warmup took 0.68–0.70 seconds per request and full N32 goodput was 1,422.96 with 95.87% joint SLA and zero errors. No matched unpatched control measures speedup.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
Step 6, end-to-end part: patched job 22294 completed both real prefill/decode warmup paths in 0.68–0.70 seconds per request after workers were ready.
It then completed a full N32 confirmation: 1,422.96 good output tokens/s, 95.87% joint SLA, zero errors and zero cancellations.
Step 7 — Decision: the run establishes feasibility of the patched heterogeneous topology and that this run served requests under the local benchmark protocol.
It does not establish the patch's independent speedup: no successful no-patch end-to-end control exists for the same topology, and no old/new descriptor setup timer or causal latency decomposition was collected.

Research sources: 22271/pair-warmup.log;22294/pair-warmup.log;22294/confirm/n32/artifacts/profile_export_aiperf.json

## Slide 22

Reasoning role: Backup · Platform-specific tradeoff. Explain why evaluating only time to first token can select the wrong decode backend: latency over a long answer and qualifying throughput also matter.



The pair changes decode attention from FlashInfer to FA3 while holding H100, N54 load, and the rest of the tested path matched. Read across each metric: FA3 lowers mean time to first token by 118.922 ms, but raises mean inter-token latency by 0.773 ms. Repeated over roughly 199 token intervals, that adds about 154 ms. Mean request latency rises from 4,337.853 to 4,372.813 ms, and goodput falls 0.812%. Thus the early response improves while the full answer becomes slower on average and fewer requests qualify per second. This is one pair for this H100 decode setting, not a general ranking of attention libraries.

Observation: FA3 improves mean TTFT by 118.922 ms but worsens mean ITL by 0.773 ms and mean request latency by 34.960 ms; goodput falls 0.812%.
Hypothesis: Changing decode attention can move startup and per-token costs in opposite directions.
Conclusion: Keep FlashInfer for this tested H100 decode setting; FA3 remains used for prefill.
Unknown: One matched pair does not rank attention backends generally or isolate exact kernel-level causality.

Speaking brief: In one matched H100 N54 pair, FA3 cut mean TTFT from 713.199 to 594.276 ms, but goodput fell from 2,420.945 to 2,401.284 tokens/s, about 0.812%. A faster first token did not improve the full request objective.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
FlashInfer → FA3: good output tokens/s 2,420.945 → 2,401.284; mean TTFT 713.199 → 594.276 ms; mean ITL 18.214 → 18.988 ms; mean request latency 4,337.853 → 4,372.813 ms.
Both runs passed team-reviewed protocol, runtime, and output checks on the assigned cluster, and FA3 was confirmed active on all eight decode ranks. That establishes the tested intervention actually ran, not that it improved the service.
The historical H100 individual peak of 2,433.019859 and fresh N54 control of 2,399.186728 are context, not the two arms of this matched pair. They do not provide an H100/H200 hardware conversion.

Research sources: 222027/222028 matched fullH100N54pair;222048historicalpeak;225227freshcontrol

## Slide 23

Reasoning role: Backup · Cost hypothesis & confirmation. Teach why a favorable first pair is not enough for adopting a startup optimization: execution order, cache state, nodes, and the predeclared cost threshold affect interpretation.



Compare the first pair with the reversed-order confirmation. In the first pair, off/read-first walltime was 934/759 seconds, a reported 18.74% saving, while goodput fell 0.659%. In the reverse-order pair, walltime was 854/770 seconds, a 9.84% saving, and goodput changed −0.326388%. The planned rule required at least 10% walltime saving and at most 2% goodput loss. The reverse pair meets the throughput tolerance but misses the walltime requirement. Scheduler walltime includes startup and cleanup; it is not the 120-second steady-state score window.

Observation: Read-first saved 18.74% walltime in the first order but 9.84% after reversing the order; goodput changed −0.659% and −0.326388%, respectively.
Hypothesis: Reading prefill weights before measured startup may reduce startup walltime.
Conclusion: The reverse-order confirmation missed the predeclared 10% saving threshold, so the team did not adopt the change.
Unknown: Unverified OS cache state and node differences prevent a causal cold-storage explanation.

Speaking brief: Read-first initially reduced scheduler walltime by 18.74%, but the reversed-order confirmation saved only 9.84%, below the predeclared 10% threshold. Goodput changed slightly in both pairs; unknown cache state prevents a cold-storage causal claim.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The first pair looked favorable for startup time but had a 0.659% goodput loss. The reversed pair cut the apparent saving below the 10% decision threshold.
The reverse pair's 0.326388% goodput change is within the stated 2% tolerance, but that alone cannot rescue the branch because the walltime threshold was missed.
Node differences and unverified file-cache state mean the result cannot be assigned to cold storage. A cold prefix is a model KV-cache condition and is not the same as cold filesystem pages.

Research sources: Startup-prefetch original and reverse-pair reviews; static locality222412

## Slide 24

Reasoning role: Backup · Negative measured interventions. Show how the team used source inspection, runtime activation checks, matched controls, and output review to decide whether small interventions deserved adoption.



The rows are independent hypotheses, not pieces of one cumulative optimization. Source review first identified a setting the runtime could consume; logs then confirmed activation; full serving runs measured the result. A small positive goodput change can fall below a useful threshold or worsen p95 first-token latency. Negative and neutral results therefore answer the research question: functionality is necessary, but only improvement in the service objective justifies changing the retained configuration.

Observation: Changes had source/runtime checks and full serving observations, but measured gains were small, negative, or mixed with worse tail latency.
Hypothesis: Changes in tokenization, collective, cache, request cap, polling, or attention might improve goodput.
Conclusion: Keep a change only when the intended path ran and a controlled service comparison improves the objective enough to matter.
Unknown: Small single-run differences may reflect run variation; these rows do not establish a CPU bottleneck or universal feature ranking.

Speaking brief: Several H200 changes were activated and measured, but gains were small, negative, or worse in a tail metric. For example, a prefill attention change lost 6.385% goodput. A working flag is not enough to replace the selected configuration.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
Tokenizer wait changes measured +0.192% and +0.270%; the team kept tokenizer batching off. Switching the auto-selected prefill collective from TRT-LLM to MNNVL activated on all eight prefill ranks but gained only +0.109807% in full run 27138.
Prefill RadixCache to ChunkCache gained +0.240921%, but p95 TTFT worsened, so RadixCache stayed. Request-cap and polling comparisons were +0.26% or negative and did not demonstrate useful gain.
Prefill FlashInfer page 1 reduced ITL but lost 6.385% goodput. Percentages belong to separate branches; do not add them as if they were components of one run.

Research sources: 26949/26951/26953;27138 actual collective source/activation;27077;27365;27376/27378;27270/27272/27274

## Slide 25

Reasoning role: Backup · Diagnostics versus full serving. Answer what kernel names, profiles, and source inspection can establish, and prevent a component result on one hardware family from being mistaken for full-model evidence on another.



Read each row as an evidence boundary. The N52 H200 attention package is a real serving score but has coupled changes. H100 Triton probes test selected kernel shapes, not every model shape. SM budgets are bounded kernel/runtime checks, not model-level speed results. NCCL logs corrected an earlier interpretation: the label LL did not mean the tested control used that low-latency protocol for all messages. The real Qwen compile reached a native RoPE/fused-KV assertion before scoring. C++ CPU fixtures and source findings are narrower still. Mixing these rows would mix H200, H100, and CPU evidence.

Observation: Evidence ranges from one H200 serving score through H100 kernel/resource probes to CPU-only helpers and source review; their scopes differ.
Hypothesis: Alternative kernels, communication protocols, resource budgets, or APIs might improve a specific part of serving.
Conclusion: Use component evidence to select a full-model test only when the code path and hardware support it; do not claim service improvement from probes or source alone.
Unknown: Untested shapes and configurations may differ. The failed Qwen compile and CPU tests leave full-model compatibility and performance unresolved.

Speaking brief: The 2,549.20 N52 attention package changed several factors; representative Triton probes, CPU fixtures, and source review answer narrower questions. Full Qwen compilation stopped at a RoPE/KV assertion. None alone proves a full-model serving gain.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The H200 N52 attention-DP plus DeepGEMM/DeepEP package scored 2,549.20, below the retained MNNVL point; coupled settings block one-factor attribution.
Representative H100 FP8 Triton probes lost to DeepGEMM in tested shapes. H100 SM budgets 80/96/120 were mixed or below consistency criteria; 132 was retained without claiming a model gain.
The small 0.2315% NCCL point did not justify adoption after logs showed the control already selected Simple for large messages. Qwen compile failed before score; CPU fixtures did not test serving.

Research sources: JOURNEY stages15,29-31;DeepGEMM representative probes;NCCL source correction;27383;27506

## Slide 26

Reasoning role: Backup · Exact deployment settings. Document the currently retained measured recipes on each platform and add the completed H200 portable deployment acceptance. Keep H100 measurements separate; a successful H200 package run does not convert H100 scores or certify official quality.



Keep the existing H200/H100 configuration table and add a separate H200 acceptance note: job 28197, 16 H200, N64, full portable path, 611 seconds, 3051.518173 good tokens/s, 1881/1907 joint passes. Label H100 N54 configuration as its own measured operating point; do not imply it matches or predicts the H200 result. Note official model quality is UNKNOWN.

Observation: The retained configurations share some decode and precision settings but differ in hardware, concurrency, prefill backend, and chunk size.
Hypothesis: Explicit platform-specific settings make the replicated operating points reproducible and interpretable.
Conclusion: Use the H200 N64 settings for the selected primary and report H100 N54 independently.
Unknown: This table does not establish that the settings are optimal or that performance transfers between platforms.

Speaking brief: The retained H200 recipe and H100 recipe remain separate. H200 now also has a complete portable acceptance run at 3,051.52 good tokens/s; this validates deployment, not H100-to-H200 conversion.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
H200: client concurrency 64; two TP4/EP1 prefill workers; DeepGEMM; chunk 8,192; one HPC-Ops TP8/EP8 decode worker.
H100: client concurrency 54; two TP4/EP1 HPC-Ops prefill workers; chunk 4,096; TP8/EP8 HPC-Ops decode. Keep H100 point separate from H200 scores.
Both use the listed weight/activation/KV precision and shared decode attention, collective, routing, and request-quality rules. Official full-set accuracy is not certified by this configuration table.
New H200 portable acceptance job 28197 completed the full entry in 611 seconds at N64 and measured 3051.518173 good output tokens/s.
This confirms the H200 package path once; it is not a matched H100/H200 GPU speed comparison and does not certify full-set quality.

Research sources: 26766 frozen worker/runtime; 25487 operational settings; staged portable deployment validation

## Slide 27

Reasoning role: Backup · Fixed protocol & negative result. Explain the benchmark protocol behind the chunk table so its negative result is interpreted as a controlled, bounded comparison rather than a claim about all workloads.



The table compares three full runs with the same target concurrency, requested prompt/answer lengths, seed, cold-prefix setting, model, precision, and runtime path. Only prefill chunk size changes: 8,192, 10,240, or 12,288 input tokens handled together. Read good output tokens/s as qualifying throughput, joint SLA as the fraction meeting both limits, and p95 TTFT as the slow-response tail. Goodput and the tail both worsen at larger chunks. One run per setting supports retaining 8,192 for this configuration, but cannot identify a general optimum.

Observation: Goodput decreases from 3,045.50 to 3,020.94 tokens/s and p95 TTFT increases from 1,311.69 to 1,624.12 ms as chunk grows from 8,192 to 12,288.
Hypothesis: A larger prefill chunk might increase throughput by handling more input tokens per scheduling batch.
Conclusion: Retain 8,192 for this service configuration; the tested larger chunks did not improve the objective.
Unknown: One run per chunk makes the comparison bounded; it does not establish a global optimum or rule out order/seed variation.

Speaking brief: Under the same full N64 workload, increasing prefill chunk from 8,192 to 12,288 reduced goodput from 3,045.50 to 3,020.94 tokens/s and worsened p95 TTFT. Each setting has one reviewed H200 run; this does not establish a global optimum.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
At chunk 8,192, job 26766 scored 3,045.501509 good output tokens/s, 98.580% joint SLA, and 1,311.69 ms p95 TTFT. At 10,240, job 26768 scored 3,034.088251, 98.524%, and 1,518.87 ms.
At 12,288, job 26770 scored 3,020.943099, 98.310%, and 1,624.12 ms. All three were full N64 runs with the same 60/120/30 schedule and requested 4,000/200 workload; each chunk setting was observed once.
The runs passed team protocol, runtime, latency, and output checks with zero profiling errors/cancellations. That is a reviewed result on the assigned cluster, not organizer quality certification.

Research sources: 4000/200seed2026closedloop;26766/26768/26770 fullreviews

## Slide 28

Reasoning role: Backup · Resource metric versus objective. Explain why a lower resource metric is not automatically a service improvement, and separate capture memory from total GPU memory and end-to-end throughput.



Compare dense control 27376 with sparse candidate 27510. The candidate stores 12 decode graph buckets instead of 64 and reduces logged graph-capture memory per rank, but goodput is 3,029.861122 versus 3,041.119598, 0.370208% lower. Mean request ITL rises from 14.991 to 15.136 ms; TTFT improves. Fewer buckets may force requests into less exact padded shapes, which can add work, but padding was not isolated or measured here. The reported capture memory excludes other GPU allocations such as model weights and KV cache, so it is not a VRAM capacity figure. The service score, not the smaller capture number, determines whether this is useful.

Observation: Sparse capture reduced logged per-rank graph memory from 1.15 to 0.36 GB and slightly shortened capture, while goodput fell by 0.370208% against the earlier control.
Hypothesis: Fewer captured shapes might save resources while maintaining service throughput; padding was a possible mechanism but not measured.
Conclusion: The service objective did not improve, so the team retained dense graphs for this deployment.
Unknown: There is one earlier control and generated seeds differ; total VRAM use and any padding effect were not measured by the capture-memory metric.

Speaking brief: Sparse capture cut logged memory from 1.15 to 0.36 GB per decode rank, but goodput fell 0.370208% and mean ITL worsened. Padding was not measured as a cause. The team retained dense graphs; this pair does not prove a causal effect.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The dense control has 64 buckets, 1.15 GB capture memory per rank, 101.46–101.49 s capture time, 3,041.119598 good output tokens/s, and 14.991 ms mean ITL.
The sparse candidate has 12 buckets, 0.36 GB/rank, 95.98–96.05 s capture time, 3,029.861122 good output tokens/s, and 15.136 ms mean ITL. Captures were confirmed on all eight decode ranks with model compilation off.
Candidate mean/p95 TTFT was 1,102.404/1,240.481 ms and improved, while mean/p95 ITL was 15.136/15.324 ms and worsened. One earlier control, different engine seeds, and candidate-only startup instrumentation limit causal interpretation.

Research sources: 27510 terminal raw/runtime/capture review;27376 prior control

## Slide 29

Reasoning role: RQ4 · Robustness & confounder checks. Investigate a discrepancy rather than explain it with a convenient single flag. The evidence identifies changed settings and measurement context, but the completed comparison does not isolate one sufficient cause.



The question is why historical full N64 averaged 3,044.400475 while a newer short control was about 2,560. Show that ServerArgs differ in prefill graph policy and max-running-request cap, and that harness/observation protocol also differs. Exact legacy replay 26313 reaches 2,830.923547; new native run 26766 reaches 3,045.501509. These rows are different runtime/protocol series, not a clean single-factor ladder.

Observation: Scores vary across the historical full series, short control, legacy replay, and native runtime; several settings and measurement conditions changed together.
Hypothesis: Changed graph policy, server admission cap, runtime, or measurement harness could contribute to the observed drift.
Conclusion: Retain the lower valid result and label its protocol/runtime; no single-factor explanation was established.
Unknown: The factorial evidence did not isolate one causal factor sufficient to explain the historical-to-new score difference.

Speaking brief: Historical full N64 averaged 3,044.40 while a newer short control was about 2,560. Graph policy, server admission cap and measurement procedure changed. The completed tests did not isolate one cause, so we retain the drift without attributing it to one flag.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The historical full N64 mean is 3,044.400475, while a later short control is approximately 2,560. Actual ServerArgs show a changed prefill graph policy and max-running-request cap; harness and observation conditions also differ.
An exact legacy operational replay 26313 reaches 2,830.923547, and native-runtime full run 26766 reaches 3,045.501509. The completed graph/admission factorial did not identify one useful cause. Therefore neither restoring one flag nor changing the launcher alone can be credited for the whole score difference.

Research sources: Incumbent recovery plan;26313 legacy full result;graph/admission factorial;26766 native full review

## Slide 30

Reasoning role: RQ3 · Failed hypothesis → revised test. Trace the full EAGLE3 reasoning chain: a placement hypothesis, a validator defect, a corrected short retry, and a separate full test. Repairing a measurement tool makes a rerun valid; it does not turn a losing performance result into a win.



Read stages in order: all-worker draft 25948 fails the joint latency gate; decode-only attempt 25988 is rejected because the validator expects draft KV regions on target-only prefill; repaired short run 25998 passes its limited protocol but loses 4.74% goodput; separate shallow full run 27238 loses 2.080318% versus control 26949.

Observation: After validator repair, the short decode-only retry loses 4.74%, and the distinct shallow full trial loses 2.080318% goodput.
Hypothesis: Restricting draft execution to decode or using a shallow draft may reduce TTFT without sacrificing total service throughput.
Conclusion: The tested variants do not solve this workload; close them while preserving the tooling failure and repair history.
Unknown: The observations do not explain precisely which service phase causes the slowdown, nor rule out every possible speculative configuration.

Speaking brief: EAGLE3 placement missed latency; a validator bug was repaired; the short retry and separate full shallow trial both lost goodput. The tested method therefore did not help this workload, although other configurations remain untested.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
The initial all-worker trial 25948 misses the joint latency gate. Moving the draft to decode-only was hypothesized to reduce first-token delay. Attempt 25988 is then rejected by a validator that wrongly applies draft KV-region counts to target-only prefill; the role-aware repair preserves the original failure.
Short retry 25998 passes its limited protocol but loses 4.74% goodput against its own target-only control. Later full shallow run 27238 reaches 2,971.628430 versus control 26949 at 3,034.761104, a 2.080318% loss. Low draft acceptance is descriptive telemetry, not a causal timing explanation.

Research sources: 25948;25988 role-aware KV repair;25947/25998 short review;26949/27238 full shallow review

## Slide 31

Reasoning role: RQ4 · Real replay & failure analysis. Present the complete debugging sequence so the audience can distinguish preserved failures, CPU-only reader repair, a separate gateway readiness race and the eventual complete GPU acceptance. Do not retroactively relabel any failed scheduler job as successful.



Use a four-step timeline: 27136 portable GPU inference/client completed then nested-result reader failed; 27145 portable GPU inference/client completed then alias-path reader failed; 27152 zero-GPU CPU job passed both readers on real saved exports; 28194 exact-ZIP retry failed prebenchmark with curl exit 22 because gateway health returned HTTP 200 while asynchronous model registration still returned HTTP 503; 28197 changed only deploy readiness wait/checksum, kept workers, official client, readers and semantic checks unchanged, and completed the whole entry in 611 seconds on 16 H200 N64. Mark each original failure FAILED; 28197 is the successful new allocation.

Observation: The two reader failures were corrected on CPU; one exact-ZIP attempt then failed prebenchmark due to a gateway readiness race; a new full GPU entry passed after a narrowly scoped readiness adjustment.
Hypothesis: Waiting for actual model registration readiness, rather than accepting the health endpoint alone, addresses the remaining startup race.
Conclusion: 28197 demonstrates that the repaired portable deployment can pass its full local acceptance path. Keep 27136, 27145 and 28194 recorded as failures.
Unknown: One complete pass does not establish statistical deployment reliability or official model quality; broader failure mechanisms outside the observed paths remain unknown.

Speaking brief: Jobs 27136 and 27145 failed in separate result-reader defects; 27152 verified both fixes on CPU. Exact-ZIP job 28194 then hit a gateway health/registration race before scoring. Job 28197 changed readiness wait/checksum and passed the full 611-second H200 entry.

27136 and 27145 remain failed jobs; their saved outputs allowed diagnosis of two distinct reader bugs.
CPU job 27152 verified both reader repairs against real saved data, but did not test a GPU deployment.
Exact-ZIP retry 28194 was a separate failure before AIPerf scoring: health responded HTTP 200 before asynchronous model registration was ready, which still returned 503; curl exited 22.
Job 28197 adjusted only readiness waiting and checksum. Worker images, official client, result readers and both semantic routes remained unchanged.
28197 completed gateway readiness, both P/D semantic routes, client workload, summary acceptance gates and cleanup in 611 seconds using 16 H200 at N64.
The full entry scored 3051.518173 good output tokens/s, with 1881/1907 jointly qualifying requests, 26 TTFT misses, zero ITL misses and zero errors/cancellations.
This closes full post-reader-fix GPU deployment acceptance once; it does not certify model quality or erase earlier failed statuses.

Research sources: 28194failure;28197completeindependentreview;27136/27145/27152

## Slide 32

Reasoning role: RQ3 · Hypothesis → intervention. Ask whether attention and collective-communication choices work better together than separately at a fixed H200 load. The comparison is a motivation for a combination, not proof that independent component gains add up.



Interpret the N52 observations as separate backend configurations at one load: FlashInfer alone 2,440.386, MNNVL alone 2,592.162, the combined choice 2,631.085, and a later MNNVL control 2,594.028 good tokens/s. Compare the combination with the later same-load MNNVL control: about +1.43%.

Observation: The combined observation exceeds the later MNNVL control by about 1.43% at H200 N52; standalone FlashInfer and MNNVL observations are lower.
Hypothesis: The attention and communication choices may interact favorably when used together.
Conclusion: The measured combination is promising at this load and merits comparison as a complete serving setting.
Unknown: The result does not quantify component-level causal gains or establish behavior at another load, model, or hardware setup.

Speaking brief: At H200 N52, combining attention and communication measured about 1.43 percent above a later MNNVL control. This supports the combined setting at this load, not additive component gains or a universal rule.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
Question: does choosing both an attention implementation and a communication backend improve the service? At H200 N52, the standalone and combined observations are 2,440.386, 2,592.162, and 2,631.085 good tokens/s. A later MNNVL control at the same load is 2,594.028; the combined observation is approximately 1.43% higher than that control.
The evidence supports testing or retaining the combined operating point for this configuration. It does not establish a general interaction law, isolate each backend's causal contribution, or permit adding the standalone differences as if the components were independent.

Research sources: 23777; 23778; 23904; 23974

## Slide 33

Reasoning role: Backup · forecast and uncertainty limits. Assess whether a platform-specific calibration transfers to a nearby held-out operating point, while keeping an operational tolerance distinct from statistical uncertainty.

Problem: A cross-platform score ratio might help plan nearby measurements, but it could be mistaken for a general hardware multiplier.
Why It Matters: Hardware, software, and workload interact; one ratio can fit a local setting while failing elsewhere.
Why This Test: Use H100/H200 N52 means to freeze an H200 N50 forecast, then compare against a result not used in calibration.
What We Learned: Job 24272 missed the frozen prediction by −1.5371%, within the predeclared ±2% band, while exposing that the earlier sensitivity range omitted model error.
Next Logic: Retain this as one local prospective check and avoid using it to convert other loads or platforms.

The calibration comparison uses the same N52 combo configuration: H100 mean 2,215.460 good tokens/s across two allocations and H200 mean 2,632.181 across four, ratio 1.188096805. Applying that ratio to H100 N50 produced a forecast frozen before seeing H200 job 24272: 2,642.244. The held-out H200 measurement is 2,601.629, signed error −1.5371%. It falls within the predeclared ±2% operational tolerance but outside the earlier input-only sensitivity range, which omitted model error. The forecast is not refit after seeing the answer.

Observation: One held-out H200 result is 1.5371% below forecast, within operational tolerance and outside the prior incomplete sensitivity range.
Hypothesis: A ratio measured at N52 may predict a nearby H200 N50 result when the tested combo is held comparable.
Conclusion: This one prospective check meets the team's tolerance; preserve the missing-model-error limitation and do not refit the forecast.
Unknown: Accuracy across other loads/configurations, total predictive uncertainty, physical-device diversity, and a universal platform conversion remain unknown.

Speaking brief: A forecast recorded before the H200 measurement misses by about 1.54%, inside our stated 2% tolerance. It nevertheless exposes missing uncertainty. One near-correct prediction supports a limited check, not a universal H100-to-H200 conversion.

Same N52 combo: H100 mean 2,215.460; H200 mean 2,632.181 good tokens/s; ratio 1.188096805.
Frozen H200 N50 forecast: 2,642.244. Held-out job 24272: 2,601.629, signed error −1.5371%.
The result is within ±2% operational tolerance but outside the incomplete earlier sensitivity range. These statements are compatible because the range omitted model error.

Research sources: frozenN52calibration;held-out24272

## Slide 34

Reasoning role: Backup · final controls, ports and decisions. Keep the complete final H200 verification auditable for questions. Distinguish the nine scheduler jobs from the four distinct additional H100-derived intervention ports, show the proper control for each branch, and explain why none replaced the incumbent.



The compact ledger has with columns job, intervention/control, good output tokens/s and delta against its stated H200 control. Rows: 27777 fresh DeepGEMM/chunk-8192 incumbent control 3038.022907; 27779 FA3 decode 2999.245473 (−1.276404%); 27781 H100 both-HPC-Ops/chunk-4096 recipe N54 2738.940099; 27783 same recipe N64 2721.815800 (−10.408319% vs 27777); 27804 HPC-Ops chunk 6144 2821.884862 (−7.114431%); 27806 HPC-Ops chunk 8192 2900.606831 (−4.523207%); 27826 explicit no_grad phase control 3039.167093; 27828 decode-only inference mode 3039.356215 (+0.006223%); 27830 prefill-only inference mode 3043.141258 (+0.130765%). The control column labels comparison branches so percent denominators cannot be confused. Units: good output tokens/s. Nine GPU allocations include controls and repeated-load/coupled arms; they are not nine unique winning candidates.

Observation: Nine allocations completed with zero scored errors/cancellations. The candidates either lost to their applicable H200 control or remained below the team’s prospective 1% threshold.
Hypothesis: Testing H100-derived settings directly on the target H200 system can reject harmful transfers and identify small effects before changing the recipe.
Conclusion: No candidate changes the H200 incumbent. Retain DeepGEMM prefill/chunk 8192 with HPC-Ops/FlashInfer/MNNVL decode at N64.
Unknown: These are single-run ports and bounded local validation. They do not establish statistical confidence, official quality, or a global optimum.

Speaking brief: Nine final H200 allocations tested controls and H100-derived alternatives. No distinct candidate cleared the team’s 1% usefulness gate; the existing H200 recipe remains the measured choice.

The nine jobs are one bounded target-hardware verification set, not nine independent innovations or nine candidates with the same denominator.
Fresh incumbent control 27777 scored 3038.022907 good output tokens/s on 16 H200 at N64.
FA3 27779 lost 1.276404%; the H100-derived recipe 27783 lost 10.408319% against that N64 control. Its partner 27781 ran at N54; that point describes the branch at a different load and is not a same-load comparison against the N64 incumbent.
Within the HPC-Ops branch, chunk 6144/8192 recovered some performance versus its 4096 arm, but still lost 7.114431%/4.523207% versus incumbent 27777. The prefill runner and generated seeds differ in the incumbent comparison, so do not claim a pure chunk causal effect from that row.
The explicit mode control 27826 is compared with decode-only 27828 and prefill-only 27830. Gains are +0.006223% and +0.130765%, both below the prospective 1% gate.
All nine runs passed retained local raw/runtime/output gates; smoke checks were 7/8, retrieval 12/12, and official full-set model quality remains UNKNOWN.
Decision: keep H200 DeepGEMM prefill/chunk 8192 and HPC-Ops/FlashInfer/MNNVL decode at N64. These comparisons do not establish a global optimum or official rank.

Research sources: Final transfer, chunk and phase review reports; integrity audit20261101

## Slide 35

We optimize execution of the official OpenFOAM v2512 car-flow case, not its mathematics. The mesh contains 65,334,765 cells. The job completes the prescribed preparation and 150 solver iterations on four nodes. The measured metric is the solver's average wall-clock seconds per time step, beginning with the second solver iteration; lower is better. The retained final drag coefficient is a physical sanity signal, not the performance score.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/FOUNDATIONS.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/equinix-private-ai-dgx/hybrid-ai-infrastructure-m460-d.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/dgx-superpod/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 36

MPI means Message Passing Interface: separate solver processes exchange information about cells at partition boundaries. Mesh decomposition assigns cells to ranks; CPU affinity maps ranks to CPUs. These are different decisions. A complete run includes mesh decomposition, renumbering, potential-flow initialization, boundary-layer setup, and the 150-step simpleFoam solve. Skipping preparation or solver work would not be a valid comparison.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/FOUNDATIONS.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/dgx-superpod/Automotive-Collaboration-6701.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/dgx-superpod/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 37

The NUMA-aware decomposition hypothesis was that grouping work by memory locality might reduce communication and improve speed. Its graph cut fell by 10.63%, but the solver mean worsened from 13.881 to 14.359 seconds per step, a 3.4416% slowdown. The comparison also changed other partition properties, so the cut alone cannot explain the runtime. We closed the unchanged branch. A separate offline mapping reduced a graph cut by 4.5741% but has no measured solver result.

Research sources: /home/apacsc42/workspace/reports/hpc-research-journey-20261023/JOURNEY.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/figures/research-journey.png
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/nvidiaweb/networking/infiniband-switching/nvidia-infiniband-switch-ndr-400gbs-2c50-d-2x.jpeg", "reference_page": "https://www.nvidia.com/en-us/networking/infiniband-switching/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 38

These are separately allocated observations at 128 ranks per node, not an identical-work strong-scaling experiment. Endpoints are 40, 80 and 150 solver steps. Hierarchical led the two-node pair at 7.169996913 seconds per step versus Scotch at 7.462835189. At four nodes, Scotch led at 3.677906731 versus hierarchical at 3.819929017. Different allocations and endpoint lengths limit causal claims.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/RESULTS.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/figures/observed-scaling.png
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/networking/spectrumx/spectrum-x-og-2.jpg", "reference_page": "https://www.nvidia.com/en-us/networking/spectrumx/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 39

The six reviewed four-node logs all complete 150 steps with 149 timed samples. At 64 and 96 ranks per node, hierarchical has the lower observed mean; at 128, Scotch is lower. Requested CPU counts differ across some configurations, and these are separate allocations. We therefore describe measured candidate means, not a causal effect or a universal best method. The lowest mean is 3.677906731 seconds per step for Scotch-128.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/networking/spectrumx/spectrumx-multiplane-ari-1920x1080.jpg", "reference_page": "https://www.nvidia.com/en-us/networking/spectrumx/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 40

Scotch-128 has a median of 3.298742 seconds, p95 of 3.795740 seconds, and maximum of 35.883552 seconds at solver Time 119. All 149 timed samples remain in the arithmetic mean. The review did not collect enough hardware counters to attribute the spike to MPI, CPU scheduling, memory or I/O. The sample-size warning motivates independent repeats; it does not authorize removing the slow point or changing the prescribed endpoint.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/figures/iteration-spikes.png
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/ai-homepage/inference/inferencemax-promo-reference/dgx-press-gb300-1920x1080.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 41

The best reviewed four-node native mean is a candidate observation, not an accepted official score. The independent confirmation job 25940700 was submitted on 23 October at 12:51 UTC. A fresh scheduler query at 15:06 UTC still showed Q/q5 with the comment Not Running: Insufficient amount of resource: node_pool. No result is available. The job is configured to re-run the full preparation and 150-step solve on four exclusive nodes. Its fresh 54-file bundle requires source/mesh identity, explicit stage returns, startup 512-physical-core/four-host proof, and zero-field seals. These are required proofs, not completed checks.

Research sources: /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/scheduler-status.json; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-four-node-confirm-20261023/submission.json
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/technologies/blackwell-architecture/nvidia-gb200-nvl72-1920-1080.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}

## Slide 42

The research has narrowed choices, rejected the unchanged NUMA-aware branch, and identified Scotch-128 as the lowest mean among six reviewed four-node native observations. This is not a proven global optimum or accepted score. At 15:06 UTC on 23 October, job 25940700 was still Q/q5; PBS reported Not Running because node_pool resources were insufficient. No result was available. Next review its complete terminal proof and all iteration tails, then use bounded matched sampling to investigate stability before choosing another configuration.

Research sources: /home/apacsc42/workspace/reports/hpc-research-journey-20261023/JOURNEY.md; /home/apacsc42/workspace/reports/hpc-research-journey-20261023/TALK_TRACK.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/scheduler-status.json; /home/apacsc42/workspace/notes/HPC_CURRENT.md
Background attribution: {"author": "NVIDIA", "credit": "NVIDIA; NVIDIA reference imagery; all rights retained.", "license": "NVIDIA reference imagery; all rights retained.", "source": "https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/h100/hpc-web-gtc23-h100-2560x1440.jpg", "reference_page": "https://www.nvidia.com/en-us/data-center/h100/", "role": "Faint atmospheric backdrop; reference imagery, not the contest cluster."}
