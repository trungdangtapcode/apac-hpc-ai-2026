# S55 target-only control for unranked EAGLE3 performance exploration

This prospective source bundle derives from S46. It retains the S46 deterministic BF16 target runtime, all-rank NIXL/runtime checks, native 188-region target geometry, and both P/D semantic warmups. It uses the shared S55/S56 worker and topology source; `QWEN_HAS_DRAFT=0` selects target-only decoding. The common serving flags match S56.

The post-readiness stage runs one AIPerf N=64 point (20-second warmup, 40-second measurement, 30-second grace; fixed 4000 input and 200 output tokens, seed 2026), then the same eight-case smoke check and 12 retrieval checks used by S56. The independent head checker requires the raw AIPerf input configuration, request counts, SLA values, zero errors/cancellations, at least 7/8 smoke responses without a known regression, all 12 retrieval responses, runtime readiness, native geometry, and both semantic P/D paths.

Job wall time is hard capped at 17 minutes (1,020 seconds), with a 600-second startup deadline, 120-second semantic warmup window, client deadline at 960 seconds, head-check deadline at 980 seconds, and bounded teardown. The batch script verifies the model/image manifest and the pinned AIPerf image identity before launching topology.

The pair is unranked and quality is UNKNOWN. This bundle does not evaluate official accuracy and does not make a speedup claim. Root review and a root-owned submission controller remain required. No job was submitted and no GPU or endpoint action was taken during preparation.
