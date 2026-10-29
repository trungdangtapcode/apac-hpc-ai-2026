# Conditional native zyx graph-placement screen

## Purpose and scope

This bundle prepares one short, non-scored, native OpenFOAM measurement of a
NUMA rank-placement hypothesis. It does not claim a performance gain. The
retained processor-graph search reduced the logical cross-NUMA interface-face
proxy from 129,700 to 90,953 for the zyx order (29.8743%) while preserving the
existing 28/28 rank split and the same cell loads. The proxy is a reason to
screen the candidate, not evidence that the solver will run faster.

The experiment uses one prepared zyx case with hierarchy `(7 4 2)` and runs an
BAAB order: default-equivalent identity mapping, graph mapping, graph mapping,
then identity mapping. Each arm runs 14 native solver steps and retains 13
positive wall-time samples. This is one allocation and one BAAB cycle, so any
favorable result is only a short screening signal. A separately reviewed full
run is required before claiming an improvement.

## Runtime mapping qualification

The actual 56-rank probe from job 2294358 found the default post-MPI main-thread
CPU masks. At runtime, the bundle repeats the default probe, creates an
identity rankfile with Open MPI global logical slots `slot=r`, then verifies
that this identity rankfile reproduces the default rank-to-OS-CPU and NUMA
masks exactly. It creates the graph candidate by inverting that measured
default rank-to-CPU map, not by treating Linux `lscpu` package/core labels as
Open MPI logical slots. A second native probe must prove the candidate's exact
planned CPU permutation and NUMA-group assignment before solver execution.

The native probe gate establishes rank-to-main-thread CPU masks for the probe
process. It does not establish memory-page placement, MPI helper-thread
affinity, hardware traffic, or a causal explanation for any solver difference.

## Controls and retained evidence

All four solver arms use the same explicit rankfile launch form and
`--bind-to core`; only the rank-to-core assignment differs. Each arm is copied
from the same frozen initialized zyx source into a separate working directory.
The only case edit is `system/controlDict:endTime`, set to 14. Time-zero fields,
fixed iterations, solver inputs, function objects and hierarchy remain pinned.

The complete initialized source tree must match the separately retained source
manifest from reviewed job 2294262 before any probe or solver starts. The
accepted manifest covers 1,040 regular files and its `constant/polyMesh`
symlink target. The run then hashes that complete tree once before and once
after the BAAB sequence. The initial inventory supplies hashes for all 336 time-zero
rank fields. Each private arm copy is hashed against that frozen inventory and
checked for separate source inodes; the source is not rehashed per copy. Cases,
logs and native results are retained under `runs/<job-id>/arms/`; affinity
probes and rankfiles are under `runs/<job-id>/probes/` and
`runs/<job-id>/mapping/`.

Each arm must finish all 14 solver steps, produce 13 finite positive timings,
14 force-coefficient rows, unchanged fixed-iteration counts, a successful
native exit, and stable solver/library identities. The report averages both
control arms and both candidate arms while retaining every individual arm
mean, so order drift remains visible. A failed, partial or truncated run is
not a valid comparison.

## Resource envelope and state

The prepared request is one exclusive Iris node with 56 CPUs, no GPU and a
50-minute wall limit. The runner has a 2,850-second internal deadline, a
2,970-second outer timeout, and protected complete-screen guards. Each arm has
a 150-second copy and a 650-second solver ceiling. Before each arm, the runner
protects a 530-second solver window, an 80-second expected copy window, 15
seconds of between-arm review, and 50 seconds for final review for every
remaining arm. A slow arm can therefore prevent later arms from starting; the
runner does not shorten an arm to squeeze in BAAB.

This folder is a prepared payload only. It contains no scheduler receipt,
measured solver result, or submission claim. Root admission and any later
submission remain separate reviewed actions.

## Reverse confirmation provenance

This is a derived payload from completed job 2294366. The treatment sequence is B1-graph, A1-default, A2-default, B2-graph. Physics, 14 steps, actual mapping gates, source inventory, candidate, all output gates and time limits are unchanged. The prior aggregate advantage is unconfirmed because the final baseline slowed sharply. This new order tests treatment-position confounding; it is not a blind duplicate or a full 150-step result.
