# Presenter notes — 22 October 2026

## Slide 1: Qwen serving

Research through 22 October: topology, request-scoped KV transfer, phase-specific kernels, full-protocol replication and the next load frontier. Full N64 independently repeats at 3044.489701 and 3044.074628 good output tokens/s. Short N68 improves by 2.273457%, but full confirmation remains pending. H100 remains a separate platform. Official full-set accuracy is unverified.

## Slide 2: Two measured frontiers

H200 full N64 source 25366 scores 3044.489701 good output tokens/s. Independent deployment 25373 scores 3044.074628, a difference of -0.013634%; the mean is 3044.282165. Both have about 98.63% joint SLA and zero request errors. Source N64 improves by 1.082867% over fresh observed N62 control 25365. H100 incumbent 222048 remains 2433.019859 at N54 with different hardware and settings. These peaks are local results, not a matched cross-platform algorithmic comparison or official quality pass.

Research sources: 25366 and 25373 full reviews; fresh 25365 control; retained H100222048

## Slide 3: Optimise useful throughput under a latency gate

Each request must satisfy both time to first token at most 3,000 ms and mean inter-token latency at most 20 ms. At least 90% of evaluated requests must meet both. Errors remain in the denominator. Goodput is qualifying requests per second; multiplying by 200 gives the good output tokens per second reported here. Mean latencies alone do not establish the per-request gate.

Research sources: Qwen task rules and 25 September addendum

## Slide 4: One workload, two deployment systems

Both platforms provide two eight-GPU nodes, but they are not interchangeable experimental environments. Firmus uses H200, Slurm and Enroot; NSCC ASPIRE 2A+ uses H100 80GB, PBS and Singularity. We stage the same serving and client image artifacts and official FP8 checkpoint. CPU, driver, network, launcher, node cache and timing can still differ. A hardware-specification ratio is not a performance conversion.

Research sources: Qwen rules; NSCC asset contract; matched-anchor audit

## Slide 5: Separate prompt processing from token generation

The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.

Research sources: Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents

## Slide 6: Topology search established the serving layout

We explored the balance between replication and parallelism. The original 07 and 09 names were identifiers, not software versions. The 07 configuration used four TP2 prefill workers and two TP4/EP4 decode workers. The next layout widened prefill to TP4. The selected split also widened decode to TP8/EP8. We explored 17 usable arrangements across 8+8, 4+12 and 12+4 GPU splits, retaining incompatible originals and EP2 replacements separately. These initial operating points differ in load and transport history.

Research sources: 22197; 22219; 22415; prior topology campaign

## Slide 7: Make KV-transfer setup scale with the request

Cold disaggregated serving initially stalled while preparing whole-pool KV descriptors. The request-scoped patch constructs descriptors for the pages actually transferred and coalesces contiguous ranges. A representative TP8 source geometry drops from approximately 403.8 million source entries per rank for the pool to 188 coalesced entries for one contiguous 4,000-token request. These numbers are descriptor counts, not a measured speedup factor. The range mapping tests retained head mapping, byte ranges and notifications. Connection warming uses separate traffic before the official client warmup.

Research sources: NIXL patch metadata; 720 + 936 range checks; historical cold-start logs

## Slide 8: FP8 block geometry constrains parallelism

A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The TP8/EP2 replacement is a combined layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.

Research sources: Exact staged SGLang source; failed job 24282; corrected trial 24321

## Slide 9: A repeatable experiment loop

We combine source research with observed runtime, output checks, failures and cost before choosing a trial. Each useful hypothesis gets a control and a stopping rule. Exploratory short sweeps screen configurations; records in this talk use full 60/120/30 confirmations. We retain raw exports, per-request data, submitted payloads, logs and terminal artifacts. Candidate gains require runtime activation checks and independent replication. An exited job without a valid export is not a successful experiment. Loading time is also a resource cost: H100 is billed at 128 SU per GPU-hour, making a 16-GPU, 45-minute cap 1,536 SU. Three submitted jobs reserve 4,608 SU and run sequentially; prefetch targets startup cost rather than assumed throughput gains.

Research sources: Research plans; payload hashes; sealed reviews

## Slide 10: H200 journey: recover, specialise, then reproduce

This historical progression spans different loads, observation settings and configurations, not a cumulative causal ablation. The campaign recovered disaggregated serving, made NIXL setup request-scoped, combined FlashInfer and MNNVL, then found a DeepGEMM prefill / HPC-Ops decode interaction. N58 and N60 gains repeat. N62 repeats at 3022.034919 / 3023.072304; full observed N64 repeats at 3044.489701 / 3044.074628. The final bar uses the N64 mean, not a new single-run score.

Research sources: Historical retained milestones; 24724/24737/24819; 24738/24913; 24915

## Slide 11: Backend combinations matter

At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.

Research sources: 23777; 23778; 23904; 23974

## Slide 12: The next load step survives a full repeat

Fresh equally observed full N62 control 25365 versus full N64 source 25366 improves by 1.082867%. Independent full N64 deployment 25373 differs from the source by -0.013634%; the two-run mean is 3044.282165 good output tokens/s. Both full N64 runs pass runtime, protocol, zero-error SLA, short output non-regression and long retrieval checks. Same sampled GPU UUID sets limit hardware diversity. Two measurements do not establish a confidence interval or global optimum.

Research sources: 25365/25366 matched full proof; 25373 replication and telemetry

## Slide 13: Profile the deployed interaction

Job 24819 repeats the winning N58 deployment, then collects a separate N48 diagnostic: 425 successful requests and 16 sealed nonempty rank traces. Decode named HPC group GEMM accounts for 21.642%, MNNVL allreduce/RMSNorm 23.479% and FlashInfer paged attention 15.064% of summed recorded kernel duration. They are descriptive sums, not a partition of end-to-end wall time or predicted speedups. Old controller parse/stop errors remain recorded; actual trace coverage is checked separately. The new profiler response fix is deployed only in later derived bundles.

Research sources: 24819 sealed traces; H200_PROFILE.md; observability correction

## Slide 14: The N60 gain survives an independent deployment

Fresh auto-decode control 24912 versus HPC-Ops decode repeat 24913, both DeepGEMM prefill chunk8192 at N60. Goodput rises 5.295%, first-token latency rises 125.335 ms and ITL falls 1.644 ms. The original treatment 24738 scored 2990.151; its independent repeat scores 2989.175, only 0.033% lower. This reproduces the interaction rather than establishing a universal HPC-Ops effect. Runtime, raw per-request SLA, short nonregression and 12 long checks pass; full organiser quality remains open.

Research sources: 24912/24913 full reviews; 24738 original treatment

## Slide 15: The remaining losses are first-token tails

Independent full N64 job 25373 has 1901 scored requests: 1875 joint-good, 26 TTFT breaches, zero mean-ITL breaches and zero request errors/cancellations. TTFT mean/p95 is 1113.240 / 1309.781 ms; request-mean ITL mean/p95 is 14.993 / 15.160 ms. All 26 failures start within 30.864687 ms of profiling beginning. This localizes the first cohort, not the causal bottleneck. Every request stays in the official denominator.

Research sources: 25373 sealed raw request export; full review

## Slide 16: H100 must find its own kernel and load combination

Earlier MNNVL paired repeats improved N32/N34 by 7.52/8.24 percent and combining MNNVL with attention extended useful capacity. The later both-phase HPC-Ops incumbent at N54 reaches 2433.020 as the highest individual observation. Fresh controls remain around 2421 to 2431, not an official rank or confidence interval. H100 uses prefill chunk4096, unlike H200 DeepGEMM chunk8192. Hardware, runner, load and configuration interactions must be measured independently.

Research sources: Historical paired MNNVL reviews; 222048 retained full-protocol export; 222027 fresh control

## Slide 17: FA3: faster first token does not guarantee goodput

Only decode attention changes in the H100 N54 pair. FlashInfer control 222027 versus FA3 222028 both pass the local protocol/runtime/output gates, and FA3 execution is verified on eight decode ranks. Mean TTFT falls 118.922 ms, while mean ITL rises 0.773 ms. Across roughly 199 token intervals that adds about 154 ms, outweighing the first-token gain. Measured mean end-to-end latency rises from 4337.853 to 4372.813 ms; goodput falls 0.812%. This is one matched pair, not a universal FA3 ranking or precise kernel-level explanation. Prefill continues using FA3.

Research sources: 222027/222028 full reviews and extended inspections; scoped interpretation

## Slide 18: Compare matched systems, not unrelated peaks

Comparing H100 N50 with H200 N56 changes both the platform and the workload. For a calibrated comparison we hold the combo configuration and N52 load fixed. Selected runtime fields, the model, checkpoint precision, BF16 KV, worker placement, CUDA graphs, backends and client protocol match. The audited differences include engine random seeds; unobserved or unbalanced hardware and runtime conditions remain. We report a system association, not a causal GPU-only multiplier.

Research sources: Matched-anchor audit and cross-platform report

## Slide 19: A local N52 calibration, not a universal multiplier

The matched combo N52 anchor uses two H100 allocations and four H200 allocations. Their means are 2,215.460 and 2,632.181 good tokens/s, producing an empirical system ratio of 1.188096805. This is one calibration load for one configuration. Repeat measurements at one load do not identify a cross-platform function or a prediction interval. We do not apply this factor to TTFT, ITL, SLA or other backend branches.

Research sources: H100 221052/221058; H200 23904/23973/23975/24174

## Slide 20: Freeze the forecast, then test it on H200

Before the held-out H200 N50 result was available, we froze a prediction of 2,642.244 good tokens/s from the H100 N50 mean and the N52 ratio. We predeclared a 2% operational tolerance. Job 24272 measured 2,601.629, an error of minus 1.5371%, so this one local check is within tolerance. However, the result lies outside the earlier input-only sensitivity range, which omitted model error. We retain that negative finding, do not refit the frozen factor, and do not claim broad predictive validity.

Research sources: Frozen prediction and hashes; held-out 24272 review; cross-platform report

## Slide 21: Negative results narrow the next hypothesis

The grad-mode trials were flat, so we do not combine unproved gains. Forced NCCL Simple showed only a single +0.23% observation and no established useful gain. Its activation is proved by sealed TUNING decisions, not kernel-name guesses; representative LL symbols do not identify actual protocol. Isolated H100 collective microbenchmarks reject forced one-shot and disabling PDL. Their percentages describe microseconds per collective at 54 tokens, not full-serving goodput. H100 decode FA3 loses 0.81% goodput in one pair and stays closed at this setting.

Research sources: Phase-specific inference review; NCCL correction; graph32 one-shot and PDL screens; H100 attention pair

## Slide 22: Reproducible latency is not a quality certificate

Both full N64 deployments pass local protocol, runtime, zero-error SLA and output non-regression. Repeat joint SLA is 98.632299%. The short diagnostic retains seven of eight passes with the known reverse failure; long retrieval passes 12/12. These do not establish official accuracy at least 99% of the organisers own unchanged FP8 reference score. The official checks include but are not limited to model-card benchmarks and AIPerf checks. No official ranking or accuracy pass is claimed.

Research sources: 25366/25373 full reviews; Qwen addendumQ1

## Slide 23: EAGLE3: small components pass, full serving is open

H100 reference 222761 supplies 1600 actual output IDs. Explicit BF16/unquant fixes the reproduced draft norm mismatch; uniform eager prefill addresses rank-divergent graph capture. Full 223055 reaches requests but fails an earlier NIXL remote disconnect. Its old warm marker masked child failure; the final token gate correctly rejects HTTP 500 and zero outputs. Later two-GPU probes 223091, 223097 and 223132 pass small base transfers, actual descriptors, native 190-range registration and DRAM auxiliary writes on different hosts. They do not prove full-pool EAGLE3 correctness. Next prepare a fresh H200 reference and a separately gated candidate with semantic pair receipts. The public nebius draft uses the pinned revision, about 1.146 GB serialized BF16 tensors, with no team training. No speculative speedup is claimed.

Research sources: 222761;223055;223091;223097;223132 sealed reviews; semantic warmup gate

## Slide 24: What the campaign has established

Topology recovery and request-scoped KV transfer enabled serving. Phase-specific kernels and controlled load selection extended throughput. Full N64 now repeats at 3044.489701 and 3044.074628 good output tokens/s, with mean 3044.282165. Short N68 improves by 2.273457% and awaits fresh full confirmation. H100 remains independently measured. No global optimum, official quality pass or speculative speedup is claimed.

## Slide 25: Appendix · H200 metric records

Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.

Research sources: Current full-protocol historical scan; complete reviews for current peak

## Slide 26: Appendix · H100 metric records

Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.

Research sources: Current full-protocol historical scan; complete reviews for current peak

## Slide 27: Appendix · exact settings behind the current results

The reproduced H200 N64 point uses two TP4/EP1 DeepGEMM prefills with chunk size 8192 and one TP8/EP8 HPC-Ops decode. H100 uses both-phase HPC-Ops and chunk size 4096 at N54. Both retain FA3 prefill attention, FlashInfer decode attention, MNNVL, dense decode graph sizes 1 through 64, native FP8 weights and BF16 KV. Different hardware, runner and load settings prevent interpreting the peaks as a matched platform comparison.

Research sources: 24915/24913 submitted payloads and resolved arguments; H100 incumbent records

## Slide 28: Appendix · the first cohort contains the TTFT misses

Full N62 control 25365 has 24 failures, all starting by 35.444853 ms after profiling begins. Full N64 source 25366 has 26 by 33.481316 ms; repeat 25373 has 26 by 30.864687 ms. No later TTFT failures or ITL failures occur in these inspected points. This is an association, not proof of a prefill, transport or decode cause. Recovering every failure at unchanged total count and duration would add about 1.2-1.4%, not a promised speedup. Keep every request, the fixed arrival protocol and official warmup.

Research sources: Sealed per-request timestamps in 25365/25366/25373

## Slide 29: Appendix · what the benchmark actually measures

The synthetic serving workload is separate from full-set accuracy evaluation. The client sustains a declared concurrency and streams through the gateway. Every prefill/decode path is warmed with separate traffic before the unchanged official client warmup. The scored window uses AIPerf accounting; grace settles outstanding requests rather than adding another steady-state window. Do not recompute goodput by blindly dividing the completed request count by 120. Accuracy compares benchmark scores with the organisers FP8 reference; no fixed exhaustive public task list is assumed here.

Research sources: Qwen workload and addendum; normalized AIPerf configs

## Slide 30: Appendix · N68 wins the screen, not a full score

Short same-deployment job 25371 measures N64 then N68 with 20/40/30 timing. Both local gates pass and good throughput improves by 2.273457%, while TTFT/ITL rise and joint SLA falls slightly. This fixed-order short evidence is unranked. Actual scored decode running-request maxima 54 / 58 stay below unchanged graph cap 64. Fresh full N64 control 25487 and N68 candidate 25488 are submitted, with no result yet. Require full local gates and at least 1% matched gain before N68 replication.

Research sources: 25371 strict short review and raw timing;25487/25488 receipts

## Slide 31: Appendix · losses guide the next hypothesis

Full N60 both-HPC job 24965 loses 3.1904% versus fresh control 24964; power-of-two router 25283 loses 3.8067%; locality capture 25051 is only +0.1375%, not a useful gain. Retain these valid results and close unchanged repeats. P12/D4 is withheld before GPU submission: equal TP4-to-TP4 NIXL enumerates whole KV pools, while actual candidate setup geometry, memory, time and reviewer support remain unbounded. This is a source-level risk, not a measured loss. Historical CPU and prefetch trials remain below their prospective practical gates.

Research sources: H200 wave review; current P12/D4 source assessment; earlier scoped negatives

## Slide 32: Discussion

Discuss worker balance, request-scoped KV transfer, phase-specific kernels, replication, first-token tails, observer limits and matched platform comparison. N64 independently repeats within 0.014%; short N68 awaits full confirmation. EAGLE3 needs a passing full-model correctness result, and official full-set accuracy remains unverified. Backgrounds are reference infrastructure photographs, not photographs of the contest installation.
