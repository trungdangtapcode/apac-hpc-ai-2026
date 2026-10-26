# Current HPC/OpenFOAM handoff

Updated 26 October 2026. This thread 01a1508d-26b0-7dd0-9dc1-f217ce0aff40 owns HPC only. The owner explicitly confirmed **NSCC CPU and Iris CPU**. Keep one own active CPU allocation per cluster, retain NSCC combined CPU/AI PBS cap three, and preserve the other worker's payloads and queues. No background Codex, schedules or autopilot.

## Measured best

NSCC four-node Scotch / 512 ranks, job **25940700**: mean **3.364622070 seconds/step**, median 3.282042638, p95 3.936922984, maximum 5.900973952; 150 steps / 149 timings, all retained. Numerical work, fields, source and mesh gates pass. This is an independent repeat of the same intended configuration, not a demonstrated placement optimization or organizer-confirmed score. The mean improved 8.52% over the earlier repeat, while p95 worsened 3.72%. [Complete review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md).

Iris hierarchical (7 4 2) / 56 ranks, job **2293754**: mean **21.9653538363 seconds/step**, 40 steps / 39 timings. Keep Iris and NSCC results separate; different machines and rank counts do not establish a speedup. [Iris baseline](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/STATUS.md).

## Active work and next decisions

**Iris 2294040 completed 0:0 in 267 seconds** on iris005. The fresh Scotch cut has 56 partitions / 65,334,765 cells and 336 restored initial fields. Full serial mesh and pinned source checks pass. Its maximum reservation was retired once and replaced by a rounded five allocated CPU-hour allowance under the 224-hour branch envelope. No Iris SU charging rate or balance is exposed. Review the completed native cut and restored fields before initialization, then plan matched hierarchical/Scotch solver arms. [Payload, receipts and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch56-20261025/STATUS.md).

**NSCC launcher diagnostic is sealed, not yet submitted.** Its deploy failed before namespace routing, before qsub; no reservation was added. A later VPN reconnect returned Authentication failed after the preceding tunnel expired at 06:11:08 UTC, approximately 24 hours after establishment. Cause of rejection is unknown. Continue Iris work while this is unavailable. Installed mpirun is a symlink to the same PALS mpiexec binary. The next bounded test compares bare launch, global binding option and command-specific binding option, all at method 0, with complete Python-entry and native pre/post MPI observations. It accepts wide masks as data and retains records before MPI initialization; it contains no solver, PMPI shim or performance claim. Admission still requires fresh CPU/AI queues, budget locks and a definite receipt. [Design](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-launcher-order-20261026/README.md).

The full ABBA solver remains an **unsealed, unsubmitted draft** because affinity qualification failed. Its lifecycle metadata now correctly matches a 90-minute PBS request (768 SU maximum), 87-minute internal deadline, and all four required solver arms. Offline checks are not cluster qualification.

## Failed branch and corrected interpretation

Job **25957725** did not qualify pre-exec capture: 128 successful pre-exec records, 17 wide-mask rejections, 367 absent ranks, no retained MPI audit or topology output. Command return 143 occurred after 4.25 seconds against a 184-second timeout; do not call it timeout expiry. A wide mask can already occur before exec of the MPI probe, so MPI_Init is not established as the sole cause. Frozen lifecycle metadata was stale; retain it as provenance evidence. PBS history is unavailable, so final scheduler state and charge remain unknown and the full **42.666667 SU reservation stays retained**. [Replayed review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/exec-25957725/RESULTS.md).

Previous method-0 and PALS-environment controls lost affinity; the first entry-time shim restored only 253/512 ranks. Do not repeat those unchanged losing arms or weaken the actual mapping gates.

## Budget, access and preservation

Owner authorized remaining CPU grant before their 30 October planning deadline. Cumulative NSCC campaign ceiling **29,777.846 SU**; last captured commitment **4,752.866667 SU**, headroom **25,024.979333 SU**, before new admission and conservative site reconciliation. Unknown old/shared maxima remain retained. Live 26 October read displays **27,532.791 SU site balance**, used 2,467.209, zero in doubt, with a 25 October 21:55:31 site label. Site metadata says 15 November expiry; it does not prove the owner's 30 October date. CPU project 59000042 is distinct from AI 59010042. [Authorization](cpu-campaign-before-oct30-20261024.md).

CPU SSH was restored and verified on asp2a-login-nscc02 using a separate cpu-r6 master. The existing VPN was left running at that check; it later expired, as recorded above. That earlier access is historical. A separate read-only GPU-login connection is used only to check combined PBS capacity; no AI submission or modification. Iris requires interactive forced-TTY gateway auto-jump. One failed bridge connection did not establish loss of Iris access; later actual login01/login02 connections succeeded. Do not print or archive credentials or session state. [Access evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261026/REPORT.md).

Capture, screen, verify, commit and push each small milestone. New job receipts and failed raw logs must remain recoverable. Historical large external objects still require an off-host copy. The 23 October 40-slide package remains a dated snapshot; no submission materials changed in this turn. [Earlier handoff, historical](history/HPC_CURRENT-before-dual-cpu-20261026.md). [Latest full reasoning](../reports/research-journey-20261019/journal/entries/20261026-hpc-dual-cluster-next-tests.md). [Research journal](../reports/research-journey-20261019/journal/README.md).
