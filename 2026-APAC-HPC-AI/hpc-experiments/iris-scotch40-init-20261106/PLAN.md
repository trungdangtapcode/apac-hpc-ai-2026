# Scotch40 initialization plan

The accepted native cut job 2294919 produced the 40-domain Scotch artifact at the exact official 65,334,765-cell mesh. This bounded job performs only the organizer-required native initialization: `renumberMesh -constant -overwrite -parallel`, `potentialFoam -initialiseUBCs -parallel`, then `applyBoundaryLayer -ybl 0.0450244 -parallel`.

It requests one exclusive Iris node, 56 allocated CPUs, 40 MPI ranks, zero GPUs, low QoS, and at most 20 minutes (18.667 allocated CPU-hours). Open MPI default placement is retained and logged. This is a preparation/READY gate, not a solver benchmark or score.

The job verifies cut accounting, exact 40-rank native cut evidence, the eight-member official serial mesh identity, source pins, 240 restored time-zero fields and one-host MPI rank coverage before mutation. Each utility needs its native completion markers, exact arguments, 40 processes, successful return, and no fatal diagnostics. It snapshots fields before and after; writes READY only after every gate passes. A failure leaves the artifact in-progress and is not resumed in place.

If reviewed READY, a later controlled solver test may compare this 40-rank decomposition with already initialized controls using the same 40-step horizon and 56-CPU allocation. Cell balance alone does not predict speed.
