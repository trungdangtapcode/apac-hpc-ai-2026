# NSCC rank-zero affinity trace: job 26004608

## Question and controlled comparison

The preceding launcher-order diagnostic, job 25999546, observed singleton native masks before `MPI_Init_thread` and masks containing logical CPU IDs 0–255 afterward, but collected no syscall trace. This follow-up asked which calls rank zero makes while MPI initializes and whether an affinity setter is visible.

The five-minute, four-node allocation ran two 512-rank arms with the same native probe and runtime: an untraced control, followed by an arm traced only on PMI rank zero with `strace -f -k` for `sched_getaffinity` and `sched_setaffinity`. The probe records affinity immediately before and after `MPI_Init_thread`. No solver runs and the probe does not modify affinity.

## Collection and terminal evidence

The real PBS query was retried from `asp2a-login-nscc01` and returned `Unknown Job Id` (exit 153); PBS history was no longer available. The terminal classification below therefore uses the saved filtered query at **2026-10-26 16:31:10.939654 UTC**, not a live status: state F, Exit_status 0, project 59000042, four scattered exclusive nodes, 512 CPUs, zero GPUs, five-minute walltime request, 11 seconds reported walltime, and 6 minutes 31 seconds reported CPU time. `fresh-qstat.stdout.json`, `.stderr.txt`, and `.exit-code.txt` preserve the failed fresh query.

Native `tar` collected only `runs/26004608` and the explicitly selected batch stdout `cpu-affinity-strace.o26004608` outside that directory. The archive is 86,968 compressed bytes and contains 3,102 regular files totaling 1,442,271 bytes. The compiled `mpi-init-probe` and `runtime-environment-whitelist.txt` were excluded before transfer. `collection.json` records each member's byte count and SHA-256; `review.py` replays the archive and verifies every hash. Archive SHA-256: `0e8706b87589bdad0cef4d662653db840041360870b49d10334fb8513dfe2363`.

## Findings

Both arms retained all 512 entry records, all 512 native pre-init records, and all 512 native post-init records. Every native affinity query succeeded with errno 0. Both MPI summaries report world size 512 and zero capture or identity errors. The six relevant source files passed before/after checks with identical hash-check output. The worker and each arm command returned zero. The wrapper records per-arm return codes but does not make an arm failure fatal; here the recorded arm codes and summaries independently confirm success.

All post-init ranks in both arms had the same observed mask: logical CPU IDs 0–255. Each host contributed 128 world ranks. PMI rank and MPI world rank form a complete one-to-one crosswalk, with 510 of 512 pairs nonidentity in each arm; join placement records by PMI rank rather than assuming world rank equals PMI rank.

Pre-init masks contain a material asymmetry. In the traced arm, all 512 ranks had singleton masks, 128 per host. In the untraced control, three hosts each had 128 singleton masks, but all 128 ranks on `x1002c7s7b1n0` reported the full logical CPU set 0–255 before MPI initialization. The other three control hosts stayed singleton. All hosts in both arms reported 0–255 after initialization. The reason for this control-arm, one-host pre-init difference is unresolved; this single allocation does not establish a general node-specific policy.

The rank-zero trace contains three `sched_getaffinity` calls and no `sched_setaffinity` call. Two stacks point to the probe's own pre- and post-init snapshots. The third is inside Cray MPICH 8.1.15: `_cray_ofi_get_my_rank_numa_node`, called through `MPIDI_CRAY_ofi_nic_assign_policy`, `open_fabric`, and `MPIDI_OFI_mpi_init_hook` during `MPI_Init_thread`. This identifies the caller of an affinity **query**, not the actor or mechanism that widened the mask. The trace is limited to PMI rank zero and its followed process descendants; it cannot rule out activity outside that traced process tree.

The native OpenFOAM 2512 `libPstream.so` path was recorded and `ldd` resolves it with Cray MPICH 8.1.15 (`libmpi_gnu_91.so.12`), matching the probe's MPI linkage. `strace` was version 5.18 with libdw stack tracing enabled.

## Resource coverage and limits

The batch stdout, phase markers, per-arm `/usr/bin/time -v` reports, scheduler resource fields, module logs, MPI/strace versions, native `libPstream` path and dependencies, and all per-rank masks were collected and inspected. The per-arm probe elapsed times were 3.64 seconds for control and 2.52 seconds for rank-zero tracing; these startup diagnostics are not solver timings and do not support a performance claim. PBS reported 329,400 KB memory and 86,248,492 KB virtual memory for the job; these are scheduler accounting fields, not sampled per-phase hardware telemetry. No CPU/GPU utilization sampling, physical-core topology, or solver diagnostics were collected.

The observations bracket the MPI initialization call but do not by themselves prove MPI initialization caused the mask transition. In the traced arm, the captured MPI library call is a `sched_getaffinity` query; no setter was captured. The untraced control's anomalous pre-init host also prevents treating the arm comparison as a clean placement control. No affinity fix or solver benefit is established.

## Next hypothesis

The rank-zero trace can identify MPI's NUMA-query call but cannot identify who changes the mask, and the control showed an unexplained one-host pre-init exception. A distinct, bounded follow-up would compare per-node entry masks under the same 512-rank launch while tracing one representative process on each host across process creation and MPI initialization, with native pre/post snapshots retained for every rank. The acceptance question is whether the widening is host-wide, rank-local, or outside the observed MPI process tree. Review fresh queue and budget state before any submission; this report does not submit or reserve work.

## Replay

Run `python3 review.py` in this directory to validate the retained archive, manifest, both arm record sets, world-rank/PMI crosswalk, command and worker return codes, trace caller frames, and native Pstream evidence, then regenerate `review.json`.
