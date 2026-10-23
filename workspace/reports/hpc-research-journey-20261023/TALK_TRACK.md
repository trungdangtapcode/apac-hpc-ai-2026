# HPC presenter script and likely questions

Use this as a **6–8 minute HPC section** inside the single 15–20 minute combined AI/HPC presentation. Coordinate time with the AI presenter. The script explains the computation and decisions; job paths and detailed proofs stay in the linked reports. The observations below are dated 23 October, before confirmation job 25940700 has produced a reviewed result.

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
| Does UnknownJobId mean failure? | No. It means that query no longer provides the job history; native logs and terminal accounting answer different questions. |
| Can the HPC task use the AI GPUs? | GPU acceleration is prohibited for this CPU task in every tier. AI resources and scoring are separate. |
| Do we need a source patch for Bonus points? | No. Carefully explained Basic tuning can earn Bonus recognition. Experimental changes are optional and require self-proof. |
| What did you actually improve? | We narrowed configuration choices, rejected a losing locality idea and strengthened reproducibility. The four-node native lead is observational; a stable performance gain has not yet been established. |
| What did you not collect? | Measured MPI traffic/wait, bandwidth, frequency, power, page residency and solve-time affinity. Missing telemetry is not zero or healthy. |

The supporting reviews and raw sources are linked from [the journey](JOURNEY.md). The presentation should explain the reasoning and limits, not display this directory structure.
