# Completed H200 transfer integrity check

Checked **2026-11-01T09:09:43.729316+07:00**, Vietnam time (UTC+7). The own H200 Slurm queue is empty.
All nine allocations 27777, 27779, 27781, 27783, 27804, 27806, 27826, 27828, 27830 are
COMPLETED 0:0 and retain 16 H200 allocations in current accounting. No new own
allocation or unreviewed result was found after the latest phase stage.

## What was verified

- **1261 files** match their sealed source SHA256 and size.
- **2,229,023,012 bytes** of source artifacts were read and checked.
- Every sealed file has matching archive capture metadata. Inline archive bytes
  match and are tracked by Git.
- **19 unique external zstd objects** were decompressed and their
  full uncompressed bytes rehashed, rather than only checking file existence.
- Git HEAD matched origin/main at reference commit 9697a539facb8a3472b4a342ab1c1e72db78ad63.

Per-file source/archive/object checks (retained source: `audit.json`), repeatable read-only audit (retained source: `audit.py`).

The scope is these nine retained H200 allocations, not every historical run,
chat message, full image/model reconstruction or official model accuracy.
Git origin contains the tracked bytes and recovery metadata; the external
artifact store is local and this check does not establish an off-host copy.
Actual nine-allocation occupancy is 28.337778 GPU-hours,
zero PBS SU; this audit submits no GPU job and incurs no new PBS reservation.

## Result interpretation is unchanged

The four additional distinct source-intervention ports are reviewed: 27804
chunk 6144, 27806 chunk 8192, 27828 decode-mode, 27830 prefill-mode. The extra 27826
explicit control is not counted as a candidate. The chunk ports lose 7.114431%
and 4.523207% to their documented H200 reference. The phase ports change goodput
by +0.006223%/+0.130765% against their fresh explicit control. No useful gain
above the prospective 1% gate is established; retain the existing H200 recipe.
Full official quality remains UNKNOWN; local smoke/retrieval is not certification.

The candidate register's old pre-execution wording is corrected: actual native
phase provider/context/restoration preflights passed, while per-rank steady
mode/kernel tracing remains uncollected. Add missing control IDs and exact
percentages for the two chunk rows. No measured values, raw files or frozen
submitted payloads are rewritten by that metadata correction.

The requested transfer stage is complete and no winning repeat qualifies.
No broad research restart, H100 authentication/spending, HPC payload/budget
change, background Codex, schedule or published package change is made here.
Completed phase review (retained source: `RESULTS.md`),
corrected four-port register (retained source: `distinct-port-register.json`).
