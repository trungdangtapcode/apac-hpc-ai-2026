# HPC section speaker notes

Target duration: 3–4 minutes. The slides are numbered 33–40 for integration after the existing 32 AI slides. Sources and background credits are in each PowerPoint slide’s Notes pane and `slide-content.json`.

## Slide 1 · The task: same 65-million-cell airflow calculation

We optimize execution of the official OpenFOAM v2512 car-flow case, not its mathematics. The mesh contains 65,334,765 cells. The job completes the prescribed preparation and 150 solver iterations on four nodes. The measured metric is the solver's average wall-clock seconds per time step, beginning with the second solver iteration; lower is better. The retained final drag coefficient is a physical sanity signal, not the performance score.

## Slide 2 · The whole required pipeline comes before the score

MPI means Message Passing Interface: separate solver processes exchange information about cells at partition boundaries. Mesh decomposition assigns cells to ranks; CPU affinity maps ranks to CPUs. These are different decisions. A complete run includes mesh decomposition, renumbering, potential-flow initialization, boundary-layer setup, and the 150-step simpleFoam solve. Skipping preparation or solver work would not be a valid comparison.

## Slide 3 · A smaller partition cut did not make the solver faster

The NUMA-aware decomposition hypothesis was that grouping work by memory locality might reduce communication and improve speed. Its graph cut fell by 10.63%, but the solver mean worsened from 13.881 to 14.359 seconds per step, a 3.4416% slowdown. The comparison also changed other partition properties, so the cut alone cannot explain the runtime. We closed the unchanged branch. A separate offline mapping reduced a graph cut by 4.5741% but has no measured solver result.

## Slide 4 · Observed scaling changed which decomposition led

These are separately allocated observations at 128 ranks per node, not an identical-work strong-scaling experiment. Endpoints are 40, 80 and 150 solver steps. Hierarchical led the two-node pair at 7.169996913 seconds per step versus Scotch at 7.462835189. At four nodes, Scotch led at 3.677906731 versus hierarchical at 3.819929017. Different allocations and endpoint lengths limit causal claims.

## Slide 5 · At four nodes, the winner depends on ranks per node

The six reviewed four-node logs all complete 150 steps with 149 timed samples. At 64 and 96 ranks per node, hierarchical has the lower observed mean; at 128, Scotch is lower. Requested CPU counts differ across some configurations, and these are separate allocations. We therefore describe measured candidate means, not a causal effect or a universal best method. The lowest mean is 3.677906731 seconds per step for Scotch-128.

## Slide 6 · Keep the slow step in the mean; inspect the tail

Scotch-128 has a median of 3.298742 seconds, p95 of 3.795740 seconds, and maximum of 35.883552 seconds at solver Time 119. All 149 timed samples remain in the arithmetic mean. The review did not collect enough hardware counters to attribute the spike to MPI, CPU scheduling, memory or I/O. The sample-size warning motivates independent repeats; it does not authorize removing the slow point or changing the prescribed endpoint.

## Slide 7 · A reproducible candidate needs more than a fast log

The best reviewed four-node native mean is a candidate observation, not an accepted official score. The independent confirmation job 25940700 was submitted on 23 October at 12:51 UTC. A fresh scheduler query at 15:06 UTC still showed Q/q5 with the comment Not Running: Insufficient amount of resource: node_pool. No result is available. The job is configured to re-run the full preparation and 150-step solve on four exclusive nodes. Its fresh 54-file bundle requires source/mesh identity, explicit stage returns, startup 512-physical-core/four-host proof, and zero-field seals. These are required proofs, not completed checks.

## Slide 8 · What we learned — and the next measurement

The research has narrowed choices, rejected the unchanged NUMA-aware branch, and identified Scotch-128 as the lowest mean among six reviewed four-node native observations. This is not a proven global optimum or accepted score. At 15:06 UTC on 23 October, job 25940700 was still Q/q5; PBS reported Not Running because node_pool resources were insufficient. No result was available. Next review its complete terminal proof and all iteration tails, then use bounded matched sampling to investigate stability before choosing another configuration.
