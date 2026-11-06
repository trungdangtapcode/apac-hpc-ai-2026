# Iris best recipes 40-step R2 comparison

## Question and prior evidence

The 5 November six-arm recipe trial, job 2294920, ended unsuccessfully during the T2 preparation probe because rank records interleaved on stdout. It is preserved as a failed operational trial and does not establish a recipe ranking. Its five native arms that returned were T1 teammate56 33.59285, O1 original48 24.78138, H1 hybrid48 34.84965, H2 hybrid48 29.89715, and O2 original48 24.71403 seconds per step. These are incomplete, sequence-confounded observations. The unchanged hybrid48 bundle is not repeated.

The 6 November R2 test compares the teammate 56-rank recipe with a controlled 48-rank I/O-handler contrast. The historical 22-second observation remains unbeaten as a credible absolute observation; no new historical record is claimed before actual results and repeat review.

## Hypothesis and design

On the accepted Scotch48 source, using the collated OpenFOAM file handler while keeping the default MPI mapping may reduce native solver time relative to the default uncollated handler. Arms D1/D2 versus O1/O2 isolate the file-handler setting on the same 48-rank initialized source and default mapping. T1/T2 retain a full teammate 56-rank peer-recipe comparison, not a single-factor causal contrast.

Six arms run in this order: T1 teammate56, O1 original48, D1 io48, D2 io48, O2 original48, T2 teammate56. Each has 40 solver steps and 39 timed intervals, fixed solver iteration settings, the same OpenFOAM v2512 double-precision runtime, one exclusive 56-CPU Iris node (constrained to iris001 to match the historical reference), and the same sampler. Teammate56 alone uses `--map-by socket --bind-to core`. Teammate56 and io48 use `-fileHandler collated`; original48 uses the default uncollated handler. Rank counts are guarded at 56 for teammate56 and 48 for original48/io48. The MPI preparation probe uses per-rank proof files, not stdout parsing; the R2 admission gate requires the separate Ediag protocol qualification to pass before deployment.

## Acceptance and interpretation

All six arms must complete successfully with exactly 40 steps and 39 intervals, fixed iteration counts, unchanged initialized source fields, stable runtime identity, valid before/after source and payload checks, correct observed handler, complete unique rank proofs and nonoverlapping affinity masks. Force trajectories must repeat within each recipe and between the paired original48/io48 arms under the inherited tolerance. Independent native-output replay remains required. A failed arm or gate yields no ranking. Retain all arm and timing tails, phase markers, sampler records and missing-data states. Compare equal-length pooled per-step times and both replicate values; do not generalize from this one allocation or infer mechanism from aggregate telemetry.

## Resource envelope

One low-QoS exclusive Iris node, 56 CPUs, zero GPUs, four-hour site walltime, 96 GiB free-space preflight, six solver caps of 1,800 seconds, six preparation caps of 150 seconds, 480 seconds finalization reserve, 13,900 seconds internal deadline, and 14,340 seconds outer timeout. Maximum request is 224 allocated CPU-hours; it is not a billed-SU estimate. These limits describe the prepared runner only; budget authorization, deployment, queue checks and submission are owned by the parent workflow and are not recorded as completed here.
