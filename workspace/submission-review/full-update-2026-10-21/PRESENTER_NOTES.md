# Presenter notes — 21 October 2026

## Slide 1: Qwen serving

We present the research journey through 21 October: topology, transport repair, phase-specific kernels, controlled replication and resource observability. The workload is 4000 input and 200 output tokens. H200 and H100 results are separate systems. The new N62 H200 observation is not independently repeated; the N60 interaction is reproduced. Official full-set quality is still unverified.

## Slide 2: Two measured frontiers

Highest H200 individual observation: 24915, N62, 3022.034919 good output tokens/s, 98.7261% joint SLA. It passes complete local protocol/runtime/output checks but still needs an independent N62 repeat. N60 independently repeats at 2990.150791 and 2989.174711. Highest H100 individual is 222048, N54, 2433.019859. These peaks use different hardware, runner and load settings, and must not be plotted as a matched algorithmic comparison. Full organiser quality remains unverified.

Research sources: 24915 full review; 24738/24913; full-protocol historical scan; H100 222048

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

The historical progression spans different loads and configurations, not a single cumulative causal ablation. We recovered the 16-GPU split and request-scoped NIXL transfer, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, increased its chunk to 8192, and found an interaction with HPC-Ops decode. N58 and N60 treatment gains reproduce. New N62 is a single accepted observation and needs its own repeat.

Research sources: Historical retained milestones; 24724/24737/24819; 24738/24913; 24915

## Slide 11: Backend combinations matter

At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.

Research sources: 23777; 23778; 23904; 23974

## Slide 12: The runner interaction extends useful load

Both series use DeepGEMM prefill chunk8192 with the same layout, precision, transport and scoring protocol. Auto controls are 24736/24912/24914. HPC-Ops N58 has three observations; N60 has two; N62 has one. H200 N62 reaches 3022.035, about 4.54% above fresh auto N62 2890.878. We do not infer unrestricted concurrency growth. The N62 treatment still needs an independent repeat; mean summaries and sparse logs do not identify the bottleneck.

Research sources: H200 reviewed N58/N60/N62 points and exact source hashes

## Slide 13: Profile the deployed interaction

Job 24819 repeats the winning N58 deployment, then collects a separate N48 diagnostic: 425 successful requests and 16 sealed nonempty rank traces. Decode named HPC group GEMM accounts for 21.642%, MNNVL allreduce/RMSNorm 23.479% and FlashInfer paged attention 15.064% of summed recorded kernel duration. They are descriptive sums, not a partition of end-to-end wall time or predicted speedups. Old controller parse/stop errors remain recorded; actual trace coverage is checked separately. The new profiler response fix is deployed only in later derived bundles.

Research sources: 24819 sealed traces; H200_PROFILE.md; observability correction

## Slide 14: The N60 gain survives an independent deployment

Fresh auto-decode control 24912 versus HPC-Ops decode repeat 24913, both DeepGEMM prefill chunk8192 at N60. Goodput rises 5.295%, first-token latency rises 125.335 ms and ITL falls 1.644 ms. The original treatment 24738 scored 2990.151; its independent repeat scores 2989.175, only 0.033% lower. This reproduces the interaction rather than establishing a universal HPC-Ops effect. Runtime, raw per-request SLA, short nonregression and 12 long checks pass; full organiser quality remains open.

Research sources: 24912/24913 full reviews; 24738 original treatment

## Slide 15: Tail latency explains the requests we lose

Raw N62 H200 job 24915 has 1884 scored requests: 1860 meet both limits, 24 miss TTFT, none miss request-mean ITL, and none error or cancel. Joint SLA is 98.7261%. Passing average latency does not remove the first-token tail. The score is locally accepted; an independent N62 repeat and official quality remain open. Separately, the H100 FlashInfer/FA3 comparison also loses 22 requests to TTFT in each run, with zero request-mean ITL breaches. These are different runs, not one pooled result.

Research sources: 24915 raw request rows and terminal review; H100 raw failure component inspection

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

## Slide 22: Latency passes; official quality is still open

The new H200 N62 result passes local per-request latency/error, protocol, runtime and diagnostic output checks. Its 98.7261% joint SLA exceeds 90%, but this does not establish the required full-set quality at 99 percent of reference. The small output suite retains seven of eight passes with the known reverse failure and no new regressions; twelve long retrieval cases pass. N60 treatment replication is established; N62 still needs independent repetition. No official leaderboard score or full-set MMLU-Pro/GPQA result is claimed.

Research sources: 24915 complete review; unchanged local output baseline and quality policy

## Slide 23: EAGLE3: prove correctness before measuring speed

The target-only reference 222761 supplies 1600 actual output IDs in four exact repeated prompt pairs. The first native PD candidate 222763 fails before readiness: a shared BF16 target embedding reaches a draft FP16 input RMSNorm. Native one-GPU fixture 222769 reproduces that mismatch and validates explicit BF16 draft normalization, including CUDA graph replay. A separately frozen full PD repair 222780 adds explicit BF16 and draft unquant on both roles; its result is not yet collected because remote access is unavailable. These are integration findings, not a speculative speedup or official quality result. The retained public draft is nebius EAGLE3 at the pinned revision, about 1.146 GB serialized BF16 tensors, no team training. Full output equality and actual PD state/graphs must pass before a matched-load short screen. CPU-envelope tuning delivered only 0.289% against a prospective 1% gate; startup prefetch reverse confirmation saved 9.836% against 10%; neither is promoted.

Research sources: 222761 reference; 222763 failure; 222769 native dtype fixture; 222780 frozen repair; CPU and prefetch pair reviews

## Slide 24: What the campaign has established

We moved from topology and request-scoped KV transfer through combined attention/collectives and phase-specific MoE kernels. The N60 H200 interaction reproduces around 2989 to 2990 good output tokens/s, 5.295 percent above the fresh same-load auto control. The new N62 observation is 3022.035 but has not independently repeated. H100 has its own N54 frontier and rejected decode FA3 tradeoff. The next work collects the BF16 EAGLE3 integration repair, validates output equality before a matched screen and completes quality evaluation; no global optimum or official score is claimed.

## Slide 25: Appendix · H200 metric records

Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.

Research sources: Current full-protocol historical scan; complete reviews for current peak

## Slide 26: Appendix · H100 metric records

Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.

Research sources: Current full-protocol historical scan; complete reviews for current peak

## Slide 27: Appendix · exact settings behind the current results

The H200 N62 single peak and reproduced N60 treatment share the deployment shown here. H100 highest individual and current incumbent use both-phase HPC-Ops at N54, with FlashInfer decode attention. Both keep FA3 prefill attention, TP4/EP1 prefill replicas and TP8/EP8 decode, native FP8 checkpoint and BF16 KV. MNNVL remains automatic strategy with PDL enabled. CUDA graph decode sizes are dense 1 through 64. Hardware, MoE runners, prefill chunk and load differ, so peaks are not a matched platform comparison.

Research sources: 24915/24913 submitted payloads and resolved arguments; H100 incumbent records

## Slide 28: Appendix · topology failures remain separate

In the first 17-job wave, only eight layouts produced measurements and nine failed before a useful benchmark. We corrected the earlier mistake of treating terminal scheduler states as completed measurements. Recovery addressed environment, registration, slow path warmup and FP8 block alignment. The final usable-layout accounting kept 14 compatible originals and three explicitly named EP2 replacements separate from the incompatible TP8/EP1 originals. No failed original receives a replacement result under its name.

Research sources: Historical topology review; recovery records; prior 17-layout presentation

## Slide 29: Appendix · what the benchmark actually measures

The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.

Research sources: Qwen workload and addendum; normalized AIPerf configs

## Slide 30: Appendix · the jobs behind the new decisions

These are decision-linked research IDs, not packaging instructions. Original topology and transport work remain in earlier slides. N58 interaction repeats on 24724/24737/24819. N60 treatment 24738 and 24913 compare with fresh auto control 24912. N62 24915 compares with 24914 and needs an independent treatment repeat. H100 222027/222028 is the scoped attention pair; 222022/222023/222026 are isolated collective screens. Later CPU balancing misses its 1% gate. EAGLE3 native dtype repair passes a layer fixture; the full PD repair is not yet reviewed.

Research sources: Frozen reviewed sources and definite submission receipts

## Slide 31: Appendix · preserve the context of rejected branches

FP8 KV N52 and decode DeepGEMM originally failed the latency gate. Early chunk8192 lost under the older automatic runner but later won with DeepGEMM prefill: the interaction changed, so the old rejection was not universal. One-request prefill batching lost 1.73 percent; original TP8/EP1 failed FP8 geometry before scoring. DeepEP low-latency and DP-attention comparisons did not beat their relevant contemporary controls. Preserve different controls, configurations and failure categories. A single observation does not prove an option always loses.

Research sources: Retained full-protocol historical reports; 24281/24282; later DeepGEMM chunk interaction

## Slide 32: Discussion

Questions may focus on worker balance, request-scoped NIXL transfer, phase-specific kernels, controlled replication, first-token tails, observer overhead and cross-platform comparison. N60 interaction is repeated; the new N62 single observation still requires confirmation. Official full-set accuracy remains unverified. Source-linked notes and native editable diagrams are retained; background photographs are reference infrastructure imagery, not contest-installation photographs.