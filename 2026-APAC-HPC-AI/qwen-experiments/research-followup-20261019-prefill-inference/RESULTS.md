# Prefill-only inference-mode submission

**221966.pbs111** was submitted at 2026-10-19T17:59:18.182180+00:00 with verified `afterany:221924.pbs111`. The complete serial chain is **221923 → 221924 → 221966**: explicit-default control, decode-only candidate, prefill-only candidate. The post-submit queue shows Q/H/H, so no new measurement exists at this checkpoint. Control is waiting for exclusive nodes currently in use.

[The plan](PLAN.md) explains the separate phase hypotheses, source and profile evidence, identical ranked workload and preflight/output gates. Each candidate must be compared with shared control 221923. No combined-mode performance is inferred. Preserve all raw failures or regressions and require a fresh matched repeat before promoting a useful gain.

Published Used remains **32604.728 SU**, Balance **31395.272 SU**, In Doubt **0**. The additional maximum reservation is **1536 SU**, total outstanding **4608 SU**, leaving internal headroom **13787.272 SU** under the unchanged **51000-SU cap** and **13000-SU project buffer**. Reservations are maximum bounds, not actual charges. At most one 16-GPU allocation can run in the dependency chain. Three active PBS slots and five existing H200 positions are preserved.

The [NCCL correction](../status-review-20261019-1755/CORRECTION.md) was resolved from existing sealed TUNING logs and matching-version source without another GPU job. Simple selected successfully; the control already used it for large messages. Earlier inference from LL-labelled kernels was wrong. Scores and quality claims are unchanged. No new peak, official accuracy, authentication, automation, slide or submission-package change.

Frozen payload hashes, upload verification, qsub stdout, serial dependency and pre/post scheduler snapshots are retained here.
