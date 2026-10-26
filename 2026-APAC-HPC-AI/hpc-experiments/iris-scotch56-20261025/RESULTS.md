# Iris Scotch56 cut — completed and reviewed

Job **2294040** completed with Slurm exit 0:0 on iris005 in **267 seconds**. The native cut and restored-field checks pass: exactly 56 partitions, 65,334,765 cells and 336 restored zero-time field files. All eight serial mesh members match the official retained archive hashes, and all 45 frozen payload files pass before/after checks. The ten collected artifacts match their transferred byte counts and SHA-256 values.

The largest partition has 1,178,358 cells, 1.0100 times the mean; the smallest has 1,146,243. This describes cell balance only. Communication cuts, memory traffic and solver performance are not yet measured. A balanced cell count alone does not demonstrate a faster solver.

Serial decomposePar took 243.89 seconds and peaked at 33,323,056 KiB RSS according to GNU time. Its process CPU percentage was 99%, consistent with the intended serial stage. Slurm separately reported batch MaxRSS 32,781,460 KiB; the collectors differ. Neither value is distributed memory-bandwidth telemetry.

The allocation represents approximately 4.153333 allocated CPU-hours (56 × 267 / 3600). Retire its 37.333333-hour maximum reservation once and retain a rounded five-hour planning allowance under the 224-hour Iris branch envelope. No SU charge or charging rate is inferred, and NSCC's ledger is unchanged.

Next: admit a separately frozen mandatory initialization stage, retaining renumberMesh, potentialFoam and applyBoundaryLayer, then review its outputs before solver measurement. This cut is not initialization, a Cd result, a scored run or an improvement over the older hierarchical solver baseline.

Replay with `python3 review-cut.py`. The first local replay incorrectly expected the source verifier's `files` field to be a map; the retained verifier actually emits a count. That assertion caught the reader mismatch and was corrected to compare 45 with the accepted manifest count. Raw remote artifacts were not changed.
