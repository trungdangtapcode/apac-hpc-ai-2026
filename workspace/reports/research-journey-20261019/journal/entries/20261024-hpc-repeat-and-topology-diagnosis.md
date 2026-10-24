# Independent repeat improves the observed mean; topology qualification still blocks placement

## Question, prior evidence and intervention

Can the four-node Scotch 512-rank result repeat with complete source, mesh, initialized-field and terminal-job evidence? Job 25940700 repeats the 150-step configuration; jobs 25943865 and 25947168 test method-3 rank ordering at four and 512 ranks. The previous native mean was 3.677906731 s/step with a 35.883552358-second maximum. This is a repeat, not a changed placement experiment.

## Observations and assessment

[Complete reviewed artifacts and replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md): 25940700 finishes Exit 0, mean **3.364622070 s/step**, median 3.282042638 s, p95 3.936922984 s, maximum 5.900973952 s. All 150 steps, 149 timings, fixed iterations, finite force rows, mesh/source checks and before/after initialized zero-field seals pass. The mean falls 8.52%, median falls 0.51%, p95 rises 3.72%; no samples are removed. The old extreme maximum did not recur. Separate allocations and absent distributed hardware telemetry preclude a causal speedup claim. The native statistical recommendation is 101 samples, with no short-sample warning; it is not an independent confidence interval.

The actual four-rank reorder passes the intended [0, 2, 1, 3] mapping. The large preflight exits 1 after all 512 identity processes report the generic combined topology failure. No candidate launch occurs, so this does not reject the graph assignment. Nonfatal XRC/SRX warnings are retained; no causal role is established. Serial decomposition took 419.14 seconds and solver launch 549.16 seconds; launcher CPU/RSS is not distributed rank telemetry.

## Budget and next decision

Fresh terminal PBS resources at verified CPU rate 1 justify retiring only these three known reservations. Their conservative allowance is rounded to 164 SU, including full-node treatment of the four-core diagnostic. Unknown shared and older maxima remain intact, with deliberate possible double counting. The 5,000-SU ceiling is unchanged: before further admission, commitment 4,688.2 SU and headroom 311.8 SU. These are planning allowances, not exact posted charges.

Derive a separate bounded diagnostic from the failed payload. Preserve mapping and acceptance gates; collect each rank's pre/post MPI affinity, physical-core lookup and NUMA lookup status before a collective failure decision. Only that evidence can identify the failed subcheck. A local synthetic MPI singleton test passes; a two-CPU mask is rejected. Neither proves a cluster fix. Submit only after safe review and locked fresh capacity/budget checks; no blind solver or proxy-polishing run. Keep the balanced mapping separate and unsubmitted until qualified.

The prior 23 October queue snapshot is historical; all three jobs are terminal in the 24 October query. Submission slides remain their dated snapshot. No background Codex or schedule is enabled.

## Reviewed diagnostic payload checkpoint

The [derived bundle](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-mpi-placement512-diagnostic-20261024/PLAN.md) is sealed and root reviewed. Its C probe emits one bounded topology record per rank and uses MPI_Allreduce before a failure decision. The existing 512-rank identity/candidate validators and aggressive assignment are unchanged. Local C uses synthetic MPI declarations only: one CPU passes, two CPUs fail without a mapping record. The unchanged randomized mapping suite passes one positive and rejects seven negatives. No actual cluster fix, candidate mapping, solver speedup or submission is claimed by this preparation checkpoint.

## Admission and next evidence gate

The derived diagnostic was submitted once as **25956623.pbs101**. Locked pre-admission checks found both own CPU and AI PBS queues empty, verified the three terminal outcomes and fresh CPU rate/balance, and reserved 25.6 SU. Post-submit 03:12:23 UTC: Q/q5, insufficient node_pool. The CPU campaign remains below its unchanged 5,000-SU ceiling: 4,713.8 SU committed, 286.2 SU headroom; shared/older unknown maxima remain. No solver, duplicate intent or background schedule was launched. The next step is to review the per-rank categorized diagnostics and actual mapping if the topology gates pass.
