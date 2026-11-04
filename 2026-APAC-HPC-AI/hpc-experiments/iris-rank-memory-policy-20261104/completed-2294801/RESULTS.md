# Outer-launcher interleave does not propagate to these MPI ranks

2294801 COMPLETED 0:0 in 2 seconds /56 CPUs. All 120 collected files and frozen runtime hashes verify. Both arms contain 56 unique ranks with exact 8 MiB /2,048-page isolated mappings. All observed rank policies are `default`, including the arm launched as `numactl --interleave=all mpirun ... python3 rank_probe.py`. Every mapping is wholly on node 0 or node 1 (N0=2048 or N1=2048), not striped. This rejects outer-launcher propagation in this observed stack; it does not identify exactly which runtime layer resets the policy, nor describe OpenFOAM solver-rank allocations.

No solver/timing score is measured. Native rank locality, frequency and bandwidth are not inferred. Next small qualification should put numactl inside each rank: `mpirun ... -- numactl --interleave=all python3 rank_probe.py`. This is a distinct launch mechanism; only if actual policy/page changes are observed should a native performance trial use that form. Preserve both failed and successful mechanism findings; no copy/hash preparation speed claim is reopened.

Allocated cost 0.031111 CPU-hours, conservatively 1 planning hour; retire 4.666667 reserved once. Ledger 1,176 consumed /zero reserved /stage 1,210, not billed SU.
