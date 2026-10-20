# Startup-cost pair submitted — 2026-10-20T13:28:06.162122+00:00

## Priorities updated and startup-cost pair submitted — 2026-10-20T13:28:06.162122+00:00

Keep the current PD architecture and measured settings; prioritise repeatability/rebuild, then lower iteration cost and profile-supported distinct changes. Latest H100 chunk 2048 loses 26.1328%, retain 4096; H200 25020 passes 256 kernel cases but yields no consistent useful provider alternative. [Updated research priorities](../reports/research-priorities-20261020/PLAN.md).

New H100 **222407 R → 222408 H**, verified serial node-prefetch off/on pair at fixed 4096/N54/round-robin. Workers, official scoring, output checks, transport, observation and profiles are unchanged. Each 16 H100/30 min/max 1024 SU, total 2048 SU reserved after fresh empty queue/credit check. Pre-submit Used 40272.495 SU, Balance 23727.505 SU, In Doubt 0; internal headroom 8679.505 SU under unchanged 51000 cap/13000 buffer. No result yet. [Exact bounded hypothesis, cache-state limits, fixtures and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/RESULTS.md). Four H200 model positions 24928/24962/24964/24965 remain pending and untouched; no blind fifth job. Model peaks unchanged; official full-set accuracy still unverified. No submission package, auth or background AI change. Earlier scheduler/credit snapshots below are historical.

[Definite receipts](pbs-receipts.json), [verified serial dependency](pbs-post-submit.txt), [fresh pre-submit ledger](pbs-pre-submit.txt), [fixtures and bounds](validation.json), [plan](PLAN.md). No startup saving or goodput improvement is claimed before terminal evidence.
