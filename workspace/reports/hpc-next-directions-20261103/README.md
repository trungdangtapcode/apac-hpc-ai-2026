# Improve the experiment before expanding the configuration search

The strongest next step is to connect solver timing to conditions **during** execution. Existing results do not identify a winning setting. A small search over more decomposition coefficients would continue mixing configuration effects with large temporal variation.

This review follows the owner's request to think about improvements on 3 November 2026, Vietnam time. It preserves the failed weight branch and changes the purpose of the next xyz/Scotch run: an instrumented diagnostic and directional comparison, not a final speedup claim.

## What the retained evidence says

| Observation | Consequence |
|---|---|
| Same Scotch control: 22.358 → 31.444 s/step in job 2294640, +40.64% | A small candidate advantage can be overwhelmed by temporal variation. |
| Xzy first looked 0.71% faster; its reverse test was 10.25% slower | Close the unchanged xzy claim. Do not keep extending until a favorable run appears. |
| Native 100:1 Scotch tree reduces logical cross-group faces 5.07%, but worst-rank faces increase 8.59% and neighbor patches 20→24 | Communication proxies have competing effects. The predeclared fanout gate rejects this tree; it does not prove that its solver would be slower. |
| Twelve arm endpoints show about 162–168 GiB MemAvailable; swap is disabled | These measurements were outside the solver. They cannot establish that memory remained sufficient during execution. |
| GNU process-tree major faults range 5,261–341,798; raw file-input counters range 3,008–380,304 | Paging/storage activity varies, but does not consistently track runtime. The fastest reverse-test arm also has high fault counts. |
| All twelve memory-pressure paths were unavailable | Missing pressure data is unknown, never zero. |
| No sustained clock, rank page-placement or bandwidth measurements exist | Do not declare a CPU-clock, NUMA or memory-bandwidth bottleneck. |

[EVIDENCE.json](EVIDENCE.json) retains 12 arm summaries and 39 source hashes. Run [replay_evidence.py](replay_evidence.py) to reproduce them from the preserved logs. Node counters cover the whole node; GNU counters cover the measured process tree. Their scopes and numerical totals differ. GNU maximum RSS is not a measurement of total memory used by all ranks.

NUMA allocation misses count pages allocated away from the preferred node; they are not remote memory-load counts, communication bytes, or a bandwidth measurement. This distinction follows the [Linux kernel's NUMA counter documentation](https://www.kernel.org/doc/html/latest/admin-guide/numastat.html). Likewise, CPU affinity and memory allocation policy are separate mechanisms; the default policy generally prefers local allocation, subject to other restrictions. [Kernel memory policy](https://www.kernel.org/doc/html/latest/admin-guide/mm/numa_memory_policy.html).

## The next actual experiment

Use the existing fully initialized `hierarchical (7 4 2), order xyz` source against accepted default Scotch. Earlier xyz timings were compared against other hierarchy orders and affected by run order; a direct controlled comparison is still useful.

One Iris allocation runs Scotch → xyz → xyz → Scotch, 20 steps per arm, with identical native runtime, numerical work per step and monitoring. All sources, fields, copies, solver outputs and runtime libraries retain their existing validation. This balances a linear time trend; it does not remove nonlinear drift or prove causality.

Add compact whole-node samples every five seconds while each solver is alive: available memory and cache, paging/reclaim/NUMA allocation counters, aggregate CPU counters, instantaneous clock summaries, and pressure files when available. Record missing files explicitly. Qualify read cost on the compute node, track collection duration, and stop/reap the collector on every solver exit. Do not inspect other users' processes, drop caches, change clock governors or perform intrusive profiling. Collector CPU cost is not the same as total observer-induced slowdown; this remains a diagnostic run.

The 19 measured intervals are inadequate for a final optimization claim under the observed drift. The historical xyz recommendation of 361 intervals estimates its own mean precision; it is not a universal power calculation for an A/B comparison. Keep all prescribed samples and warnings. No post-hoc trimming, automatic promotion, or ranking entry comes from this screen. An apparent advantage needs a later independent reverse-order run with the official horizon and adequate repeatability.

Resource maximum: 56 CPUs × 1 hour = **56 allocated CPU-hours**. With 949 consumed, the maximum committed allowance is 1,005, below the existing internal stage 1,009. This is not billed SU or a claim about a site balance. Before admission, verify the actual queue, full frozen payload, source lineage and budget lock. The payload is prepared until a definite receipt is recorded.

## Initial priority ordering (historical after the second review)

| Priority | Hypothesis and exact change | Evidence needed before spending |
|---|---|---|
| 1 | **Reduce MPI density:** 48 ranks, balanced 24 per CPU package, versus 56 / 28 per package; native Scotch in both cases | If runtime traces indicate pressure or per-rank overhead worth testing, initialize the full 48-rank case and compare complete work. Fewer ranks may also lose compute throughput; no gain is assumed. |
| 2 | **Improve memory locality:** retain the rank count and decomposition, test one explicit memory/placement policy | First measure actual rank affinity and page residency in a separate bounded diagnostic. Current launcher maps and node allocation counters are insufficient. |
| 3 | **Choose xyz or Scotch from a real comparison** | Candidate behavior must repeat against simultaneous controls. A graph score or one fast arm is insufficient. |
| 4 | **Build or MPI optimization targeting a measured hotspot** | Collect a representative profile first. Rebuild the same v2512 tree or change one MPI parameter; preserve IEEE double precision and fixed numerical work. |

The rank-count hypothesis is allowed in Basic: the current rules leave rank count free, restrict decomposition methods to hierarchical/scotch, and do not require filling every core. The official scored workload remains 4 nodes / 150 steps; one-node scaling uses 40, so this 20-step diagnostic does not satisfy that submission requirement. [Official task rules, checked 3 November Vietnam](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md).

Do not revive the closed weight-only, xzy, graph-placement or collated-I/O claims unchanged. Do not switch to a Bonus-only decomposition or unsafe arithmetic under a Basic label. Iris is a practice platform; any selected improvement must be validated on NSCC or Gadi at the official scale. Current NSCC access remains unverified after the separately recorded VPN rejection; no Gadi identity/project has been supplied.

## Interpretation and stop decisions

If time variation dominates both repeated controls and candidates, report the comparison as inconclusive and use its time series to choose one causal test. If xyz is consistently slower, close it. If it appears faster, retain it as a lead only; independent official-horizon validation is still needed. If monitoring files are unavailable or expensive, record that limitation rather than claiming a healthy machine. This experiment is valuable only if its collected evidence changes the next decision.

## Actual admission

Job **2294671** was accepted 03 November 2026 02:05:12 Vietnam, with its 56 CPU-hour maximum reserved under lock and all 62 runtime files frozen and verified. [Receipt, payload and operational status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/STATUS.md). The diagnostic is now submitted; no runtime result is claimed.

## Deeper mechanism review

The first in-solver capture changes the next-test priority. See [preparation locality, MPI waiting and allocator qualification](MECHANISMS.md). The earlier rank-density-first ordering is retained as history, not the latest dispatch decision.
