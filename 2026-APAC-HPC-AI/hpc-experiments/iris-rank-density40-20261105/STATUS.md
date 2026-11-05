# Forty-step rank-density comparison accepted

Iris accepted **job 2294916** at `2026-11-05T09:09:22.865597Z` UTC. This is a new rank-density question, not a repeat of the rejected graph-placement candidate. The owner asked why the selected 21.0512 s/step observation had only 14 steps; that short graph arm was not a matched winner, and its complete reversed short comparison lost 5.3685%. Its raw evidence remains preserved. The new comparison uses the same forty-step horizon in all four arms.

## Hypothesis and exact comparison

A1 uses 56-rank Scotch; B1 and B2 use 48-rank Scotch; A2 returns to 56. All four arms use the same physical 65,334,765-cell problem, v2512 double precision, fixed iteration work, default uncollated handler and one exclusive 56-CPU Iris allocation. The required partition and native initialization differ with rank count. Fewer ranks increase average cells per rank by 16.7%; reduced communication is a hypothesis, not an observed bottleneck or predicted win. No socket balance is assumed under the default launcher.

Each arm must complete **40 steps /39 measured intervals** with finite force outputs, fixed iteration counts, native End, clean exit, matching source and runtime identities. Source files and initialized fields are pinned independently for each partition. The 48-rank prerequisite initialization 2294915 passed all mandatory stages. Same-partition force repeats use the existing numerical tolerance; cross-partition Cd drift is retained without an invented universal Basic tolerance. Shortened or timed-out arms cannot become a complete result.

## Bounds and evidence

One node, 56 allocated CPUs, zero GPUs, low QoS, maximum **2.5 hours /140 allocated CPU-hours**. Each solver arm has an 1,800-second cap and each preparation a 150-second cap. The runner protects the entire remaining sequence and 480 seconds for final review under its 8,700-second internal deadline. Five-second procfs samples and phase markers are diagnostic; missing telemetry is not zero or evidence of healthy hardware. The Python affinity probe measures pre-MPI_Init process masks, while native binding reports are retained separately.

Root imported the runner and exercised the time-window, rank-header, source-transform, binding completeness and repeat-tolerance gates. Review caught and corrected an unused missing-module import before freezing. Both actual caseDefinition transformations match the accepted source hashes. The 48-rank native-parser fixture changes only headers of a retained 56-rank log and is explicitly a test, not a measurement. All **100 frozen file hashes** verified after deployment; a fresh queue check preceded locked admission.

The internal ledger had 1,227 conservatively consumed and zero reserved. This one selected 140-hour envelope raises the agent's internal stage from 1,289 to **1,367** (an explicit 78-hour extension), not a new owner budget or known site SU allowance. Site SU is unknown; NSCC/AI accounting is separate. The one-own-allocation cap remains in force.

## Current interpretation and next decision

Submitted is not a result. No new speedup, winner against organizer/teammate, full official simulation or contest score is claimed. Review all four complete means, adjacent contrasts, repeat drift, tails, Cd trajectories, node/resource samples, transport warnings and cost before deciding whether a confirmation is justified. Keep the old losing branches closed. No background Codex or automatic follow-up was enabled.
