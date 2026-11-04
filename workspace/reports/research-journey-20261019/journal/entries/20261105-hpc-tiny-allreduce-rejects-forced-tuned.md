# Cheap collective qualification avoids a losing solver trial

After in-rank NUMA interleave timed out, a distinct tiny-message MPI hypothesis was qualified first. Actual 2294805 completed 0:0 in 20 seconds on 56 ranks, with exact MPI 5.0.10rc2 metadata, raw selection logs, correctness-checked 8/64-byte SUM, 100 warmups and two 1,000-call blocks in each of four ABBA launches. CPU binding matches, all raw timing arrays/nearest-rank quantiles replay. Forced tuned algorithm 3 increases median latency 56.8–70.4% and p95 44.4–85.0%; no ≥10% qualifying benefit. Close the forced configuration without spending another native allocation.

Default verbose shows ucc priority 100 enabled, candidate tuned 100; no per-operation solver profile or UCX transport is inferred. The prior timeout is a different factor, not proof of MPI causation. Actual 0.311111 allocated CPU-hours, conservatively 1, retires 4.666667 once, leaving 1,220 consumed /0 reserved /stage 1,289. All raw arrays/tool/selection records preserved.

Bounded read-only compiler inspection finds -O3 and -march=cascadelake in the installed rule tree. This is not full binary build provenance, but prevents blindly assuming generic flags. No changed build or new qualified faster solver candidate is claimed.

[Full collective result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-allreduce-qualify-20261105/completed-2294805/RESULTS.md). [Compiler-rule provenance](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-build-flags-review-20261105/README.md).
