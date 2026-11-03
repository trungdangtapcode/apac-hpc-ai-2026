# Iris: our configurations, teammate and organizer

Reviewed **3 November 2026**, for the owner's direct comparison question. The teammate recipe has a favorable short-run signal against the organizer recipe on Iris. Our own configurations have **not established a stable improvement over the organizer control**, and there is no matched three-way trial proving that we beat the teammate.

## Compare each candidate with its own control

All rows use one Iris node, 56 MPI ranks, the full-size physical mesh and the same native double-precision runtime within that job. Each row is a separate allocation with two control and two candidate arms. Times below average the two arm means; the arms within each row have equal measured-interval counts. Smaller time is better. A negative change is favorable; a positive change is slower.

| Comparison | Job | Steps / measured intervals per arm | Control mean, s/step | Candidate mean, s/step | Candidate time change |
|---|---|---:|---:|---:|---:|
| Teammate recipe versus organizer recipe | 2294637 | 40 / 39 | 27.8735 | 24.7453 | -11.2228% |
| Our zyx versus organizer Scotch | 2294640 | 40 / 39 | 26.9011 | 29.6490 | +10.2150% |
| Our xzy first screen | 2294643 | 40 / 39 | 33.3785 | 33.1416 | -0.7097% |
| Our xzy reverse confirmation | 2294644 | 52 / 51 | 26.3600 | 29.0626 | +10.2525% |

**Do not rank rows by raw seconds.** Different allocations, order and horizons produced substantial drift; each percentage is against that row's own control. These are Iris practice measurements, not final official platform scores. The organizer is the competition organizer (BTC in Vietnamese).

## What the results mean

The teammate comparison (2294637) uses the supplied socket/core MPI and collated-I/O settings against the organizer's default MPI and uncollated I/O, with the same initialized Scotch source. Teammate time is **11.2228% lower** overall, with both adjacent comparisons favorable. However, repeats drift by about 18–21%, and the organizer's recommended sample counts exceed the 39 observed intervals. This is promising but needs confirmation. All four reported rank/core maps and force-coefficient trajectories match; the experiment does not prove which runtime mechanism caused the difference. It tests the portable Iris runtime settings, not the teammate's entire Gadi environment.

Our `zyx` decomposition loses **10.2150%** in its complete comparison. Our `xzy` first signal of **0.7097% lower time** reverses to **10.2525% slower** in the longer reversed-order check. Neither is a stable improvement to promote.

The latest `xyz` job 2294671 is incomplete: Scotch 33.672468410 s/step, xyz 25.585999316 s/step, then another xyz printed 34.792584778 but timed out at 720 seconds. The final Scotch did not run. No full comparison or valid repeat exists. [Failed-run review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/completed-2294671/RESULTS.md).

## Why our old 21.23 does not establish first place

Our hierarchical `zyx` job 2294234 really completed 150 steps with mean **21.229593669 s/step**. In the reversed full-length comparison, the same choice reached 26.610795524. The two allocations each favored their first arm. The old best is a valid observation, but it was not measured against the teammate and organizer in the same controlled comparison. Selecting it against another allocation's slower result would give a misleading ranking.

The teammate's **2.079045460 s/step on Gadi** and organizer's **3.210832548 s/step on NSCC** come from other hardware. Our **3.364622070 s/step on NSCC** reproduces the organizer recipe. None can be numerically ranked against Iris seconds to attribute an optimization gain.

## Current mechanism investigation

Job **2294675 completed 0:0 in 216 seconds**, after correcting a parser spelling defect in failed 2294674. It ran four case-copy/hash preparations, not OpenFOAM. In the inherited-policy arms, node-wide file-page counters grew by about 0 / 9.78 GiB across the two NUMA nodes; interleaved-child arms showed about 4.89 / 4.89 GiB twice. This consistently changes the observed preparation behavior, but does not attribute every page to a particular file or prove faster solver steps. A separate native matched test is required.

The native test is now actually submitted as **2294676**, accepted 3 November 13:57:02 Vietnam; its first solver arm started at 13:58:25. It uses identical Scotch inputs and solver settings in all arms, changing only preparation-child policy. Maximum 75 minutes / 56 CPUs. No result is available yet. [Actual receipt and dated status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/STATUS.md).

## Evidence

[EVIDENCE.json](EVIDENCE.json) retains source paths and SHA-256 identities with the exact arm values. Detailed reviews: [teammate versus organizer](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/completed-2294637/RESULTS.md), [our zyx](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/completed-2294640/RESULTS.md), [xzy screen](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/completed-2294643/RESULTS.md), [xzy reversal](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy52-reverse-20261102/completed-2294644/RESULTS.md).
