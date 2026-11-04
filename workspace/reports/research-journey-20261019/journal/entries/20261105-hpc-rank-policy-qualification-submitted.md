# Actual MPI-rank memory policy: bounded qualification submitted

After independent 2294800 reversed the preparation-only gain, that unchanged performance branch is closed. A distinct remaining question is whether changing launcher policy propagates into MPI ranks and changes actual anonymous first-touch placement. New diagnostic 2294801 was accepted at 2026-11-04T17:22:17.718827Z. It compares inherited and launcher-interleave 56-rank Python probes, 8 MiB each, exact isolated numa_maps segment plus actual policy/masks. No mesh, OpenFOAM solver or throughput score is run.

The root added guard pages so adjacent mappings cannot silently inflate page counts; missing/ambiguous records fail. Offline resource/syntax/hash checks pass. The local one-rank runtime attempt failed because numactl is absent on this login machine; no placement validation is invented. Frozen remote code and five-path hashes require actual terminal review of both launches and 112 rank records.

One node 56 CPUs /zero GPU /low QoS /maximum 5 minutes reserves 4.666667 CPU-hours within the unchanged 1,210-stage budget, after 1,175 consumed. No additional owner limit, billed SU or AI/NSCC resources are inferred. All earlier receipts and failures remain preserved. A diagnostic outcome will qualify or reject a new mechanism, not establish faster solver steps.

[Actual receipt and code](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-memory-policy-20261104/STATUS.md).
