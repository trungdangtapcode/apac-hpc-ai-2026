# TripleU presenter notes — 30 October 2026

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

Reasoning role: Engineering decision · compare feasible layouts. Explain the engineering tradeoff that led to the retained split. The same sixteen GPUs can be spent on more replicas or wider parallelism, and prefill/decode have different needs. Historical topology scores show feasibility and progression, not a matched causal ranking.

Problem: Allocate sixteen H200 GPUs across prefill and decode, balancing the number of worker replicas against the GPUs assigned to each worker.
Why It Matters: Too few replicas can limit prompt-side admission, while overly narrow workers may not process their share efficiently; decode also has different parallelism needs.
Why This Test: Explore feasible topology branches and record their concurrency and goodput, while retaining failures and replacement configurations as distinct evidence.
What We Learned: Seventeen reviewed usable configurations were recovered, including EP2 replacements; selected examples rose from 1,297 at N32 to 1,912 at N48, but these are different loads.
Next Logic: The next slide presents the retained architecture as an engineering decision under this tradeoff, not as the causal winner of a matched topology sweep.

Use branches for feasible ways to allocate the fixed sixteen GPUs: several narrower prefill replicas and multiple decode groups, then fewer wider prefill workers and a wider decode group. Label the historical usable observations N32/1,297.02, N40/1,666.01, and N48/1,912.30 good tokens/s. Mark N explicitly as client requests in flight. Connect the branches as candidates, not a chronological line or causal ranking, because concurrency and other trial conditions differed.

Observation: The fixed GPU budget forced a choice between replication and parallel width. Reviewed usable examples include N32 at 1297.02, N40 at 1666.01, and N48 at 1912.30 good tokens/s; fourteen original layouts plus three EP2 replacements were counted.
Hypothesis: A layout with enough prefill replicas and a wider decode worker could balance prompt processing and generation at the intended load.
Conclusion: Topology recovery established feasible candidates and informed a later selected split. The displayed score progression is not a causal ranking because concurrency and historical conditions differed.
Unknown: The selected architecture's advantage over every alternative under one matched load is not established by these points; the count does not include a common statistical comparison.

Speaking brief: More prefill replicas improve request concurrency, while wider parallel groups give each model worker more GPUs. The historical usable points were 1,297 at N32, 1,666 at N40, and 1,912 good tokens/s at N48, but load changed too.

Four TP2 prefill replicas plus two TP4/EP4 decode groups use the GPUs differently from two TP4 prefill workers plus one TP8/EP8 decode worker.
The historical observations shown are 1,297.02 at N32, 1,666.01 at N40, and 1,912.30 at N48 good tokens/s.
N changes across these points, so higher score cannot be attributed to topology alone.
The count of seventeen usable configurations summarizes reviewed evidence, not a controlled sweep with a common load.

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

Reasoning role: Technical contribution · intervention and checks. Explain why descriptor preparation was prioritized, what the team changed, and what correctness tests actually showed. This is the direct implementation contribution: build transfer descriptions for the request's KV pages rather than enumerate the full pool, while retaining mapping behavior.

Problem: Full-pool descriptor enumeration appeared in the cold heterogeneous-TP path after pair warmup had failed.
Why It Matters: Preparing metadata for pages the request will not transfer could add setup work before the service can handle its first request.
Why This Test: Change descriptor construction to the request's pages, preserve KV range mapping, and compare original and patched address geometry across CPU cases.
What We Learned: The patch reduces the illustrated descriptor count from about 403.8 million per rank for the pool to 188 for the request, and 720 tested CPU range cases pass. These counts do not measure elapsed time.
Next Logic: A real patched deployment is needed to establish feasibility; a matched unpatched deployment and setup timing would still be needed to claim patch-only speedup.

Show the old full-pool scope beside the patched request scope: about 403.8 million source entries per rank for the representative pool geometry versus 188 coalesced descriptors for one contiguous 4,000-token request. Then separate a CPU range-equivalence gate from a real GPU transport gate marked not validated in the fixture. Do not depict the count ratio as a time or speedup ratio.

Observation: Representative source geometry gives about 403.8 million whole-pool source descriptors per rank; a contiguous 4,000-token request uses 188 coalesced descriptors. CPU equivalence checks pass 720 cases.
Hypothesis: Removing descriptors for KV pages unrelated to the active request should reduce setup work while preserving the exact bytes and mapping needed for transfer.
Conclusion: The source patch and CPU geometry tests support request-scoped range construction and tested address equivalence. They establish a plausible setup target and implementation correctness for tested cases, not measured end-to-end acceleration.
Unknown: No old-versus-new descriptor initialization time was measured. The geometry fixture did not validate actual GPU transport, and it does not prove descriptor work was the dominant cause of the timeout.

Speaking brief: We replaced whole-pool descriptor setup with request-scoped ranges. The representative counts are 403.8 million entries per rank versus 188 per request, with different scopes. CPU range equivalence passed 720 cases; actual GPU serving is checked separately.

The symptom preceded scoring, and source inspection found whole-pool descriptor enumeration in the heterogeneous-TP path.
The patch creates source and destination descriptors only for the current request and coalesces contiguous ranges; equal-TP paths, weights, precision, head mapping, and notifications were retained.
The 403.8 million and 188 values count descriptors at different scopes. They are not bytes, seconds, bandwidth, or a measured speedup.
The CPU fixture passes 720 byte-range equivalence cases but sets real GPU transport validation to false.

Research sources: nixl-ondemand/README.md;nixl-ondemand.patch;metadata.json;geometry-test.json

## Slide 7

Reasoning role: Technical contribution · end-to-end evidence boundary. Report the end-to-end result of the patched recovery branch and define its evidence boundary. The path became usable and completed a full local N32 benchmark, but this does not measure the descriptor patch's independent contribution because there is no successful matched unpatched control.

Problem: Determine whether the source change was followed by a usable service path, not just a passing CPU fixture.
Why It Matters: Only a real end-to-end request and benchmark can show the patched recovery topology became usable; CPU address checks alone cannot do that.
Why This Test: Use the actual patched H200 deployment, observe pair warmup, then run a full N32 local confirmation with request-level SLA and error accounting.
What We Learned: Job 22294 warmed both P/D paths in 0.68–0.70 seconds per request after readiness and completed N32 at 1422.96 good tokens/s, 95.87% joint SLA, and zero errors/cancellations. It demonstrates feasibility in that run.
Next Logic: Close the claim at feasibility. A patch-only speedup would require a successful matched no-patch run plus isolated setup and latency evidence; the available records do not provide these.

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
Why This Test: A separate N48 diagnostic recorded kernel categories; request-level N64 measurements separately identified TTFT failures.
What We Learned: The profile gives candidate components, while the N64 data says only that 27 of 1,902 requests missed TTFT and none missed ITL.
Next Logic: Use the profile to motivate a controlled service experiment, and treat the N64 tail as a separate unresolved question.

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

Reasoning role: Experimental method · hypothesis and control. Show how a controlled comparison turns a backend idea into a service-level hypothesis, while making clear which factors were held fixed and which result is a repeat.

Problem: A backend change is only useful if a measured service objective improves under comparable workload conditions.
Why It Matters: Without a control and fixed prefill/load settings, observed score changes could come from other configuration differences.
Why This Test: Run a fresh full N60 automatic-decode control against an HPC-Ops decode treatment, retaining DeepGEMM prefill, chunk 8,192, and the 60/120/30 protocol; repeat the treatment independently.
What We Learned: The design provides a matched service comparison and a separate repeat, with decoder implementation as the intended factor.
Next Logic: Read the metric tradeoff and repeat result before deciding whether this setting is supported.

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

Reasoning role: Robustness · selection and unresolved drift. Separate robustness from peak selection: repeated measurements support N64, but distinct runtime series and unexplained drift prevent a single pooled trend or causal story.

Problem: Selecting the maximum observation risks choosing noise or a setting that does not reproduce.
Why It Matters: A deployment choice should survive repeated full runs, and distinct protocols/runtime paths should not be pooled as if they were identical experiments.
Why This Test: Compare the historical three-run N64 series, separate native full run, matched cache control/treatment, and a valid lower legacy replay.
What We Learned: N64 reproduces near 3,044–3,046 in two separately labeled series; cache gain is only 0.240921%, below adoption threshold; lower replay remains unexplained.
Next Logic: Choose based on replicated evidence and state the remaining accuracy and deployment validations explicitly.

The two panels contrast the strength of repeated evidence with a single higher measurement; they are not a matched treatment/control pair. The historical series is a three-run N64 mean. Native full run 26766 is a separate later series at nearly the same score. Cache pair 27376/27378 compares a fresh control with one treatment: 3,041.119598 versus 3,048.446289, +0.240921%, below the useful-gain criterion and with worse p95 TTFT. A valid legacy full replay 26313 scored 2,830.923547. The lower replay is retained; completed graph/admission controls did not identify one cause for drift. Keep the series labeled rather than joining them into a misleading line.

Observation: Replicated historical and separate native N64 results are near 3,044–3,046; an isolated cache peak is slightly higher; a valid legacy replay is lower.
Hypothesis: N64 is a reproducible operating point, while cache or runtime differences may account for some score variation.
Conclusion: Support N64 from repeated evidence; do not replace it with the isolated cache score or attribute the drift to one cause.
Unknown: The relationship among runtime path, graph policy, request cap, harness, and the lower valid replay remains unresolved.

Speaking brief: Three full N64 runs average about 3,044 qualifying output tokens per second. A single cache result is higher but gains only 0.24% over its own control. Repetition supports our choice more strongly; lower valid replays remain unexplained.

Historical N64 three-run mean: 3,044.400475 good output tokens/s. Later native full run 26766: 3,045.501509; keep it as a separate series.
Fresh control 27376 scored 3,041.119598. Cache treatment 27378 scored 3,048.446289, +0.240921%; its p95 TTFT worsened, so it was not adopted as a useful improvement.
Legacy full replay 26313 scored 2,830.923547 and remains valid. No completed control isolated a single cause of the difference from the later native series.

Research sources: N64repeats;26766;27376/27378;26313

## Slide 14

Reasoning role: Robustness · cross-platform limits. Assess whether a platform-specific calibration transfers to a nearby held-out operating point, while keeping an operational tolerance distinct from statistical uncertainty.

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

Reasoning role: Conclusion · claim boundaries and OpenFOAM handoff. Close the main AI argument at the level the evidence supports, state two unresolved validation tasks, and hand off cleanly to the unchanged OpenFOAM section without implying more AI work was run.

Problem: A strong serving score can be mistaken for verified answer quality or successful portable deployment.
Why It Matters: Competition quality and end-to-end artifact reliability are independent acceptance dimensions; local metrics cannot substitute for either.
Why This Test: Retain local output-check counts, official-quality status, original scheduler outcomes, and the narrow CPU reader-verification result as separate evidence.
What We Learned: Serving performance at H200 N64 is supported; official accuracy is UNKNOWN; original portable GPU jobs failed in post-processing; the reader-only repair passed on CPU data.
Next Logic: The AI main section ends here. The two validation tasks are open proposals, AI backup slides stay hidden, and the unchanged OpenFOAM slide 33 follows.

The two open cards are independent. First, local output checks were 7/8 on smoke tests and 12/12 on retrieval checks; neither is the organizer's full-set quality evaluation, which requires at least 99% of reference and remains UNKNOWN. Second, portable GPU jobs 27136 and 27145 completed the serving client but ended terminal FAILED in result-reader path handling. CPU-only job 27152 passed the repaired readers against both saved datasets; it did not rerun GPU serving. Thus, raw score recovery cannot convert the original jobs into successful end-to-end deployments. The next visible slide is unchanged OpenFOAM slide 33; AI backup slides 17–32 remain hidden during the main presentation.

Observation: N64 serving performance is supported by repeated evidence; official quality and complete portable deployment after reader repair remain unverified.
Hypothesis: Independent full-set quality evaluation and a complete post-repair portable GPU replay would close separate validation gaps.
Conclusion: Bound the claim to measured H200 serving, keep accuracy UNKNOWN, preserve failed job status, and hand off to the unchanged OpenFOAM slide 33.
Unknown: Whether official accuracy reaches 99% and whether the packaged portable deployment completes end to end after reader repair remain unknown. No new jobs are implied or scheduled by this summary.

Speaking brief: Repeated measurements support our H200 service operating point. Official model quality and a complete packaged GPU replay after the reader repair remain unverified. Those are the limits of the claim. We now hand over to the independent OpenFOAM presenter.

The selected H200 N64 configuration has repeated full-run evidence near 3,044 good output tokens/s. This supports a serving-performance claim at the tested setting, not official answer quality.
Smoke checks passed 7/8 and retrieval checks 12/12. The official full-set requirement of at least 99% of reference is still UNKNOWN.
Portable jobs 27136/27145 remain FAILED due to reader failures after the client; CPU job 27152 verified corrected readers on retained data only. No post-fix full GPU replay is claimed.
The next-step labels are unperformed validation tasks. No official acceptance, human mock outcome or new GPU job is claimed by this report.

Research sources: 26766;27136/27145/27152;officialqualityrules

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

Reasoning role: Backup · Exact deployment settings. Provide exact deployment context so earlier results can be interpreted without mixing platform settings or treating configuration labels as performance evidence.



Read columns within each platform, not across H200 and H100 as if they were a matched benchmark. Both use target-model FP8 weights, BF16 activations and KV state, TP8/EP8 decode, FlashInfer decode attention, MNNVL collectives, and round-robin routing to two prefill workers. The H200 choice is N64 with DeepGEMM prefill, chunk 8,192, and dense decode graph buckets 1–64. H100 is N54 with HPC-Ops prefill and chunk 4,096. The table defines the operating points; it does not claim equal capacity or rank hardware performance.

Observation: The retained configurations share some decode and precision settings but differ in hardware, concurrency, prefill backend, and chunk size.
Hypothesis: Explicit platform-specific settings make the replicated operating points reproducible and interpretable.
Conclusion: Use the H200 N64 settings for the selected primary and report H100 N54 independently.
Unknown: This table does not establish that the settings are optimal or that performance transfers between platforms.

Speaking brief: The retained H200 setup uses N64, two TP4 DeepGEMM prefill workers with chunk 8,192, and TP8/EP8 HPC-Ops decode. H100 is separate: N54, HPC-Ops prefill with chunk 4,096, and its own measured settings.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
H200: client concurrency 64; two TP4/EP1 prefill workers; DeepGEMM; chunk 8,192; one HPC-Ops TP8/EP8 decode worker.
H100: client concurrency 54; two TP4/EP1 HPC-Ops prefill workers; chunk 4,096; TP8/EP8 HPC-Ops decode. Keep H100 point separate from H200 scores.
Both use the listed weight/activation/KV precision and shared decode attention, collective, routing, and request-quality rules. Official full-set accuracy is not certified by this configuration table.

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

Reasoning role: RQ4 · Real replay & failure analysis. Distinguish successful GPU inference from successful end-to-end packaging. Two real portable allocations completed serving but failed while readers located and interpreted result files; a later CPU-only replay verified the reader repair, not a repaired full allocation.



Trace the pipeline in order: real portable jobs 27136 and 27145 ran the official GPU client and both semantic P/D routes, then failed in result processing. First repair handled exports nested in an immediate child directory; second canonicalized the input root where /scratch/home and /home paths referred to the same files. Actual zero-GPU compute job 27152 passed both repaired readers on both real datasets. Keep original scheduler states FAILED.

Observation: Two real GPU jobs completed inference and client work but failed in result reading; CPU-only job 27152 verified both reader fixes on real outputs.
Hypothesis: The deployment's remaining failure was caused by file-layout and path-alias assumptions in post-processing, rather than serving execution.
Conclusion: The precise reader defects were repaired and verified against actual datasets; the full post-repair deployment remains unverified.
Unknown: Whether a complete new allocation would pass launch, inference, export, reading, and all gates after the fixes is unknown.

Speaking brief: Two real H200 portable jobs completed serving but failed during result reading. A zero-GPU job verified reader fixes on real exports. This does not establish a successful full deployment after repair; the original jobs remain failed.

This is supporting evidence for Q&A, hidden during the main slide show. It does not add a new experiment to the main argument.
Real H200 portable jobs 27136 and 27145 completed both serving routes and the official client, but the scheduler jobs failed during post-processing. In 27136, AIPerf 0.12 placed exports in an immediate child directory; the first fix handled that layout. In 27145, lexical /home and canonical /scratch/home paths caused an alias mismatch; canonicalizing the root fixed the second issue.
Zero-GPU job 27152 then ran the corrected readers on both real datasets and passed. Raw 27145 score 3,055.330517 is recoverable evidence from the failed original job, not a successful whole-allocation rerun after repair. No post-repair full GPU deployment is claimed.

Research sources: 27136 nested export failure;27145 canonical alias failure;27152 actual compute reader verification

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
