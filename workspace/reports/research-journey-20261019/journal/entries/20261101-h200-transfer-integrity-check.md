# Verify that completed transfer evidence remains recoverable

Owner steering: continue checking, 1 November 2026. The four source interventions
have already been measured and none clears the incumbent useful-gain gate.
The current question is whether any job or unreviewed result remains and whether
the retained evidence is intact; no new GPU experiment is necessary to answer it.

At 2026-11-01T09:09:43.729316+07:00, Vietnam time (UTC+7), own H200 queue is empty. Current sacct confirms
all nine referenced allocations COMPLETED 0:0 with 16 H200 each. Source/archived
inline/external checks verify 1261 files, 2,229,023,012 source bytes, and 19 unique
external zstd objects fully decompressed and rehashed. All checks pass against
sealed SHA256/size and matching archive metadata. Inline files are Git-tracked;
HEAD equals origin/main at reference 9697a539. This is evidence integrity for
these retained runs, not a claim that all history/chat/full runtime rebuild or
official model quality was checked. External objects remain local; off-host
copy is not established. Actual nine-run occupancy 28.337778 GPU-hours, zero PBS SU,
no new GPU submission or credit reservation.

Correct a minor metadata drift: the four-port register still described native
phase checks in future tense. Actual allocated source/provider/context checks
passed and are linked; per-rank steady-state mode/kernel traces remain missing.
Add the existing chunk comparator IDs/exact deltas without changing raw results
or frozen payloads. Performance interpretation remains no useful gain, keep
the existing H200 recipe; source H100 hardware-transfer limits stay explicit.

Decision: complete this audit and preserve its receipt. No unchanged losing
repeat or broad restart is justified by an empty queue. This does not authorise
H100 login/spending, HPC work, schedules/background Codex or publication edits.

[Full audit and per-file source/archive/object results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-integrity-check-20261101/README.md).
