# First 65M Iris practice baseline

The native toy job 2293751 passed both methods. The next question is whether
the actual 65,334,765-cell DrivAer case can complete the full mandatory chain
on one Iris node with the supplied native double-precision build. This is a
validity baseline, not a new optimization or contest score.

Use the organiser hierarchical N56 example unchanged, factors (7 4 2), xyz.
Preserve the three reviewed scripts and input text in this directory. The
shared case text matches the recovered pinned upstream case for all 39
common retained files; two extra root property copies match constant/.
The existing shared binary mesh header declares 65,334,765 cells, label32
and scalar64; file sizes are retained. Its complete content hash and original
archive MD5 were not independently recomputed. Do not claim full mesh identity
from a header alone.

At 11:35:56 UTC our shared-account queue was empty and the new artifact path
ready-N56-h742 did not exist in our unique work root. The filesystem reports
16 TiB available, with no user hard quota reported. Iris advertises 180000 MB
per node. Serial preparation previously used about 40–46 GB on other machines;
that is a planning estimate, not an Iris RSS measurement.

First submit only 03.1-cut-65M-N56.sbatch: one whole Iris node, one serial
process, maximum 15 minutes. Require clean scheduler exit, native utility End,
exactly 56 processor directories and correct global cell count/method before
promotion. Then submit 03.2-init (one node, 56 ranks, maximum 20 minutes),
review its three mandatory stages, and finally 04-simpleFoam (one node,
56 ranks, 40 steps, maximum 40 minutes). Keep at most one active practice
allocation in this branch. Stage gates prevent wasting dependent allocations
on an invalid processor tree; no submitted payload is edited in place.

The complete planned chain is at most 75 allocated node-minutes (70 physical
CPU-hours at 56 allocated CPUs). This is a resource envelope, not a billed SU
quote. Iris charging/SU balance was not exposed. No Gadi/NSCC project reservation
or GPU work is made. Do not launch a parameter sweep or change numerical work.

Collect preparation logs, output directory identity, input dictionaries, final
scheduler accounting including available RSS/CPU evidence, solver step timing
and coefficient.dat. Missing CPU/NUMA/network telemetry remains uncollected.
Accepting a kit PASS line alone is insufficient. The first successful full
chain will justify a matched Scotch comparator in its own new artifact tree.

A bounded inspection mistake used head on the binary owner file and printed
binary bytes into the terminal. Replace it with a bounded binary read for
header metadata; no mesh payload is intentionally downloaded or committed.
