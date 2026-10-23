# Gates before a full two-level placement test

This is an implementation specification, not a runnable submission or an extra budget authorization. Existing jobs 25940700 and 25943865 and their frozen payloads stay unchanged.

## Establish the control and graph

Review the independent Scotch confirmation and four-rank method-3 preflight first. A four-rank pass only demonstrates that interface on one host. Retain complete original source/mesh identity, all mandatory preparation commands, DP precision, fixed numerical work and all 150 steps for a future full-size run. Its fresh 512-way decomposition must reproduce the sealed processor adjacency and reciprocal face counts before using this mapping. If the graph changes, stop and analyze it separately.

## Measure placement on every allocated host

Use an MPI-linked probe reporting actual MPI_Comm_rank and size, processor name, affinity mask, and physical package/core and NUMA domain read locally on that rank's host. PMI_RANK alone is not the reordered MPI world rank. Reading every host's topology from the first host's sysfs is also insufficient.

The control uses method 3 with an identity file and the same PALS thread binding and thread limits as the candidate. Require four hosts with 128 distinct physical cores each and 512 unique world ranks. Eight logical NUMA groups of 16 are only a candidate assumption: verify eight domains with 16 eligible slots each on every host, or recompute the grouping for the observed topology. Startup placement does not measure page residency or solver-time migration.

## Render against observed slots

A group-major file split every 16 entries does not establish NUMA locality: launcher slot order may differ from NUMA order. Use the identity probe to map each original slot to its host/NUMA/core. Place the selected logical groups into those observed slots and render the rank order in original slot order. Keep MPI rank 0 in its original first slot. Preserve all 512 IDs and the four fixed host memberships. Map the logical NUMA group containing rank 0 to its observed original domain.

Re-probe with the exact candidate file and MPI environment. Compare every actual world rank's host/core/NUMA with its intended control slot. Reject duplicate/missing ranks, shared physical cores, wrong hosts or wrong domains before expensive initialization. Apply the verified order to every mandatory parallel initialization stage and the solver. Do not relabel processor directories to emulate placement.

## Keep validity, performance and cost separate

Both arms need native command return codes, source/field seals, complete work and timer checks, finite forces and final PBS/accounting evidence. Report numerical differences; unchanged source does not guarantee bitwise identical MPI reductions. Do not invent a Basic Cd tolerance. Retain every timed sample and report Average plus the distribution; one pair does not establish stable benefit.

Compare host and NUMA proxies separately. The refined candidate has fewer cross-host faces but still 3.19% more same-host cross-NUMA faces than the original control. Do not assign arbitrary weights or convert face percentages into speedup. Physical memory pages, network topology and measured traffic remain unknown.

Select a walltime from reviewed setup/solve evidence with headroom, then perform fresh locked budget, rate and capacity checks. The cumulative ceiling remains 5,000 SU. Capture derived source and hypothesis before submission. Keep heavy profiles outside ranked scoring; qualify future sampler overhead before rollout.
