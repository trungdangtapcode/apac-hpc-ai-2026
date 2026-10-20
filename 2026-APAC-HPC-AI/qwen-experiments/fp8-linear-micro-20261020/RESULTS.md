# Native FP8 kernel screens submitted on both platforms

| Platform | Job | Scope | Last retained state |
|---|---|---|---|
|H100|222210.pbs111|1 node, 8 GPUs, 10 minutes|Q at 07:05:56 UTC|
|H200|24983|1 node, 8 GPUs, 10 minutes|Priority-pending at the subsequent queue query|

Both use the same frozen bench.py, config and run script. Source-hash, shape/numeric/input-integrity and bounded graph-timing gates are inside the payload; syntax/inverse-byte/checksum checks passed before submission. There are **no microbenchmark timings or numerical results yet**. These isolated jobs do not load the Qwen model or produce contest goodput. Do not count exit zero alone as kernel acceptance or infer model speedup from microseconds.

H100 was submitted only after both prior model jobs were terminal, their allocated-walltime charges reconciled and a fresh queue/credit query confirmed an empty own queue. Maximum reserve **170.666667 SU**, published Used **37215.572**, Balance **26784.428**, In Doubt zero at pre-submit publication; internal headroom **13613.761333 SU** under unchanged 51000 cap/13000 project buffer. One 8-GPU allocation only, no parallel 16-GPU PBS allocation. H200 submitted under the shared watcher lock as the fifth active job; four previously queued model jobs keep their positions and frozen bytes.

Every receipt was persisted immediately; no retry or uncertainty. This standalone H200 micro has its authoritative receipt here rather than a model-run registry entry, so it cannot be mistaken for an accepted full serving run. Real scheduler counts still enforce the five-job cap.

[Plan](PLAN.md) contains evidence, exact native helper paths, two projection shapes, M values, guards, timing/numeric limits and the >=5% representative signal required before a later full-model pair. The prior unobserved H100 receive2 check is closed at +0.0464%; default interval1 remains. Official accuracy is unverified; no numerical or workload shortcut, native hardware-guard bypass, package edit or background Codex.

## Final queue check

At 2026-10-20T07:09:11.533394+00:00, H100 222210 remains Q: Not Running: Job is requesting an exclusive node and node is in use. All five H200 jobs remain Priority-pending. No kernel timing or numerical result is available; preserve queue positions. Raw scheduler evidence is in pbs-final.txt, slurm-final.txt and final-live.json.
