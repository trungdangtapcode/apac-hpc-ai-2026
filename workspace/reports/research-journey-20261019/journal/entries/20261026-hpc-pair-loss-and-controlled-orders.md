# 26 October: reject the Iris Scotch loss and add a fresh hierarchical control

## Question and controlled change

The static Scotch partition had 21.97% fewer interface faces than the old hierarchical partition. Could that reduce real solver time? Job 2294047 ran H then S on the same exclusive Iris node, with 56 ranks, independent initialized copies, identical numerical controls and 150 intended steps each. All source dictionaries, copies and initial fields were checked before solver execution. The split algorithm and its resulting partition were the intended difference.

## Observation and assessment

The batch ended FAILED / 124:0 in 7,442 seconds. H completed 150 steps and 149 intervals at 21.8703015244 seconds per step, median 21.806776234 and p95 23.015001746. Its Cd was 0.2870700944 and the native fixed linear-solver counts match the shipped configuration. All 116 bounding-omega messages remain in the log. No official accuracy certification is implied.

S hit its 3,900-second per-arm cap during step 143. It completed only 142 steps and 141 intervals; the final End, full mean and post-run source verification are absent. This is not a complete pair. On equal completed intervals 2–142, H averaged 21.8653891659 and S 27.1272501866 seconds per step: S took 24.06% longer. This is an exploratory censored comparison, not a replacement full score. Close unchanged Scotch on Iris. A lower interface-face count did not predict a faster solver; these logs do not identify a causal hardware bottleneck.

The 216 raw artifacts are retained in a verified compressed archive. Slurm reports MaxRSS 142,664,880 KiB; per-arm GNU time reports are retained separately. No memory-bandwidth, NUMA-traffic or kernel profile was collected. [Full failed-pair replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-matched-solver56-20261026/completed-2294047/RESULTS.md).

## Provenance correction

The older H cut had no complete serial-mesh checksum recorded at its 21 October creation. Current source and copy hashes do not retroactively prove those historical serial bytes. Earlier wording about the same mesh describes intended provenance and a shared path, not independently established old byte identity. Preserve the old logs and this limitation. The next screen therefore includes a fresh xyz control; all new cases share full current canonical checks before and after.

## Next hypothesis and actual admission

Keep hierarchical structure and factors (7 4 2), but change recursive axis order. The [official OpenFOAM guide](https://www.openfoam.com/documentation/user-guide/3-running-applications/3.2-running-applications-in-parallel) documents xyz and its permutations. On a nonuniform mesh this changes how cells are grouped. It does not change the CFD problem or prove a speedup.

Job **2294097** screens xyz, xzy, yxz and zyx. It requests one exclusive 56-CPU node for at most 40 minutes, 37.333333 allocated CPU-hours maximum. At most three independent serial cuts overlap when available memory is at least 128 GiB; the prior measured serial peak was about 31.8 GiB. Otherwise the job falls back to sequential execution. Cut durations are unranked. Require all 56 partition meshes, total 65,334,765 cells, 336 restored fields, native completion, resource logs and source/mesh seals. No initialization or solver is included. Review the combined cell/face/neighbor tradeoff before any further spending; do not initialize every case automatically.

The original three-order draft was never deployed or submitted. The derived r2 preserves it and adds the fresh control. [Source, checks and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-hierarchical-order56-r2-20261026/README.md).

## Cost and preservation

The failed pair estimates 115.764444 allocated CPU-hours; its 140-hour maximum was retired once and replaced by a rounded 116-hour allowance. Iris now retains 123 consumed planning hours and the 37.333333-hour screen reservation within its 224-hour envelope. The SU rate is unknown. NSCC accounting is separate. Scripts, frozen sources, failed outputs, hashes, reviews and definite receipts are captured in separate safe commits; no authentication material is included.
