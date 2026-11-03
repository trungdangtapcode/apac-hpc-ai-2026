# Iris preparation locality qualification: parser-corrected R2

Derived from frozen job 2294674, which failed before copying because the parser did not recognize the observed `interleavemask` spelling. The only runtime changes are recognition of that spelling and a distinct job name. The exact observed non-sensitive numactl output is a regression fixture. The original submitted bundle remains untouched. No performance result is carried over.


This small diagnostic tests whether the memory policy used while copying and hashing a fresh copy of the accepted 56-rank Scotch case changes whole-node NUMA counters. It does not run OpenFOAM and cannot establish solver speed or a performance improvement.

The four arms use fresh retained directories in `A1, B1, B2, A2` order. A uses the inherited policy, which is recorded rather than assumed; each A child must report the same memory policy, interleave mask, and membind mask as the initial snapshot. B launches only the copy/hash child under `numactl --interleave=all`. The original accepted 1,040-file solver-input manifest remains unchanged. A separately reviewed supplementary manifest pins 13 legitimate initialization metadata files (50,497 bytes) plus the actual directory set; both manifest sets are hashed and copied, with a source inode-reuse check. A strict whole-root path walk permits only the combined files, approved symlinks, and explicitly recorded directories, rejecting other root files, processor directories, or empty directories. Source inventory and exact path set are checked before and after the sequence. Two NUMA nodes, process CPU/memory masks, effective B policy, per-node sysfs `meminfo` and `numastat`, copy duration, and destination verification duration are recorded.

The run is bounded to one Iris node, 56 CPU cores, no GPU, and ten minutes. Each arm has a 90-second cap; all remaining-time checks reserve time for later arms and a final source check. It fails closed if topology, policy, counters, accepted source, or four-copy disk headroom cannot be verified. It never flushes global caches, migrates pages, changes sysctls, or inspects other users' processes.

NUMA counters are whole-node cumulative observations, not process-attributed page placement. They can be affected by other node activity, and the filesystem/page cache can persist between arms. Thus even a consistent delta is only a diagnostic signal, not proof that interleaving caused a cache distribution or solver result. Copies are preserved under the run directory. No result exists until a scheduler job is actually accepted and reviewed; this directory is preparation only.

Actual acceptance and dated scheduler state: [STATUS.md](STATUS.md).
