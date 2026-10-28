# TripleU presenter notes — 28 October 2026

AI slides updated; original HPC notes retained unchanged.

## Slide 1

Research through 28 October 2026: topology recovery, request-scoped KV transfer, phase-specific kernels, full-protocol replication, negative trials and deployment reliability. Historical N64 three-run mean is 3044.400475 good output tokens/s, with separate new-runtime full 26766 at 3045.501509. Full N68 gains only 0.083056% in its matched pair and is not promoted. H100 stays separate. Official full-set accuracy remains unverified.

## Slide 2

The selected H200 N64 point has three historical full runs with mean 3044.400475; a new native-runtime full observation 26766 passes at 3045.501509 and98.580442% joint SLA. Do not pool these launcher regimes or claim a causal runtime improvement. H100 highest retained individual222048 is2433.019859 atN54; fresh full 225227 gives2399.186728. These are separate platform/configuration series, not a matched algorithmic comparison or official accuracy pass. N68 full gain0.083056% does not clear our useful-gain gate.

Research sources: 25366/25373/25487 full reviews;26766 independent raw review;222048 retained export;225227 fresh full review

## Slide 3

Each request must satisfy both time to first token at most 3,000 ms and mean inter-token latency at most 20 ms. At least 90% of evaluated requests must meet both. Errors remain in the denominator. Goodput is qualifying requests per second; multiplying by 200 gives the good output tokens per second reported here. Mean latencies alone do not establish the per-request gate.

Research sources: Qwen task rules and 25 September addendum

## Slide 4

Both platforms provide two eight-GPU nodes, but they are not interchangeable experimental environments. Firmus uses H200, Slurm and Enroot; NSCC ASPIRE 2A+ uses H100 80 GB, PBS and Singularity. We stage the same serving and client image artifacts and official FP8 checkpoint. CPU, driver, network, launcher, node cache and timing can still differ. A hardware-specification ratio is not a performance conversion.

Research sources: Qwen rules; NSCC asset contract; matched-anchor audit

## Slide 5

The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.

Research sources: Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents

## Slide 6

We explored the balance between replication and parallelism. The original 07 and 09 names were identifiers, not software versions. The 07 configuration used four TP2 prefill workers and two TP4/EP4 decode workers. The next layout widened prefill to TP4. The selected split also widened decode to TP8/EP8. We explored 17 usable arrangements across 8+8, 4+12 and 12+4 GPU splits, retaining incompatible originals and EP2 replacements separately. These initial operating points differ in load and transport history.

Research sources: 22197; 22219; 22415; prior topology campaign

## Slide 7

Cold disaggregated serving initially stalled while preparing whole-pool KV descriptors. The request-scoped patch constructs descriptors for the pages actually transferred and coalesces contiguous ranges. A representative TP8 source geometry drops from approximately 403.8 million source entries per rank for the pool to 188 coalesced entries for one contiguous 4,000-token request. These numbers are descriptor counts, not a measured speedup factor. The range mapping tests retained head mapping, byte ranges and notifications. Connection warming uses separate traffic before the official client warmup.

Research sources: NIXL patch metadata; 720 + 936 range checks; historical cold-start logs

## Slide 8

A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The TP8/EP2 replacement is a combined layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.

Research sources: Exact staged SGLang source; failed job 24282; corrected trial 24321

## Slide 9

We combine source research with observed runtime, output checks, failures and cost before choosing a trial. Each useful hypothesis gets a control and a stopping rule. Exploratory short sweeps screen configurations; records in this talk use full 60/120/30 confirmations. We retain raw exports, per-request data, submitted payloads, logs and terminal artifacts. Candidate gains require runtime activation checks and independent replication. An exited job without a valid export is not a successful experiment. Loading time is also a resource cost: H100 is billed at 128 SU per GPU-hour, making a 16-GPU, 45-minute cap 1,536 SU. Three submitted jobs reserve 4,608 SU and run sequentially; prefetch targets startup cost rather than assumed throughput gains.

Research sources: Research plans; payload hashes; sealed reviews

## Slide 10

The historical progression spans different loads and configurations, not a single cumulative causal ablation. We recovered the 16-GPU split and request-scoped NIXL transfer, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, increased its chunk to 8192, and found an interaction with HPC-Ops decode. N58 and N60 treatment gains reproduce. N62 repeats at 3022.034919/3023.072304; N64 repeats at 3044.489701/3044.074628. Observation settings also differ across this historical journey; it is not one cumulative causal ablation.

Research sources: Historical retained milestones; 24724/24737/24819; 24738/24913; 24915

## Slide 11

At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.

Research sources: 23777; 23778; 23904; 23974

## Slide 12

Fresh equally observed full N62 control 25365 versus full N64 candidate 25366 improves1.082867%. Independent N64 deployment 25373 differs from the source by−0.013634%; the two-run mean is3044.282165. Same serving topology, precision, transport and observation; source operational bytes differ only in load/provenance. Same sampled GPU UUID sets limit hardware diversity. Two runs do not establish a confidence interval or a global optimum.

Research sources: 25365/25366 matched full proof; 25373 replication and telemetry

## Slide 13

Job 24819 repeats the winning N58 deployment, then collects a separate N48 diagnostic: 425 successful requests and 16 sealed nonempty rank traces. Decode named HPC group GEMM accounts for 21.642%, MNNVL allreduce/RMSNorm 23.479% and FlashInfer paged attention 15.064% of summed recorded kernel duration. They are descriptive sums, not a partition of end-to-end wall time or predicted speedups. Old controller parse/stop errors remain recorded; actual trace coverage is checked separately. The new profiler response fix is deployed only in later derived bundles.

Research sources: 24819 sealed traces; H200_PROFILE.md; observability correction

## Slide 14

Fresh auto-decode control 24912 versus HPC-Ops decode repeat 24913, both DeepGEMM prefill chunk8192 at N60. Goodput rises 5.295%, first-token latency rises 125.335 ms and ITL falls 1.644 ms. The original treatment 24738 scored 2990.151; its independent repeat scores 2989.175, only 0.033% lower. This reproduces the interaction rather than establishing a universal HPC-Ops effect. Runtime, raw per-request SLA, short nonregression and 12 long checks pass; full organiser quality remains open.

Research sources: 24912/24913 full reviews; 24738 original treatment

## Slide 15

Full new-runtime job 26766 passes the independently replayed protocol and local output gates at 3045.501509 good output tokens/s. Exactly 1875 of 1902 profiling requests satisfy both limits: 27 fail TTFT, none fail request-mean ITL, and errors/cancellations are zero. TTFT mean/p95 is 1108.869/1311.693 ms; ITL mean/p95 is 15.0075/15.1930 ms. All 27 failures start within 13.004085 ms of profiling admission. This is an initial-cohort association, not a proven causal bottleneck. Every failed request stays in the denominator.

Research sources: 26766 raw profile, independent full review and sealed native-runtime payload

## Slide 16

H100 retained highest individual 222048 is 2433.019859 good output tokens/s. A fresh full N54 control 225227 passes local gates at 2399.186728 and 98.015873% joint SLA, with zero request errors/cancellations. H100 uses both-phase HPC-Ops and chunk 4096, whereas H200 uses DeepGEMM prefill and chunk 8192. The fresh control is lower and must remain visible. These peaks are neither matched hardware tests nor a performance multiplier. Equal-TP H100 EAGLE transport has a functional response, but no accepted aggregate replica performance result is available.

Research sources: 222048 raw retained evidence; 225227/225228 independent review; later failed launcher retained

## Slide 17

Only decode attention changes in the H100 N54 pair. FlashInfer control 222027 versus FA3 222028 both pass the local protocol/runtime/output gates, and FA3 execution is verified on eight decode ranks. Mean TTFT falls 118.922 ms, while mean ITL rises 0.773 ms. Across roughly 199 token intervals that adds about 154 ms, outweighing the first-token gain. Measured mean end-to-end latency rises from 4337.853 to 4372.813 ms; goodput falls 0.812%. This is one matched pair, not a universal FA3 ranking or precise kernel-level explanation. Prefill continues using FA3.

Research sources: 222027/222028 full reviews and extended inspections; scoped interpretation

## Slide 18

Comparing H100 N50 with H200 N56 changes both the platform and the workload. For a calibrated comparison we hold the combo configuration and N52 load fixed. Selected runtime fields, the model, checkpoint precision, BF16 KV, worker placement, CUDA graphs, backends and client protocol match. The audited differences include engine random seeds; unobserved or unbalanced hardware and runtime conditions remain. We report a system association, not a causal GPU-only multiplier.

Research sources: Matched-anchor audit and cross-platform report

## Slide 19

The matched combo N52 anchor uses two H100 allocations and four H200 allocations. Their means are 2,215.460 and 2,632.181 good tokens/s, producing an empirical system ratio of 1.188096805. This is one calibration load for one configuration. Repeat measurements at one load do not identify a cross-platform function or a prediction interval. We do not apply this factor to TTFT, ITL, SLA or other backend branches.

Research sources: H100 221052/221058; H200 23904/23973/23975/24174

## Slide 20

Before the held-out H200 N50 result was available, we froze a prediction of 2,642.244 good tokens/s from the H100 N50 mean and the N52 ratio. We predeclared a 2% operational tolerance. Job 24272 measured 2,601.629, an error of minus 1.5371%, so this one local check is within tolerance. However, the result lies outside the earlier input-only sensitivity range, which omitted model error. We retain that negative finding, do not refit the frozen factor, and do not claim broad predictive validity.

Research sources: Frozen prediction and hashes; held-out 24272 review; cross-platform report

## Slide 21

These are scoped negative findings, not universal engine rankings. Full N68 25488 gains only 0.083056% over paired N64 25487, below our predeclared 1% practical gate. Modern full prefill graph/admission factors improve less than 1%; no confirmation was justified. H100 decode FA3 loses 0.812% in the retained pair. Decode-only EAGLE3 loses 4.74% against its short target-only control, although the local screen passes. Close unchanged branches and preserve their raw observations rather than combine small favorable peaks.

Research sources: 25487/25488 full review; full graph/admission study; 222027/222028 attention pair; 25998 short review

## Slide 22

Full N64 26766 passes actual runtime, fixed workload and request-level latency checks with 98.580442% joint success. The local output suite passes 7/8 without new regression and retrieval 12/12. These small checks do not establish at least 99% of the organiser reference score on official full-set model-quality benchmarks. FP8 weights and BF16 activation/KV are retained, with no quantized KV or speculative decoding in the selected primary. Official accuracy and organiser re-verification remain open. Do not describe this as an official ranking or contest acceptance.

Research sources: 26766 full gate; official Qwen rules and goodput clarification

## Slide 23

The research progressed from draft dtype and full-pool NIXL failures to actual equal-TP H100 transfer and valid H200 decode-only short serving. H200 25998 completes at 2626.71 good output tokens/s versus short target-only control 25947 at 2757.36, a 4.74% loss. Joint SLA is 94.84%; errors/cancellations are zero; smoke 7/8 and retrieval 12/12. Native draft acceptance around 0.12-0.15, approximately 1.24-1.29 accepted tokens per verification, is consistent with overhead not being repaid, but is not a causal kernel decomposition. This is a 20/40/30 unranked screen, not comparable directly with the full N64 frontier. Official accuracy is unknown and the unchanged draft/runtime branch is closed.

Research sources: 25998 complete short review; 25947 control; H100 225228 equal-TP native observer

## Slide 24

Three historical full N64 observations 25366/25373/25487 have mean 3044.400475 good output tokens/s. A later native-runtime observation 26766 independently passes at 3045.501509 and 98.580442% joint SLA. We report these separately rather than pool runtime paths. Valid lower legacy/modern replays around 2802-2831 remain retained; exact parity checks do not establish why the operating regime changed. N64 is chosen for replication, not because of the highest historical individual N68. No official quality certificate, global optimum, speculative speedup or causal native-runtime speedup is claimed.

Research sources: N64 three-run review; 26766 independent full review; lower 26313/26317/26319 retained

## Slide 25

Historical full N64 runs 25366, 25373 and 25487 are 3044.489701, 3044.074628 and 3044.637094 good tokens/s, mean 3044.400475. Later exact legacy replay 26313 gives 2830.923547, with operational file parity and the same validated model/protocol but other unobserved runtime/node conditions. New native-runtime 26766 gives 3045.501509. Retain the lower result rather than omit it from the story. These runs span launcher and observation differences, so neither the difference from 26313 nor the new approximately 3k result isolates a causal improvement. Highest individual N68 25488=3047.165853 misses the paired useful-gain gate and is not selected.

Research sources: 25366/25373/25487; 26313 recovery audit; 26766 full review

## Slide 26

Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.

Research sources: Current full-protocol historical scan; complete reviews for current peak

## Slide 27

The AI primary is updated from stale N62 to the replicated N64 setting, while the HPC package and its slide section are preserved. The package is a portable derivation rather than the historical research job itself; a separate GPU replay of that portable entry has not been performed. Native FP8 target and BF16 activation/KV remain. H200 uses two TP4 DeepGEMM prefills, chunk 8192 and breakable prefill graphs, with one TP8/EP8 HPC-Ops decode, FlashInfer decode attention, MNNVL and dense decode graphs 1 through 64. Round-robin routing and all original fixed-workload goodput limits remain. H100 is a separate point, not an alternate device setting for the same result.

Research sources: 26766 frozen worker/runtime; 25487 operational settings; staged portable deployment validation

## Slide 28

Historical N62 control 25365 has 24 failures starting by 35.444853 ms after profiling begins; N64 25366 has 26 by 33.481316 ms; repeat 25373 has 26 by 30.864687 ms. New native-runtime N64 26766 has 27 TTFT failures, all starting by 13.004085 ms, with zero ITL failures and zero errors/cancellations. The request-start calculation was replayed from the raw profiling JSONL. This is an association with initial admission, not a causal prefill, transport or decode diagnosis. Fixing every miss at unchanged request count/accounting would be a hypothetical ceiling, not an achieved speedup. Keep cold prefixes and every request in the denominator.

Research sources: Raw per-request exports 25365/25366/25373/26766

## Slide 29

The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.

Research sources: Qwen workload and addendum; normalized AIPerf configs

## Slide 30

All three new R3 arms are full N64, 60/120/30, fixed 4000/200 seed 2026 cold prefixes, same model/source/precision and same runtime path. 26766 chunk8192 gives 3045.501509 good output tokens/s; 26768 chunk10240 gives 3034.088251; 26770 chunk12288 gives 3020.943099. All pass local protocol/runtime/SLA/output checks, have zero profiling errors/cancellations, smoke 7/8 and retrieval 12/12. Mean TTFT rises 1108.869 to 1138.225/1145.943 ms; p95 rises 1311.693 to 1518.870/1624.120 ms. One ordered observation per arm is not a global optimum. Retain8192 and close the bounded larger-chunk branch.

Research sources: 26766/26768/26770 independent full reviews; sealed raw exports

## Slide 31

Shared storage pressure blocked default container extraction. A native unprivileged Enroot route under ordinary Slurm cgroups was verified on one GPU and two independent four-GPU groups with eight distinct UUIDs, then passed full serving. The AIPerf image needed an explicit exec command script; private rootfs cleanup was verified after scored runs. The newer tokenizer trials all wrote valid semantic P/D receipts but the outer warmup step timed out before AIPerf. They have no measured speedup. The derived repair retains the semantic120-second command and global17-minute job deadlines while separating rootfs lifecycle timing. These are reproducibility and failure-accounting findings, not inference optimization gains.

Research sources: Native runtime R3, eight-GPU proof, full26766, failed26849/26851/26853 and bounded lifecycle repair

## Slide 32

The chosen primary remains replicated N64 target-only serving. Larger chunks, unchanged N68 increases and unchanged low-acceptance EAGLE3 are closed at their tested settings. Native asynchronous tokenizer batching is a new bounded hypothesis: CPU-only exact input IDs pass for64 concurrent and one single request, but no complete serving benchmark exists yet because the first full arms failed an outer lifecycle timeout. Repaired trials are submitted, not scored improvements. Evaluate useful matched gains, first-cohort TTFT tails, complete model-quality evaluation, and portable deployment replay. Background photos remain reference infrastructure, not contest-installation photographs. The unchanged HPC section follows.

Research sources: Full research journal through28October2026; tokenizer and lifecycle repair records

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
