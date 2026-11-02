# Reviewed xzy mandatory initialization

Job **2294642 completed 0:0** on iris001, 56 CPUs, **272 seconds**. All 50 collected text-file hashes pass. Independent replay confirms the original eight serial-mesh members, 41 canonical inputs, the exact xzy transform, source-preserving independent clone, one-node 56-rank MPI probe and native v2512 double-precision initialization commands.

- renumberMesh: 14.7034 seconds, return 0 and native End.
- potentialFoam: 68.0174 seconds, return 0 and native End.
- applyBoundaryLayer: 12.1428 seconds, return 0 and native End.

All 336 initialized field seals agree with the new **1040-file accepted xzy manifest**, SHA256 `e52d67b1a9a2bcad002fdbd17da982362a8d2e92e678cb81cb442b0601745987`. READY bytes are separately hash-bound by the completion record. Source before/copy/after inventories agree. The initialized source is `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-xzy-init-20261102T033918Z/initialized/order-xzy`. It is neither the old xyz source nor the old zyx manifest.

This establishes a legitimate input for a solver experiment, **not a solver speedup**. Native stage/resource logs and source inventories are retained; hardware bandwidth/cycles, sustained clocks and later solver telemetry were not collected by this preparation. No Gadi or NSCC performance is inferred.

Allocated cost is 56 × 272 / 3600 = **4.231111 CPU-hours**, conservatively **5**. The 28-hour maximum was retired once under the Iris budget lock. Local planning is now **750 consumed, zero reserved, internal stage 873**, not billed site SU. A subsequent 140-hour native BAAB would require a separately documented bounded internal-stage adjustment of 17 to 890, plus fresh queue/financial and root payload review. It is not submitted or reserved by this initialization result.

[Native initialization review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy-init-20261102/completed-2294642/RESULTS.md), native logs and source seals in collected/, raw-evidence.tar.gz. The reviewed manifest is copied byte-for-byte into the prepared xzy-versus-Scotch payload. AI and submission materials remain unchanged.
