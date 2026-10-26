# Fresh hierarchical control and three split orders

The intended 150-step hierarchical/Scotch pair, job 2294047, failed because Scotch reached its 65-minute per-arm cap during step 143. Hierarchical completed all 150 steps at 21.8703015244 seconds per step. On equal completed intervals 2–142, Scotch took 24.06% longer. That prefix is exploratory; the complete pair remains invalid. Close this unchanged Scotch branch on Iris.

This allocation screens xyz (control), xzy, yxz and zyx with hierarchical factors (7 4 2), 56 partitions and the current canonical 65,334,765-cell mesh. In xyz, cells are divided along x first, then y, then z. Changing the order changes which cells are grouped together on a nonuniform mesh. The partition count and numerical problem stay the same. The [official OpenFOAM guide](https://www.openfoam.com/documentation/user-guide/3-running-applications/3.2-running-applications-in-parallel) documents these order choices.

A fresh xyz control addresses a provenance gap: the older 21 October hierarchical cut did not retain a complete serial-mesh checksum at its creation. All four new cuts share full current mesh checks before and after. Preserve the older measurements with that historical limit; do not treat a shared pathname as proof of identical historical bytes.

The job requests one exclusive 56-CPU Iris node for at most 40 minutes, or 37.333333 allocated CPU-hours maximum. Three independent serial cuts may overlap only when MemAvailable is at least 128 GiB; otherwise they run sequentially. Previous serial decomposition peaked near 31.8 GiB RSS. Concurrent cut durations are unranked and do not measure solver performance. Each case has independent files and pinned numerical inputs.

Review the 56 partition meshes, cell totals, 336 restored fields, interface faces, maximum rank interface work and neighbor counts. A smaller interface count alone already failed to predict Scotch performance. Select any further solver experiment from the complete tradeoff and remaining budget. Do not automatically initialize every case. No initialization or solver is included in this job.

The parent three-order draft was never deployed or submitted. This derived payload retains that draft and adds a fresh control before CPU spending.
