# Full default-versus-NUMA Scotch pair submitted

**25907753.pbs101: R** at 2026-10-21T19:54:02.909127+00:00. Accepted 2026-10-21T19:52:53.014595+00:00; one exclusive CPU node / 128 ranks / 440 GB / no GPU, max 29 min / **61.866667 SU**. Native default Scotch control and fresh NUMA tree candidate each run 40 steps after mandatory candidate initialization. Physical-core and NUMA grouping guards run outside solver timing. Keep zero-field/source hashes, all fixed numerical work, native timers, force outputs and resource/phase evidence. See PLAN.md.

Fresh CPU own queue was empty, read-only combined PBS capacity and project balance passed, durable intent/reservation and exactly one qsub retained. Expanded cumulative ceiling **1,000 SU**, conservative consumed **85 SU**, new reservation **61.866667 SU**, total **146.866667 SU**. Old 100-SU first-wave ceiling remains historical. No AI changes or background Codex.

Native graph filter passed in 25907688; still no NUMA solver gain. One ordered pair does not establish a stable win. The wrapper preserves the inherited CPU_HS_PAIR_PASS marker for compatibility; exact role input hashes identify **default Scotch vs NUMA Scotch**, not hierarchical vs Scotch. No frozen payload is changed after submission.

Next prepare validated 256-rank inputs as an afterok follower while this pair runs, if combined cap permits. A failed parent blocks that follower; keep one CPU allocation active at a time.
