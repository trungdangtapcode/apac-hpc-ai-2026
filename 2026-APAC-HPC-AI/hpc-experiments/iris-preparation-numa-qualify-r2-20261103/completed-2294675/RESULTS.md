# NUMA preparation-policy qualification

Job **2294675 completed 0:0** on `iris001`, using one node and 56 CPUs for 216 seconds. Independent replay verified all **10 collected-file** hashes, the raw archive SHA-256, and all **7 frozen payload/source-manifest** hashes. Source-before and source-after inventories are identical and match the accepted source manifest. Run `python3 replay.py` from this directory to repeat the checks and regenerate [REVIEW.json](REVIEW.json).

This is a preparation-only result. It compares the inherited default memory policy with a child-only `numactl --interleave=all` policy during four copy/hash arms in A/B/B/A order. Each treatment used the same CPU mask (CPUs 0–55) and the two allowed memory nodes (0 and 1). The reported inherited policy was `default`; each interleaved child reported policy `interleave` over nodes `[0, 1]`. The solver was not run.

## Source and clone integrity

The accepted source inventory contains **1,040 regular files** and one approved `constant/polyMesh` symlink. The separate supplementary manifest contains **13 regular-file pins**, for 1,053 regular source inputs plus that one symlink. Source-after matches source-before and the accepted manifest; the source-after gate passed.

All four arms report successful policy and clone checks. Each verified the 1,040-file main manifest, all 13 supplementary pins, the approved symlink, no source inode reuse, and the same source-inventory SHA-256. The byte-identical source hashes show that the policy arms prepared the same input content. The retained local packet contains the arm verification records, not four full cloned directory trees.

## Per-node whole-node counter response

`FilePages` changes below are differences from each arm's own `before_copy` snapshot. “After copy” is the snapshot before checksum verification; “after hash” is the final snapshot. Values are GiB converted from the reported node `meminfo` kB counters.

| Arm | Policy | Copy / hash seconds | Node 0 FilePages Δ after copy / after hash | Node 1 FilePages Δ after copy / after hash |
|---|---|---:|---:|---:|
| A1 inherited | default | 11.268 / 27.309 | 0.000 / 0.000 GiB | 9.779 / 9.781 GiB |
| B1 interleave | interleave on 0,1 | 11.907 / 27.565 | 4.890 / 4.891 GiB | 4.889 / 4.890 GiB |
| B2 interleave | interleave on 0,1 | 12.012 / 27.585 | 4.890 / 4.891 GiB | 4.890 / 4.890 GiB |
| A2 inherited | default | 10.898 / 27.242 | 0.000 / 0.000 GiB | 9.780 / 9.781 GiB |

The whole-node `numastat` `interleave_hit` counter did not change during either inherited arm's copy or hash phase. In B1, it increased on nodes 0/1 by **1,309,955 / 1,307,873** during copy and a further **234,833 / 235,705** during hash verification. In B2, the corresponding increases were **1,310,032 / 1,307,819** during copy and **235,477 / 236,284** during hash verification. Thus the child policy was actually applied, and the node-level `FilePages` and `interleave_hit` response repeated across the two treatment arms.

These are cumulative whole-node counters. They do not identify which file or process supplied the pages, exclude unrelated node activity, or prove per-file placement. The results qualify a controllable preparation policy and a consistent node-counter response; they do not establish a solver speedup or that the copied files themselves were distributed exactly as the counters suggest.

## Measurements not collected

There is no OpenFOAM solver timing, final output, score, or solver resource record in this job. Per-process and per-file page residency, page-cache attribution, CPU/memory pressure, memory bandwidth, and hardware cycles were not collected. No solver-performance or billed site-SU claim follows. Scheduler allocation arithmetic is 56 CPUs × 216 seconds = **3.36 allocated CPU-hours**; billed SU remains unknown.
