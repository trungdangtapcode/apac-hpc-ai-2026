# Current HPC/OpenFOAM handoff

Updated 26 October 2026. This thread 01a1508d-26b0-7dd0-9dc1-f217ce0aff40 owns HPC only. The owner explicitly confirmed NSCC CPU and Iris CPU. Keep one own active allocation per CPU cluster and combined own NSCC CPU/AI PBS cap three. Preserve AI payloads, queues and its separate project. No background Codex, schedules or autopilot.

## Measurements and corrected conclusions

**NSCC reference remains 3.364622070 seconds per step**, job 25940700, four nodes / 512 ranks / 150 steps / 149 retained timings. Source, fields and numerical work pass. This is a repeat of the same intended configuration, not a demonstrated placement optimization or organizer-confirmed score. [Review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md).

**Iris 2294047 is FAILED / 124:0**, not a completed matched pair. Its H arm completed 150 steps at 21.8703015244 seconds/step; S reached its per-arm cap during step 143. H and S means on equal completed intervals 2–142 are 21.865389166 and 27.127250187 seconds, respectively: S took 24.06% longer. This prefix is exploratory, not a full S mean. Close unchanged Scotch on Iris. [Complete failure review and useful H reference](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-matched-solver56-20261026/completed-2294047/RESULTS.md).

The H reference has 116 bounding-omega messages and finite Cd 0.2870700944. They are retained; neither finite output nor a successful arm certifies organizer accuracy. The older H cut lacked a complete serial-mesh checksum at its 21 October creation. Current input and copy hashes do not retroactively prove that historical identity. A shared pathname is insufficient; new static comparisons require a fresh xyz control. Do not pool Iris and NSCC timing values.

## Active research

**NSCC 26004608.pbs101** is the admitted rank-zero syscall observer. At 13:01 UTC it was Q/q5 waiting for node_pool; refresh the real scheduler before another action. Four nodes / 512 ranks / five-minute maximum / 42.666667 SU maximum. It compares an untraced native control against strace on PMI rank zero only, recording affinity syscalls and call stacks without changing affinity. No solver is included. The installation has strace 5.18 with libdw stack support; compute behavior and permissions remain unverified. [Frozen payload and receipts](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-affinity-strace-20261026/STATUS.md).

The preceding **25999546 completed F / Exit 0 in 13 seconds**. All three launcher syntaxes captured every rank. Python and native pre-init masks contain one CPU; all native post-init masks contain CPUs 0–255. All six commands returned zero. World-rank and PMI-rank mappings are one-to-one but mostly nonidentity; use actual MPI world ranks for placement. No physical-core topology was collected by this diagnostic. Close unchanged option-placement tests and inspect the next trace before proposing a binding fix. [Verified 4,630-record replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-launcher-order-20261026/completed-25999546/RESULTS.md).

**Iris 2294097** is admitted for the hierarchical-order r2 screen. It screens fresh xyz plus xzy, yxz and zyx with the same factors (7 4 2), 56 partitions and full canonical mesh checks. This is only native decomposition and restored fields, not initialization or a solver score. The locally sealed three-order parent was never deployed or submitted; r2 adds the required fresh control. [Plan](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-hierarchical-order56-r2-20261026/README.md). Do not automatically initialize every cut; inspect cell balance, interface faces, peer counts and resources first.

The NSCC ABBA solver remains unsealed and unsubmitted: binding qualification failed. Its lifecycle metadata now matches a 90-minute request and an 87-minute internal deadline. Offline tests are not a site qualification.

## Budget and access

NSCC CPU project 59000042: cumulative ceiling 29,777.846 SU, committed 4,809.533333 SU, internal headroom 24,968.312667 SU after the trace reservation. The known 13-second diagnostic retired only its own maximum and added a rounded two-SU allowance; all older unknown maxima remain. No individual posted charge is claimed. The latest retained site read still displays 27,532.791 SU with a dated site label, so do not present it as fresh accounting. Owner's planning deadline is 30 October; site expiry metadata says 15 November. [Authorization](cpu-campaign-before-oct30-20261024.md).

Iris uses a separate 224 allocated CPU-hour envelope; SU rate and balance are unknown. Completed preparation and failed pair retain 123 rounded planning hours; no pair reservation remains before the new cut screen. The new 40-minute maximum reserves 37.333333 CPU-hours, bringing commitment to 160.333333 and headroom to 63.666667 CPU-hours until terminal reconciliation. Keep the ledger in iris-scotch56-20261025/budget.json as the shared Iris campaign ledger; do not create parallel ledgers or debit NSCC for Iris.

The earlier VPN rejection is historical: a later check found an existing live namespace, and CPU SSH was separately authenticated through cpu-r8. The helper's dead-pane guard preserved the active VPN. Iris uses forced-TTY gateway auto-jump and the verified bridge on actual login01/login02. Never copy credentials, private keys, VPN caches or SSH state into notes or Git. [Access record](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261026/REPORT.md).

## Recovery and continuation

Capture, verify, commit and push small explicit milestones. Complete raw diagnostic records are stored once in inline compressed archives with manifests and replay scripts; avoid duplicating thousands of extracted files in Git. New retained cut/init/pair archives are small Git objects. Historical external large objects still require an off-host copy. Existing submission materials were not changed in this research turn.

Next: collect terminal trace evidence before a new NSCC hypothesis; review the four fresh cuts before any Iris initialization. Preserve every failed and losing branch and source seal. [Research journal](../reports/research-journey-20261019/journal/README.md), [earlier handoff, historical](history/HPC_CURRENT-before-failed-Iris-pair-20261026.md).
