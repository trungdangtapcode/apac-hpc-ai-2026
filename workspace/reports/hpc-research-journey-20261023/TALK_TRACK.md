# HPC presenter script and likely questions

The owner requested **about 20% HPC and 80% AI**. The published deck has 32 AI slides and eight HPC slides (33–40). Rehearse the concise **3–4 minute** script below inside the combined 15–20 minute presentation. This is a presentation allocation, not a change to the official scoring weights. The longer original script is retained afterward for learning and questions. No reviewed result is available for confirmation job 25940700; the retained 23 October 15:06:39 UTC snapshot shows Q/q5, waiting for node_pool resources.

## Concise script for the eight published slides

| Slide | What to say |
|---|---|
| 33 — Fixed calculation | “We optimize the official airflow-around-a-car calculation: 65.3 million cells, OpenFOAM v2512, double precision. On four CPU nodes we run 512 MPI processes and all 150 required solver iterations. The metric is average seconds per iteration from the second iteration onward. Lower is better.” |
| 34 — Complete pipeline | “We retain every preparation stage: assign cells to processes, restore the original fields, reorder cells, initialize the flow, apply the prescribed boundary layer, then solve. Decomposition decides which cells a process owns; CPU affinity decides where that process runs. They are different optimization choices.” |
| 35 — A failed idea | “Our NUMA-aware partition looked promising because fewer faces crossed logical memory groups. But its measured mean was 3.44 percent slower. We retained the loss and closed that unchanged candidate. A smaller graph cut is a proxy, not measured communication or a guaranteed speedup.” |
| 36 — Scaling | “We compared the prescribed one-, two- and four-node endpoints. Hierarchical leads the two-node observations, while Scotch leads at four nodes. These are different allocations and endpoint lengths, so we show descriptive scaling rather than claim a controlled causal speedup.” |
| 37 — Rank density | “Among six four-node native records, Scotch at 128 ranks per node has the lowest mean: 3.678 seconds per iteration. Hierarchical leads at the lower rank densities. Configuration choice depends on the actual node count and process density; a method name alone is insufficient.” |
| 38 — Timing tail | “The selected record's median is 3.299 seconds, but one step took 35.884 seconds. We keep all 149 timed samples in the mean. The trace shows the event, not its cause. MPI wait, bandwidth, frequency, power and page residency were not measured.” |
| 39 — Independent confirmation | “The old native work and timer checks pass, but final scheduler history and some provenance checks are missing. We therefore report a candidate observation, not an accepted official score. Job 25940700 independently repeats the setting with frozen inputs, explicit exits, physical-core startup checks and field seals.” |
| 40 — Next decision | “We narrowed the configuration choice, rejected a losing hypothesis and strengthened reproduction. The independent repeat is still queued in the dated snapshot. Next we inspect its full results and timing tails, then choose a measured followup. We do not invent a new performance gain from an unrun plan.” |

The portable package's main entry is `submit-best.pbs`; the one/two-node scripts are scaling checks. Keep command syntax and historical provenance detail for questions, not the spoken story.

## Expanded learning script — original 6–8 minute version

The following longer version is retained for private rehearsal and Q&A. Its old 12:52 queue sentence is a historical snapshot; use the current dated status above during the presentation.

## 1. The problem — about 45 seconds

“Our task is to make the same airflow-around-a-car calculation faster. We use the official OpenFOAM v2512 case with about 65 million mesh cells, double precision and the prescribed numerical work. A cell is a small volume of air; many solver processes work on different groups of cells. We are optimizing how that fixed computation uses the CPU cluster. We are not simplifying the geometry, reducing precision or reducing solver iterations.”

Show the pipeline diagram in [Foundations](FOUNDATIONS.md). Explain that solver `Time` is an iteration index for this steady-flow solve, not a second of real driving.

## 2. What we measure — about 45 seconds

“The official performance metric is average wall-clock seconds per solver iteration, starting from the second iteration. Lower is better. We still execute all required steps: 40 on one node, 80 on two nodes and 150 on four nodes. The four-node case is scored; the others explain scaling. We also retain Cd, the dimensionless drag coefficient, as a physical sanity check. Whole-job duration and allocated CPU hours are separate cost metrics, so a lower solver time does not automatically mean a cheaper job.”

Do not call Cd the speed score. Do not turn the Basic sanity check into an invented percentage tolerance.

## 3. Establish a valid baseline — about 50 seconds

“We first checked the real access route and the complete native pipeline on Iris as practice. That result was not a contest score. On ASPIRE-2A we retained every required initialization command and established a CPU baseline. We then compared hierarchical and Scotch decomposition. Decomposition decides which cells each MPI process owns; CPU placement decides where that process runs. In an early same-node pair Scotch's mean was about one percent lower, but the result was noisy, so we did not declare a stable win.”

Use the first half of the [journey picture](figures/research-journey.svg). Emphasize the baseline and one controlled factor, not command syntax.

## 4. A useful failed experiment — about one minute

“Our NUMA-aware Scotch candidate looked promising on the partition graph: about 10.6 percent fewer faces crossed the logical memory groups. But it changed other partition properties too. When we ran the solver, the mean increased from 13.881 to 14.359 seconds per step, a 3.44 percent slowdown. We kept the losing data and closed that unchanged candidate. This taught us that a graph cut is only a proxy. We did not measure memory traffic or MPI wait time, so we cannot claim a hardware cause for the slowdown.”

A separate offline rank-placement search keeps the same partitions and reduces the logical cut by 4.57%. State explicitly that this is a graph candidate; its mapped solve has not been submitted and is not a speedup result.

## 5. Scaling changed the observed choice — about one minute

“Next we compared rank density and node count. At two nodes, hierarchical with 128 MPI ranks per node gave the lowest mean in that set. At four nodes, the lowest of six native records is Scotch with 128 ranks per node: 3.678 seconds per step. Hierarchical leads the 64- and 96-rank-per-node comparisons, while Scotch leads at 128. We therefore cannot choose a configuration from its name or from a one-node result alone.”

Show [four-node means](figures/four-node-means.svg), then [observed scaling](figures/observed-scaling.svg). Say that allocations differ and the prescribed endpoints differ. Avoid calling the plotted difference a proven causal speedup, a global optimum, or an improvement over the organizer reference.

## 6. The mean and the slow steps — about 50 seconds

“The record with the lowest native mean is not perfectly stable. Its median is about 3.299 seconds, but one iteration took 35.884 seconds. We keep that iteration in the official-style arithmetic mean; we do not remove it to make the result look faster. Every four-node record has a native short-sample warning. The traces identify slow iterations, but they do not tell us whether MPI, CPU scheduling, memory or the filesystem caused them. That needs additional measurements.”

Show [iteration durations](figures/iteration-spikes.svg). Explain the difference between an observed event and a causal diagnosis.

## 7. What we can claim and what comes next — about one minute

“We now have a defensible native comparison and a clear next experiment. The older four-node jobs lost their final scheduler history, and their wrapper did not retain every command return code. We can report their native measurements, but we do not present them as accepted official scores. We have submitted an independent Scotch128 confirmation with frozen source hashes, complete initialization, explicit command exits, physical-core startup checks and field seals. We will review that run before claiming reproducibility, then investigate the timing tails with bounded diagnostics.”

The submitted confirmation is **25940700.pbs101**, maximum 40 minutes on four exclusive 128-core nodes. It was queued in the retained 12:52 UTC snapshot; the script has no new result yet. Keep this sentence current when rehearsing. The 5,000-SU campaign ceiling is a research spending limit, not the CPU project's remaining site balance.

## Questions you should be able to answer

| Likely question | Short answer |
|---|---|
| Is an MPI rank a CPU core? | It is a process. A job can reserve 128 cores and run 64 processes; allocated CPUs and active ranks differ. |
| Why does adding nodes not give exact linear speedup? | Communication, synchronization, imbalance and memory behavior add costs. Our endpoint lengths and allocations also differ. |
| Why did the smaller graph cut lose? | Other partition properties changed and the proxy is not measured traffic. The recorded data do not establish the cause. |
| Is 4.57% less cut equal to 4.57% faster? | No. It is only an offline candidate; the runtime test is unmeasured. |
| Can you delete the 35.88-second sample? | No. The native Average includes every measured step. We retain it and investigate it. |
| Why is the fastest configuration not called the final score? | Native work/time checks pass, but the old terminal scheduler/return/provenance evidence is incomplete. A stronger confirmation is in the queue. |
| Are your extra proof checks new contest rules? | No. They are our research/reproducibility checks, not additional official eligibility conditions or a judge acceptance decision. |
| Does UnknownJobId mean failure? | No. It means that query no longer provides the job history; native logs and terminal accounting answer different questions. |
| Can the HPC task use the AI GPUs? | GPU acceleration is prohibited for this CPU task in every tier. AI resources and scoring are separate. |
| Do we need a source patch for Bonus points? | No. Carefully explained Basic tuning can earn Bonus recognition. Experimental changes are optional and require self-proof. |
| What did you actually improve? | We narrowed configuration choices, rejected a losing locality idea and strengthened reproducibility. The four-node native lead is observational; a stable performance gain has not yet been established. |
| What did you not collect? | Measured MPI traffic/wait, bandwidth, frequency, power, page residency and solve-time affinity. Missing telemetry is not zero or healthy. |

The supporting reviews and raw sources are linked from [the journey](JOURNEY.md). The presentation should explain the reasoning and limits, not display this directory structure.
