# H100–H200 comparison and transfer estimate

Updated: 17 October 2026, 11:56 UTC. **One held-out measurement is available. A general cross-platform conversion is not established.**

This is an internal research report. It does not replace a benchmark or provide an official converted competition score.

## Results we can report

At the original calibration snapshot, the highest measured H100 result was **2,229.83 good output tokens/s**, job **221058.pbs111**, at **N50** with MNNVL + FlashInfer. SLA was **98.5684%**, with no errors or cancellations. The independent run 221052 measured 2,218.03. Their mean is **2,223.93**.

Both H100 runs passed sealed artifact, protocol, payload, runtime, short-output nonregression and 12/12 long retrieval checks. These checks do not prove the organisers' full-set 99% reference-accuracy requirement.

H200 N56 measured 2,671.11 and 2,669.80 in the original calibration analysis, mean **2,670.46**. Comparing that number with H100 N50 describes two operating points. It does **not** establish a 20% algorithmic speedup: hardware and concurrency both differ.

## What is matched?

Use **the same combo configuration at the same N52 load** as the calibration anchor. Do not mix other backends, topologies or loads into its mean.

| Variable | Matched setting | Evidence |
|---|---|---|
| Model | Qwen3-235B-A22B-Instruct-2507-FP8 | Model identity and staging records; config/ServerArgs |
| Allocation | 16 GPUs, two nodes | Placement and job scripts |
| Prefill | Two workers, each TP4/EP1; chunk4096 | Resolved ServerArgs and logs |
| Decode | One worker, TP8/EP8 | Resolved ServerArgs and logs |
| Decode backends | FlashInfer attention + MNNVL collective | Runtime configuration and rank initialization logs |
| KV cache | BF16 | Allocation logs, not inferred from the requested `auto` setting |
| Decode CUDA Graphs | Dense batch sizes 1–64 | Resolved runtime configuration |
| Routing / transfer | Round-robin / NIXL with the same geometry patch | Frozen execution payload and patch hash |
| Load | 52 concurrent requests | AIPerf export |
| Benchmark | Closed-loop,4000/200 tokens;60s warmup/120s measurement/30s grace;dataset seed2026 | Identical normalized input_config |
| SLO | TTFT≤3000ms, meanITL≤20ms; errors included in the denominator | Export and raw-request review |
| Serving/client images | Same staged image artifacts | Staging contracts and transfer verification |

[matched-anchor-audit.json](matched-anchor-audit.json) records selected resolved runtime fields, normalized benchmark configuration, source paths and hashes. On those audited fields, the differences are **engine random seeds**. The AIPerf dataset seed remains2026. This does not prove the complete systems differ only in GPU model.

Remaining confounders include GPU, CPU, NIC/IB, host driver libraries, power/clock settings, scheduler/container launcher, nodes, cache, time drift and unpinned engine seeds. H100 uses PBS/Singularity; H200 uses Slurm/Enroot. Hardware was not randomly swapped between the same nodes. Interpret the observed ratio as a **deployment-system association**, not the causal effect of H200 alone.

Previously verified image records, not rehashed in this reporting turn:

- SGLang SHA256: `b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`.
- AIPerf SHA256: `58fc1cbc2aec897fe39bf74d8f38f055b63c3690429162134f818d9597d22c0a`.
- [Asset contract](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/asset-contract.json) and [transfer verification](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/transfer-status.json).

## Measurements used

All values are good output tokens/s. Means include every listed run, rather than selecting only the peak.

| Platform | N | Job IDs | Individual results | Mean | Role |
|---|---:|---|---|---:|---|
| H100 |52|221052,221058|2215.247;2215.673|2215.460|Calibration |
| H200 |52|23904,23973,23975,24174|2631.085;2632.065;2632.610;2632.964|2632.181|Calibration |
| H100 |50|221052,221058|2218.032;2229.827|2223.930|Prediction input |
| H200 |50|24272|2601.629|2601.629, one run|Held-out measurement; NOT fitted back into calibration |
| H200 |56|24190,24235|2671.109;2669.803|2670.456|Separate operating-point comparison, NOT calibration |

H100 N50 and N52 were measured in the same allocations. They are not independent replicates of each other. The independent unit is an allocation/job; H100 has only two. H200 jobs ran at different times, without a matched-time cross-platform control.

## Coverage across research branches

| Branch | H200 coverage | H100 coverage | Supports a transfer factor? |
|---|---|---|---|
| MNNVL + FlashInfer,N52 |4 jobs|2 jobs|One calibration load only; a holdout is required |
| MNNVL alone |N52/N54|N32–48, including failedN48|No matching passingN52 pair in this analysis |
| FlashInfer alone |N52|N32–38|Different loads; no direct conversion |
| Original FA3/default collective |Several higher loads|N32–36|No same-load pair used here |
| DeepGEMM/CUTLASS/FP8KV/DP-attention/chunk variants |Several H200 trials|No corresponding matched H100 evidence here|No branch-specific transfer factor |

A factor fitted to the combo must not be applied to these other branches. Keep backend, topology and load in every plot label.

## Frozen model and prediction

The proposed local hypothesis is that the system throughput ratio changes modestly near the calibration load, for this exact configuration.

```
k52 = mean(H200,combo,N52) / mean(H100,combo,N52)
    = 2632.180931 / 2215.459986
    = 1.188096805

predicted(H200,combo,N50)
    = mean(H100,combo,N50) * k52
    = 2223.929512 * 1.188096805
    = 2642.243548 good output tokens/s
```

**This is our empirical model, not a conversion certified by NVIDIA or the organisers.** References support the methodology and its limitations; they do not prove our numerical factor.

Only **one concurrency value,N52**, is available for calibration. Repeated measurements at that load do not identify the function k(N), load-dependent bias, or a 95% prediction interval.

Varying inputs over the observed run minima/maxima produces **2633.887–2650.293**. This is an **input-only sensitivity range**, not a confidence interval, prediction interval or performance guarantee. It excludes model error and unobserved system variation.

The SLA is nonlinear: small latency changes near20ms can remove many requests from goodput. Do not scale SLA, TTFT, ITL or other configurations using this throughput ratio. VRAM capacity, TensorFLOPS and peak memory bandwidth are not direct goodput multipliers.

## Held-out validation: keep the original forecast

Job **24272** was submitted to measure H200 N50 directly with the same model, configuration and protocol. The prediction, input hashes and **2% operational tolerance** were saved while the job was pending. They have not been fitted to the result.

| Quantity | Value |
|---|---:|
| Frozen prediction | 2642.244 good tokens/s |
| Measured H200 N50 | 2601.629 good tokens/s |
| Signed error,(measured−predicted)/predicted | −1.5371% |
| Absolute relative error | 1.5371% |
| Predeclared operational tolerance | 2% |
| Measured SLA | 99.1326% |
| Mean TTFT / ITL | 505.178ms / 16.367ms |
| Long retrieval checks |12/12 passed |

Sealed raw/protocol/payload/runtime and short-output checks passed. The prediction passes the predeclared2% operational check at this one point. **That is not a claim of 95% prediction coverage or general transfer validity.** The2% threshold was a research decision, not a statistical confidence level or organiser rule.

The measurement is **outside the earlier input-only sensitivity range**. Preserve this negative finding: that range omitted load-dependent model error and cannot be presented as a prediction interval.

The measured ratio at N50 is about **1.1698×**, versus **1.1881×** at N52. It is not exactly constant. Do not refit the frozen factor using this holdout and then call its training error a validation result.

If the operational check had failed, the model would be marked unsupported at that point, without changing the original forecast or excluding the measurement. Invalid protocol/output evidence would block a performance-validation claim even if throughput happened to match.

For broader prediction, collect several matched loads spanning the intended range, repeat each platform, retain additional untouched validation points, and examine residuals and platform×configuration interactions. A practical next design would include at least three matched loads; this is a proposed design, not data already collected.

[Validation record](holdout-validation.json) · [Frozen preregistration](pre-registered-prediction.json) · [Validation script](validate-holdout.py).

## References and what they establish

1. [Competition task rules](/home/apacsc42/2026-APAC-HPC-AI/1.%20Qwen3%20AI%20Task%20Rules.md): permitted platforms, protocol/SLA/quality rules, and no direct cross-platform raw-throughput ranking. They provide no conversion formula.
2. [NVIDIA TensorRT-LLM performance overview](https://nvidia.github.io/TensorRT-LLM/latest/developer-guide/perf-overview.html): GPU/model, batch size, parallelism and tuning affect performance. This supports controlling workload; its TensorRT-LLM numbers are not substituted for SGLang measurements.
3. [NVIDIA H200 specifications](https://www.nvidia.com/en-au/data-center/h200/):141GB memory,4.8TB/s bandwidth, approximately1.4× H100 bandwidth. This establishes a hardware difference, not a1.4× Qwen goodput guarantee.
4. [NIST prediction uncertainty](https://www.itl.nist.gov/div898/handbook/pmd/section5/pmd512.htm): prediction uncertainty differs from uncertainty in an estimated mean response. A few run minima/maxima are not a prediction interval.
5. [NIST Engineering Statistics Handbook](https://www.itl.nist.gov/div898/handbook/toolaids/pff/E-Handbook.pdf): interpolated/extrapolated predictions require additional confirmatory real data. N50 lies outside the calibration design containing only N52.

Web sources were accessed 17 October 2026 UTC; latest websites may change. Quantitative evidence for our ratio comes from our retained experiments, not marketing specifications.

## Reading and reproducing the plots

Use [matched-comparison.png](matched-comparison.png) or [SVG](matched-comparison.svg): panelA matchesN52, panelB normalizes each platform to its ownN52, and panelC separates the frozen forecast from the held-out measurement. Do not label the difference between two best points at different loads as an algorithmic speedup.

The older comparison.png is retained as an exploratory historical plot. It is not sufficient evidence on its own. The earlier Vietnamese report is retained as historical text; this English report is current.

[Derived inputs](data.json) · [Runtime audit](matched-anchor-audit.json) · [Plot script](build.py) · [Source experiment reviews](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/manual-20261017-0858/RESULTS.md).

## Later control observation — 17 October, 16:58 UTC

Fresh H100 combo N50 control 221151 measured **2,231.429 good tokens/s**, SLA 98.4286%, with full protocol, runtime, short-output and 12-case long review passing. This is about 0.072% above the earlier peak with the same configuration; it does not establish a new optimisation. It is later control data and is not refitted into the frozen calibration, prediction or held-out evaluation above. Review: qwen-experiments/nscc-pbs/inspection/manual-20261017-continue-1655/review-221151.json.

## Phase-specific backend results — 17 October, 23:42 UTC

DeepGEMM for prefill is now independently confirmed on H200 at N56: 2,715.842 and 2,716.787 good tokens/s (mean 2,716.315), gains of 1.8136% and 1.7401% versus respective fresh controls. H100 N50 DeepGEMM job 221177 passed review at 2,232.720, only +0.0579% versus its control. Loads and systems differ, so this is not a causal GPU-only effect, but it demonstrates why the earlier combo calibration must not predict a backend's percentage gain on another platform.

H100 prefill prefetch job 221153 measured 2,241.336 (+0.444%) and shorter startup, while H200 prefetch 24322 measured 2,665.572 (−0.178%) with longer representative weight loading than its control. Ordering/cache/node confounds remain. A reversed-order H100 prefetch/control pair is submitted. Neither observation changes the frozen combo calibration or held-out forecast above. Reviews: qwen-experiments/research-followup-20261017-2335/RESULTS.md.
