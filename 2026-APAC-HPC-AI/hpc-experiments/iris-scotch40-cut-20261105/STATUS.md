# Distinct Scotch40 cut accepted

Iris accepted **2294919** at `2026-11-05T16:21:46.687207Z` UTC. Two reviewed opposite-order forty-step comparisons (2294916/2294918) favor 48 over 56 ranks by 17.3826% and 19.2133% on iris001. They justify exploring a lower rank density, not assuming it will help. The next hypothesis compares 40 to 48 after required preparation. More cells per rank and fewer active cores can offset any lower overhead.

This job only creates and validates a fresh **Scotch40 cut** from the exact official 65,334,765-cell serial mesh and unchanged physical input/field pins. The sole pinned case-text difference from the valid N48 cut is nCores 48→40; the native cut must produce exactly processor0..39, all 40 positive per-domain cell counts summing to 65,334,765, and 240 restored initial fields. All eight mesh file hashes and source hashes before/after must pass. No READY, parallel initialization, solver, speedup or score is claimed.

One exclusive Iris node, 56 allocated CPUs, one serial task, zero GPUs, low QoS, maximum 40 minutes: **37.333333 allocated CPU-hours reserved**. Native decomposition is capped at 30 minutes. Root replayed 45 payload hashes, Bash/Python syntax, exact 40 acceptance and 39/41 rejection fixtures, and unchanged mesh/physics. A fresh queue check preceded locked admission; the remote deployment verifies all 45 hashes and refuses any existing artifact. No old run or source is overwritten.

Parent 2294918 used 81.666667 CPU-hours, conservatively 82; its 140 maximum retired once. Internal ledger is **1,392 consumed +37.333333 reserved** under unchanged 1,450 stage. Billed site SU is unknown, NSCC/AI accounting separate, one-own active allocation cap preserved.

On completion, independently review scheduler/native mesh/cut/source/resource evidence and retire this maximum once. A valid cut enables a separately reviewed mandatory initialization chain before any forty-versus-forty-eight solver comparison. Failure is retained and diagnosed, not counted as a valid measurement. No background Codex or automatic follow-up was enabled.
