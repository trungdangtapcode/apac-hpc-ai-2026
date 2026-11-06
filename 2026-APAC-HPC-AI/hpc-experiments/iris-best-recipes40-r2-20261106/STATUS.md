# R2 accepted with actual qualified proof files and a new I/O-only candidate

Iris accepted **2294997** at `2026-11-06T04:27:14.649386Z` UTC. At **11:28 on 6 November 2026 Vietnam time**, it is RUNNING on iris001, elapsed 1:42, with empty batch stderr at that snapshot. This is allocation/startup status, not a new native performance result.

## Why this run differs

The old 2294920 failed before its final teammate solver arm because our stdout line parser dropped rank 28 when two probe records interleaved. All 56 rank records are diagnostically recoverable, but the job remains FAILED 1:0, five-of-six arms only, with no final source/runtime gates or certified matrix score. Its five complete native outputs remain preserved and independently replayed. Both unchanged hybrid48 arms were slower than neighboring original48 arms, so that combined mapping+I/O candidate is not repeated.

The replacement preserves original48 default mapping and tests **collated I/O alone** against its existing uncollated handler, with the actual teammate56 socket/core+collated recipe as a peer control. All sources, original physics, initialization, precision and fixed iterations remain pinned. The node is explicitly constrained to iris001 to retain the historical hardware context.

| Order | Recipe | Ranks | MPI mapping | Handler |
|---|---|---:|---|---|
| T1 | teammate56 |56|socket/core|collated|
| O1 | original48 |48|default|uncollated|
| D1 | io48 |48|default|collated|
| D2 | io48 |48|default|collated|
| O2 | original48 |48|default|uncollated|
| T2 | teammate56 |56|socket/core|collated|

Every arm retains **40 steps /39 intervals**, native work/output checks, source/initialized-field/payload/runtime hashes before/after, same-recipe force repeats, unchanged-partition O/D force regression checks, all slow timings and bounded resource telemetry. Cross-decomposition teammate56-versus48 force trajectories have no invented universal Basic equality threshold. Absolute seconds and both repeated credible controls are primary. No historical 22-second improvement, new winner or performance gain is claimed before actual complete data.

## Repair qualification and provenance

Diagnostic **2294996 COMPLETED 0:0**. All four 56/48/48/56 modes and 208 strict proof files pass actual MPI execution and root replay; 227 retained hashes verify. The exact qualified probe_writer.py/read_rank_proofs.py bytes are reused. Each rank writes a unique exclusive file with rank, world size, hostname and CPU mask; exact filenames/schema/count/host/nonoverlap are required. Rank identity is not extracted from stdout. MPI return and separate binding/native output checks remain. This is pre-MPI_Init launcher affinity evidence, not solver-thread residency proof.

Root tests pass actual writer JSON/overwrite rejection, protocol rejection cases, 101 source hashes, full-window guards, valid handler/rank wiring, source transformations and synthetic label arithmetic (test fixtures, not measurements). The actual qualification review hash is checked before admission. Old submitted payloads are immutable. Each rank proof and verifier output is preserved by the R2 collector.

## Bounds, accounting and next review

One exclusive node /56 allocated CPUs /zero GPUs /maximum 4 hours = **224 allocated CPU-hours reserved**. Each solver cap is 1,800 seconds; preparation 150 seconds; final reserve 480; internal deadline 13,900; wrapper 14,340. Six full windows require 12,180 seconds. Free filesystem 96 GiB is checked separately from quota. Iris low QoS 12-hour limit was verified during preparation; no early arm shortening or blind resubmission.

The failed parent's actual 102.277778 CPU-hours was conservatively 103, and its 224 maximum retired once. The diagnostic cost 0.031111, conservatively 1, retired 4.666667 once. Before admission, 1,500 is consumed and zero reserved. This one 224-hour request extends the internal stage 1,620→1,724 (+104), not a new owner budget or known billed site SU. NSCC/AI are separate; fresh queue, locks and one-own allocation cap remain enforced.

Collect the entire matrix and terminal/source/runtime-after evidence, replay native output independently, then report absolute means/arms/tails/errors first. A relative percentage against a slow control is not an absolute record. Retain every losing branch; no new score until all gates pass. No background Codex, automatic schedules or unsolicited MFA was enabled.

## Actual integrated startup — 6 November 2026, 11:32 Vietnam

Job 2294997 is RUNNING on iris001, elapsed 5:12. T1 preparation passed the actual file verifier with exactly 56 proof files, complete rank/world-size/schema/host/nonoverlap checks; native solver has started step 5. Batch stderr is empty at this snapshot. This verifies the repaired integration has reached native execution, not that all six arms or final measurement gates have passed. No complete new seconds-per-step result, winner or historical record is claimed. Source proof: startup-verification.json.
