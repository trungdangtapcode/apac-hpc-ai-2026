# Launcher option placement diagnostic: job 25999546

This review replays the retained archive and manifest and cross-checks the
separately retained exact PBS stdout against its byte and SHA-256 metadata. It
made no scheduler connection and changed no submitted payload.

## Result

The three arms were bare `mpiexec -n 512`, deprecated global
`mpiexec --cpu-bind thread -n 512`, and command-specific
`mpiexec -n 512 --cpu-bind thread`. Each arm retained 512 Python-entry records,
512 native records immediately before `MPI_Init_thread`, and 512 native records
after it. All six probe commands returned 0.

For every arm, every Python-entry and native pre-init mask contained one CPU.
The Python and native pre-init CPU and hostname records matched for each PMI
rank. After initialization, all 512 native masks contained CPUs 0–255. Affinity
status was 0 throughout, as were native `errno` values. Each phase had 128
records on each of four hosts. The Python and native pre-init records show 128
unique logical CPU IDs per host. Physical-core uniqueness was not measured;
these records contain no core topology.

Native post-init records cover world ranks and PMI ranks 0–511, each unique.
Joining by PMI rank produces a complete one-to-one world-rank mapping; 510 of
the 512 pairs are nonidentity mappings. The pre-init record's `rank` field
matches its PMI rank, so the review does not treat it as an MPI world rank.
Hostname stays consistent across Python, native pre-init and native post-init
records for each PMI rank.

The exact PBS stdout is 254 bytes with SHA-256
`cc1d07ef8635b00c04400f140d2263c608d65acd48944b9eb3d88cb2944198d4`, matching
its metadata. It contains three `MPI_SUMMARY_JSON` records, one for each arm;
each reports world size 512 and zero ranks with capture or identity errors,
followed by `COLLECTION_FINISHED`.

## Source and allocation evidence

The before/after payload hashes are identical. All three pinned source-file
checks report `OK` before and after. The PBS terminal record is state `F`, exit
status 0, project 59000042, with 512 CPUs, zero GPUs and 13 seconds walltime.
The request was four exclusive scattered nodes, 128 CPUs and MPI processes per
node, 32 GB per node (128 GB total), no GPUs, and five minutes walltime. PBS
reports `cput=00:04:23`, `mem=3254988kb`, `vmem=90162296kb`, and `cpupercent=2086`.
These are scheduler resource fields, not per-phase hardware telemetry.

At the recorded queue rate of 1, `512 CPUs × 13 seconds ÷ 3600` estimates
1.848888889 SU (about 1.85 SU). This is a walltime-based estimate, not posted
billing. The rank-probe wall times were 0.50–0.53 seconds for Python and
2.12–2.24 seconds for native probes.

## Interpretation and limits

For this method-0 order-control run, moving the CPU-binding option between the
bare, global and command-specific forms did not change the observed pre-init or
post-init masks. Close this unchanged launcher-option-placement branch. The
earlier method-3 job 25957725 had partial pre-exec wrapper rejections; this
method-0 run does not establish all method-3 behavior or explain those earlier
rejections. The common post-init expansion shows when the mask changed in this
probe, but does not prove `MPI_Init_thread` alone caused it.

The retained collection has 4,630 archived files, compressed archive size
123,230 bytes and aggregate uncompressed file size 1,995,910 bytes. The replay
checks the archive SHA-256 and each member's manifest byte count and SHA-256.
An earlier per-file Python packaging attempt timed out without leaving a
retained archive; the completed collection used native `tar`. The collection
contains diagnostic text and per-rank records, but excludes the runtime
environment snapshot and compiled executable. No system-call trace or physical
core topology was collected. This is a short startup diagnostic, not an
OpenFOAM solver or performance result.

A bounded one-rank `strace` observer matched to this launcher and probe sequence
is the next diagnostic direction for identifying which process or library
changes affinity. The current evidence does not itself authorize or start that
work.

Run `python3 review.py` from any directory to re-verify the archive and stdout
metadata and regenerate `review.json`.
