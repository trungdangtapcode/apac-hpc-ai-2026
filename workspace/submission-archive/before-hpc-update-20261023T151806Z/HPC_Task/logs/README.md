# OpenFOAM CPU measurements and provenance

The selected candidate is default Scotch with 128 MPI ranks per node on four
ASPIRE-2A CPU nodes (512 total ranks). Historical job **25921488** completed the
native 150-step solve, with 149 timed samples and a mean of **3.677906731 s/step**.
The final dimensionless drag coefficient Cd is 0.2839830076. Lower solver time is
better; Cd is a physical sanity signal, not the performance metric.

The native one/two-node Scotch records are included for scaling context:
25921487 uses one node, 40 steps, 39 timed samples, **14.450756959 s/step**;
25921492 uses two nodes, 80 steps, 79 timed samples, **7.462835189 s/step**.
These are different allocations and prescribed endpoints, so their plotted
differences are descriptive scaling, not an identical-work causal comparison.

The six-configuration four-node comparison is retained in
`four-node-comparison.json`. Raw selected 1/2/4-node native stage logs, original
ASCII case inputs, solverInfo, forces and wall-clock functions are under `native`.
The old collected launcher copies are under `historical-scripts`; they were not
sealed at original submission time. Source-to-package hashes are in `provenance.json`.

All 149 four-node samples are retained. The selected run has median 3.298741570 s,
linearly interpolated p95 3.795740 s and a maximum of 35.883552 s at Time 119.
The script validation report separately labels its nearest-rank p95 convention.
The native short-sample warnings remain. No hardware cause of the timing tail,
independent confidence interval or global optimum has been established.

The older four-node final PBS history is no longer available; native logs do not
prove final scheduler exit status or posted cost. The newly derived portable PBS
scripts in `../job_scripts` have passed offline checks and native-output validator
replays, but they have not yet produced a new compute run. A separate frozen
confirmation, **25940700.pbs101**, was submitted on 23 October and remains Q/q5
in the dated scheduler JSON because node_pool resources are insufficient. Its
performance is pending. This is not a claim of an accepted official score.

The portable script package keeps the complete official initialization, original
v2512 double-precision numerical work and four-node 150-step endpoint. No GPU,
source patch, mesh reduction or removed timing sample is used. Additional
integrity checks are our reproducibility measures, not new organizer rules.
