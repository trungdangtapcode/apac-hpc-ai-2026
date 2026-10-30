# Slide-by-slide transcript and learning guide — English

This is a **proposed speaking script and learning guide**, not a verbatim record of a delivered talk. It follows all 40 slides of the current presentation. The separately requested Vietnamese companion is a narrow language exception; code and other reports remain English.

**How to use it:** read the purpose and technical interpretation, then rehearse the spoken script. Use the terminology and evidence sections to prepare answers to why questions. This guide explains the research, rather than narrating slide decoration. Do not read every explanatory paragraph aloud.

- **Slides 1–24:** main AI talk. Follow the [15–20 minute plan](PRESENTATION_PLAN.md); select and shorten the scripts when rehearsing.
- **Slides 25–32:** AI backup material. Slides 31–32 remain backups even though their titles omit Appendix.
- **Slides 33–40:** read-only explanation of the existing HPC section. Its scheduler statements are **23 October snapshots**, not live 30 October status. This guide neither updates nor independently certifies later HPC work. Do not automatically include HPC in the AI time allowance.
- Colors have **slide-local meanings**. Orange does not always mean a win or a failure. Background photographs, gradients and footer decorations are not measurements.
- **↑ / ↓** generally indicate the desired optimization direction, not an observed increase/decrease. “No axes” means a table, card or schematic; do not invent X/Y quantities.
- Research has stopped at the owner's request. Future actions shown on slides are proposals or historical next decisions, not newly executed jobs.

Sources: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-journey-update-20261030/TripleU_APAC2026_Presentation.pdf), [Vietnamese companion](TRANSCRIPT_VI.md). PowerPoint SHA-256: `b2e1c88aba8d5a3d5ec181e3fccc6b95bb6ea12c29f214e7c3c964619dc81616`. This guide describes that version; recheck it if the deck changes.

## Understand the claims before presenting them

**Team-measured, formerly called “local”:** the benchmark ran on the assigned cluster's H200 or H100 compute nodes identified for that result. The team submitted the job and reviewed the data. Local described the scope of validation; it did not mean a laptop, the login node or a single compute node. Running on provided infrastructure does not itself make a result an organiser-scored or certified result.

**Full run:** the campaign protocol uses 60 seconds of warmup, 120 seconds of profiling, and 30 seconds of grace for outstanding requests to finish. Full distinguishes it from a shorter idea-screening test. It does not mean all model-quality datasets were evaluated or every request passed. The latency rule requires at least 90% of all requests to jointly meet both limits.

**Reviewed pass:** the team examined retained data against the checks implemented for that run, such as protocol, actual runtime settings, latency/errors and small output checks. Read each run's exact conditions. Scheduler COMPLETED alone means the script returned successfully. Neither label substitutes for the official model-quality evaluation requiring at least 99% of the organiser reference; that remains unverified.

**Control and candidate:** a control is the retained comparison configuration; a candidate changes the factor being tested. Cache candidate 27378 should be compared with fresh control 27376. Comparing it against a historical mean from another series mixes the tested change with time and environment differences.

**Repeat and useful gain:** another job returning a similar result is stronger evidence than one peak, although it may use the same physical GPUs. For late trials, the team used a prospective >1% gain threshold to select changes worth confirming. This is a team decision rule, not an organiser rule. A 0.24% observed increase did not meet it and was not shown to be separable from run-to-run variation.

**Observation, hypothesis and conclusion:** “TTFT rose” is measured. “The queue grew” is a hypothesis until wait and computation times are separated. “Keep the old setting because the candidate did not exceed our stated threshold” is a supported decision. State missing measurements rather than turning a plausible explanation into an established cause.

**A score inside a failed job:** GPU inference and the client can finish and save JSON, followed by a reader/summary exception that makes the job FAILED. Repairing that reader can recover a score from old data; it does not change the original job status or replace a fresh full-deployment replay after the fix.

## Shared vocabulary

| Symbol / term | Plain explanation |
|---|---|
| cluster / node / job | A cluster is a group of connected compute servers; a node is one server. A scheduler job requests resources and runs commands there. A job ID identifies that execution, not its performance rank. |
| allocation | A scheduler grant of particular nodes, CPUs/GPUs and time. A new allocation is a new grant; it can reuse the same physical GPUs. It is not automatically an independent hardware sample. |
| serving / inference | Inference computes a model response. Serving keeps the model loaded behind an API and schedules multiple incoming requests; the benchmark measures that service. |
| Qwen3-235B-A22B | The model has about 235 billion total parameters, with about 22 billion active per token. The total weights still need storage; active count is not the total model-memory footprint. |
| checkpoint / container image | A checkpoint stores the model parameters. A container image supplies the software and dependencies used to run them. Changing one is different from changing the other. |
| runtime / backend / native | Runtime is the software path executing the service. A backend is a selected implementation of one operation, such as attention. Native names the built-in execution path in this pinned software; it does not mean personal-machine execution or automatically faster code. |
| request | One prompt submitted to the service and its generated response. |
| token | A model vocabulary unit: a word, word fragment, or punctuation; it is not necessarily one word. |
| prefill / decode | Prefill processes the prompt; decode repeatedly generates the next token. |
| TTFT | Time to first token, in milliseconds (ms). Includes the observed wait before the first response token. |
| ITL | Inter-token latency. The gate here uses each request’s mean interval between output tokens, in ms. |
| SLO / SLA fraction | The latency objective / fraction of all requests jointly meeting both latency limits. This is not model accuracy. |
| goodput | Qualifying requests per second. The official displayed score is this value multiplied by 200 output tokens per request. |
| N / concurrency | Maximum simultaneous in-flight benchmark requests in the closed-loop workload; not the GPU count. |
| closed-loop | Keep up to N requests in flight; after one finishes, send another. There is no separate fixed request rate. |
| p50 / median; p95; max | Median: half the samples are at or below it. p95: 95% are at or below it. Max: largest observed value. A mean is a different statistic. |
| TP / EP / replica | Tensor parallelism splits model computation; expert parallelism distributes MoE experts; a replica is another worker instance. |
| MoE | Mixture of Experts: a model routes each token to selected expert networks rather than activating every expert. |
| KV cache | Stored attention keys and values representing processed context, used when generating later tokens. |
| attention | The model operation that lets the current token use relevant earlier context. Keeping earlier keys and values avoids recomputing those stored representations from scratch at every decode step. |
| batch / queue / in-flight | A batch groups work for one engine execution. A queue holds work waiting to run. In-flight includes requests sent but not finished. Client concurrency is not necessarily the instantaneous GPU batch size. |
| NIXL | The transfer layer used here to move KV state between prefill and decode workers. |
| FP8 / BF16 | 8-bit floating-point / 16-bit bfloat formats. Weights, activations and KV can use different formats. |
| FI / FA3 / DG / HPC-Ops | FlashInfer / FlashAttention 3 / DeepGEMM / the reused HPC-Ops kernel implementation. HPC-Ops is not the OpenFOAM HPC track. |
| kernel / GEMM | A GPU computation routine / general matrix multiplication. Faster isolated kernels do not automatically improve the whole service. |
| profiling / GPU utilization | Profiling records selected execution events to investigate time and work. GPU activity shows whether sampled GPU work was active; 100% activity does not establish peak FLOPs, a compute bottleneck, or absence of communication stalls. |
| MNNVL / collective | Multi-node NVLink communication path / an operation in which multiple ranks communicate together. The actual enabled path must be checked. |
| CUDA graph / bucket | A captured GPU execution graph / a selected execution shape to capture. Bucket count is not request concurrency. |
| baseline / control / candidate | Reference configuration / comparison arm / proposed changed configuration. State the exact baseline for every percentage. |
| matched trial / repeat | A comparison preserving intended factors except the tested change / another allocation to check reproducibility. Neither automatically proves causality. |
| gate / promotion / close a branch | A gate is a stated acceptance condition. Promotion means choosing a candidate as the retained setting. Closing a branch means deciding not to repeat the unchanged losing setting; none of these words implies organiser approval. |
| 99% of reference | A relative model-quality requirement, separate from the request latency fraction. As an arithmetic illustration, if a reference metric were 80 points, 99% of it would be 79.2 points, not 99% of answers correct. This example is not a measured contest result. |
| cold prefix / cold startup | Cold prefix means requests cannot reuse prompt KV from earlier requests. Cold startup means the service is newly starting; OS file caches can still be warm. These are different states. |
| ms / s / tokens/s / req/s | 1,000 ms = 1 s. tokens/s counts tokens per second; req/s counts requests per second. |
| % / percentage points | A move from 90% to 95% is +5 percentage points, or +5.56% relative to 90%; these are different. |
| 2,989.175 / 2.989,175 | The deck uses English separators: comma for thousands and point for decimals. These two forms express the same value in English and Vietnamese conventions. |
| MPI rank / affinity / NUMA | An MPI process / placement on CPU cores / a CPU memory architecture with different local and remote access costs. CPU HPC ranks differ from GPU serving ranks. |
| Scotch / Hierarchical / graph cut | Mesh partitioning methods / another partitioning method / a partition-boundary proxy. A smaller cut is not automatically faster runtime. |

## Slide navigation

- [Slide 01 — Qwen serving: from topology to reproduced performance](#slide-01)
- [Slide 02 — Highest observation and strongest recommendation](#slide-02)
- [Slide 03 — Optimise useful throughput under a latency gate](#slide-03)
- [Slide 04 — One workload, two deployment systems](#slide-04)
- [Slide 05 — Separate prompt processing from token generation](#slide-05)
- [Slide 06 — Topology search established the serving layout](#slide-06)
- [Slide 07 — Make KV-transfer setup scale with the request](#slide-07)
- [Slide 08 — FP8 block geometry constrains parallelism](#slide-08)
- [Slide 09 — A repeatable experiment loop](#slide-09)
- [Slide 10 — H200 journey: recover, specialise, then reproduce](#slide-10)
- [Slide 11 — Backend combinations matter](#slide-11)
- [Slide 12 — H200: the N62-to-N64 step survives a full repeat](#slide-12)
- [Slide 13 — Profile the deployed interaction](#slide-13)
- [Slide 14 — The N60 gain survives an independent deployment](#slide-14)
- [Slide 15 — The reproduced N64 service still loses first-token tails](#slide-15)
- [Slide 16 — H100 has its own operating point and uncertainty](#slide-16)
- [Slide 17 — FA3: faster first token does not guarantee goodput](#slide-17)
- [Slide 18 — Test the cost hypothesis, then reverse the order](#slide-18)
- [Slide 19 — A local N52 calibration, not a universal multiplier](#slide-19)
- [Slide 20 — Freeze the forecast, then test it on H200](#slide-20)
- [Slide 21 — Use source evidence to test one small hypothesis](#slide-21)
- [Slide 22 — Latency acceptance is separate from model accuracy](#slide-22)
- [Slide 23 — EAGLE3: follow the failed hypothesis through its repairs](#slide-23)
- [Slide 24 — Topology → transport → kernels → replication](#slide-24)
- [Slide 25 — Appendix · diagnose performance drift with controlled cells](#slide-25)
- [Slide 26 — Appendix · profiles and source also close attractive detours](#slide-26)
- [Slide 27 — Appendix · the selected AI deployment is N64](#slide-27)
- [Slide 28 — Appendix · sparse graphs save memory, not goodput](#slide-28)
- [Slide 29 — Appendix · what the benchmark actually measures](#slide-29)
- [Slide 30 — Appendix · larger prefill chunks did not help](#slide-30)
- [Slide 31 — A real replay can invalidate a static deployment claim](#slide-31)
- [Slide 32 — What the evidence supports next](#slide-32)
- [Slide 33 — The task: same 65-million-cell airflow calculation](#slide-33)
- [Slide 34 — The whole required pipeline comes before the score](#slide-34)
- [Slide 35 — A smaller partition cut did not make the solver faster](#slide-35)
- [Slide 36 — Observed scaling changed which decomposition led](#slide-36)
- [Slide 37 — At four nodes, the winner depends on ranks per node](#slide-37)
- [Slide 38 — Keep the slow step in the mean; inspect the tail](#slide-38)
- [Slide 39 — A reproducible candidate needs more than a fast log](#slide-39)
- [Slide 40 — What we learned — and the next measurement](#slide-40)

---

<a id="slide-01"></a>

## Slide 01 — Qwen serving: from topology to reproduced performance

![Slide 01](../../submission-review/ai-journey-update-20261030/slides/assets/slide-01.png)

### Purpose

Open the AI research story and define its scope: turning a distributed Qwen deployment into a reproducible service measurement. The talk follows the engineering and evidence from topology through transfer and kernels to repeated performance; the title does not claim an official win or certified model quality.

### Technical interpretation and reasoning

The title describes the sequence of technical work: first choose how the model is split across GPUs, then make the prompt-state transfer correct, then tune the GPU implementations, and finally repeat the measurements. Reproduced performance means another run returns a similar result under the stated configuration; it does not mean that the organisers certified it.

### Terms and symbols to understand

- **Qwen:** The family of language models used in the serving task; this study serves the specified Qwen3-235B checkpoint.
- **APAC HPC-AI 2026:** The competition context for the research, not a statement of award or official acceptance.
- **30 October 2026:** The date of this research update; results are historical observations through that date.
- **VNUHCM - TripleU:** The presenting team identity.

### Interpreting the evidence or diagram

- The title also states the argument: the distributed system must function correctly before its speed comparisons are meaningful.
- Reproduction here means similar results on another run; it does not establish all-platform or all-workload performance.

### Tradeoff and strength of evidence

- **Observation:** The work progressed from resolving the two-node serving topology and KV transfer to phase-specific backend experiments and repeated full-protocol measurements.
- **Hypothesis:** Reliable performance depends on making the deployment and measurement path work end to end before tuning individual kernels.
- **Supported conclusion:** The presentation will support a reproduced operating point and selected configuration, while distinguishing that evidence from isolated peaks and official accuracy verification.
- **Unknown / limitation:** Official full-set model accuracy remains unverified, and the local result is not an official contest ranking.

### Spoken script

Hello, we are VNUHCM–TripleU. Our Qwen work starts with a distributed service on sixteen GPUs: choose a layout, transfer prompt state correctly, then test implementations for each phase. I will explain which improvements survived a repeat, which attractive ideas failed, and what our measurements still cannot prove. We report our own experiments on the assigned clusters; we do not present them as organiser-certified scores.

### Avoid this interpretation

Do not call the displayed work a contest win, official acceptance, or accuracy certification. The date limits the claim to this research update.

### Transition

First I will state what counts as a useful result and how to read the headline numbers.

---

<a id="slide-02"></a>

## Slide 02 — Highest observation and strongest recommendation

![Slide 02](../../submission-review/ai-journey-update-20261030/slides/assets/slide-02.png)

### Purpose

Separate the largest independently reviewed local full-pass observation from the configuration supported by repeated evidence. The slide teaches that the headline peak and the strongest recommendation need not be the same item.

### Technical interpretation and reasoning

The comparison separates the largest individual measurement from the configuration we can recommend with repeat evidence. The left result is a team-run experiment on the assigned 16-H200 cluster, not a personal computer or an organiser-scored run. The right result is the mean of three full N64 measurements. The higher recovered number in the note belongs to a job whose benchmark produced data but whose result-processing step failed; that is a different level of completion.

### Terms and symbols to understand

- **Team-measured / local result:** The team launches the benchmark on its assigned cluster and evaluates retained logs. Local describes the scope of validation, not a personal laptop or organiser approval.
- **Full run:** The campaign protocol: 60-second warmup, 120-second profiling and 30-second grace. It does not mean every quality dataset was evaluated or every request passed.
- **Reviewed pass:** The team inspects data against the checks implemented for that run: protocol, actual runtime configuration, latency/errors and small output checks. Job 27378 has smoke 7/8 without added regression and retrieval 12/12; official model accuracy is still unverified.
- **3,048.45; +0.24%:** Job 27378 measured 3048.446289 good output tokens/s, 0.240921% above control 27376. This is one observation.
- **1% useful-gain threshold:** A team-set decision rule declared before the comparison to decide which changes deserve confirmation, not an organiser scoring requirement.
- **3,044.40; N64:** Mean 3044.400475 good output tokens/s over three full runs; the client keeps up to 64 requests in flight.
- **Recovered raw 3,055.33:** The GPU benchmark saved data but the reader/summary step failed. Repairing the reader recovered 3055.330517; the original job remains FAILED.

### Interpreting the evidence or diagram

- Read 3,048.45 as one observation and 3,044.40 as a three-run mean. They are different series, not a directly matched treatment/control pair.
- Evaluate the cache change against its control 27376, not against the historical 3,044.40 mean.
- A small increase can be mixed with run-to-run variation. A higher single number does not justify replacing a repeatedly measured setup; this comparison did not exceed the team-set threshold.

### Tradeoff and strength of evidence

- **Observation:** 27378 reached 3048.446289 good output tokens/s and passed local gates; its matched cache-pair gain was 0.240921%. The historical N64 series mean is 3044.400475. Recovered portable raw data reached 3055.330517, but the originating job was FAILED.
- **Hypothesis:** A seemingly higher point should be promoted only if the change is useful under the predeclared gate and survives matched independent replication.
- **Supported conclusion:** Retain replicated N64 as the stronger recommendation. Keep 27378 as the highest reviewed local full-pass observation, not as a demonstrated useful optimization.
- **Unknown / limitation:** This slide alone does not compare the two callouts under identical runtime conditions, and the portable raw peak is not a successful end-to-end allocation result.

### Spoken script

This slide separates the largest measurement from the configuration we recommend. We ran job 27378 on the assigned sixteen-H200 cluster with 60 seconds of warmup, 120 seconds of measurement and 30 seconds of grace. The benchmark and our implemented checks completed, yielding 3,048.45 qualifying output tokens per second. But its cache change improved only 0.24% over a fresh control, below our own 1% threshold for pursuing a useful gain. We therefore retain N64, averaging 3,044.40 across three full runs: a slightly lower number with repeat evidence. These are team-measured results, not organiser-certified scores. The 3,055.33 recovered number came from a job that failed during summary processing; it is not a successful end-to-end job.

### Avoid this interpretation

Do not rank these callouts as if they were one matched experiment. The recovered 3055.33 is not a passed scheduler job or proof of a portable end-to-end repeat.

### Transition

To understand what good output tokens per second means, we need the workload and its per-request latency gate.

---

<a id="slide-03"></a>

## Slide 03 — Optimise useful throughput under a latency gate

![Slide 03](../../submission-review/ai-journey-update-20261030/slides/assets/slide-03.png)

### Purpose

Define the benchmark objective before discussing system changes: maximize qualifying service throughput while meeting both latency thresholds for enough individual requests. This prevents confusing raw generation speed or an average latency with the scoring rule.

### Technical interpretation and reasoning

Goodput rewards requests that are both completed and fast enough. A service could generate many tokens overall yet score worse if too many users wait longer than the allowed thresholds. Passing the mean latency of all requests is insufficient: first test both latency limits for each request, then count the qualifying fraction.

### Terms and symbols to understand

- **4,000 input tokens → 200 output tokens:** The fixed synthetic request shape: a 4,000-token prompt and 200 requested output tokens.
- **TTFT ↓:** Time to first token; lower is better, with a per-request limit of 3,000 milliseconds.
- **Mean ITL ↓:** Mean inter-token latency, the average interval between generated tokens in a request; lower is better, limit 20 milliseconds.
- **Joint SLA ↑:** Share of all evaluated requests that satisfy both latency limits; target is at least 90%. Errors remain in the denominator.
- **Goodput ↑:** Rate of requests that qualify under the joint gate. Multiply qualifying requests per second by 200 to report good output tokens per second.
- **ms:** Milliseconds, one thousandth of a second; a latency unit.
- **req/s × 200:** Qualifying requests per second multiplied by the requested 200 output tokens per request.

### Interpreting the evidence or diagram

- Read each arrow as the preferred direction: latency down, qualifying share and goodput up.
- Both TTFT and mean ITL limits must pass on the same request for it to count as qualifying.
- The 90% threshold applies to the proportion of all evaluated requests, not just successful requests.

### Tradeoff and strength of evidence

- **Observation:** The benchmark fixes the request size and applies a joint per-request latency rule; errors count against the service. Goodput is based on requests passing both limits.
- **Hypothesis:** A system that produces more raw tokens can still be worse if too many requests violate first-token or token-spacing requirements.
- **Supported conclusion:** We judge candidates by qualifying throughput together with the latency and output gates, not by a single mean or raw token count.
- **Unknown / limitation:** The table defines the protocol but contains no candidate measurement; it does not show any configuration's actual latency distribution.

### Spoken script

Our objective is useful throughput under a latency gate. Each synthetic request has 4,000 input tokens and asks for 200 output tokens. A request qualifies only if its time to first token is at most 3,000 milliseconds and its mean interval between tokens is at most 20 milliseconds. At least 90 percent of all evaluated requests must meet both limits; errors count against us. Goodput is qualifying requests per second, and multiplying by 200 gives the good output tokens per second used in the talk. This is why an average latency by itself cannot tell us whether the service passed: the decision is made request by request.

### Avoid this interpretation

Do not infer per-request compliance from an aggregate mean. Do not drop errors from the denominator or multiply by a different output length.

### Transition

With the objective fixed, the next slide shows why platform details must travel with every comparison.

---

<a id="slide-04"></a>

## Slide 04 — One workload, two deployment systems

![Slide 04](../../submission-review/ai-journey-update-20261030/slides/assets/slide-04.png)

### Purpose

Show the two hardware environments used for separate platform studies and establish the rule that comparisons must name the platform, topology, backend, and load. Sharing workload and model checkpoint does not make two clusters interchangeable.

### Technical interpretation and reasoning

Both platforms run the same intended model and benchmark workload, but a result also depends on GPU memory, communication, runtime and process placement. Slurm and PBS grant access to compute nodes; they are not inference engines. Containers carry the software environment, while SGLang executes the model and AIPerf sends and times requests. This separation explains why moving a configuration between clusters needs a fresh measurement.

### Terms and symbols to understand

- **2 × 8 H200:** Two nodes with eight NVIDIA H200 GPUs each, sixteen GPUs in the Firmus allocation.
- **2 × 8 H100 80GB:** Two nodes with eight 80-gigabyte H100 GPUs each on NSCC ASPIRE 2A+. This is a different GPU generation and environment.
- **Slurm / PBS:** Different cluster schedulers used to request and manage compute allocations.
- **Pyxis / native Enroot:** Firmus container-launch path. NSCC uses Singularity.
- **SGLang / AIPerf:** Serving engine and benchmark client used in the study; same staged image artifacts are used across systems.
- **Qwen3-235B FP8:** The model/checkpoint and weight precision held in common for the displayed platform setup.
- **80GB:** Nominal GPU memory capacity per H100 as shown in the table; it is not a performance unit.

### Interpreting the evidence or diagram

- Rows describe allocation, scheduler, container launcher, serving/client, and model.
- The table says the staged image artifacts and checkpoint are shared, while the GPUs and deployment software differ.
- Identify GPU, worker layout, backend, load and measurement duration for every important result; the same model name does not make two runs equivalent.

### Tradeoff and strength of evidence

- **Observation:** Both sites provide sixteen GPUs in two nodes and use the same staged serving/client artifacts and checkpoint, but hardware, scheduler and container launcher differ.
- **Hypothesis:** Matched workload and model are necessary controls, but hardware and software environment differences may still affect performance.
- **Supported conclusion:** Keep platform, topology, backend and load attached to every result; never convert an H100 score to an H200 score using hardware names alone.
- **Unknown / limitation:** This slide does not quantify the contribution of each platform difference or provide a general H100-to-H200 conversion.

### Spoken script

We used two deployment systems. Firmus has two nodes with eight H200 GPUs per node, managed by Slurm and launched with Pyxis or native Enroot. NSCC ASPIRE 2A+ has two eight-GPU H100 nodes with 80 gigabytes per GPU, PBS, and Singularity. We stage the same serving and client images and use the same Qwen checkpoint, but the machines and deployment stacks still differ. Therefore, every comparison needs its platform, topology, backend, and load. A GPU model name or memory size is not a conversion factor for performance.

### Avoid this interpretation

Do not pool H100 and H200 measurements as one series or claim equal system performance because the allocation sizes and software images match.

### Transition

Now we can look inside the selected sixteen-GPU H200 topology and follow the request through it.

---

<a id="slide-05"></a>

## Slide 05 — Separate prompt processing from token generation

![Slide 05](../../submission-review/ai-journey-update-20261030/slides/assets/slide-05.png)

### Purpose

Explain the disaggregated serving design: dedicate one node to prompt prefill and one to autoregressive decode, then transfer each request's KV state between roles. The figure links hardware placement to the later transfer and layout experiments.

### Technical interpretation and reasoning

A request is handled in two phases on different GPU groups. One of the two four-GPU prefill workers reads the prompt and produces attention KV state; NIXL transfers that state to the eight-GPU decode worker, which generates the answer. The transferred object is context state, not the entire model weights. Separating phases lets us choose different implementations for prompt processing and token generation, but adds transfer and coordination work.

### Terms and symbols to understand

- **Prefill:** The prompt-processing phase. It reads the input tokens and creates the KV state needed for generation.
- **Decode:** The token-generation phase. It produces the requested output tokens using the prompt's KV state.
- **P0 / P1 / D0:** Names for two prefill workers and one decode worker; they are worker labels, not GPU IDs.
- **TP4 / TP8:** Tensor parallelism across four or eight GPUs within the worker. TP is a model-partitioning configuration.
- **EP1 / EP8:** Expert parallelism across one or eight expert partitions for the mixture-of-experts model.
- **KV state:** Key/value attention data generated during prompt processing and required to continue decoding the same request.
- **NIXL:** The transfer mechanism used here to move KV data between the prefill and decode sides.
- **2 × 4 + 1 × 8 = 16 GPUs:** Two four-GPU prefill workers plus one eight-GPU decode worker, for sixteen GPUs total.

### Interpreting the evidence or diagram

- Read from left to right: requests are processed for prefill on either P0 or P1, then KV data moves to D0 for generated output.
- Each prefill worker is TP4/EP1; the decode worker is TP8/EP8. The TP groups stay within their node.
- Orange squares and arrows are visual role cues in this slide, not a general chart color key or evidence of traffic volume.

### Tradeoff and strength of evidence

- **Observation:** The selected layout allocates two TP4/EP1 prefill workers on Node 0 and one TP8/EP8 decode worker on Node 1; the request's KV state must cross between roles.
- **Hypothesis:** Separating prompt processing from generation can let each phase use a fitting topology, but adds a correctness- and startup-sensitive transfer path.
- **Supported conclusion:** Round-robin routes requests to a prefill worker, and decode produces all generated tokens. The diagram defines the experiment's architecture, not a measured performance benefit by itself.
- **Unknown / limitation:** The drawing does not quantify network bandwidth, transfer latency, utilization or the causal advantage over a unified deployment.

### Spoken script

This is our sixteen-GPU disaggregated layout. The left node runs two prefill workers, P0 and P1, each on four GPUs with TP4 and EP1. The right node runs one decode worker on eight GPUs with TP8 and EP8. A request is sent to one prefill worker, which processes its prompt and creates the key/value state, or KV state. NIXL transfers that request's state to the decode worker, which generates every output token. The orange squares and arrows mark the prefill side and transfer in this drawing; they do not report traffic volume. Splitting the roles gives us a topology to study, but it also makes transfer correctness and readiness part of the service.

### Avoid this interpretation

TP and EP values are specific to each worker and this configuration. Do not interpret each square as a measured GPU utilization or claim the diagram proves a speedup.

### Transition

The next slide shows how earlier topology trials led to this split, while keeping failed attempts separate from replacements.

---

<a id="slide-06"></a>

## Slide 06 — Topology search established the serving layout

![Slide 06](../../submission-review/ai-journey-update-20261030/slides/assets/slide-06.png)

### Purpose

Show a small selection of topology search results and explain that the selected split emerged from measured, usable configurations. The lower caption protects the experimental record: replacements are new configurations, not retroactive repairs of failed originals.

### Technical interpretation and reasoning

A topology is a resource layout: how many model workers exist and how many GPUs each worker shares. Changing from four smaller prefill workers to two wider workers changes both per-request work sharing and how many requests those workers can serve. The rows also use different client concurrency, so this table records useful historical layouts rather than isolating the speedup caused by one topology change.

### Terms and symbols to understand

- **07 / 09:** Identifiers for early layout trials, not software versions.
- **4 × TP2 / 2 × TP4:** Four prefill workers with tensor parallelism two; the next listed layout uses two prefill workers with tensor parallelism four.
- **TP4/EP4:** Decode workers configured with tensor parallelism four and expert parallelism four.
- **Selected split: 2 × TP4; 1 × TP8/EP8:** Two prefill workers each TP4 and one decode worker TP8/EP8.
- **N:** Client concurrency: the target number of requests kept in flight, not number of GPUs or tokens.
- **good tokens/s:** Qualifying output token throughput under the per-request latency gate.
- **14 + 3 = 17 usable configurations:** Fourteen measured original layouts plus three measured EP2 replacements in the recovery ledger.

### Interpreting the evidence or diagram

- Compare rows horizontally across role topology, concurrency N, and good output tokens per second.
- N rises from 32 to 40 to 48 across these illustrative rows; the measurements also differ in load and transport history.
- The summary counts usable measured configurations; it does not say all attempted originals passed.

### Tradeoff and strength of evidence

- **Observation:** The selected split reached 1912.30 good tokens/s at N48 in this early topology sample, after displayed N32 and N40 configurations reached 1297.02 and 1666.01. Overall, the recovery ledger counted 14 original layouts plus three EP2 replacements.
- **Hypothesis:** A balanced allocation of prefill replication and decode parallelism could better serve the chosen request concurrency.
- **Supported conclusion:** These trials established a usable architecture to develop. They are initial operating points, not a clean causal ranking because load and transport history varied.
- **Unknown / limitation:** The slide does not show all 17 configurations or confidence intervals; it cannot isolate which topology change caused the score differences.

### Spoken script

This table gives three points from the topology search. Layout 07 used four TP2 prefill workers and two TP4/EP4 decode workers; at concurrency 32 it measured 1,297 good tokens per second. Layout 09 widened prefill to two TP4 workers and reached 1,666 at concurrency 40. The selected split used two TP4 prefill workers and one TP8/EP8 decode worker, reaching 1,912 at concurrency 48. These loads and transport histories were not identical, so read them as architecture milestones, not a controlled causal sweep. Our recovery ledger contains 14 measured original layouts and three measured EP2 replacements. A replacement is a different configuration; failed originals remain failures.

### Avoid this interpretation

Do not treat 07 or 09 as software versions. Do not infer that the throughput increase was caused only by the displayed topology because N and other history differed.

### Transition

The next obstacle was not just choosing parallelism: cold request setup examined far more KV metadata than the request needed.

---

<a id="slide-07"></a>

## Slide 07 — Make KV-transfer setup scale with the request

![Slide 07](../../submission-review/ai-journey-update-20261030/slides/assets/slide-07.png)

### Purpose

Explain why cold-start KV setup was redesigned around the pages a request actually transfers. The numerical comparison is descriptor geometry, demonstrating the scale of metadata enumeration; it is deliberately not presented as an inference speedup.

### Technical interpretation and reasoning

Before sending KV bytes, the transfer layer needs a list of memory ranges to read. The original path prepared descriptions for the whole reserved KV pool; the change describes only the pages owned by the current request and merges adjacent ranges. Fewer descriptions can reduce setup work, but descriptor counts have different scopes here and do not measure transfer bandwidth or end-to-end speed. Address correctness must be checked before a smaller list can be trusted.

### Terms and symbols to understand

- **KV pool:** The full allocated key/value cache address space available to a rank, much of which a particular request will not transfer.
- **403.8 million source entries per rank:** Approximate count of descriptor source entries enumerated for the whole-pool geometry in a representative TP8 case.
- **188 coalesced entries per request:** Number of contiguous descriptor ranges after combining adjacent request pages in the illustrated 4,000-token request geometry.
- **rank:** One distributed model process/partition participating in the parallel deployment; not a server rank in a competition.
- **descriptor:** Metadata that describes memory ranges to a transfer layer; it is not the KV tensor contents themselves.
- **coalescing:** Combining adjacent memory ranges into fewer larger range descriptions.
- **CPU range tests → GPU transfer → response checks:** The layered validation path: check address calculations, then actual transfer, then request response semantics.

### Interpreting the evidence or diagram

- The left count describes whole-pool source enumeration per rank; the right count describes coalesced ranges for one request. Their scopes differ.
- The values are descriptor counts, with no seconds, bytes-per-second, or score unit on the slide.
- Read the bottom sequence as successive evidence gates. A correct CPU mapping alone is insufficient; real GPU transfer and response checks follow.

### Tradeoff and strength of evidence

- **Observation:** Cold disaggregated serving stalled during whole-pool KV descriptor preparation. A request-scoped implementation constructs ranges for only the pages actually transferred and coalesces contiguous ones; the shown TP8 example is about 403.8 million pool entries versus 188 entries for one request.
- **Hypothesis:** Enumerating request pages rather than the full pool should reduce setup work and improve readiness without changing the request's KV mapping.
- **Supported conclusion:** Range correctness was checked on CPU, then the path was tested with real GPU transfer and response validation. A later EP2 route with superficially successful execution still failed short-output checks, so startup success is necessary but not sufficient.
- **Unknown / limitation:** Descriptor counts do not measure wall-clock startup speed, inference throughput, memory savings, or a 2-million-fold speedup. The diagram's geometry example is not a universal ratio for every request/topology.

### Spoken script

Our cold-start investigation found that KV transfer setup was enumerating descriptors for the whole cache pool, although one request touches only a fraction of it. In a representative TP8 geometry, that meant about 403.8 million source entries per rank, compared with 188 coalesced range entries for one 4,000-token request. These are counts of transfer descriptions, not measurements in seconds and not a two-million-fold inference speedup. We changed setup to describe only the pages the request needs and combine adjacent ranges. We validated the mapping on CPU, then checked a real GPU transfer and response behavior. One later EP2 route looked as though it ran, yet produced too few valid responses. That taught us that efficient setup and successful transfer still do not prove correct service output.

### Avoid this interpretation

Do not divide the counts and call the result an inference speedup. The count scopes differ, and the figure does not report latency or throughput. Do not equate a transfer that completes with a valid response.

### Transition

That EP2 recovery also exposed a different prerequisite: the FP8 weight blocks must align with the model partition.

---

<a id="slide-08"></a>

## Slide 08 — FP8 block geometry constrains parallelism

![Slide 08](../../submission-review/ai-journey-update-20261030/slides/assets/slide-08.png)

### Purpose

Explain a concrete deployment failure caused by FP8 block alignment and the geometric change used to recover a compatible partition. The key learning is that compatibility permits a load attempt but does not establish successful service or quality.

### Technical interpretation and reasoning

The failing implementation requires each weight shard to contain whole FP8 blocks. Dividing the relevant dimension by eight leaves 192 elements: one complete 128-element block plus a 64-element remainder. In this tested TP8/EP2 path the effective MoE tensor split is four, giving 384 elements or three complete blocks. EP2 changes expert distribution; it does not halve the model or reduce numerical precision further.

### Terms and symbols to understand

- **FP8:** Eight-bit floating-point weight format used by the checkpoint; weights are organized into fixed-width blocks for the relevant kernel path.
- **1,536:** MoE intermediate dimension used in this partition calculation.
- **128:** FP8 block width in this implementation path; a full compatible chunk contains 128 elements.
- **TP8 / EP1:** Eight-way tensor parallelism with one expert partition; effective MoE tensor parallelism is eight, giving 1536 ÷ 8 = 192 elements per partition.
- **128 + 64:** The 192-element partition contains one full 128-element block plus a 64-element remainder, which is not a whole FP8 block.
- **TP8 / EP2:** Eight-way tensor parallelism with two expert partitions; effective MoE tensor parallelism is four, giving 1536 ÷ 4 = 384 elements.
- **3 × 128 = 384:** The EP2 partition maps to three complete 128-element blocks. This changes the layout; it does not drop experts or weights.
- **SLA:** Service-level agreement: the joint request latency acceptance rule defined earlier.

### Interpreting the evidence or diagram

- Read both equations before the blocks: 1536 ÷ 8 = 192 and 1536 ÷ 4 = 384.
- Left blocks show 128 plus 64; the red remainder marks a partial block and load failure in the tested path.
- Right blocks show three complete 128 chunks. The footer lists additional required checks: startup, SLA, and output quality.

### Tradeoff and strength of evidence

- **Observation:** A TP8/EP1 prefill partition gives 192 elements, which is 128 plus 64 and does not align to 128-wide FP8 blocks. With EP2, effective MoE tensor parallelism is four and each partition has 384 elements, or three full blocks.
- **Hypothesis:** Changing expert partitioning can make the tensor shape compatible with the kernel's FP8 block requirement while retaining all model weights and experts.
- **Supported conclusion:** The EP2 replacement corrected the tested block geometry and enabled a compatible deployment attempt. It is a combined layout change, not an isolated TP speedup; compatibility is only a necessary precondition.
- **Unknown / limitation:** Alignment alone does not prove startup success, request-level SLA, output quality, or performance gain. The figure is a shape calculation rather than a measured throughput comparison.

### Spoken script

Here is why one prefill configuration failed before performance measurement. The model's MoE intermediate dimension is 1,536 and this FP8 path expects blocks of 128 elements. With TP8 and EP1, each partition gets 1,536 divided by 8, or 192 elements. That leaves one full 128-element block plus a remainder of 64, so the kernel cannot load the partial block. With TP8 and EP2, the effective MoE tensor parallelism is four. Each partition has 384 elements, exactly three blocks of 128. This keeps the weights and experts; it changes how the model is partitioned. The right side therefore shows compatible geometry, not a performance win. Startup, service latency, and output quality still need their own checks.

### Avoid this interpretation

The red 64 is a leftover portion of a weight partition, not 64 GPUs or tokens. EP2 changes the configuration, so do not describe this as an isolated tensor-parallel speedup or as a throughput result.

### Transition

With the deployment path made workable, the next slide lays out how we turn each such explanation into a controlled experiment.

---

<a id="slide-09"></a>

## Slide 09 — A repeatable experiment loop

![Slide 09](../../submission-review/ai-journey-update-20261030/slides/assets/slide-09.png)

### Purpose

Describe the evidence discipline used to decide which ideas deserve a run and which should be closed. It connects the early engineering stories to the later measured backend results and makes the full measurement phases explicit.

### Technical interpretation and reasoning

The loop prevents a plausible idea from becoming a performance claim too early. Write down the proposed cause, preserve a reference configuration, change the intended factor, check that the intended code actually ran and outputs remain valid, then compare the score. Repeat a useful gain before selecting it. A run that ends with an error teaches us about integration, but does not become a valid performance measurement.

### Terms and symbols to understand

- **01–04:** Sequence numbers for the four experimental stages, not scores or job IDs.
- **60 s warmup:** A one-minute measured-protocol warmup before the scoring window.
- **120 s measurement:** Two-minute scoring window for the shown full measurement protocol.
- **30 s grace:** A settling interval after measurement for in-flight requests to finish; not another steady-state scoring period.
- **closed loop:** A client keeps the target number of requests in flight, replacing completed requests.
- **4,000 / 200 tokens:** Fixed input and requested output sizes for the workload described earlier.
- **SLA accounting:** Evaluating latency and success for each request, including failed requests in the denominator.

### Interpreting the evidence or diagram

- Stage 1 uses logs, traces and source to formulate a hypothesis; stage 2 changes one defined factor.
- Stage 3 checks protocol, runtime activation, SLA and output; stage 4 confirms useful gains or closes losing branches.
- The times below are seconds, not milliseconds. The 120-second window is the measurement phase.

### Tradeoff and strength of evidence

- **Observation:** The retained workflow keeps the benchmark protocol and output/runtime gates visible, and distinguishes a terminal job from a reviewed valid result.
- **Hypothesis:** A bounded change with a control and stopping rule should yield more interpretable evidence than broad or repeated blind sweeps.
- **Supported conclusion:** Candidates need actual activation checks and independent replication before promotion; a run without valid export or passing gates does not establish a result.
- **Unknown / limitation:** The diagram is a process summary; it does not show any particular trial, cost, failure rate, or replication statistics.

### Spoken script

Our loop has four steps. First, use logs, traces, and source to form a hypothesis. Second, change a defined factor against a control. Third, validate that the intended setting actually ran, then check the protocol, request-level SLA, and output. Finally, repeat a useful gain independently or close the branch. The full protocol shown here uses 60 seconds of warmup, 120 seconds of measurement, and a 30-second grace period for outstanding requests. The grace period is not more scored steady state. This discipline helped us keep failed runs, distinguish terminal status from a valid result, and stop changes that were real but too small to justify promotion.

### Avoid this interpretation

A four-step diagram is not evidence that every historical experiment followed an identical protocol. Cite each result's actual protocol and job record.

### Transition

Now I will use that evidence framework to summarize the H200 progression, while warning that it is not one cumulative experiment.

---

<a id="slide-10"></a>

## Slide 10 — H200 journey: recover, specialise, then reproduce

![Slide 10](../../submission-review/ai-journey-update-20261030/slides/assets/slide-10.png)

### Purpose

Give a historical overview of measured H200 goodput as the serving system recovered and acquired phase-specific backends, then reached repeated operating points. This is orientation for the detailed evidence on the following slides, not a causal ablation plot.

### Technical interpretation and reasoning

Read the bars as a history of operating points, not a single experiment in which one optimization is added at each step. The horizontal categories change layout, backend and client concurrency; the vertical value is latency-qualified output tokens per second. The rise shows the campaign found better measured configurations, but does not assign a causal contribution to each named change.

### Terms and symbols to understand

- **H200:** The GPU platform used for these milestones; do not combine these values with H100 results.
- **x-axis milestones and N:** Categorical experiment stages and client concurrency values, not elapsed time or a continuous independent variable. N is target in-flight requests.
- **y-axis: Good output tokens/s:** Qualifying output-token throughput under the joint latency gate; the plotted labels are rounded.
- **FI:** FlashInfer, the attention backend in the named stage.
- **MNNVL:** The collective/communication backend used in the decode-side combination.
- **DG:** DeepGEMM, used for prefill in the named milestones.
- **HPC:** HPC-Ops decode backend in the “DG + HPC” milestone.
- **N60 / N62 / N64 repeated:** Later full operating points with repeated observations; N64's 3,044 bar summarizes three historical full runs.

### Interpreting the evidence or diagram

- Read the x-axis as a sequence of named historical milestones; it does not encode calendar time or equal intervals.
- Read the y-axis in good output tokens per second, increasing upward; each label is a rounded score.
- Gray, teal, and orange distinguish broad thematic groups in this chart only. The bars do not indicate pass/fail.
- The footer warns that load and runtime settings vary between stages, so a taller later bar is not by itself a causal effect.

### Tradeoff and strength of evidence

- **Observation:** The historical chart moves from early layouts at N32–N48 to backend specialization and later repeated N60, N62, and N64 operating points. Its N64 label, 3,044, is a rounded mean of three historical full runs.
- **Hypothesis:** After recovering a usable split and transfer path, tuning phase-specific attention, collective, and prefill backends could improve qualifying throughput.
- **Supported conclusion:** The chart documents research progression and points to later matched comparisons and replication; it is useful as a map of milestones, not evidence for one monotonic cumulative gain.
- **Unknown / limitation:** Loads, runtime settings, and historical observation conditions change. The chart cannot attribute the total rise to one change, establish statistical uncertainty, or identify a global optimum.

### Spoken script

This chart is a map of the H200 research journey, not one cumulative ablation. The horizontal axis lists categorical milestones and their client concurrency N, from initial layouts at N32 and N40 through the selected split at N48, backend work, and later N60, N62, and N64 points. N means target requests kept in flight; it is not elapsed time. The vertical axis is good output tokens per second. We recovered the split, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, and later tested HPC-Ops decode. N60, N62, and N64 have repeated evidence, with the N64 bar rounded to 3,044 from three historical full runs. The groups use gray, teal, and orange as thematic stages only. Loads and runtime settings changed, so the rising bars do not show that each change caused the entire increase.

### Avoid this interpretation

The x-axis is categorical, not time. Do not interpolate between milestones or interpret color as a pass/fail legend. Do not describe the bars as a causal ablation or a global optimum.

### Transition

The next slide zooms into one more controlled comparison: attention and collective backend combinations at the same H200 load.

---

<a id="slide-11"></a>

## Slide 11 — Backend combinations matter

![Slide 11](../../submission-review/ai-journey-update-20261030/slides/assets/slide-11.png)

### Purpose

Introduce the first detailed backend interaction result: a combined attention and collective configuration outperformed the individual choices in a same-load H200 N52 comparison. The design lesson is to measure interactions directly rather than add separate gains arithmetically.

### Technical interpretation and reasoning

An attention backend performs the attention calculation; a collective backend moves or combines information among cooperating GPU processes. They share GPU execution and communication resources, so changing both can interact. The fresh MNNVL-only measurement is a renewed reference before judging the combination. The combination is measured directly: its benefit is not calculated by adding gains from separate trials.

### Terms and symbols to understand

- **H200 · N52:** The GPU platform and client concurrency for the displayed comparison. N52 means a target of 52 in-flight requests.
- **FlashInfer decode only:** The decode attention path uses FlashInfer while collective configuration remains at its comparison setting.
- **MNNVL decode only:** The decode collective/communication path uses MNNVL without the FlashInfer combination shown in the last row.
- **MNNVL fresh control:** A later fresh control measurement at the MNNVL setting, used to reduce reliance on an older comparison point.
- **MNNVL + FlashInfer:** The combined backend choice measured directly in job 23904.
- **good tokens/s:** Qualifying output tokens per second under the request-level latency gate.
- **SLA:** Percentage of requests satisfying both TTFT and mean ITL limits; the displayed values are local measurements.
- **job:** Scheduler record identifier linking a row to its run evidence; not a ranking.

### Interpreting the evidence or diagram

- Compare 23777 (2,440.39), 23778 (2,592.16), and combo 23904 (2,631.09) as exploratory same-load evidence.
- The fresh MNNVL control 23974 reaches 2,594.03, giving the more relevant comparison to the combo; the difference is about 1.43%.
- All displayed SLA values are percentages. The table itself has no axes; row order does not imply time or a statistical ranking.

### Tradeoff and strength of evidence

- **Observation:** At H200 N52, standalone FlashInfer decode measured 2440.386 good tokens/s; MNNVL decode measured 2592.162; fresh MNNVL control 2594.028; the combination measured 2631.085. Against the fresh control, the combo is about 1.43% higher, with SLA values near 99%.
- **Hypothesis:** Attention-kernel choice and collective choice may interact, so their combined service performance should be tested as a configuration rather than predicted by adding isolated improvements.
- **Supported conclusion:** The combo provides a promising operating point and supports measuring attention plus communication tuning together. Later runtime checks and repeats add evidence, but this table alone is not a universal backend rule.
- **Unknown / limitation:** The small gain and listed single observations do not establish a broad causal effect, confidence interval, or that component gains add linearly. Full official model accuracy is not represented by SLA.

### Spoken script

This table compares backend choices on H200 at client concurrency N52. FlashInfer decode alone reached about 2,440 good tokens per second. MNNVL alone measured about 2,592, and a fresh MNNVL control measured 2,594. The directly measured combination of MNNVL and FlashInfer reached about 2,631, around 1.43 percent above that fresh control in these observations. The request-level SLA values are all close to 99 percent. The lesson is not that the separate gains add up. Attention and collective operations interact, so we measured their combination as its own configuration. Later activation checks and repeats support this operating range, while this table by itself does not make a universal claim about every workload or backend.

### Avoid this interpretation

Do not calculate a predicted combined score by adding the two standalone changes. These are not repeated distributions, and latency SLA is not model-accuracy certification.

### Transition

The following slides test these backend observations more deeply, including profile evidence and a matched repeat of the N60 treatment.

---

<a id="slide-12"></a>

## Slide 12 — H200: the N62-to-N64 step survives a full repeat

![Slide 12](../../submission-review/ai-journey-update-20261030/slides/assets/slide-12.png)

### Purpose

Show why the team selected N64: a full comparison and an independent repeat support a modest gain, while a promising short N68 screen did not survive full measurement.

### Technical interpretation and reasoning

The left column is the N62 control, the middle is the first full N64 run, and the right is a new N64 deployment. Compare the goodput row first, then check that request acceptance, latency, and errors do not contradict the throughput gain.

### Terms and symbols to understand

- **N62/N64:** Configured client concurrency; not GPU count or decode batch size.
- **Good tokens/s:** Qualifying requests per second multiplied by the fixed 200-token output target.
- **Joint SLA:** Share of requests meeting both TTFT ≤ 3,000 ms and request-mean ITL ≤ 20 ms.
- **60/120/30:** Warmup seconds / scored seconds / grace seconds.
- **N68:** Higher-concurrency screen whose gain shrank in the full pair.
- **Full 60/120/30 protocol:** Warm the service for 60 seconds, score requests for 120 seconds, then allow 30 seconds for in-flight requests to finish. The grace period is not scored throughput.
- **Independent deployment repeat:** A newly scheduled deployment/run of the same N64 setting. It is a repeat allocation, not proof of different GPU hardware; both N64 runs sampled the same GPU UUID set.
- **N62 / N64 / N68:** Client in-flight concurrency settings, not GPU counts or decode batch sizes.

### Interpreting the evidence or diagram

- Independent N64 deployment 25373 repeats at 3,044.075, only 0.014% below the source. Read columns in order: goodput, joint SLA, mean TTFT, mean ITL, errors/cancellations. N64's higher throughput trades against slightly higher mean TTFT and a small SLA decline. The full protocol is 60 seconds warmup, 120 scored, 30 grace. A short N68 screen suggested +2.27%, but its full pair narrowed to +0.083%; short screens are triage, not final evidence. The repeated N64 pair reused sampled GPU UUIDs, so it supports a local repeatability claim, not a confidence interval or global optimum. Hypothesis: moderate client concurrency improves pipeline utilization. Supported conclusion: keep reproduced N64 at this operating point. Unknown: separate queue, transfer and compute causes, other loads, and global optimum.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- The full-run label refers to a fixed protocol: 60 seconds to warm the service, 120 seconds of scored requests, and 30 seconds of grace so outstanding requests can finish. A repeat allocation means the scheduler launched another run; it does not mean different GPU architecture. Here both N64 runs sampled the same GPU UUID set, so the repeat supports reproducibility of this setting but not hardware diversity or a confidence interval.

### Tradeoff and strength of evidence

- **Observation:** N64 gains 1.083% and repeats within 0.014%; TTFT rises modestly and SLA dips slightly.
- **Hypothesis:** Moderately higher client concurrency may improve pipeline use.
- **Supported conclusion:** Keep reproduced N64 at this measured point.
- **Unknown / limitation:** Queue, transfer, compute contributions and global optimum remain unknown.

### Spoken script

“N62 produced about 3,012 good output tokens per second. N64 reached about 3,044, and an independent deployment repeated almost exactly. That is a roughly 1.08 percent full-protocol gain. Mean TTFT rose modestly and ITL stayed near 15 milliseconds. The short N68 screen looked better, but its full result nearly disappeared. We keep N64 because the full comparison and repeat support it, without calling it globally optimal.”

### Avoid this interpretation

Keep units and configuration attached; do not state a hypothesis as a measured cause.

### Transition

“Next we use traces to choose diagnostic questions.”

---

<a id="slide-13"></a>

## Slide 13 — Profile the deployed interaction

![Slide 13](../../submission-review/ai-journey-update-20261030/slides/assets/slide-13.png)

### Purpose

Explain how profiling generates the next testable question, while keeping diagnostic kernel shares separate from end-to-end service performance.

### Technical interpretation and reasoning

Read each percentage as that named kernel group's portion of all recorded kernel duration in the separate diagnostic traces. The percentages are not slices of request wall time: GPU kernels can overlap, while request wall time also includes queueing and other unprofiled work. Use the rows to choose a test, not to estimate its speedup.

### Terms and symbols to understand

- **GEMM:** General matrix multiplication used in compute kernels.
- **MNNVL:** NVIDIA NVLink communication backend.
- **RMSNorm:** Root mean square normalization operation.
- **Kernel duration:** Recorded GPU-kernel time; not end-to-end wall time.
- **N48/N58:** Separate diagnostic and repeated deployment concurrency settings.
- **Profile:** A diagnostic run that records selected GPU kernel timings and other runtime signals while serving a workload.
- **Kernel-time share:** A named group's fraction of summed recorded kernel durations. GPU kernels can overlap, so this is not its fraction of elapsed request walltime.
- **N48 diagnostic vs N58 repeat:** Separate stages in job 24819: N58 repeats a deployment; N48 collects profile traces. Do not attribute N48 kernel shares to N58 service behavior.
- **MNNVL / RMSNorm:** MNNVL is the NVLink collective communication path; RMSNorm normalizes model activations.

### Interpreting the evidence or diagram

- Named decode groups are HPC group GEMM 21.642%, MNNVL collective/RMSNorm 23.479%, and FlashInfer paged attention 15.064% of summed recorded kernel duration. These percentages are descriptive sums, not shares of end-to-end wall time: kernels can overlap and the trace covers only recorded activity. Terms: GEMM is matrix multiplication; MNNVL is a communication backend; RMSNorm normalizes hidden activations; rank is one distributed process. The three groups suggest questions about MoE implementation, communication strategy, and phase-specific attention backend. They do not predict equivalent speedups, prove FLOP saturation, or causally explain N58/N60 service results. Keep the N48 diagnostic distinct from the N58 repeat. Hypothesis: large recorded groups deserve follow-up. Conclusion: use traces to design a controlled full-service test. Unknown: per-request phase attribution and causal latency shares.
- A profile is instrumentation: it records selected activity while a workload is running. The percentages sum kernel durations across recorded ranks/GPUs. Because kernels overlap and because queueing, CPU work, communication gaps, and unrecorded activity also consume elapsed time, those percentages cannot be read as the fraction of a request spent in each component. The N48 diagnostic was separate from the N58 deployment repeat.

### Tradeoff and strength of evidence

- **Observation:** Three named groups account for stated shares of recorded kernel duration.
- **Hypothesis:** Large recorded groups may guide next experiments.
- **Supported conclusion:** Use profile as a hypothesis source, not an end-to-end explanation.
- **Unknown / limitation:** Wall-time shares, overlap effects, FLOP saturation and causality are unknown.

### Spoken script

“These profile percentages help point to follow-up questions. They are summed kernel durations in a separate N48 diagnostic, not fractions of request wall time. Kernels may overlap. We use the trace to choose a controlled experiment, not to claim the same percentage as an achievable speedup.”

### Avoid this interpretation

Keep units and configuration attached; do not state a hypothesis as a measured cause.

### Transition

“A separate full N60 comparison tests a backend interaction.”

---

<a id="slide-14"></a>

## Slide 14 — The N60 gain survives an independent deployment

![Slide 14](../../submission-review/ai-journey-update-20261030/slides/assets/slide-14.png)

### Purpose

Demonstrate a repeatable backend tradeoff: improved useful throughput and token gaps can coexist with worse first-token delay.

### Technical interpretation and reasoning

Compare the control and treatment at the same N60 load. Throughput rises and token gaps shrink, but the first token arrives later on average. This is a service-level tradeoff measured in a fresh deployment, not a claim about every use of the backend.

### Terms and symbols to understand

- **HPC-Ops:** The supplied decode runner tested here; this work evaluates it, not claims authorship of it.
- **DeepGEMM:** Prefill matrix multiplication backend held fixed.
- **TTFT:** Time to first token, in milliseconds.
- **ITL:** Inter-token latency; here request-mean intervals.
- **N60:** Configured client concurrency for this full comparison.
- **Independent repeat:** A separate fresh deployment that repeats the treatment. It confirms a similar score under this setup but does not mean a different hardware generation.
- **TTFT / request-mean ITL:** Time until the first output token / average time between output tokens within one request.
- **Goodput:** Here, qualifying AIPerf requests per second × fixed target of 200 output tokens.
- **Full protocol 60/120/30:** 60 seconds of warmup, 120 seconds of scored serving, then 30 seconds for outstanding requests to finish; only the middle interval contributes score.

### Interpreting the evidence or diagram

- Both hold DeepGEMM prefill and chunk 8192 at full N60. Mean TTFT rises 125.335 ms (822.292 to 947.627), while mean request-mean ITL falls 1.644 ms (16.579 to 14.934). Joint SLA is 98.7599% versus 98.8178%. Original treatment 24738 scored 2,990.151; repeat 24913 is 0.033% lower. The close repeat supports reproducibility of this interaction. HPC-Ops is a provided backend, not a team-invented kernel. Terms: TTFT is time to first token; ITL is inter-token interval; joint SLA requires both limits. Conclusion: local full-service evidence supports this setup, not universal HPC-Ops superiority. Official full-set quality remains unverified; no exact kernel cause follows.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- “Independent deployment” means another fresh scheduled run of the same treatment, not an experiment on another GPU generation. The repeat at 2,989.175 is 0.033% below original treatment 24738 at 2,990.151. It supports a repeat at this operating point. The higher goodput does not erase the increase in mean TTFT; a service choice can trade first-token delay against the time between subsequent tokens.

### Tradeoff and strength of evidence

- **Observation:** Goodput rises 5.295%, ITL falls, mean TTFT increases 125.335 ms; treatment repeat is close to original.
- **Hypothesis:** Decode backend interaction may improve useful throughput at N60.
- **Supported conclusion:** Evidence supports this matched configuration, not universal backend superiority.
- **Unknown / limitation:** Exact kernel cause and official full-set quality remain unknown.

### Spoken script

“Goodput rises about 5.30 percent, and the treatment repeat is nearly identical to the original. But first-token latency gets about 125 milliseconds worse while ITL improves. This is a reproduced tradeoff at N60, not a universal backend claim.”

### Avoid this interpretation

The down arrow beside TTFT states the desired direction; actual TTFT rises in this pair. Do not say every latency metric improved or that the team invented HPC-Ops.

### Transition

“The next plot shows request-level misses rather than averages.”

---

<a id="slide-15"></a>

## Slide 15 — The reproduced N64 service still loses first-token tails

![Slide 15](../../submission-review/ai-journey-update-20261030/slides/assets/slide-15.png)

### Purpose

Teach the audience to inspect individual requests: high average performance can hide first-token tail failures, and averages alone do not explain their cause.

### Technical interpretation and reasoning

Read one point as one request, not one token. A point is accepted only when it lies left of the red vertical TTFT threshold at 3,000 ms and below the red horizontal request-mean ITL threshold at 20 ms. Dark teal (#23373B; can appear blue-green) marks requests meeting both; orange (#EB811B; can appear yellow) marks requests missing at least one. The pale green band marks TTFT only, not joint acceptance. Darker clusters show alpha overlap, not a third request class.

### Terms and symbols to understand

- **TTFT:** Request start to first generated token, milliseconds.
- **Request-mean ITL:** Average interval between consecutive generated tokens for one request; it is not the same as end-to-end request latency.
- **Joint pass:** Both limits apply to the same request. A request under the TTFT line can still fail if it is above the ITL line.
- **Good/all:** 1,875 joint passes divided by all 1,902 requests.
- **Alpha overlap:** Overlapping points render darker; darkness is not another outcome class.
- **Native runtime:** The server's native execution path used by job 26766, distinct from the portable replay path. It describes software execution, not a different GPU model.
- **P95:** The 95th percentile: 95% of observed requests are at or below this value; it describes a tail, not the mean.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- X is TTFT in milliseconds; Y is per-request mean ITL. Red vertical and horizontal lines mark 3,000 ms and 20 ms. A request passes only if it is left of and below both lines. Dark teal (#23373B; may look blue-green) marks joint passes; orange (#EB811B; may look yellow) marks requests missing at least one condition. The pale green region represents TTFT only and does not certify the ITL condition. Darker clusters are alpha overlap, not a third class. Result: 1,875/1,902, or 98.580%, jointly pass; 27 miss TTFT, zero miss ITL, zero request errors/cancellations. Mean/p95 TTFT is 1,108.869/1,311.693 ms; mean/p95 ITL is 15.0075/15.1930 ms. All misses begin within 13.004 ms of profiling admission, an association only. Hypothesis: an initial-cohort effect may contribute. Conclusion: all observed SLA misses are TTFT-only in this run. Unknown: causation and queue/prefill/transfer/compute decomposition.
- Moving left means shorter first-token delay; moving down means shorter mean token gaps. The acceptable region is on or left of x = 3000 AND on or below y = 20; equality passes. Orange points are larger only to make failures easier to see, not because they have larger requests or token counts.
- This is a distribution of individual requests from one run, not a Pareto frontier of competing configurations. It cannot decompose queueing, prefill computation, transfer and decode time.
- This is a profile of requests from the native server runtime, not a synthetic kernel benchmark. TTFT measures the wait until the first token; request-mean ITL summarizes intervals after generation begins. P95 describes the slower tail. The 27 misses began within 13.004 ms after profile admission, but that timing alone cannot say whether queueing, prefill, KV transfer, or compute caused them.

### Tradeoff and strength of evidence

- **Observation:** 1,875/1,902 jointly pass; 27 miss TTFT only and no request errors occur.
- **Hypothesis:** An initial-cohort effect may contribute to TTFT misses.
- **Supported conclusion:** The observed miss type is precisely TTFT-only in this run.
- **Unknown / limitation:** Admission timing is association, not proof; phase-level causes are unresolved.

### Spoken script

“Each dot is one request. It passes only left of 3,000 ms TTFT and below 20 ms ITL. Teal passes both, orange misses at least one. There are 1,875 passes from 1,902; all 27 misses are TTFT-only. Their timing near admission motivates investigation, but does not prove startup caused them.”

### Avoid this interpretation

The green band marks TTFT only. Do not treat it as the joint pass region; every request stays in the denominator.

### Transition

“We now treat H100 as a separate operating point.”

---

<a id="slide-16"></a>

## Slide 16 — H100 has its own operating point and uncertainty

![Slide 16](../../submission-review/ai-journey-update-20261030/slides/assets/slide-16.png)

### Purpose

Keep the H100 operating point, backend settings and repeat variation separate from H200 claims.

### Technical interpretation and reasoning

The historical high and the fresh full control answer different questions: one is the best retained individual observation; the other is a new complete run with its own acceptance result. H100 uses different prefill/decode settings from H200, so these numbers cannot isolate a hardware-generation effect.

### Terms and symbols to understand

- **H100/H200:** Distinct accelerator systems with separately measured operating points.
- **N54:** Configured client concurrency in the H100 comparison.
- **TP8:** Tensor parallelism across eight GPUs.
- **EP8:** Expert parallelism across eight partitions.
- **Chunk 4096:** Configured prefill chunk size on this H100 setup.
- **Allocation:** One scheduler-granted resource assignment and run. Allocation counts are repeat counts, not counts of unique GPU models or necessarily unique physical devices.
- **Retained individual peak:** Highest single observation preserved in the cited historical series; it is not a fresh control or a distribution estimate.
- **TP8 / EP8:** Tensor parallelism spans eight GPUs; expert parallelism distributes experts across eight partitions.
- **Operating point:** A result attached to a particular hardware, software, load, and backend configuration.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- Fresh full control 225227 reached 2,399.186728 with 98.015873% joint SLA and zero errors/cancellations. H100 uses HPC-Ops for prefill and decode, chunk 4096, TP8/EP8; H200 uses DeepGEMM prefill and chunk 8192. Thus these values are not a matched hardware comparison or multiplier. Retain both peak and fresh control: they answer different questions. TP means tensor parallelism; EP means expert parallelism. A functional EAGLE transport response is not an accepted aggregate performance result. Hypothesis: hardware families require their own settings. Conclusion: report a distinct H100 point with its actual configuration. Unknown: cross-generation causal effect and universal conversion.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- An allocation is a scheduled run/resource assignment, whereas H100 versus H200 is a hardware-family distinction. A retained maximum is one observed run; a fresh control is a new complete observation. Since the H100 setup uses HPC-Ops for both phases and a 4,096-token chunk, while H200 uses a different prefill backend and 8,192-token chunk, the values cannot be divided to obtain a GPU-generation multiplier.

### Tradeoff and strength of evidence

- **Observation:** Historical individual peak exceeds fresh full control; settings differ from H200.
- **Hypothesis:** Hardware families may need separate configurations.
- **Supported conclusion:** Report H100 as its own operating point.
- **Unknown / limitation:** No matched cross-generation effect or universal multiplier is established.

### Spoken script

“The historical H100 peak is about 2,433, while a fresh full N54 control is about 2,399 and passes 98.016 percent of joint latency checks. The H100 recipe differs from H200, so these are separate observations, not a hardware conversion experiment.”

### Avoid this interpretation

Keep units and configuration attached; do not state a hypothesis as a measured cause.

### Transition

“Within H100, one decode-attention change tests whether faster first token improves the whole request.”

---

<a id="slide-17"></a>

## Slide 17 — FA3: faster first token does not guarantee goodput

![Slide 17](../../submission-review/ai-journey-update-20261030/slides/assets/slide-17.png)

### Purpose

Use a losing FA3 decode trial to explain why optimizing first-token latency alone can reduce the final throughput objective.

### Technical interpretation and reasoning

FA3 lowers the time to the first token, but its longer average token interval compounds across a long output. Read the measured mean request latency and goodput rows as the end-to-end decision; do not select a backend from TTFT alone.

### Terms and symbols to understand

- **FlashInfer:** Control decode-attention backend.
- **FA3:** Treatment decode-attention backend; prefill remains FA3.
- **Goodput:** Qualifying output tokens per second.
- **Request latency:** End-to-end request duration, including generation.
- **Matched pair:** Full runs differing only in the intended decode attention factor.
- **Mean request latency:** Average end-to-end duration for a request, including first-token wait and the remaining output generation.
- **Why TTFT can mislead:** A reduction before the first token may be outweighed by a small per-token slowdown repeated over a long response.
- **Matched change:** Only decode attention changes in this H100 N54 pair; prefill remains FA3 in both conditions.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- FlashInfer versus FA3: good tokens/s 2,420.945 vs 2,401.284; mean TTFT 713.199 vs 594.276 ms; mean ITL 18.214 vs 18.988 ms; mean request latency 4,337.853 vs 4,372.813 ms. FA3 saves 118.922 ms to first token, but ITL increases 0.773 ms; over about 199 intervals that adds roughly 154 ms. Mean request latency rises and goodput falls 0.812%. Keep FlashInfer for this decode setting; FA3 remains the prefill backend. One pair cannot rank backends universally or identify exact kernel causality.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- The measured mean request latency rises by 34.960 ms (4,372.813 − 4,337.853), and goodput falls 0.812%. The ITL change is small per gap but repeats over a long response; this is a plausible interpretation of the tradeoff, not a separately isolated kernel-level causal measurement. The comparison supports keeping FlashInfer only for this tested H100 decode setting.

### Tradeoff and strength of evidence

- **Observation:** FA3 reduces TTFT but worsens ITL/request latency and loses 0.812% goodput.
- **Hypothesis:** Attention choice shifts startup and per-token costs differently.
- **Supported conclusion:** Keep FlashInfer for this decode setting; retain FA3 prefill.
- **Unknown / limitation:** One pair cannot rank backends generally or identify exact kernel causality.

### Spoken script

“FA3 lowers TTFT, but token intervals widen. Across the output those intervals outweigh the initial saving: request latency rises and goodput falls. We keep FlashInfer for this decode configuration.”

### Avoid this interpretation

Keep units and configuration attached; do not state a hypothesis as a measured cause.

### Transition

“Next we assess a startup cost change using a predeclared gate.”

---

<a id="slide-18"></a>

## Slide 18 — Test the cost hypothesis, then reverse the order

![Slide 18](../../submission-review/ai-journey-update-20261030/slides/assets/slide-18.png)

### Purpose

Show the value of reversing trial order and enforcing a predeclared promotion gate rather than selecting a favorable first result.

### Technical interpretation and reasoning

Compare the second pair after reversing which condition ran first. The first pair's 18.74% walltime saving does not reproduce: the reverse-order pair saves 9.84%, below the predeclared 10% threshold. Scheduler walltime includes startup and cleanup, so it is not the same metric as steady-state goodput.

### Terms and symbols to understand

- **Read-first:** Read the prefill checkpoint before the measured service run to test a startup-cost hypothesis.
- **Walltime:** Scheduler-measured runtime in seconds.
- **Reverse order:** Confirmation that runs the pair in the opposite sequence.
- **Cost gate:** Predeclared requirement of at least 10% walltime saving.
- **Goodput change:** Change in qualifying throughput relative to the paired control.
- **Scheduler walltime:** Elapsed allocation time includes startup and cleanup; it is distinct from the 120-second scored serving window and from goodput.
- **Cold prefix vs cold OS cache:** A cold prefix means the prompt prefix is not reused from the model's prefix/KV cache. A cold OS page cache means file data is not already cached by the operating system. This experiment did not verify cold OS cache, so it cannot claim a cold-storage cause.
- **Reverse-order confirmation:** Repeat the pair with execution order reversed to check whether order or warm cache drove the first difference.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- First full pair: off/read-first 934/759 s, saving 18.74%, goodput −0.66%. Reverse-order confirmation: 854/770 s, saving 9.84%, goodput −0.33%. Prospective gate required at least 10% saving and no more than 2% goodput loss; confirmation meets throughput tolerance but misses walltime gate, so no promotion. Unknown cache state and node differences prevent a cold-storage causal claim. Walltime is scheduler duration, not steady-state throughput.
- The read-first idea concerns loading the prefill checkpoint during startup. “Cold prefix” describes whether the model can reuse a prompt-prefix/KV-cache entry; it does not describe operating-system file cache. A cold OS cache means checkpoint pages must be fetched from storage instead of memory cache. Since cache state was not verified and nodes differed, the walltime difference cannot be assigned to cold storage. The reversed-order result misses the predeclared threshold, so the team did not adopt the change.

### Tradeoff and strength of evidence

- **Observation:** First saving is 18.74%; reversed confirmation is 9.84%, below the 10% gate.
- **Hypothesis:** Read-first loading may reduce startup walltime.
- **Supported conclusion:** Close without promotion after the confirmation misses the gate.
- **Unknown / limitation:** Cache state and node effects prevent cold-storage attribution.

### Spoken script

“The first pair saved 18.74 percent, but reversing the order gave 9.84 percent, below the declared 10 percent gate. Goodput changed only slightly. Since the confirmation misses the threshold, we close this branch rather than đưa vào cấu hình chính its favorable first result.”

### Avoid this interpretation

Do not report only the favorable first order. Unknown cache state limits causal interpretation.

### Transition

“A separate question asks whether a do nhóm tự chạy trên cluster được cấp hardware ratio can forecast a nearby load.”

---

<a id="slide-19"></a>

## Slide 19 — A local N52 calibration, not a universal multiplier

![Slide 19](../../submission-review/ai-journey-update-20261030/slides/assets/slide-19.png)

### Purpose

Define a limited, measured bridge between platforms and explain why it is not a universal H100-to-H200 conversion rule.

### Technical interpretation and reasoning

The ratio is H200 mean goodput divided by H100 mean goodput for one matched model/configuration at N52. Two and four allocations are repeated scheduled runs; they do not mean two and four different GPU models, nor prove that every allocation used unique hardware. This single ratio is a calibration point, not a conversion law.

### Terms and symbols to understand

- **N52:** Client concurrency used for this calibration point.
- **Allocation:** One scheduled resource assignment/run.
- **System ratio:** H200 mean goodput divided by H100 mean goodput here.
- **Dimensionless:** A ratio with no physical units.
- **Calibration point:** One load/configuration, not a validated conversion curve.
- **Allocation means repeats, not independent hardware:** Two H100 and four H200 allocations are scheduled observations. The counts alone do not prove distinct machines, unique GPU devices, or general hardware diversity.
- **Ratio 1.188096805:** H200 mean 2,632.181 ÷ H100 mean 2,215.460 for this N52 combo. It has no unit and applies only to this comparison.
- **Calibration:** A measured reference point used to make one prospective estimate; not a validated conversion function across workloads.
- **Independent hardware:** Different accelerator type (H100 vs H200), not simply another scheduler allocation of the same type.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- H200/H100 observed system ratio is 1.188096805, dimensionless. It describes this measured point only. Repeats at one load do not define a conversion function or prediction interval, and the ratio must not be applied to TTFT, ITL, SLA or other backend branches. Allocation means scheduled resources, not independent hardware generations. Hypothesis: local calibration may inform a nearby held-out forecast. Conclusion: use it only as a scoped forecast input. Unknown: variation across loads/configurations and uncertainty.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- The printed means are 2215.460 and 2632.181 good output tokens/s, summarized over two H100 and four H200 allocations respectively. The ratio 1.188096805 has no unit; locally it corresponds to about 18.81% higher observed system throughput, not 18.81 percentage points of SLA.
- The two H100 and four H200 allocations are repetitions of scheduled runs. They are not evidence of two versus four distinct hardware units, nor of four independent hardware populations. “Independent hardware” here means a different accelerator family, H100 versus H200. Repeating at one load estimates that particular operating point more directly, but cannot establish a conversion function for other concurrency levels or backends.

### Tradeoff and strength of evidence

- **Observation:** N52 means yield a local H200/H100 ratio of 1.188096805.
- **Hypothesis:** Local calibration may inform a nearby held-out point.
- **Supported conclusion:** Treat it as a scoped ratio, not a hardware conversion rule.
- **Unknown / limitation:** Variation across loads, settings and latency metrics is unknown.

### Spoken script

“At the same N52 combo, H200 goodput divided by H100 goodput is 1.1881. It is a do nhóm tự chạy trên cluster được cấp system association, not a universal conversion factor. The next slide tests one frozen forecast at N50.”

### Avoid this interpretation

This ratio applies only to the stated load and configuration; it is not a percentage or conversion for latency.

### Transition

“We now check a forecast fixed before seeing held-out (phép đo được giữ riêng để kiểm tra dự báo) H200 data.”

---

<a id="slide-20"></a>

## Slide 20 — Freeze the forecast, then test it on H200

![Slide 20](../../submission-review/ai-journey-update-20261030/slides/assets/slide-20.png)

### Purpose

Show an honest forecast test: freeze the prediction, test a held-out point, and report both the operational pass and the missing uncertainty.

### Technical interpretation and reasoning

The forecast was recorded before the held-out (phép đo được giữ riêng để kiểm tra dự báo) H200 result was examined. Its −1.5371% signed error is within the predeclared ±2% operational tolerance. The earlier sensitivity range varied selected inputs but omitted model error, so it was not a complete prediction-uncertainty interval; being outside it is a real limitation, not a reason to alter the frozen forecast.

### Terms and symbols to understand

- **Held-out:** A measurement kept out of calibration and revealed only after the prediction is written down; it tests transfer to a new observation.
- **Signed error:** (measured − predicted) relative to prediction; negative means measured goodput was lower.
- **±2% tolerance:** Predeclared operational gate, not a 95% confidence interval.
- **Sensitivity range:** Range from changing selected inputs. It is not total predictive uncertainty if it omits model error, run-to-run variation, or other unmodeled factors.
- **N50:** Client concurrency of this forecast check.
- **Operational tolerance:** A predeclared practical pass band of ±2%; it is not a 95% confidence interval or measurement error bar.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- Held-out job 24272 measures 2,601.629; signed error is −1.5371%, within the predeclared ±2% operational tolerance. It is outside the earlier sensitivity range because that range omitted model error. The tolerance is not a 95% confidence interval or measurement error bar. Do not refit the frozen ratio after observing the point. One held-out (phép đo được giữ riêng để kiểm tra dự báo) pass supports only this do nhóm tự chạy trên cluster được cấp check, not broad predictive validity.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- The minus sign means the measurement is below the forecast: 2601.629 versus 2642.244 good output tokens/s. The signed percentage is (measured − predicted) / predicted × 100; ± means a symmetric allowed tolerance, not a measurement error bar.
- The prediction is held out because the H200 N50 result was not used to calculate it. The ±2% band is an operational acceptance rule selected before the measurement. A sensitivity interval asks how a calculation changes as chosen inputs change; it becomes a prediction uncertainty interval only if it also represents important errors and variation. This earlier range omitted model error, so the held-out (phép đo được giữ riêng để kiểm tra dự báo) observation exposed a limitation even though it passed the practical tolerance.

### Tradeoff and strength of evidence

- **Observation:** Held-out error is −1.5371%, within ±2% but outside an incomplete sensitivity range.
- **Hypothesis:** N52 calibration may predict nearby N50 throughput.
- **Supported conclusion:** One local gate passes; retain the omitted model-error caveat.
- **Unknown / limitation:** Broader predictive accuracy and complete uncertainty are unknown.

### Spoken script

“The forecast was frozen before the result. H200 measured 2,601.629 against 2,642.244 predicted, a −1.5371 percent error. That is within the predeclared operational tolerance, but outside an earlier incomplete sensitivity range. We keep both findings and do not refit.”

### Avoid this interpretation

±2% is an operational tolerance, not a confidence interval. Do not refit after observing held-out (phép đo được giữ riêng để kiểm tra dự báo) data.

### Transition

“Next, we compare small source-guided hypotheses by complete outcome.”

---

<a id="slide-21"></a>

## Slide 21 — Use source evidence to test one small hypothesis

![Slide 21](../../submission-review/ai-journey-update-20261030/slides/assets/slide-21.png)

### Purpose

Show how source-based ideas are closed or retained after complete measured trials; plausible code paths and small gains are not enough for promotion.

### Technical interpretation and reasoning

For each row ask three questions: did source inspection predict a real code path, did runtime evidence confirm it was active, and did a full matched run improve the service enough to matter? The small percentages are separate experiments and must not be added together.

### Terms and symbols to understand

- **Source evidence:** Code and runtime show which path was selected/activated.
- **Exact-ID preflight:** Checks tokenizer batching preserves intended token IDs.
- **p95 TTFT:** 95th-percentile first-token latency; it can worsen even when the mean improves.
- **Useful-gain gate:** Prospective threshold for promotion.
- **Prefill/decode:** Prompt processing / autoregressive generation phases.
- **Source inspection:** Read the implementation to identify the branch that should execute; runtime evidence must then confirm the branch actually ran.
- **Exact token-ID preflight:** A correctness check that batching preserves the same token IDs before measuring speed.
- **Useful gain:** A predeclared minimum improvement needed to justify changing the serving configuration; a tiny positive number is not automatically useful.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- Source evidence and runtime activation establish what executed; they do not prove a bottleneck. Each decision relies on full matched outcomes and a useful-gain gate. p95 is the 95th percentile tail, not a mean. Do not add percentages across branches.
- Source inspection and runtime confirmation answer whether the intended implementation was used; the full matched run answers whether it helped. These are separate evidence steps. A small positive change may be noise or too small to matter, and a metric improvement can coexist with a worse tail or lower goodput. This is why the table retains negative and below-threshold branches instead of accumulating headline gains.

### Tradeoff and strength of evidence

- **Observation:** Small gains fail the useful-gain threshold; cache tail or attention goodput worsens.
- **Hypothesis:** Source-supported settings may improve a service metric.
- **Supported conclusion:** Adopt in the main configuration only an activated matched change with useful full-run gain.
- **Unknown / limitation:** A shared bottleneck or cross-setting effect is not established.

### Spoken script

“A working flag is only the start. We verify activation, run the full protocol, and compare the result to its control. Small gains below the useful threshold are not đưa vào cấu hình chínhd; a better ITL that costs 6.39 percent goodput is also not a win.”

### Avoid this interpretation

Keep units and configuration attached; do not state a hypothesis as a measured cause.

### Transition

“Service latency and model accuracy are separate acceptance questions.”

---

<a id="slide-22"></a>

## Slide 22 — Latency acceptance is separate from model accuracy

![Slide 22](../../submission-review/ai-journey-update-20261030/slides/assets/slide-22.png)

### Purpose

Separate fast service from correct model behavior: local sanity checks and latency acceptance cannot certify the official full-set quality gate.

### Technical interpretation and reasoning

Latency acceptance asks how quickly requests are served; model quality asks whether answers meet the organiser's reference score. The 7/8 smoke and 12/12 retrieval checks are small team-run regression checks, not the official full-set accuracy evaluation. Passing the latency gate cannot establish the required score of at least 99% of reference.

### Terms and symbols to understand

- **SLA:** Request-level service latency acceptance.
- **Smoke:** Small basic-behavior/regression check suite.
- **Retrieval:** Local retrieval sanity suite, not official quality benchmark.
- **99% of reference:** Official model-quality threshold, still unverified.
- **FP8/BF16:** FP8 weights; BF16 activation and KV cache formats.
- **Service performance:** Measures speed/latency and request acceptance; it says nothing by itself about semantic correctness.
- **Official model quality:** Separate organiser evaluation comparing model answers with a reference on the prescribed full test set; the requirement here is at least 99% of reference.
- **Smoke / retrieval checks:** Small team-run checks for regression and retrieval behavior, not a substitute for the official quality test.
- **FP8 weights, BF16 activation/KV:** Weight precision differs from activation and KV-cache precision; these labels describe numerical formats, not quality scores.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.
- **Team-run sanity checks:** Small checks run by the team on the assigned environment to look for regressions; they are not the organiser’s prescribed full-set quality evaluation.

### Interpreting the evidence or diagram

- Local smoke is 7/8 with no new regression; retrieval is 12/12. These small local checks do not certify the official quality requirement of at least 99% of reference. The primary retains FP8 weights and BF16 activation/KV; it does not use quantized KV or speculative decoding. Terms: SLA is service-level latency acceptance; reference is organiser's quality comparator. Conclusion: report service performance separately, and leave official quality explicitly unverified.
- The latency result is a performance result: it measures request service time and pass fraction. The 99%-of-reference requirement is a quality result: it compares generated answers with the organiser's specified reference evaluation. Smoke and retrieval suites check a limited set of regressions; they do not estimate the full-set quality score. Those checks therefore support “no detected do nhóm tự chạy trên cluster được cấp regression,” not “official accuracy passed.”

### Tradeoff and strength of evidence

- **Observation:** Latency SLA and small local checks pass; official model quality is unverified.
- **Hypothesis:** Preserve model while evaluating serving independently from quality.
- **Supported conclusion:** Report latency and official quality as separate outcomes.
- **Unknown / limitation:** The 99%-of-reference full-set threshold remains unverified.

### Spoken script

“The service meets its do nhóm tự chạy trên cluster được cấp latency gate, and small sanity checks show no new regression. The official 99-percent-of-reference quality evaluation has not been verified. We therefore make no quality certificate or ranking claim.”

### Avoid this interpretation

Smoke and retrieval checks are not full accuracy certification.

### Transition

“The EAGLE3 case shows how failed hypotheses and repaired tools should be reported.”

---

<a id="slide-23"></a>

## Slide 23 — EAGLE3: follow the failed hypothesis through its repairs

![Slide 23](../../submission-review/ai-journey-update-20261030/slides/assets/slide-23.png)

### Purpose

Preserve the entire speculative-decoding failure-and-repair chain, and explain why fixing integration did not establish a speedup.

### Technical interpretation and reasoning

Follow the chronology. First, placing draft workers everywhere misses the joint latency gate. Next, a validator mistakenly demands draft KV regions on target-only prefill; repairing that checker allows a valid retry but does not change the performance. The short retry and later full trial both lose goodput, so the tested variants are closed.

### Terms and symbols to understand

- **EAGLE3:** Speculative decoding method that proposes draft tokens.
- **Draft placement:** Worker role on which the draft model is run.
- **KV region:** Role-specific key/value cache memory region.
- **Short protocol:** Limited test, not the complete benchmark protocol.
- **Full protocol:** Complete fixed workload, warmup, score window and grace period.
- **EAGLE3 speculative decoding:** A draft model proposes tokens; the target model verifies them. Correct draft transfer is a functional result, not proof of faster end-to-end serving.
- **Role-aware validator:** The check must apply draft-KV expectations only to worker roles that actually host the draft. Target-only prefill has no draft KV region.
- **Short vs full run:** A short pass establishes limited execution behavior; the full fixed-workload run is required to compare serving goodput.
- **Goodput loss:** A lower qualifying output-token rate versus the matched target-only control.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.

### Interpreting the evidence or diagram

- Decode-only attempt 25988 is rejected by a validator incorrectly applying draft KV-region counts to target-only prefill. A role-aware validator repair preserves the old failure. Short retry 25998 passes its limited protocol but loses 4.74% goodput against its target-only control. Separate shallow full trial 27238 scores 2,971.628430 versus 3,034.761104 for control 26949, a 2.080318% loss. Functional draft transfer is not speedup; low acceptance telemetry is not a causal timing breakdown. Terms: EAGLE3 speculative decoding; KV key/value cache; full protocol complete workload; short protocol limited test. Conclusion: close tested arms while retaining failure and repair history. Unknown: other configs and official quality.
- The validator failure was a tooling/interface mistake, not evidence that the model itself failed. The repaired validator applies checks by worker role: target-only prefill should not be required to own draft KV. After that correction, the short decode-only rerun loses 4.74% goodput, and the later full shallow run loses 2.080318%. Functional speculative token transfer and passing a short run do not justify a serving change when complete goodput is lower.

### Tradeoff and strength of evidence

- **Observation:** Repaired checks permit reruns; decode-only and shallow variants lose goodput.
- **Hypothesis:** Changed draft placement or shallow decoding may recover TTFT.
- **Supported conclusion:** Close tested variants and preserve failure/repair provenance.
- **Unknown / limitation:** Other settings, causal timing and official quality remain unknown.

### Spoken script

“The first attempt missed latency. A tooling bug then rejected a decode-only run; we repaired the validator and kept the original failure. The short retry ran but lost goodput, and a distinct full trial also lost. These tested settings close; we do not claim the method can never help.”

### Avoid this interpretation

Do not erase the validator failure or confuse short and full protocols.

### Transition

“The summary returns to replicated N64 and the small unđưa vào cấu hình chínhd cache result.”

---

<a id="slide-24"></a>

## Slide 24 — Topology → transport → kernels → replication

![Slide 24](../../submission-review/ai-journey-update-20261030/slides/assets/slide-24.png)

### Purpose

Close the main AI talk with the replicated configuration and the limits of its evidence, instead of choosing an isolated peak.

### Technical interpretation and reasoning

The selected reference is the mean of three historical full N64 runs. The later native-runtime run is a separate measurement because it used a different server execution environment; do not pool the values as if they were one controlled series. The cache candidate is the numerical high, but its 0.240921% gain is below the declared useful-gain threshold.

### Terms and symbols to understand

- **Three-run mean:** Mean of historical full N64 runs 25366/25373/25487.
- **Native runtime:** Job 26766 uses the native server execution environment, separate from the historical runtime path. Runtime means software stack that launches/executes the serving server, not GPU hardware.
- **Cache pair:** 27376 fresh control versus 27378 candidate.
- **+0.240921%:** Candidate gain, below the prospective useful-gain gate.
- **Official quality:** Full-set accuracy requirement, not verified here.
- **Historical N64 series:** Three full runs 25366/25373/25487 average 3,044.400475 good output tokens/s.
- **Fresh cache control:** Job 27376 compared with candidate 27378; the +0.240921% score difference is below the useful-gain threshold.
- **Team-reviewed run:** A run executed by the team on the assigned organiser cluster and checked against local raw-output/runtime gates. This is not an organiser-issued ranking or quality certification.
- **Full protocol 60/120/30:** For this benchmark: 60 seconds warmup, 120 seconds scored measurement, and 30 seconds grace for in-flight requests; grace is not scored.
- **Team-run and team-reviewed:** The team submitted and inspected the run on the assigned organiser cluster. “Reviewed” means checking retained raw request results, runtime and required gates; it is not organiser certification, a contest ranking, or a claim that the run was on a personal machine.

### Interpreting the evidence or diagram

- Later native-runtime job 26766 independently reaches 3,045.501509 and 98.580442% joint SLA; keep it separate because runtime path differs. Highest full cache result 27378 reaches 3,048.446289, only +0.240921% over fresh control 27376, below useful-gain gate. Lower valid replays around 2,802–2,831 remain retained. Replication supports choosing N64, not a global optimum. No speculative speedup, official quality certificate, or causal native-runtime speedup is claimed.
- Good output tokens/s is a throughput unit (higher is desirable); latency values are milliseconds (lower is desirable); joint SLA is a percentage of requests, not model accuracy. N is concurrent client requests, not GPUs. Read only the metrics actually printed on this slide.
- The historical mean and the native-runtime score are both team-run, fully reviewed measurements on the assigned accelerator cluster; “reviewed” means raw request/runtime checks were inspected, not that the organiser certified a ranking or quality score. The native runtime is the software execution environment, not a new GPU generation. Keep its 3,045.501509 separate from the three-run historical mean because the runtime paths differ. A numerically higher cache result is not selected when its gain is below the predeclared useful-change threshold.

### Tradeoff and strength of evidence

- **Observation:** Historical N64 mean is replicated; cache point gains 0.240921%; native path is separate.
- **Hypothesis:** A reproduced point is a safer selection basis than isolated peak.
- **Supported conclusion:** Retain N64; do not select for the main configuration the small cache gain.
- **Unknown / limitation:** Global optimum, official quality and causal runtime differences are unknown.

### Spoken script

“The selected point is the replicated historical N64 mean. A later native result is similar but separately reported. The cache high is only 0.24 percent above its control and is not đưa vào cấu hình chínhd. We retain lower valid runs too. This is a measured operating point, not a global optimum; official quality still needs verification.”

### Avoid this interpretation

Keep units and configuration attached; do not state a hypothesis as a measured cause.

### Transition

“The next section changes topic to the HPC CPU/OpenFOAM study.”

---

<a id="slide-25"></a>

## Slide 25 — Appendix · diagnose performance drift with controlled cells

![Slide 25](../../submission-review/ai-journey-update-20261030/slides/assets/slide-25.png)

**AI backup section: open when a deeper explanation is needed.**

### Purpose

Explain why the observed score drift did not identify a cause, and why the later full result is a reproduction rather than a causal recovery claim.

### Technical interpretation and reasoning

Read the scores as three different evidence classes. The historical mean comes from three full N64 runs. The roughly 2,560 control was short and also had changed graph policy, request cap, and harness/observation conditions, so the gap mixes protocol and configuration differences. The 2,830.923547 legacy replay is a valid full run under retained old operational settings. The 3,045.501509 native run is another full observation in a later execution path. Similar endpoints do not prove that a particular changed setting restored performance.

### Terms and symbols to understand

- **N64:** The client aims to keep 64 requests in flight; it is a request load target, not 64 GPUs.
- **full vs short protocol:** Full scoring uses 60 s warmup, 120 s profiling, 30 s grace. A short control uses a shorter measurement and is not directly score-matched to full runs.
- **score drift:** A difference between observations that raises a question; by itself it does not identify the cause.
- **native runtime:** The distinct later serving execution path used for full run 26766. The label identifies that tested path; it does not itself mean faster or explain why the score changed.
- **causal recovery:** Evidence that a specific change restored a score, usually from controlled comparisons that isolate that change.
- **request cap / graph policy:** The cap limits running requests. Graph policy decides which decode shapes use captured GPU graphs; both changed in the later control.

### Interpreting the evidence or diagram

- A full run uses the fixed 60-second warmup, 120-second scored profiling window, and 30-second grace. A short control does not provide the same observation window, so its score is useful as a drift signal, not a matched full-protocol comparison.
- The legacy replay scored 2,830.923547; the later native full run scored 3,045.501509. Controlled graph/admission comparisons found no single useful cause for the spread. Keep both valid results visible.

### Tradeoff and strength of evidence

- **Observation:** Historical full N64 averaged 3,044.400475; the short control was about 2,560; a valid legacy full replay scored 2,830.923547; native full run 26766 scored 3,045.501509.
- **Hypothesis:** Changed prefill graph policy, maximum running-request cap, or harness conditions may contribute to the drift.
- **Supported conclusion:** The later full result reproduces the historical level in a distinct runtime series; no single setting was shown to cause the difference.
- **Unknown / limitation:** The relative contribution of graph policy, request cap, protocol length, harness, and observation variation is unresolved.

### Spoken script

Three historical full runs at a target load of 64 simultaneous requests averaged about 3,044 good output tokens per second. A later short control was around 2,560, but it used less measurement time and different graph and request-limit settings. Replaying the old full setup scored lower; a later run through a different serving execution path returned near the historical level. That is a separate reproduction, not proof that a setting caused recovery.

### Avoid this interpretation

Do not compare the short control as if it were a full run, attribute the later score to one setting, or discard the valid lower legacy replay.

### Transition

Next, distinguish a promising component probe from evidence about full-model serving.

---

<a id="slide-26"></a>

## Slide 26 — Appendix · profiles and source also close attractive detours

![Slide 26](../../submission-review/ai-journey-update-20261030/slides/assets/slide-26.png)

### Purpose

Show how component-level experiments and source review can eliminate leads without demonstrating a faster full model.

### Technical interpretation and reasoning

Each row answers a different question. The attention-DP score is an end-to-end observation at N52, but several settings changed together, so it cannot identify which one hurt. Triton results are kernel probes on representative shapes: they test a component, not the complete Qwen serving path. The torch.compile attempt reached real model code but stopped at a RoPE/fused-KV assertion before a score. C++ fixtures exercised CPU helpers only. Those evidence levels explain why the decisions are conservative.

### Terms and symbols to understand

- **probe:** A small, isolated experiment on a component or a few shapes. It says what that component did there, not what the full service will do.
- **fixture:** A small test input used to check helper code or an API. A passing CPU fixture is not a GPU serving run.
- **source review:** Reading code to see whether a setting is supported or consumed. It establishes possible behavior, not that the behavior ran in the model.
- **full-model test:** A run that starts the actual distributed model, serves requests, and measures outputs. The compile attempt here stopped before scoring.
- **DP / FP8:** DP is data parallelism, a way to distribute request/model work. FP8 is 8-bit floating point used for model weights.
- **Triton / DeepGEMM:** GPU-kernel systems tested in representative shapes; conclusions apply only to those probes.
- **SM budget:** A limit on how many GPU streaming multiprocessors a kernel may use; a kernel-level result need not transfer to end-to-end service.
- **RoPE / fused-KV:** RoPE encodes token positions. The compiled model path asserted when this operation met the fused key-value cache interface.

### Interpreting the evidence or diagram

- The attention-DP package with DeepGEMM/DeepEP scored 2,549.20 at N52, below the retained MNNVL point; the coupled settings prevent a single-flag conclusion. Representative FP8 Triton probes lost to DeepGEMM.
- SM budgets 80/96/120 produced mixed results or failed the consistency criterion. The real-model compile asserted before benchmarking. CPU cache/API fixtures can check helper logic, but do not exercise GPU model integration, distributed startup, or serving quality.

### Tradeoff and strength of evidence

- **Observation:** A coupled attention package scored lower; representative kernel probes lost; SM checks were mixed; real-model compilation had no score; C++ fixtures were CPU-only.
- **Hypothesis:** A different attention layout, kernel, SM budget, compile path, or cache API might improve the full service.
- **Supported conclusion:** Component leads can be closed or retained as source findings, but they do not establish a full-model speedup. The tested Triton shapes did not beat DeepGEMM.
- **Unknown / limitation:** Other shapes or a compatible compile interface could behave differently; no full compiled model run passed.

### Spoken script

Some rows test a small GPU kernel, some test helper code on a CPU, and some only inspect source. These checks can reject unsupported ideas, but they do not start the complete distributed model and score its answers. The real compile attempt entered Qwen code, then stopped when rotary position encoding met an incompatible fused key-value-cache interface. It produced no serving score.

### Avoid this interpretation

Do not turn a kernel probe, CPU fixture, or code-path inspection into a claim about full-model speed or correctness.

### Transition

The next slide describes the actual selected H200 and separate H100 serving configurations.

---

<a id="slide-27"></a>

## Slide 27 — Appendix · the selected AI deployment is N64

![Slide 27](../../submission-review/ai-journey-update-20261030/slides/assets/slide-27.png)

### Purpose

Describe the retained AI service configuration without implying H100 and H200 results are directly comparable.

### Technical interpretation and reasoning

Read each row as one operational choice: input processing (prefill), token generation (decode), parallel GPU groups, or numeric precision. H200 uses client concurrency 64; the separate H100 observation uses 54 and a different prefill backend/chunk. Both use target weights in FP8 and activation/KV state in BF16. The bottom line names shared decode and communication components. Because hardware and settings differ, this is a deployment map, not a hardware benchmark.

### Terms and symbols to understand

- **prefill / decode:** Prefill processes the prompt before generation; decode produces answer tokens one step at a time.
- **TP / EP:** Tensor parallelism splits tensor operations across GPUs. Expert parallelism distributes mixture-of-experts expert blocks across GPUs.
- **FP8 / BF16:** FP8 weights use 8-bit floating point. BF16 activation and KV values use a 16-bit format; the formats describe different tensors.
- **HPC-Ops / DeepGEMM:** GPU execution backends used for different service phases; naming a backend does not alone establish a speed advantage.
- **FlashInfer / MNNVL:** FlashInfer supplies decode attention kernels; MNNVL supplies GPU collective communication. They serve different roles.
- **round-robin:** Requests are distributed in turn across the two prefill workers.
- **deployment map:** A description of how a measured service was configured, not evidence that another GPU or setting has the same performance.

### Interpreting the evidence or diagram

- The H200 selection uses two TP4 prefill workers with DeepGEMM and chunk 8,192, plus one TP8/EP8 HPC-Ops decode worker. Its decode graph set is dense, with buckets 1 through 64.
- H100 keeps two TP4 HPC-Ops prefill workers with chunk 4,096 and the same TP8/EP8 decode grouping. FlashInfer decode attention, MNNVL communication, and round-robin prefill routing are shared.

### Tradeoff and strength of evidence

- **Observation:** H200 and H100 differ in concurrency and prefill backend/chunk, while retaining the listed weight and activation/KV formats.
- **Hypothesis:** A replicated H200 N64 setup is the more defensible primary because it has repeated full-run evidence.
- **Supported conclusion:** Report H100 separately; matching a few settings does not make the GPU results a controlled hardware comparison.
- **Unknown / limitation:** Official model accuracy and complete portable deployment verification after the reader fixes remain open.

### Spoken script

This is the selected H200 deployment, not a direct race against H100. H200 processes prompts on two groups of four GPUs, then generates tokens on one group of eight GPUs with experts distributed across the group. H100 uses fewer simultaneous requests and a different prompt-processing backend and chunk. Both keep 8-bit weights and 16-bit activation and KV values. Reader fixes were checked on real data, but not through a complete GPU replay afterward.

### Avoid this interpretation

Do not pool H100 and H200 scores, infer a hardware multiplier, or confuse FP8 weights with BF16 activation/KV values.

### Transition

Now compare what sparse decode-graph capture saved with what it did to goodput.

---

<a id="slide-28"></a>

## Slide 28 — Appendix · sparse graphs save memory, not goodput

![Slide 28](../../submission-review/ai-journey-update-20261030/slides/assets/slide-28.png)

### Purpose

Explain the sparse-graph tradeoff: less logged capture memory per rank, slightly shorter capture, but lower measured goodput.

### Technical interpretation and reasoning

Compare the same three quantities across the two settings. The 64-to-12 change is the number of captured decode-shape buckets, not 64-to-12 concurrent requests or GPUs. A bucket is a reusable captured execution shape; requests that do not exactly match a supported shape may be padded or mapped to a nearby bucket. Fewer buckets can reduce stored graph and associated capture-buffer memory, but can increase padding work. Padding and its cost were not isolated here. The reported 1.15/0.36 GB is capture-related memory per decode rank, not total VRAM: model weights, KV cache, workspaces, and other allocations are separate. Capture elapsed time is only the capture phase.

### Terms and symbols to understand

- **decode graph bucket:** A captured GPU execution shape the server can replay for a class of decode batches. It is not a request count.
- **padding:** Filling a batch or shape to a supported graph size. Fewer available buckets may require more padding, but this run did not measure its amount or cost.
- **graph-capture memory:** Memory associated with recorded reusable GPU execution graphs and their buffers, reported here per decode rank.
- **VRAM / GB / GiB:** VRAM is all memory on a GPU. The log reports capture-related GB per rank, not total VRAM or GiB; weights and KV cache use other memory too.
- **rank:** One distributed worker process; these values are per decode worker/rank, not summed over eight ranks.
- **goodput / ITL:** Goodput is qualifying requests/s multiplied by 200 requested output tokens. ITL is the interval between generated tokens.
- **compile off:** Model compilation was disabled for this capture test; successful graph capture does not validate the compiled model path.

### Interpreting the evidence or diagram

- The candidate reduced buckets from 64 to 12; captures were observed on all eight decode ranks with compile off. Logged capture memory fell from 1.15 to 0.36 GB per rank. Capture time changed from 101.46–101.49 to 95.98–96.05 seconds.
- Goodput fell from 3,041.119598 in earlier control 27376 to 3,029.861122 in candidate 27510, or 0.370208%. Mean request ITL rose from 14.991 to 15.136 ms, although TTFT improved.

### Tradeoff and strength of evidence

- **Observation:** Candidate capture memory was lower and capture slightly shorter; measured goodput was 0.370208% below the earlier control.
- **Hypothesis:** Fewer graph shapes could save capture resources while preserving the service objective.
- **Supported conclusion:** The candidate did not improve goodput; the team retained dense graphs. Do not claim padding caused the score change because padding was not separately measured.
- **Unknown / limitation:** There was one earlier control, engine-generated seeds differed, and capture memory is not total GPU memory.

### Spoken script

The candidate captured 12 decode shapes instead of 64. That cut logged graph-capture memory per rank from 1.15 to 0.36 gigabytes, while capture time changed by only a few seconds. But goodput was 0.370208 percent lower and mean token interval slightly higher. Fewer graph shapes can require extra padding, but padding was not measured here. We retain dense graphs and do not assign a cause to the score difference.

### Avoid this interpretation

Do not call bucket count concurrency, capture memory total VRAM, or capture time total job time. Padding is a possible mechanism, not a measured explanation.

### Transition

Next, see what the synthetic serving score includes and what separate model-quality checks remain.

---

<a id="slide-29"></a>

## Slide 29 — Appendix · what the benchmark actually measures

![Slide 29](../../submission-review/ai-journey-update-20261030/slides/assets/slide-29.png)

### Purpose

Explain what the serving benchmark actually times, how its score is derived, and why that result is separate from model accuracy.

### Technical interpretation and reasoning

The key distinction is between requested workload and scored evidence. The synthetic client requests 4,000 input and 200 output tokens; it sustains closed-loop concurrency. Workers and serving paths get separate warmup traffic, then AIPerf runs its own 60-second warmup, 120-second scored profiling interval, and 30-second grace. Only profiling contributes to performance metrics. Grace drains outstanding requests and is not another scoring window. The separate 99% criterion is a full-set quality evaluation, not a serving latency result.

### Terms and symbols to understand

- **AIPerf / closed loop:** AIPerf sends requests and calculates metrics. Closed loop replaces each completed request to maintain a target number in flight.
- **60/120/30 protocol:** Seconds for AIPerf warmup, scored profiling, and grace. Only the middle 120 seconds score; grace lets in-flight requests settle.
- **goodput:** Qualifying requests per second. The official displayed good output tokens/s equals exported goodput multiplied by 200 requested output tokens.
- **request latency limits:** A request is good only when TTFT is at most 3,000 ms and request-mean ITL at most 20 ms; at least 90% of all requests must pass both.
- **99% accuracy requirement:** The organizer requires full-set model quality at least 99% of its FP8 reference. Team-run small output checks on the assigned cluster do not establish this.
- **requested vs actual tokens:** 4,000/200 are client requests. They do not prove how many token IDs the model actually consumed or generated for every request.

### Interpreting the evidence or diagram

- Goodput is AIPerf Goodput in qualifying requests/s multiplied by the requested 200 output tokens. Do not divide all completed requests by 120: completions can fall in warmup or grace, and goodput counts only requests meeting service limits.
- Requested token counts are client settings; retokenized input and actual generated IDs/usage were not fully retained. The synthetic prompt/answer workload is not the organizer quality dataset. Full-set accuracy remains UNKNOWN.

### Tradeoff and strength of evidence

- **Observation:** Serving uses synthetic 4,000/200 requests and a 60/120/30-second warmup, profiling, and grace schedule.
- **Hypothesis:** A fixed workload and scoring interval permit useful comparisons when protocol and settings match.
- **Supported conclusion:** The result describes serving performance under this workload; it neither certifies accuracy nor supplies a simple completion-count rate.
- **Unknown / limitation:** Actual per-request token IDs/usage and the official full-set score have not been established.

### Spoken script

The serving test uses synthetic prompts requesting 4,000 input and 200 output tokens. The benchmark client keeps a target number of requests active, warms up, scores a fixed 120-second window, then lets outstanding requests finish. Its goodput counts requests meeting both latency limits; multiplying by 200 gives the reported good output tokens per second. This does not test the organizer’s full quality set, whose 99-percent requirement remains unknown.

### Avoid this interpretation

Do not divide all completions by 120, count grace as scored time, infer actual token usage from requested lengths, or claim the accuracy threshold passed.

### Transition

Next, compare chunk-size runs using this same full scoring protocol.

---

<a id="slide-30"></a>

## Slide 30 — Appendix · larger prefill chunks did not help

![Slide 30](../../submission-review/ai-journey-update-20261030/slides/assets/slide-30.png)

### Purpose

Show that larger prefill chunks passed the team’s local checks but reduced measured goodput and worsened the TTFT tail in this bounded comparison.

### Technical interpretation and reasoning

Each row is one full N64 run; compare the same score and latency columns across chunk sizes. Chunk size is input work handled together, not client concurrency. Good output tokens/s is the qualifying service rate, joint SLA is the share meeting both request latency limits, and p95 TTFT describes the slow tail. As chunk rose 8,192 → 10,240 → 12,288, goodput fell and p95 TTFT rose. One run per setting makes this evidence for retaining 8,192 here, not a universal optimum.

### Terms and symbols to understand

- **prefill chunk:** Number of prompt tokens handled together in one prefill scheduling unit; it is separate from client concurrency.
- **SLA / p95 / TTFT:** SLA is the share of all requests meeting both latency limits. p95 is the 95th percentile. TTFT is time from request start to first token.
- **local review:** Here “local” means team-run and reviewed on the assigned cluster. It does not mean a laptop run or organizer approval.
- **acceptance checks:** The team’s protocol, runtime, latency, and output checks. Passing them establishes a valid local result, not official acceptance or a useful improvement.
- **arm:** One tested configuration, here one chunk-size setting. There was one full run for each arm.
- **seed 2026:** Configured workload seed. Engine-generated seeds still differed across launches.

### Interpreting the evidence or diagram

- At 8,192, job 26766 recorded 3,045.501509 good output tokens/s, 98.580% joint SLA, and 1,311.69 ms p95 TTFT. At 10,240, job 26768 recorded 3,034.088251, 98.524%, and 1,518.87 ms.
- At 12,288, job 26770 recorded 3,020.943099, 98.310%, and 1,624.12 ms. All three were full 60/120/30 N64 runs using requested 4,000/200 tokens, the same model and runtime, and cold prefixes; each chunk setting was observed once.

### Tradeoff and strength of evidence

- **Observation:** Goodput declined and p95 TTFT increased monotonically across the three observed chunk sizes.
- **Hypothesis:** Larger chunks might increase throughput by processing more prompt tokens per batch.
- **Supported conclusion:** Retain chunk 8,192 for this service setting; the larger tested chunks did not improve its objective.
- **Unknown / limitation:** One run per setting leaves order and engine-seed variation; this is not proof of a global optimum.

### Spoken script

All three tests used the same full protocol with 64 requests in flight. The 8,192-token prompt chunk scored about 3,045 good tokens per second; larger chunks scored about 3,034 and 3,021. Team checks on the assigned cluster passed for every run, but that only establishes a reviewed local result, not organizer approval or improvement. Larger chunks also worsened the slow first-token tail. With one run per size, we keep 8,192 for this service, not as a universal best.

### Avoid this interpretation

A local pass is team-reviewed evidence from the assigned cluster, not organizer approval. Do not treat a passing arm as an improvement or a global optimum.

### Transition

The next slide separates a completed GPU serving run from result-reader post-processing.

---

<a id="slide-31"></a>

## Slide 31 — A real replay can invalidate a static deployment claim

![Slide 31](../../submission-review/ai-journey-update-20261030/slides/assets/slide-31.png)

### Purpose

Explain that the serving client finished, but each original whole-allocation job still ended FAILED during result-reader processing; later CPU verification did not rerun serving.

### Technical interpretation and reasoning

Follow the sequence by stage. Static and mock checks only exercised prepared examples, so they did not model AIPerf’s actual export directory. In job 27136, both semantic prefill/decode routes and the GPU client finished, then the reader failed on a nested export path. Job 27145 again completed the client, but its summary failed when two aliases of the same home directory were compared as different strings. Job 27152 ran the corrected reader on CPU against both real datasets. It verifies post-processing only; the original GPU jobs remain terminal FAILED.

### Terms and symbols to understand

- **portable replay:** Run the packaged deployment and client on the separate target environment, including its real filesystems and result paths.
- **reader / post-processing:** Code that finds client exports, joins them with metadata, and calculates a report after serving. A reader failure can occur after GPU serving has finished.
- **canonical vs lexical path:** Canonical resolves links and aliases to one filesystem location; lexical is the path text as written. They may name the same directory but compare unequal as strings.
- **whole-allocation replay:** The full GPU deployment/client job plus its result processing on the assigned allocation. A CPU-only reader check is not this replay.
- **scheduler FAILED:** The scheduler’s terminal job state remains failure even if raw measurements can later be recovered and parsed.
- **recovered raw score:** A metric read successfully from a failed job’s retained outputs. It does not change that job to a successful deployment.
- **compute-only:** A zero-GPU CPU job used here to test the reader against real saved datasets; it did not start Qwen or send serving requests.

### Interpreting the evidence or diagram

- The first repair recognized exports in an immediate child directory. The second resolved /scratch/home and /home to a canonical input root before comparing paths. Both were real reader defects after client completion, not a measured serving regression.
- The recovered raw result for 27145 is 3,055.330517 good output tokens/s. It can be reviewed as raw performance evidence, but the scheduler job did not complete successfully as a whole-allocation deployment, and no whole-allocation GPU replay was run after repair.

### Tradeoff and strength of evidence

- **Observation:** Two actual GPU jobs finished the client and semantic routes but failed in result reading; zero-GPU job 27152 passed both repaired readers on both retained datasets.
- **Hypothesis:** Path-handling bugs caused the post-client failure states.
- **Supported conclusion:** Reader repairs are verified on real outputs; the original 27136/27145 scheduler states remain FAILED.
- **Unknown / limitation:** End-to-end deployment with corrected readers on the full GPU allocation was not rerun.

### Spoken script

The first portable GPU job completed prompt processing, token generation, and the client, then failed when the result reader looked in the wrong export folder. The next job also finished serving, but its summary treated two names for the same home directory as different paths. A CPU-only job later checked the fixed reader against both real datasets. The original GPU jobs remain failed; we did not rerun the complete allocation after repair.

### Avoid this interpretation

Do not convert FAILED scheduler records into passes, call CPU reader verification a GPU replay, or present 3,055.330517 as a successful whole-allocation rerun.

### Transition

The final slide separates retained findings from validation work that remains proposed or unknown.

---

<a id="slide-32"></a>

## Slide 32 — What the evidence supports next

![Slide 32](../../submission-review/ai-journey-update-20261030/slides/assets/slide-32.png)

### Purpose

Summarize what current evidence supports and make clear that the listed follow-up checks are proposals, not completed runs.

### Technical interpretation and reasoning

The three statements form an evidence-based decision chain: keep the replicated target-only N64 service; require activation, KV transfer, and output evidence for any new path; then complete independent checks. The sparse-graph result does not change the selection because its memory saving did not improve goodput. The missing checks are official full-set accuracy and a whole-allocation portable replay after reader repair. They are not represented as scheduled work.

### Terms and symbols to understand

- **target-only / EAGLE:** Target-only serves only the main model. EAGLE proposes draft tokens for that model to verify; the tested shallow full configuration lost performance.
- **independent validation:** A separate check of official full-set accuracy or the complete deployment, beyond the serving score and helper tests.
- **adopt a configuration:** Choose it as the team’s submission/deployment setting after evidence review. A high isolated observation alone is not enough.
- **source or CPU evidence:** Source shows what code may support; CPU fixtures test narrow helper behavior. Neither shows that the full GPU service activated the path or produced correct results.
- **unknown:** No sufficient retained measurement establishes the answer. It must not be described as zero, passed, or healthy.
- **official accuracy:** The full organizer quality evaluation; it must reach at least 99% of the FP8 reference and remains unverified.

### Interpreting the evidence or diagram

- Retain the replicated target-only N64 configuration rather than the highest isolated score. Cache, cap, and polling changes showed no useful gain; the tested shallow EAGLE configuration lost; sparse graph candidate goodput was 0.370208% below the earlier control.
- Any new implementation should show the intended backend active, correct KV movement, and valid outputs before its performance score is interpreted. CPU fixtures or source inspection alone do not satisfy that standard.

### Tradeoff and strength of evidence

- **Observation:** The selected N64 service has repeated full-run evidence; several optimization trials did not show useful gain. Accuracy and post-repair portable replay remain open.
- **Hypothesis:** Path-specific runtime and output checks can prevent unsupported deployment claims.
- **Supported conclusion:** Keep the reproduced service and treat the listed validation as future work, not as completed or queued research.
- **Unknown / limitation:** Official accuracy, full deployment behavior after reader repair, and a compatible compiled RoPE/KV path remain unknown.

### Spoken script

Keep the replicated configuration that serves only the target model at a load of 64 simultaneous requests; one isolated high score is not enough to replace it. For a new method, first show that its backend ran, cached attention state moved correctly, and answers passed checks. Still open are the organizer’s full accuracy test and a complete portable GPU replay after reader repair. Those are proposed validation steps, not work already scheduled or completed.

### Avoid this interpretation

Do not claim official accuracy passed, repaired portable serving was fully rerun, sparse graphs improved goodput, or the compiled model interface was fixed.

### Transition

End here. In questions, separate measured observation, supported conclusion, and what remains unknown.

---

<a id="slide-33"></a>

## Slide 33 — The task: same 65-million-cell airflow calculation

![Slide 33](transcript-assets/slide-33.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Define the fixed CPU workload and the performance quantity being optimized. The comparison holds the prescribed calculation constant and asks how efficiently the cluster executes it.

### Technical interpretation and reasoning

Read the figures as the fixed-work contract: 65,334,765 mesh cells are distributed over four nodes and 512 MPI ranks, or 128 ranks on each node. An MPI rank is a software process; it is not the same thing as a physical CPU core. The prescribed calculation runs 150 solver iterations, with 149 timed samples because the first iteration is excluded from the reported mean. The unit is wall-clock seconds per solver step, so a smaller value means less elapsed time for each iteration. This slide defines the work and metric; it does not report an optimization result.

### Terms and symbols to understand

- **65.3 million:** Rounded display of the 65,334,765-cell mesh.
- **MPI rank:** One distributed solver process; 512 total means 128 per node on four nodes.
- **s/step:** Wall-clock seconds per solver iteration, not seconds of simulated driving.
- **physical CPU core:** A hardware execution core. An MPI rank is a software process; ranks may be bound to cores, but the mapping must be verified rather than assumed.

### Interpreting the evidence or diagram

- Read this as a workload definition, not a result comparison: same mesh and required solver work, executed on four CPU nodes.
- The 149 timed samples begin after the first solver iteration; the complete run still performs all 150 steps.
- The task is to reduce runtime through better CPU-resource use, not by reducing mesh size or required work.

### Tradeoff and strength of evidence

- **Observation:** The fixed run has substantial parallel work: roughly 65.3 million cells distributed across 512 ranks.
- **Hypothesis:** A more effective distribution and placement of work may reduce time per step.
- **Supported conclusion:** The slide establishes the measurement frame; it reports no tuning win by itself.
- **Unknown / limitation:** It does not identify a bottleneck or establish a causal performance improvement.

### Spoken script

We are optimizing the prescribed OpenFOAM airflow calculation, not changing its mathematics. The mesh has 65.3 million cells. On four nodes, 512 MPI ranks perform all 150 solver steps. The first iteration is excluded from timing, leaving 149 measured steps. We compare the average wall-clock seconds per step, where lower is better. That makes this a fixed-work CPU-efficiency question.

### Avoid this interpretation

Do not call 65.3 million the exact count, do not describe the 149 timed steps as the whole solve, and do not treat the displayed task definition as evidence of a speedup. The retained drag coefficient is a physical sanity check, not this performance metric.

### Transition

Next, show which preparation stages must be retained for a valid end-to-end run.

---

<a id="slide-34"></a>

## Slide 34 — The whole required pipeline comes before the score

![Slide 34](transcript-assets/slide-34.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Explain why the score is meaningful only after preserving the full required pipeline, and distinguish mesh decomposition from CPU affinity.

### Technical interpretation and reasoning

The sequence is part of the measured task: decomposePar assigns mesh cells to MPI ranks; renumberMesh changes the ordering of local cell data; potentialFoam initializes flow fields; applyBoundaryLayer applies the required boundary treatment; simpleFoam then performs all 150 solver steps. Decomposition determines which cells a process owns and therefore which neighboring-cell exchanges cross process boundaries. CPU affinity determines where a rank runs. Affinity can affect access to nearby CPU cores and memory, but it does not change the cells owned by that rank. Both decisions can affect performance, and they must not be confused.

### Terms and symbols to understand

- **MPI:** Message Passing Interface; separate ranks exchange data, especially across partition boundaries.
- **decomposePar:** OpenFOAM utility that partitions mesh cells among ranks.
- **CPU affinity:** Binding a process or rank to CPU resources; distinct from assigning it mesh cells.
- **neighbor exchange:** Ranks exchange field values for cells adjacent across their partition boundary; more cut edges are only a proxy for the amount and cost of this traffic.

### Interpreting the evidence or diagram

- Follow the orange arrows from preprocessing into the solver; the final timing is not a substitute for those stages.
- A decomposition answers which cells a rank owns. Affinity answers where that rank executes.
- The sequence shown is the complete required preparation and 150-step solve, not an optional menu.

### Tradeoff and strength of evidence

- **Observation:** The pipeline contains data setup, initialization, boundary treatment, then iterative solving.
- **Hypothesis:** Choices in decomposition and placement can affect execution while preserving the prescribed calculation.
- **Supported conclusion:** Valid comparisons must retain each required stage and its successful completion.
- **Unknown / limitation:** This flow diagram alone does not measure the cost of each stage or prove which mapping is faster.

### Spoken script

Before comparing solver times, we keep the entire required pipeline: assign cells to MPI ranks, reorder the local data, initialize the flow, apply the prescribed boundary layer, and run all 150 simpleFoam steps. Decomposition decides which cells each rank owns. CPU affinity decides which CPU runs the rank. Those are separate decisions, and a valid run must preserve every preparation step as well as the solve.

### Avoid this interpretation

The slide gives process order, not per-stage timings, and it does not establish that affinity was measured or optimized in a particular result.

### Transition

With the workload and pipeline fixed, the next slide tests whether a locality proxy predicted solver runtime.

---

<a id="slide-35"></a>

## Slide 35 — A smaller partition cut did not make the solver faster

![Slide 35](transcript-assets/slide-35.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Show a failed NUMA-aware locality hypothesis and explain why a partition-graph proxy cannot stand in for a runtime measurement.

### Technical interpretation and reasoning

The orange −10.63% is a reduction in a partition-graph cut proxy: fewer weighted mesh connections cross the selected locality boundary. It does not mean communication time fell by 10.63%. Actual exchanges also depend on message sizes, frequency, network and MPI behavior, while solver time includes computation, synchronization, memory access and other work. The measured mean moved in the wrong direction, from 13.881 to 14.359 seconds per step (+3.4416%, slower). Thus the proxy improvement did not produce a runtime improvement in this comparison. The slide leaves the cause open because MPI wait, bandwidth, CPU frequency, power and memory-page placement were not measured.

### Terms and symbols to understand

- **NUMA:** Non-Uniform Memory Access: memory access cost can depend on which CPU socket or locality domain owns the memory.
- **graph cut:** A proxy count/weight of partition connections crossing a selected boundary; it is not a direct measurement of communication time.
- **−10.63%:** The graph-cut proxy was reduced by 10.63% for this candidate.
- **+3.4416%:** The solver mean became 3.4416% slower in the compared observation.
- **partition graph cut:** A weighted count of mesh-neighbor connections split between partitions. It estimates potential interface traffic, but does not measure bytes transferred, MPI wait, network time or total solver runtime.
- **NUMA locality:** On multi-socket servers, a CPU core can access memory attached to its own socket more directly than memory attached to another socket; placement can therefore affect latency and bandwidth.
- **MPI wait:** Time a process spends waiting for other processes or communication to complete; it was listed as unmeasured here.

### Interpreting the evidence or diagram

- Orange marks proxy improvement; red marks worse measured solver time. Their signs make the mismatch clear.
- A smaller proxy can coexist with slower execution because other partition properties and runtime effects also matter.
- The slide explicitly leaves the cause unmeasured; it records a rejected candidate, not a diagnosis.

### Tradeoff and strength of evidence

- **Observation:** Graph cut fell 10.63%, while mean runtime rose from 13.881 to 14.359 seconds per step.
- **Hypothesis:** Grouping work by memory locality might reduce remote-memory and interface cost.
- **Supported conclusion:** The unchanged NUMA-aware branch was closed; graph cut alone did not predict solver speed.
- **Unknown / limitation:** MPI wait, bandwidth, frequency, power, page residency, and other possible causes were not measured.

### Spoken script

We tested a NUMA-aware idea: grouping work by locality should reduce remote-memory or interface cost. The graph-cut proxy fell by 10.63 percent, but the measured solver mean worsened from 13.881 to 14.359 seconds per step, a 3.4416 percent slowdown. That is why we closed this unchanged candidate. A graph proxy describes the partition; it is not measured runtime or proof of less communication time.

### Avoid this interpretation

The comparison changed other partition properties, so do not attribute the slowdown to one mechanism. A separate offline mapping with a 4.5741% smaller proxy had no solver run and is not evidence of performance. Do not interpret the percentages as reciprocal measures.

### Transition

The next comparison asks whether the better observed decomposition changes with node count.

---

<a id="slide-36"></a>

## Slide 36 — Observed scaling changed which decomposition led

![Slide 36](transcript-assets/slide-36.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Compare the observed Scotch and hierarchical means across one-, two-, and four-node allocations, while explicitly limiting the inference because work endpoints and allocations differ.

### Technical interpretation and reasoning

The orange Scotch and dark-teal Hierarchical labels identify the two decomposition methods; every value is a mean in seconds per solver step, so lower is faster. Hierarchical is lower in the one-node observation (14.366 vs 14.451) and the two-node observation (7.170 vs 7.463); Scotch is lower in the four-node observation (3.678 vs 3.820). These are not points on a controlled scaling curve: each used a separate allocation, and the required endpoint changed from 40 to 80 to 150 steps. Node count, run length, allocation conditions and configuration therefore vary together. The bars describe what was observed; they cannot isolate node count as the cause of the ranking change.

### Terms and symbols to understand

- **Scotch:** A graph-based mesh-decomposition method used by the OpenFOAM workflow.
- **Hierarchical:** A decomposition method that partitions the mesh using a hierarchy of spatial divisions.
- **s/step:** Mean wall-clock seconds for each timed solver iteration; lower is better.
- **descriptive comparison:** A report of observed values. Because node count, step endpoint and allocation changed together, it cannot isolate the effect of any one factor.

### Interpreting the evidence or diagram

- At one node hierarchical is slightly lower; at two nodes hierarchical is lower; at four nodes Scotch is lower.
- The displayed step endpoints are not identical, and each result came from a separate allocation.
- This is descriptive evidence about observed candidate means, not a controlled strong-scaling curve.

### Tradeoff and strength of evidence

- **Observation:** Hierarchical leads the displayed two-node pair, while Scotch leads the four-node pair; the one-node means are close with hierarchical lower.
- **Hypothesis:** The preferable partition may depend on node count, rank density, and allocation-specific conditions.
- **Supported conclusion:** There is no single decomposition winner across these observations; the four-node Scotch result motivates closer review.
- **Unknown / limitation:** Different allocations and endpoints prevent assigning the differences to node count alone or claiming causal scaling efficiency.

### Spoken script

The observed leader changes with the allocation. Hierarchical has a slightly lower one-node mean and leads at two nodes, while Scotch leads at four nodes. The values are seconds per solver step. However, these are separately allocated runs with different prescribed endpoints—40, 80 and 150 steps—so this is descriptive scaling evidence, not a controlled causal comparison. The candidate choice must be evaluated at the intended node count and rank density.

### Avoid this interpretation

Do not calculate or claim ideal speedup from these means. The bars show means only, without uncertainty ranges; the separate allocations and run lengths matter. This slide alone cannot show a universal advantage for either method.

### Transition

The four-node results can be split further by ranks per node, which is the next comparison.

---

<a id="slide-37"></a>

## Slide 37 — At four nodes, the winner depends on ranks per node

![Slide 37](transcript-assets/slide-37.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Show that the four-node decomposition ranking changes with process density, and identify the lowest reviewed mean without overstating it as a universal optimum.

### Technical interpretation and reasoning

At four nodes, the bars compare observed mean seconds per step at 64, 96 and 128 MPI ranks per node. Orange denotes Scotch and dark teal denotes Hierarchical. Hierarchical has the lower mean at 64 ranks (4.489 vs 10.310) and 96 ranks (4.922 vs 7.146); Scotch is slightly lower at 128 ranks (3.678 vs 3.820). Across four nodes these settings use 256, 384 and 512 ranks, respectively, but a rank is a process, not automatically one physical core. The 128-rank Scotch observation is the lowest reviewed mean among these six logs. Separate allocations and differences in requested CPU counts confound the comparison, so it identifies a candidate to repeat, not proof that rank density or method alone caused the difference.

### Terms and symbols to understand

- **ranks per node:** Number of MPI processes placed on each node; across four nodes the displayed settings correspond to 256, 384, and 512 ranks.
- **s/step:** Mean measured wall-clock seconds per solver step.
- **lowest reviewed mean:** The smallest mean among the reviewed observations in this set, not proof of global optimality.
- **rank density:** The number of MPI processes assigned per node. It is distinct from physical-core count and does not by itself prove CPU binding or exclusive core use.

### Interpreting the evidence or diagram

- At 64 and 96 ranks per node hierarchical is lower; at 128 ranks per node Scotch is lower by about 0.142 seconds per step.
- The highlighted takeaway identifies Scotch-128 at 3.677906731 seconds per step as the lowest reviewed mean.
- Each bar summarizes a separate allocation; requested CPU counts also differ in some configurations.

### Tradeoff and strength of evidence

- **Observation:** The preferred method flips at the highest displayed rank density; Scotch-128 has the smallest observed mean among these six logs.
- **Hypothesis:** Decomposition quality may interact with the density of ranks on each node.
- **Supported conclusion:** Choose based on the measured node count and rank density; method name alone does not predict the winner.
- **Unknown / limitation:** Separate allocations and differing requested CPU counts prevent attributing the differences solely to decomposition or density.

### Spoken script

At four nodes, rank density changes which method has the lower observed mean. Hierarchical leads at 64 and 96 ranks per node. At 128, Scotch records 3.678 seconds per step versus 3.820 for hierarchical. That 3.678-second value is the lowest reviewed mean among these six observations. We treat it as a candidate for confirmation, not a causal effect or universal best method, because these are separate allocations and some requested CPU counts differ.

### Avoid this interpretation

The decimal labels are seconds per step, not speedup factors. The bar display has no explicit axis or error bars; avoid implying statistical significance from bar lengths. The slide does not establish stable repeatability.

### Transition

The next slide examines the full timing distribution behind the Scotch-128 mean, especially its slow tail.

---

<a id="slide-38"></a>

## Slide 38 — Keep the slow step in the mean; inspect the tail

![Slide 38](transcript-assets/slide-38.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Explain why every timed iteration, including an extreme slow step, remains in the official-style arithmetic mean, and separate observation from causal diagnosis.

### Technical interpretation and reasoning

These are distribution summaries for the 149 timed steps: median 3.298742 s, 95th percentile 3.795740 s, and maximum 35.883552 s at solver Time 119. The median is the middle observation; the p95 marks the point below which about 95% of observations fall. The arithmetic mean is different: add every sample and divide by 149, so the 35.9-second step remains in it and pulls the mean upward. Keeping that sample preserves the actual run rather than hiding a slow event. The orange and red markers distinguish typical timing from the extreme maximum; printed numbers carry the exact units. The event is visible, but its cause is not identified by these timings.

### Terms and symbols to understand

- **median:** Middle value after sorting the 149 timed samples.
- **95th percentile (p95):** A value at or below which approximately 95% of samples fall, under the percentile convention used.
- **maximum:** Largest recorded sample; here 35.883552 seconds at solver Time 119.
- **Time 119:** Solver iteration/time index reported by the run, not 119 seconds of wall-clock duration.
- **arithmetic mean:** Sum of all timed values divided by the number of values. Unlike the median, a very large sample can noticeably raise it.
- **tail:** The slowest portion of the timing distribution; p95 summarizes a high percentile, while the maximum records the single slowest sample.

### Interpreting the evidence or diagram

- The median and p95 are near 3.3–3.8 seconds, but one retained step is about 35.9 seconds.
- All 149 samples stay in the arithmetic mean; removing the outlier would change the stated performance metric.
- The red color marks the extreme maximum; it does not indicate a known failure mechanism.

### Tradeoff and strength of evidence

- **Observation:** One unusually slow step appears at index 119, while the center and p95 are much smaller.
- **Hypothesis:** A transient system or application event may have caused the spike, but telemetry is needed to test possibilities.
- **Supported conclusion:** Preserve the tail and investigate it; do not trim the slow point or alter the prescribed endpoint.
- **Unknown / limitation:** MPI wait, bandwidth, CPU frequency, power, and memory-page residency were not measured sufficiently to identify a cause.

### Spoken script

The median step is 3.299 seconds and the 95th percentile is 3.796 seconds, but the maximum reaches 35.884 seconds at solver Time 119. We retain all 149 timed samples in the arithmetic mean. That slow point is part of the measured run, not something to discard because it is inconvenient. The trace establishes that a spike occurred; it does not explain why. We need instrumentation and independent repeats to study its cause and stability.

### Avoid this interpretation

Do not call solver Time 119 119 seconds; it is the reported iteration/time index. Do not imply the median or p95 is the official arithmetic mean. Cause is explicitly unknown: missing telemetry is not evidence that MPI, memory, or hardware was healthy.

### Transition

That uncertainty is why the next slide asks for an independently repeated, fully evidenced run.

---

<a id="slide-39"></a>

## Slide 39 — A reproducible candidate needs more than a fast log

![Slide 39](transcript-assets/slide-39.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Distinguish a reviewed candidate timing from an accepted official result and list the proofs required from an independent confirmation.

### Technical interpretation and reasoning

The left side is an already reviewed candidate observation: Scotch-128 averaged 3.677906731 seconds per step over 149 samples. The right side is a different state of evidence: job 25940700 was shown waiting in Q/q5 at 15:06 UTC because node_pool resources were insufficient, with no result yet. Its frozen 54-file bundle is an exact, fixed input package; hashes and seals are checks that source, mesh and outputs match the recorded files. Provenance means the record of which inputs, commands, resources and outputs produced a run. The checklist also asks for successful return codes from every stage and proof that 512 physical CPU cores across four hosts were actually allocated. These are requirements for confirmation, not checks already passed.

### Terms and symbols to understand

- **Q/q5:** Scheduler queue/state labels shown in the dated observation; the slide reports the job waiting, not executing.
- **Scotch-128:** Scotch decomposition at 128 MPI ranks per node on four nodes.
- **seal:** Recorded identity/integrity evidence for source, mesh, or output files; the slide lists required checks, not completed checks.
- **frozen input bundle:** A fixed, versioned set of input files kept unchanged for a repeat, so the comparison uses the same declared inputs.
- **hash / seal:** A cryptographic digest or integrity record used to check whether a file is byte-for-byte the recorded version; a seal is evidence to verify, not a performance result.
- **provenance:** Traceable record of input identities, software/source, commands, allocated resources and produced outputs.
- **scheduler terminal proof:** A scheduler record showing a definite final state such as completed or failed, rather than merely queued or running.
- **return code:** A program exit status; checking each stage helps establish that every required command completed successfully.

### Interpreting the evidence or diagram

- The candidate has a measured mean and 149 samples, but that alone does not establish official acceptance.
- The independent job is queued and has no result in the shown status snapshot.
- The checklist is prospective proof required from that queued confirmation, not claims that the checks already passed.

### Tradeoff and strength of evidence

- **Observation:** The best reviewed candidate is 3.677906731 s/step; its independent confirmation job is waiting because node_pool resources are insufficient.
- **Hypothesis:** A fresh, frozen, full-pipeline repeat can test reproducibility and verify provenance and resource placement.
- **Supported conclusion:** Report the existing number as a candidate observation, not an accepted official score; review the repeat before choosing next.
- **Unknown / limitation:** The slide gives no result, terminal scheduler proof, or completed verification for job 25940700.

### Spoken script

The reviewed Scotch-128 candidate averages 3.677906731 seconds per step over 149 samples. That is a candidate observation, not an accepted official score. We submitted job 25940700 as an independent confirmation, but the dated scheduler status still shows it queued because node-pool resources are insufficient, so it has no result. Confirmation must preserve the input bundle, execute initialization and all 150 steps, record explicit stage exits, prove 512 physical cores across four hosts, and seal source, mesh, and outputs.

### Avoid this interpretation

All scheduler wording is a historical snapshot at 15:06 UTC on the slide; do not present it as live status. The checklist describes required proof, not verified completion. A fast log by itself is not full reproducibility or acceptance.

### Transition

The final slide summarizes the evidence discipline and the next review decision without claiming a new result.

---

<a id="slide-40"></a>

## Slide 40 — What we learned — and the next measurement

![Slide 40](transcript-assets/slide-40.png)

**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**

### Purpose

Close the HPC section with four measurement principles and the next decision point: inspect complete confirmation evidence before selecting another configuration.

### Technical interpretation and reasoning

The four principles connect a credible measurement to reproducible evidence: include preparation and the full solve; judge runtime rather than a graph-cut proxy; retain all samples, including slow-tail events; and repeat independently. The status line is explicitly a historical snapshot: on 23 October at 15:06 UTC, job 25940700 was still waiting for node_pool resources and had no result. A scheduler query or terminal record proves whether the job ran and how it ended; it does not by itself prove correct inputs or a valid measurement. Hashes, stage return codes, resource-placement evidence and complete output provenance address those separate questions. The next action stated here is to review the confirmation's terminal evidence and timing tails, then use bounded hardware sampling to investigate stability. No later outcome is asserted.

### Terms and symbols to understand

- **terminal proof:** Evidence that the scheduler job reached a definite terminal state, paired with complete run outputs and return codes.
- **bounded hardware samples:** Limited, planned instrumentation samples collected with controlled scope, not an unbounded profiling run.
- **Q/q5:** The queue/state shown in the dated status snapshot, not a current query.
- **bounded hardware sampling:** A small, preplanned set of hardware measurements taken for a stated interval or phase, with scope limited to avoid changing the workload materially.

### Interpreting the evidence or diagram

- The four principles connect validity, measured runtime, preservation of outliers, and independent reproducibility.
- The next step is review, not claiming a performance gain from the queued job.
- The status line freezes the state known at 23 October 15:06 UTC: the confirmation had no result.

### Tradeoff and strength of evidence

- **Observation:** Reviewed four-node data narrowed choices and identified Scotch-128 as the lowest mean among six observations, while the confirmation remained queued in the dated record.
- **Hypothesis:** Reviewing full terminal evidence, tails, and limited hardware sampling may clarify stability before another choice.
- **Supported conclusion:** The work narrows candidates and improves evidence requirements; it does not establish a global optimum or accepted score.
- **Unknown / limitation:** The slide does not report what later happened to job 25940700 or identify the cause of the timing spike.

### Spoken script

We take four lessons forward: measure the whole job, trust runtime evidence over a partition proxy, keep every timing sample, and confirm independently. The reviewed Scotch-128 mean narrowed our choice, but it is not a proven global optimum or accepted score. At the recorded time—23 October at 15:06 UTC—job 25940700 was still queued for node-pool resources and had no result. The next decision is to inspect terminal proof and timing tails, then collect bounded hardware samples before selecting another measurement.

### Avoid this interpretation

This is a dated handoff, not live scheduler status. Do not infer a later success or failure, and do not describe bounded sampling as already collected. The presentation summarizes published evidence; it does not certify new measurements.

### Transition

This concludes the HPC slides; return to the combined presentation's overall research conclusion.
