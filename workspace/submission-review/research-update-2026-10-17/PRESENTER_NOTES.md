# TripleU presentation guide

English research presentation updated on 17 October 2026.

Use slides 1–24 for the main 15–20 minute talk. Slides 25–32 are reference material for questions; skip them during the main narrative unless useful. This is a proposed pacing, not a timed rehearsal.

The deck is a research update, not an official score claim. The new H200 candidate needs replication and full-set official accuracy. The packaged primary job scripts still describe the previously validated N48 deployment; this slide-only update does not promote the new candidate to an official re-run configuration.

PDF and image previews are generated from the same explicit drawing coordinates as the PowerPoint; no Office or LibreOffice rendering was available.

## Slide notes

### 01 · Qwen serving

We present our complete optimisation path, from the initial topology measurements to the latest phase-specific compute trial. The workload is Qwen3-235B with 4,000 input tokens and 200 generated output tokens. H200 and H100 measurements are kept separate. The headline H200 result is a research candidate awaiting independent confirmation and official accuracy evaluation.

### 02 · Two measured frontiers

The highest observed H200 goodput is 2,715.842 good output tokens per second at N56 with prefill-only DeepGEMM. It passes local protocol, runtime, SLA and research output checks; replication is pending. H100 reaches 2,229.827 at N50 with the combo configuration. Its independent N50 measurements average 2,223.930. These are different hardware and load points, not a matched algorithmic speedup.

Research sources: 24291 review; H100 221052/221058 sealed reviews

### 03 · Optimise useful throughput under a latency gate

Each request must satisfy both time to first token at most 3,000 ms and mean inter-token latency at most 20 ms. At least 90% of evaluated requests must meet both. Errors remain in the denominator. Goodput is qualifying requests per second; multiplying by 200 gives the good output tokens per second reported here. Mean latencies alone do not establish the per-request gate.

Research sources: Qwen task rules and 25 September addendum

### 04 · One workload, two deployment systems

Both platforms provide two eight-GPU nodes, but they are not interchangeable experimental environments. Firmus uses H200, Slurm and Enroot; NSCC ASPIRE 2A+ uses H100 80GB, PBS and Singularity. We stage the same serving and client image artifacts and official FP8 checkpoint. CPU, driver, network, launcher, node cache and timing can still differ. A hardware-specification ratio is not a performance conversion.

Research sources: Qwen rules; NSCC asset contract; matched-anchor audit

### 05 · Separate prompt processing from token generation

The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.

Research sources: Selected placements in 24291 and 221058

### 06 · Topology search established the serving layout

We explored the balance between replication and parallelism. The original 07 and 09 names were identifiers, not software versions. The 07 configuration used four TP2 prefill workers and two TP4/EP4 decode workers. The next layout widened prefill to TP4. The selected split also widened decode to TP8/EP8. We explored 17 usable arrangements across 8+8, 4+12 and 12+4 GPU splits, retaining incompatible originals and EP2 replacements separately. These initial operating points differ in load and transport history.

Research sources: 22197; 22219; 22415; prior topology campaign

### 07 · Make KV-transfer setup scale with the request

Cold disaggregated serving initially stalled while preparing whole-pool KV descriptors. The request-scoped patch constructs descriptors for the pages actually transferred and coalesces contiguous ranges. A representative TP8 source geometry drops from approximately 403.8 million source entries per rank for the pool to 188 coalesced entries for one contiguous 4,000-token request. These numbers are descriptor counts, not a measured speedup factor. The range mapping tests retained head mapping, byte ranges and notifications. Connection warming uses separate traffic before the official client warmup.

Research sources: NIXL patch metadata; 720 + 936 range checks; historical cold-start logs

### 08 · FP8 block geometry constrains parallelism

A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The new N56 TP8/EP2 test is a combined prefill-layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.

Research sources: Exact staged SGLang source; failed job 24282; corrected trial 24321

### 09 · A repeatable experiment loop

We combine source research with observed runtime, output checks, failures and cost before choosing a trial. Each useful hypothesis gets a control and a stopping rule. Exploratory short sweeps screen configurations; records in this talk use full 60/120/30 confirmations. We retain raw exports, per-request data, submitted payloads, logs and terminal artifacts. Candidate gains require runtime activation checks and independent replication. An exited job without a valid export is not a successful experiment. Loading time is also a resource cost: H100 is billed at 128 SU per GPU-hour, making a 16-GPU, 45-minute cap 1,536 SU. Three submitted jobs reserve 4,608 SU and run sequentially; prefetch targets startup cost rather than assumed throughput gains.

Research sources: Research plans; payload hashes; sealed reviews

### 10 · H200 progression: topology, serving, then kernels

The H200 campaign progressed from 1,297.018 good tokens/s in the initial reference operating point to 1,912.300 after topology and transfer work, then above 2,630 with serving backends at N52. Load selection reached about 2,670 at N56. Prefill-only DeepGEMM produced the latest 2,715.842 candidate. This is a historical end-to-end progression: it changes topology, load, transfer and backends over time. It is not a single-factor speedup measurement.

Research sources: Full confirmations: 22197, 22219, 22415, 23904, 24190, 24291

### 11 · Backend combinations matter

At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.

Research sources: 23777; 23778; 23904; 23974

### 12 · More concurrency eventually stops helping

The original combo configuration increases goodput as load rises toward N56. The two N56 confirmations average 2,670.456. N58 measures 2,667.966 and increases TTFT to 991.136 ms, providing no observed gain. We do not blindly keep increasing concurrency. The plot aggregates the stated jobs; N50 and N58 have only one observation each. The newer prefill DeepGEMM candidate is not mixed into this control curve.

Research sources: 24272; 23904/23973/23975/24174; 24131/24175/24189; 24190/24235; 24236

### 13 · Profile the phase before choosing the kernel

After the scored N56 benchmark, job 24263 ran a separate diagnostic at concurrency 48. All 16 rank traces contain kernels, and all 415 diagnostic requests succeeded. On each prefill worker, classified MoE kernels account for about 43% of summed kernel durations, motivating a prefill-only kernel trial. These fractions are not wall-time shares or predicted speedups. Prefill captured four steps and decode 32, so their absolute totals are not comparable. Profiling control warnings are retained, but trace coverage is valid.

Research sources: 24263 profile review; diagnostic protocol and all-rank traces

### 14 · DeepGEMM for prefill: a new candidate gain

Job 24291 changes the prefill MoE runner to deep_gemm, retaining two TP4/EP1 prefill workers, TP8/EP8 decode, MNNVL, FlashInfer, N56 and the full protocol. Against fresh control 24263, goodput improves 1.8136% and mean TTFT drops 107.569 ms. ITL rises slightly, so the gain is not a universal latency improvement. Runtime, raw protocol, short nonregression and 12 long checks pass. A speculative runner field inherits deep_gemm, but speculative_algorithm remains None. An independent repeat is submitted; this candidate is not yet a final validated selection.

Research sources: 24291-v2.json; 24263; repeat 24327 pending at snapshot

### 15 · The latency gate is checked request by request

The latest DeepGEMM candidate has 1,694 measured requests. A raw-request check finds 1,674 within both limits and 20 that miss a limit; there are no request errors or cancellations. This produces 98.8194% joint SLA. The mean TTFT of 749 ms and mean ITL of 16.446 ms are useful descriptions, but the pass fraction is determined by individual requests. The 90% latency gate passes; the official accuracy gate remains separate.

Research sources: 24291 raw profile_export.jsonl and reviewed export

### 16 · H100: repeat the tuning on its own hardware

The H100 campaign uses the same model and staged image contract, but must find its own capacity frontier. MNNVL repeats at low loads increased goodput by about 7.52% and 8.24% at N32 and N34 versus a fresh control. Standalone FlashInfer was slower in historical tests, while the combination extended useful capacity. MNNVL-only passed N46 but failed N48 in repeated measurements. Combo passed N48 and later reached its best N50 operating point. This is why a winner on one cluster cannot simply be assumed to win on the other.

Research sources: H100 matched pair 220908/220909; 221020/221021; 221052/221058

### 17 · H100 load frontier: N50 beats N48 and N52

The two independent combo sweep jobs each measured N48, N50 and N52. N50 has the highest mean goodput at 2,223.930 tokens/s, with a peak of 2,229.827. N52 is lower in both repeats and has more first-token waiting. N48 has lower TTFT and a somewhat higher SLA pass fraction. These are operating point tradeoffs, not separate accuracy scores. We select useful throughput under the SLA, rather than the smallest average latency.

Research sources: 221052 and 221058 sealed reviews

### 18 · Compare matched systems, not unrelated peaks

Comparing H100 N50 with H200 N56 changes both the platform and the workload. For a calibrated comparison we hold the combo configuration and N52 load fixed. Selected runtime fields, the model, checkpoint precision, BF16 KV, worker placement, CUDA graphs, backends and client protocol match. The audited differences include engine random seeds; unobserved or unbalanced hardware and runtime conditions remain. We report a system association, not a causal GPU-only multiplier.

Research sources: Matched-anchor audit and cross-platform report

### 19 · A local N52 calibration, not a universal multiplier

The matched combo N52 anchor uses two H100 allocations and four H200 allocations. Their means are 2,215.460 and 2,632.181 good tokens/s, producing an empirical system ratio of 1.188096805. This is one calibration load for one configuration. Repeat measurements at one load do not identify a cross-platform function or a prediction interval. We do not apply this factor to TTFT, ITL, SLA or other backend branches.

Research sources: H100 221052/221058; H200 23904/23973/23975/24174

### 20 · Freeze the forecast, then test it on H200

Before the held-out H200 N50 result was available, we froze a prediction of 2,642.244 good tokens/s from the H100 N50 mean and the N52 ratio. We predeclared a 2% operational tolerance. Job 24272 measured 2,601.629, an error of minus 1.5371%, so this one local check is within tolerance. However, the result lies outside the earlier input-only sensitivity range, which omitted model error. We retain that negative finding, do not refit the frozen factor, and do not claim broad predictive validity.

Research sources: Frozen prediction and hashes; held-out 24272 review; cross-platform report

### 21 · Negative results narrow the next experiment

The search retained losing and failed branches instead of hiding them. FP8 KV at N52 and decode-side DeepGEMM failed the latency gate. Prefill chunks 2,048 and 8,192 were slower than 4,096 in the compared combo tests. Limiting prefill batching to one request reduced goodput 1.73% versus the fresh N56 control, despite slightly lower mean ITL. TP8/EP1 failed before benchmarking. These are different outcomes: a slow passing result, an SLA failure and a deployment failure are not interchangeable.

Research sources: 23608; 23609; 23905/23906; 24281; 24282

### 22 · Latency passes; official accuracy is still open

Local research quality checks are separate from official acceptance. The latest candidate has no new short-output failures relative to the independent baseline and passes 12 long-context retrieval checks. The short diagnostic itself is seven of eight, because the baseline already fails one case; we do not hide that. These checks support nonregression research but do not replace full-set MMLU-Pro and GPQA evaluation. Retaining 99% of the reference score is relative accuracy, not 99% absolute question accuracy. No official score or re-run result is claimed.

Research sources: 24291 short nonregression and long review; Qwen addendum Q1

### 23 · Next tests follow the remaining uncertainty

At the saved queue snapshot, H200 jobs 24320, 24321, 24322 and 24327 are submitted: fresh combo control, TP8/EP2 prefill, prefill weight prefetch and independent DeepGEMM repeat. H100 jobs 221151, 221152 and 221153 form a sequential control, prefill DeepGEMM and prefill prefetch chain. These are pending experiments, not additional results. Prefetch targets startup and credit, not an assumed throughput gain. We will validate useful gains independently and keep quality checks separate from official accuracy.

Research sources: Submission receipts and scheduler snapshot on 17 October 2026

### 24 · What the campaign has established

Our main lesson is that topology, transfer, backend choice and load must be considered together. The selected topology and request-scoped KV descriptors made the deployment usable; phase-specific compute and communication tuning then lifted useful throughput. H200 currently has a promising 2,715.842 candidate; H100 has repeated N50 evidence averaging 2,223.930. Cross-platform extrapolation is narrowly calibrated and checked with a held-out result. The remaining work is independent candidate confirmation and official quality validation. The appendix contains metric records and run details for questions.

### 25 · Appendix · independent H200 metric records

These are separate observed records across the available history of full-duration passing measurements, not one configuration achieving every minimum and maximum. The lowest mean ITL is from the decode-heavy topology at N16. The lowest TTFT is from the older round-robin layout at N53. Highest goodput is the newer prefill DeepGEMM N56 trial. SLA reaches 100% at low load in two tied topology runs. The scan does not re-audit every old runtime or quality condition.

Research sources: All-history metric report and records.json

### 26 · Appendix · independent H100 metric records

The highest H100 goodput is the N50 combo run. The observed TTFT minimum is from early MNNVL job 220720, but empty role logs leave runtime incompletely verified; it is not a fully validated deployment winner. The ITL minimum is from MNNVL repeat 220909 at N32 with later task-side proof. Multiple jobs tie at 100% SLA. These records come from full-protocol exports; they are not a substitute for comparing like-for-like deployments.

Research sources: All-history metric report; pair-review 220909/220908

### 27 · Appendix · exact settings behind the frontiers

The best H200 candidate uses the same selected worker layout as the H100 combo, but it adds DeepGEMM only to prefill and operates at a different load. Both use the official FP8 checkpoint and reviewed BF16 KV allocation, with dense decode graph sizes from one through 64. Round-robin routing and the same NIXL descriptor patch remain. Backend names in config are requests; terminal logs and backend-rank initialization establish that the intended runtime actually started.

Research sources: Submitted worker scripts; resolved ServerArgs; all-rank backend reviews

### 28 · Appendix · topology failures remain separate

In the first 17-job wave, only eight layouts produced measurements and nine failed before a useful benchmark. We corrected the earlier mistake of treating terminal scheduler states as completed measurements. Recovery addressed environment, registration, slow path warmup and FP8 block alignment. The final usable-layout accounting kept 14 compatible originals and three explicitly named EP2 replacements separate from the incompatible TP8/EP1 originals. No failed original receives a replacement result under its name.

Research sources: Historical topology review; recovery records; prior 17-layout presentation

### 29 · Appendix · what the benchmark actually measures

The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.

Research sources: Qwen workload and addendum; normalized AIPerf configs

### 30 · Appendix · the job history behind key decisions

These job identifiers make each research decision traceable without putting file packaging instructions into the presentation. The main H200 progression begins with 22197, 22219 and 22415, then uses backend comparisons at N52 and repeated N56 controls before the latest 24291 prefill trial. H100 has a fresh control pair, capacity tests and two final combo sweeps. A configuration version count is not a count of successful measurements or a measure of research quality.

Research sources: Frozen presentation-data.json and terminal reviews

### 31 · Appendix · other branches and what they taught us

Early dense decode graphs and chunk4096 trials changed performance modestly at N48 and N52 before the later round-robin and backend work. DeepEP low-latency N52 reached 1,957.15 good tokens/s, below the emerging alternatives. DP-attention variants at N52 reached 2,549.20 and 2,538.08 in independent jobs, but N54 reached only 2,555.42 versus 2,634.03 for the MNNVL operating point. Original CUTLASS deployment produced no scored export. These results are historical observations with different controls over time, not a single uniformly matched ablation. Source-only ideas such as speculative decoding are not measured gains; losslessness and source compatibility must be established before expensive trials.

Research sources: 23103; 23114; 23272; 23780/23859; 23934/23924; failed 23776

### 32 · Discussion

Questions can focus on why the chosen worker balance helps, the NIXL descriptor repair, FP8 block geometry, phase-specific kernel effects, per-request latency accounting, or the limits of cross-platform estimation. The current H200 candidate still needs replication and official full-set accuracy evaluation. H100 and H200 remain separate measured systems. Background photographs are reference infrastructure imagery, not photographs of either contest installation. Asset attribution is stored in the deck metadata.

