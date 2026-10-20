# First prefetch pair accepted locally — 2026-10-20T13:59:49.446440+00:00

Both full local gates pass. Prefetch uses759s versus934s allocated walltime (-18.737%) with goodput2395.929777 versus2411.827128 (-0.659%). Different nodes and unknown initial cache state prevent a causal claim; one reverse-order confirmation is justified. [Full review](PAIR_REVIEW.md), [structured startup/cost comparison](startup-comparison.json). Older pending snapshots below are historical.

# Control accepted; candidate still running — 2026-10-20T13:51:04.547728+00:00

## Prefetch control reviewed; candidate running — 2026-10-20T13:51:04.547728+00:00

H100 222407 full local PASS at 2411.827128 good output tokens/s, 98.285% qualifying, zero errors. Topology-script-to-ready 602 s, allocation 934 s, estimated 531.342222 SU unposted. Native off receipts pass both nodes; all 16 diagnostic traces and matched scored hardware/server/tail evidence inspected. Candidate 222408 running; live read receipts complete in 27.527/27.290 s per node, no terminal saving claim. H200 24928/24962/24964/24965 still Priority-pending. [Control review and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/CONTROL_REVIEW.md). Published Used 40272.495 SU unchanged, Balance 22703.505 SU, In Doubt 1024 SU; retain both maximum reservations, internal headroom 8679.505 SU. Peaks unchanged, official accuracy unverified. Earlier scheduler/credit snapshots below are historical.

Earlier snapshots below are historical.

# Startup-cost pair submitted — 2026-10-20T13:28:06.162122+00:00

## Priorities updated and startup-cost pair submitted — 2026-10-20T13:28:06.162122+00:00

Keep the current PD architecture and measured settings; prioritise repeatability/rebuild, then lower iteration cost and profile-supported distinct changes. Latest H100 chunk 2048 loses 26.1328%, retain 4096; H200 25020 passes 256 kernel cases but yields no consistent useful provider alternative. [Updated research priorities](../reports/research-priorities-20261020/PLAN.md).

New H100 **222407 R → 222408 H**, verified serial node-prefetch off/on pair at fixed 4096/N54/round-robin. Workers, official scoring, output checks, transport, observation and profiles are unchanged. Each 16 H100/30 min/max 1024 SU, total 2048 SU reserved after fresh empty queue/credit check. Pre-submit Used 40272.495 SU, Balance 23727.505 SU, In Doubt 0; internal headroom 8679.505 SU under unchanged 51000 cap/13000 buffer. No result yet. [Exact bounded hypothesis, cache-state limits, fixtures and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/RESULTS.md). Four H200 model positions 24928/24962/24964/24965 remain pending and untouched; no blind fifth job. Model peaks unchanged; official full-set accuracy still unverified. No submission package, auth or background AI change. Earlier scheduler/credit snapshots below are historical.

[Definite receipts](pbs-receipts.json), [verified serial dependency](pbs-post-submit.txt), [fresh pre-submit ledger](pbs-pre-submit.txt), [fixtures and bounds](validation.json), [plan](PLAN.md). No startup saving or goodput improvement is claimed before terminal evidence.

## Early control launch observation — 2026-10-20T13:29:22.393401+00:00

222407 is running and 222408 is dependency-held. The common control metadata-only stage completes on both allocated nodes, verifies 24 shards / 236426193880 bytes, and takes about 0.06 s per node. This validates the actual control startup path only; there is no candidate I/O or terminal performance/cost result yet. [Dated live observation](live-control-startup.json).
