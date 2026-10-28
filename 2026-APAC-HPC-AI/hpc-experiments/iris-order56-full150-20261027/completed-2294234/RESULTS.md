# Iris full-run hierarchy-order result: job 2294234

## Finding

On one exclusive Iris node (`iris024`), 56 CPU ranks and hierarchy factors `(7 4 2)`, the `zyx` decomposition order averaged **21.229594 seconds per solver step**, compared with **26.953799 seconds** for `xyz`. This is a **21.2371% lower mean step time** for `zyx` in this full 150-step matched pair.

This is our full-length Iris measurement. It is not the NSCC result, the organizer's reference, or a contest score. It does not demonstrate the same speedup on NSCC or across Iris nodes.

| Order | Steps | Timed intervals | Mean (s/step) | Median | P95 | P99 | Maximum |
|---|---:|---:|---:|---:|---:|---:|---:|
| `zyx` | 150 | 149 | 21.229594 | 21.255870 | 21.395847 | 21.449785 | 21.480447 |
| `xyz` | 150 | 149 | 26.953799 | 26.516354 | 31.569807 | 32.238991 | 32.410898 |

The `xyz` tail is visibly wider: its P95 is 19.0% above its median, while `zyx` P95 is 0.66% above its median. This describes these 149 within-run intervals; it is not a confidence interval across independent runs.

## What was held constant

Both arms ran serially in the same allocation from independent copies of the same initialized 56-rank case. Each used OpenFOAM v2512, FP64, the same mesh and physics, fixed iteration counts (`Ux/Uy/Uz=15`, `p=12`, `k/omega=8`) and 150 solver steps. The only intended case change was hierarchical order, `zyx` versus `xyz`; both used factors `(7 4 2)`. Runtime validation allowed only `controlDict:endTime` to change to 150. No preload or audit library was used.

Each arm passed its native parser: steps 1–150, 149 positive native timings, matching function-object timings, 150 finite force-coefficient rows, fixed-iteration checks, `End` marker and GNU time exit status 0. I independently replayed the local parser. All 149 timing values and all 150 force-coefficient rows for both orders exactly match the frozen `comparison.json` values.

Source trees were unchanged during each solve. Copy manifests match the sealed sources; initialized field seals match the copied and post-solver seals. All ten recorded phase commands returned zero. The 49-file frozen runtime-kit hash set matched the submitted deployment, and executable/shared-library identities were identical before and after the pair. Slurm accounting reports `COMPLETED`, exit `0:0`, elapsed 7,585 seconds, 56 CPUs and node `iris024`.

## Numerical output and confidence limits

The two total-drag (`Cd`) trajectories are close overall but not identical. Across aligned steps 1–150, the maximum absolute stepwise `Cd` difference was **0.0410403**, and the mean absolute difference was **0.00615986**. At step 150, `zyx` Cd was **0.282424** and `xyz` Cd was **0.287070** (zyx is 1.6185% lower relative to xyz). This is a descriptive comparison; no native-task tolerance was specified, so it is not treated as an acceptance threshold. The trajectory and solver gates are retained for review.

The solver log's native 2%-error/95%-confidence sample recommendation was 0 for `zyx` and 51 for `xyz`; each arm has 149 timed intervals. The recommendation is based on within-run timings. It does not establish independent-run repeatability or provide an allocation-to-allocation confidence interval. The serial order also leaves possible time/order effects; earlier short reversed-order pairs favored `zyx`, but this full pair needs a full-length reverse-order confirmation.

## Resource and phase evidence

Slurm's 7,585-second elapsed time at 56 CPUs corresponds to **117.99 allocated CPU-hours** by arithmetic (`7,585 × 56 / 3,600`); this is not a site SU charge. Each arm's GNU `time` measured the `mpirun` command:

| Order | Solver wall time | User CPU time | System CPU time | CPU reported | Max RSS | Major page faults | Swaps |
|---|---:|---:|---:|---:|---:|---:|---:|
| `zyx` | 3,223.76 s | 177,231.22 s | 1,958.68 s | 5,558% | 2,964,632 KB | 113,325 | 0 |
| `xyz` | 4,075.94 s | 223,562.59 s | 3,185.50 s | 5,563% | 3,009,304 KB | 85,987 | 0 |

These `GNU time` counters describe the command-level measurement and are not per-rank profiles. The observed max RSS is not a sum of rank memory. Per-arm preparation and source-copy checks took about 97 seconds before each solver; post-solver source stability checks took 26.97 seconds (`zyx`) and 32.19 seconds (`xyz`). Runtime identity and node snapshots were recorded. The snapshots do not measure solver-specific bandwidth or prove a NUMA cause. Hardware memory-bandwidth counters, per-process NUMA placement, and per-rank frequency traces were not collected.

## Assessment and next experiment

The full run confirms the direction and approximate size of the earlier 30-step order screens and the 50-step `zyx` extension on this Iris node. The improvement is a measured hierarchy-order candidate, not yet a robust platform-wide claim. The key uncertainty is run-order and node repeatability, not an unqualified pinning diagnostic.

Next, run a fresh full 150-step matched pair with **`xyz` first and `zyx` second** on one exclusive Iris node using the same pinned sources, solver settings and evidence gates. Compare both arm times and output trajectories against this pair. If the direction persists, then test the selected order on NSCC as its own platform-specific result when access permits. Keep Iris and NSCC seconds separate.

## Evidence files

- `REVIEW.json`: machine-readable local replay, metrics, phase checks and evidence limitations.
- `collect_completed.py`: bounded first-pass collector; 125 files in a 543,935-byte compressed archive.
- `collect_completed_addendum.py`: collected the four native timing and force-coefficient tables omitted from the first pass; 44,950-byte archive.
- `collection.json` and `collected-addendum/collection.json`: remote and local file hashes, accounting and transfer metadata.
- `raw-evidence.tar.gz` and `collected/`: preserved selected text evidence and tables; no mesh or binary fields were transferred.
- `../comparison.json` is the local job summary retained inside `collected/runs/2294234/comparison.json`; the native logs and tables were independently replayed against it.
