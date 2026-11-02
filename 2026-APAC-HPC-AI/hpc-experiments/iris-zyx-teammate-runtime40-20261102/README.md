# Conditional method comparison under teammate runtime

**PREPARED ONLY: not deployed, submitted or reserved.** Do not run job.sbatch directly. Existing job 2294640 keeps its allocation and full reservation. This payload is not an automatic successor and no Codex schedule exists.

Question: if our hierarchical zyx choice beats default Scotch under common default MPI/uncollated, does that result survive under the same supplied teammate socket/core and collated runtime on both methods? This is closer to comparing against the teammate recipe than ranking unrelated historical Iris means. A sub-22 Iris observation does not predict beating 2.079 seconds on Gadi.

Control A: accepted initialized Scotch. Candidate B: accepted initialized hierarchical `(7 4 2)`, order zyx. Original 65M physical mesh, canonical 41 inputs, v2512 double-precision build, 56 ranks on one exclusive Iris node, fixed numerical iteration counts and native function objects are unchanged. Each method uses its own 1040-file partition/field manifest. All copies are independent and checked before/after. The standard method and parameter choice attribution stays unchanged.

Every arm uses `--map-by socket --bind-to core` and `-fileHandler collated`. Order is **B1 / A1 / A2 / B2**, 40 steps / 39 measured intervals each. The reversal places the candidate at the allocation ends, but changing common runtime means it is not a pure replication of the default-runtime parent. Native I/O headers, exact commands, complete work/output, Cd by method, runtime seals, launcher reports, resource logs and missing telemetry must be reviewed. Existing reported MPI maps were identical; do not claim this changes placement. Isolated collated I/O did not survive reversal; do not resubmit it as an already established benefit.

## Eligibility before any deployment or admission

Parent 2294640 must be terminal, completely collected and independently reviewed. Require all source/native/runtime gates, both adjacent comparisons and pooled mean favoring zyx, and explicit inspection of repeat drift and native sample recommendations. If the parent reverses direction or is materially unstable, this transfer experiment is not justified; close or revise the hypothesis rather than submit blindly. A short screen is never a full scored run.

If eligible, recheck live queues and owner authority, reconcile the parent once, and bind the exact new payload hashes with an independent root review. Review stage accounting under the existing Iris lock before any durable reservation or one-shot submission. The maximum is **9000 seconds / 140 allocated CPU-hours**, not currently reserved or added to any spending envelope. One active owned allocation remains mandatory. No Gadi identity or project budget is available; no Gadi deployment or result is claimed.

If this passes, subsequent same-platform full-length confirmation is still needed. Four-node Gadi validation would need authorized access, 416-rank factors and same-site controls; neither seconds nor percentage gains can be assumed to transfer.
