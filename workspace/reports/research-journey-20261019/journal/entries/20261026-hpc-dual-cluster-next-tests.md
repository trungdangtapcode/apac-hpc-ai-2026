# 26 October: use both CPU clusters and review the Iris Scotch partition

## Question and prior evidence

The owner explicitly confirmed that this HPC session should use NSCC CPU and Iris CPU. Qwen/GPU work remains in the other session. Our verified NSCC best is still 3.364622070 seconds per step from job 25940700, 150 solver steps and 149 retained timings. It is a repeat of the previous intended Scotch configuration, not a measured rank-placement gain. The older Iris hierarchical baseline is 21.9653538363 seconds per step at 56 ranks over 39 timings. The machines and rank counts differ; these values must not be plotted as a direct improvement ratio.

## Iris hypothesis, exact change and control

Test whether Scotch decomposition can improve the Iris workload compared with the existing hierarchical (7 4 2) method, while preserving the official 65M mesh, fixed numerical work and mandatory initialization stages. A fresh Scotch cut is a prerequisite, not the performance experiment. A later controlled solver comparison must hold the allocation, ranks, steps, source and initial-field provenance constant; the old hierarchical timing alone is not a matched control.

Job **2294040** ran on iris005 with 56 allocated CPUs and a 40-minute maximum. It completed 0:0 in **267 seconds**. The native serial decomposition took 243.89 seconds; exactly 56 partitions contain 65,334,765 cells, and 336 initial field files were restored. Full eight-member serial mesh hashes and 45 frozen source hashes pass. Ten collected run artifacts match their recorded byte counts and SHA-256 values. [Native replay and results](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch56-20261025/RESULTS.md).

The largest partition has 1,178,358 cells, approximately 1.0100 times the mean; the smallest has 1,146,243. This is cell balance, not communication volume or a speedup. GNU time reports 33,323,056 KiB peak process RSS and 99% process CPU utilization for this deliberately serial stage. No memory-bandwidth, cache-miss, interconnect or solver-time placement measurements were collected. The estimated whole allocation is 4.153333 CPU-hours; a rounded five-hour planning allowance replaces its maximum reservation under the 224-hour Iris branch envelope. The SU rate remains unknown. NSCC spending is separate.

Next, review and submit a separately frozen initialization job containing renumberMesh, potentialFoam and applyBoundaryLayer, then inspect its native output and numerical fields before solver measurement. No solver gain or official score is claimed for the completed cut.

## NSCC failed branch, corrected interpretation and next hypothesis

The retained review of **25957725** found 128 successful pre-exec capture records, 17 wide-mask rejections and 367 ranks without a retained wrapper record. No MPI audit or topology output survived. Return 143 occurred after 4.25 seconds against a 184-second timeout; it does not prove timeout expiry. Some wide masks occurred before exec of the MPI probe, so the earlier observation around MPI initialization cannot establish MPI_Init as the sole cause. The frozen lifecycle metadata also disagrees with the actual five-minute request; the raw payload is preserved. PBS's 12-hour history has expired, so final scheduler state and actual charge remain unknown and the full 42.666667-SU reservation remains. [Complete failed review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/exec-25957725/RESULTS.md).

Actual site inspection confirms mpirun is a symlink to PALS mpiexec 1.1.6. Changing that command name is not a new engine. The prepared next diagnostic instead compares bare launch, a global binding option and a command-specific binding option. All use method 0, no preload shim, no reordering file and no mask-based early abort. Plain Python captures launcher-entry affinity; native code durably records entry before MPI_Init_thread(SINGLE), then records post-init affinity. Per-rank files avoid interleaved diagnostics. This is collection with monitoring overhead, not a solver benchmark or placement qualification. [Frozen design](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-launcher-order-20261026/README.md).

The 512-rank request, five-minute limit and source checks passed offline review. Root review corrected an initial 32-mpiprocs-per-node draft to 128 before sealing and moved native entry-file persistence before MPI initialization. Real site compilation and execution remain unverified. The ABBA solver draft remains blocked on actual binding qualification. Its separate lifecycle metadata is now checked against the 90-minute PBS request and 87-minute internal deadline.

## Access and admission limit

NSCC CPU SSH was restored at the earlier check; a separate read-only AI-login query found no own PBS jobs. The first AI socket path was too long after successful authentication; a shorter path worked. No AI payloads or jobs were changed. Later, the existing VPN expired at **06:11:08 UTC**, approximately 24 hours after establishment. An authorized reconnect returned Authentication failed; the cause is not established. The diagnostic deploy therefore failed before namespace routing, before qsub, and added no reservation. No definite NSCC job receipt exists for this diagnostic. Continue useful Iris work while NSCC access is unavailable; do not report a prepared payload as submitted.

The last site CPU report shows 27,532.791 SU balance with a dated site label, while conservative internal commitment still retains older unknown maxima. Every future admission must check both NSCC queues and CPU/AI locks, project rate and remaining ceiling. One own active allocation per CPU cluster implements the owner's explicit two-cluster direction; it does not enable background Codex or change AI ownership.

## Preservation

Source, admission, completed cut, failure review, access correction and lifecycle fix are separate safe checkpoints. Preserve their native files, hashes and Git provenance; do not include private keys, VPN caches, credentials or SSH state. New artifacts are inline Git files; the historical external artifact store still requires an off-host backup.
