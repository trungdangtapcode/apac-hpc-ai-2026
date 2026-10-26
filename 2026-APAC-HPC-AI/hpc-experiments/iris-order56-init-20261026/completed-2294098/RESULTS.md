# Fresh xyz and zyx copies initialized

Job **2294098** completed 0:0 on iris001 in 455 seconds. Both independently copied cases completed renumberMesh, potentialFoam and applyBoundaryLayer with OpenFOAM 2512, scalar64, 56 ranks and the original arguments. Both READY markers were created after all checks. Original raw cuts remained unchanged.

The 77 archived artifacts match their hashes and lengths. Source pins, source/copy/original-after manifests, 336 initial-field seals before and after each initialization, and full current serial-mesh checks pass. Binary fields remain on the cluster; their byte seals and exact reproducible stages are retained. No solver comparison has run on these two initialized copies yet.

Slurm reported MaxRSS 91,899,492 KiB. These resource reports do not measure memory bandwidth or kernel utilization. The estimated allocation is 7.077778 CPU-hours; its maximum reservation was retired once and replaced by a rounded eight-hour allowance. The Iris campaign now retains 137 planning hours, leaving 87 before the next admission under its 224-hour envelope. No SU charge is inferred.

Next: a matched 30-step xyz/zyx screen on one node, preserving both initialized sources. Keep this short experiment separate from the 150-step reference. Require a clear gain before a longer confirmation and check actual remaining budget first. Replay with `python3 replay.py`.
