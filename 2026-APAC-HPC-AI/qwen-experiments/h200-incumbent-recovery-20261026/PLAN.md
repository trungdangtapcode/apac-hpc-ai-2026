# Preserve and isolate the 3k incumbent

The owner asks why older runs achieved ~3k good output tokens/s while recent results are ~2.56k, and whether the direction is exhausted. Three retained full-protocol runs average 3044.400475 tokens/s, but recent controls changed both duration and native prefill behavior. Direct inspection of real 25487 and 26083 ServerArgs proves breakable→disabled prefill CUDA graph and native max_running_requests=None → 64. Auto → explicit BF16 dtype and a geometry-instrumented NIXL wrapper are additional harness differences; actual old KV was BF16. No single causal attribution follows.

One replay and three controlled full runs answer distinct questions:

| Arm | Purpose | Prefill graph | Prefill request cap | Protocol |
|---|---|---|---|---|
| S69 | Reproduce legacy incumbent | Native breakable | Native(None) | 60/120/30 |
| S70 | Modern full control | Disabled | 64 | 60/120/30 |
| S71 | Isolate graph from S70 | Breakable | 64 | 60/120/30 |
| S72 | Isolate admission from S71 | Breakable | Native(None) | 60/120/30 |

All use 16 H200, N64, fixed 4000/200, client seed 2026, cold-prefix recipe and the FP8 target. S69 keeps all 15 legacy operational files byte-identical to 25487, including separately post-score profiling; only metadata and job bundle path/name differ. The modern arms have the same current semantic/native KV/runtime/raw workload/output/error gates. Their benchmark phase is explicitly confirm with full 60/120/30. S70/S71 differ only in prefill graph; S71/S72 differ only in explicit cap. S69/S72 cross-harness comparison does not isolate every remaining difference. A longer full protocol is deliberate regression diagnosis, not confirmation of losing fusion/router arms.

CPU checks replay actual 25487 full raw export (1901 requests, 3044.637094 tokens/s), reject wrong warmup, validate synthetic graph/admission fixtures and reject missing graph completion. These fixtures are explicitly not candidate GPU execution. The initial fixture assumed one max_running_requests text occurrence; two actual native log records existed, and the fixture was corrected before submission. All payload source/syntax/hash checks pass. Old source bundles remain immutable.

Accept only valid runtime/complete graph capture on all intended ranks, complete raw fixed workload/denominator, joint TTFT<=3000ms and request-mean ITL<=20ms for >=90% including failures, zero errors/cancellations, smoke>=7/8 without regression and retrieval 12/12. Official full-set 99% accuracy remains unverified. Need >1% paired good-output improvement plus useful tails to justify independent confirmation. Reproducing the incumbent preserves a baseline; it is not a new best score. Close losing treatment arms rather than repeat unchanged.

Collect and inspect tails/errors/concurrency, role logs/queue/KV, available CPU/GPU/VRAM and transport evidence. Client-bounded sampler windows include warmup/grace, not just profiling; report this scope. Legacy heavy profiles stay after scoring. Do not infer GPU FLOPS/saturation or a cause from activity samples. Keep actual repeated seed/host/clock differences visible.

Admission: four new 16-GPU/two-node/17-minute jobs, plus separately submitted component 26308 within cap 5. Use a definite afterany chain so control order remains visible without unsatisfiable afterok dependencies. An invalid control blocks a paired interpretation, while another full arm can still be inspected independently. Fresh queue check and sealed payloads required before every admission. No PBS SU, new budget, background Codex or submission-material update. Save definite IDs promptly and preserve all outcomes.
