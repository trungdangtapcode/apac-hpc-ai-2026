## 18 October 2026, 19:25 UTC — failed N58 replication, bounded diagnostic retry

24588 timed out: raw records 857 warmup, zero scored. Warmup sent 858 and indefinitely awaited its final completion; all model workers became ready normally. Connection refusals at shutdown are downstream, not an identified root cause. No accepted measurement. Raw artifacts/phase evidence retained. Prior peak remains unconfirmed by N58 repeat/new same-load control.

Submitted 24647: exact same serving config and scoring arguments, with a 360-second whole-client guard plus 15-second kill fallback. This is containment and one diagnostic retry, not a root-cause repair. Any aborted client is rejected; no request filtering or phase shortening. If repeated, stop this retry path and diagnose stream completion rather than unchanged retries. Queue 24589/24639/24640/24641/24647 pending Resources, five active. H100 VPN still unavailable; no new PBS outcomes or credit. No AI schedule/background watcher or official changes.

Full evidence and acceptance rules: [failure diagnosis and retry](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1923/RESULTS.md). Older entries are historical snapshots.

