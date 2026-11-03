# Native preparation-policy effect test accepted

Recorded 3 November 2026, Vietnam time. Job **2294676** was accepted at **13:57:02**, observed RUNNING at **13:58:42**, and its first OpenFOAM arm began at **13:58:25** after source, copy/hash and launcher-parent policy gates. [Actual receipt and source](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/STATUS.md).

**Evidence and hypothesis.** Parent 2294675 completed four preparation-only arms. Interleaving the copy/hash child's memory policy consistently changed node-wide file-page growth from roughly 0 / 9.78 GiB to 4.89 / 4.89 GiB. That qualified an applied controllable factor, not a solver gain. The new experiment asks whether this preparation difference changes native step time while solver command, initial input and physics remain fixed.

**Change and control.** All arms use the accepted Scotch source (1,040 core regular files plus 13 pinned metadata files), 56 ranks on one exclusive Iris node, v2512 DP, uncollated native solver, equal 5-second sampling and 20 steps / 19 intervals. A/B/B/A changes only the copy/hash child's policy. Launcher-parent memory policy is observed before each solver; individual rank policies are not measured. Frozen runtime contains 61 files. Payload/source/native/runtime checks and cross-arm force-coefficient tolerance are required.

**Time and spending.** Each solver gets an unshortened 1,000-second cap including finalization. The 75-minute request is 70 allocated CPU-hours. The full-sequence guard deliberately rejects an overly slow preflight before any arm. Parent consumed 3.36 actual / 4 conservative CPU-hours, leaving 989 consumed under stage 1009. The reviewed exact maximum requires 1059, so a documented 50-hour increment expands this agent-selected internal stage solely for the new 70-hour reservation. No owner/site quota increase, billed-SU claim, NSCC/AI debit or background schedule is implied.

**Startup observations.** Source and canonical-input checks passed. First copy/hash completed in 38.612 seconds, under 50-second bound. The policy probe passed, the sampler started, and the native 56-rank command began. This proves execution reached OpenFOAM, not a completed timing result. No score or winner is claimed.

**Next decision.** Collect all four arms, compare mean/tails and both adjacent contrasts, check repeat drift, output/work/source/runtime integrity and resource evidence. A reversed contrast or startup-only effect is not a solver improvement. A favorable 20-step signal requires longer independent confirmation before promotion. Retire the reservation once from terminal accounting.

**Preservation.** Mechanism review, frozen candidate and actual admission/receipt are separate small checkpoints. Only reviewed HPC paths are captured; Git push does not upload external object bytes.
